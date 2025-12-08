import { NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'
import OpenAI from 'openai'
import pdf from 'pdf-parse'

// Initialize OpenAI
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
})

// Initialize Supabase Admin (needed to write embeddings securely)
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
)

export async function POST(req: Request) {
  try {
    const formData = await req.formData()
    const file = formData.get('file') as File
    const userId = formData.get('userId') as string

    if (!file || !userId) {
      return NextResponse.json({ error: 'Missing file or user ID' }, { status: 400 })
    }

    // 1. Convert File to Buffer for pdf-parse
    const bytes = await file.arrayBuffer()
    const buffer = Buffer.from(bytes)

    // 2. Extract Text from PDF
    const pdfData = await pdf(buffer)
    const resumeText = pdfData.text

    // 3. AI Extraction (Turn messy text into structured JSON)
    const completion = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [
        {
          role: "system",
          content: "You are a recruiter API. Extract structured data from the resume text. Return ONLY JSON. Fields: full_name (string), skills (array of strings), experience_years (number, estimate if needed), summary (string)."
        },
        {
          role: "user",
          content: resumeText
        }
      ],
      response_format: { type: "json_object" }
    })

    const profileData = JSON.parse(completion.choices[0].message.content || "{}")

    // 4. Generate Embedding (The Vector Math)
    // We embed the "skills" and "summary" so companies can search for them
    const embeddingResponse = await openai.embeddings.create({
      model: "text-embedding-3-small",
      input: `${profileData.summary} ${profileData.skills.join(", ")}`,
      encoding_format: "float",
    })

    const embedding = embeddingResponse.data[0].embedding

    // 5. Save everything to Supabase
    const { error } = await supabase
      .from('profiles')
      .update({
        role: 'applicant', // Force role
        full_name: profileData.full_name,
        extracted_skills: profileData.skills,
        experience_years: profileData.experience_years,
        embedding: embedding, // Save the vector!
        // In a real app, you'd upload the PDF to Supabase Storage and save the URL here
        // resume_url: publicUrl 
      })
      .eq('id', userId)

    if (error) throw error

    return NextResponse.json({ success: true, data: profileData })

  } catch (error: any) {
    console.error('Resume parse error:', error)
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}