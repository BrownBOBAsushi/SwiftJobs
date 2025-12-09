import os
import json
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client
from pypdf import PdfReader
import io
import openai # We use raw openai for the Judge

# Import the brains
from agents import get_candidate_agent, get_hr_agent

load_dotenv()

# Initialize Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(url, key)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- THE JUDGE FUNCTION ---
def evaluate_match(chat_history, job_description):
    client = openai.OpenAI()
    
    prompt = f"""
    Act as a Hiring Manager Judge. 
    Review this negotiation chat between a Candidate Agent and an HR Agent.
    
    Job Description: {job_description}
    Chat Log: {json.dumps(chat_history)}
    
    Task:
    1. Did the candidate prove they have the skills? (Check for honesty).
    2. Did they reach a salary agreement?
    3. Give a score from 0 to 100.
       - < 50: Bad fit, lying, or too expensive.
       - 50-75: Good fit, but gap in salary or skills.
       - 75-90: Great fit.
       - > 95: Perfect match (Skills + Salary agreed).
    
    Output JSON ONLY: {{ "score": int, "reason": "string", "decision": "HIRED" | "REJECTED" }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Judge Error: {e}")
        return {"score": 0, "reason": "Judge failed", "decision": "ERROR"}

# --- ENDPOINTS ---

class NegotiationRequest(BaseModel):
    candidate_id: str
    job_id: str
    resume_text: str
    job_description: str
    candidate_salary: str = "$5000"
    hr_budget: str = "$4500"

@app.post("/negotiate")
async def start_negotiation(data: NegotiationRequest):
    print(f"Starting battle: Job {data.job_id} vs Candidate {data.candidate_id}")

    candidate_agent = get_candidate_agent(data.resume_text, data.candidate_salary)
    hr_agent = get_hr_agent(data.job_description, data.hr_budget)

    chat_log = []
    
    # Initial Prompt
    last_message = "I have reviewed your application. Briefly explain why you fit this role."
    chat_log.append({"sender": "HR", "message": last_message})
    
    # Run the battle (Max 4 turns each)
    for _ in range(4):
        # Candidate Turn
        response_c = candidate_agent.run(last_message)
        c_text = response_c.content
        chat_log.append({"sender": "Candidate", "message": c_text})
        
        # HR Turn
        response_hr = hr_agent.run(c_text)
        hr_text = response_hr.content
        chat_log.append({"sender": "HR", "message": hr_text})
        
        last_message = hr_text
        
        # Stop early if they agree/reject explicitly
        if "HIRED" in hr_text or "REJECTED" in hr_text:
            break

    # --- JUDGMENT DAY (This fixes the abrupt stop) ---
    print("👨‍⚖️ Calling the Judge...")
    judgment = evaluate_match(chat_log, data.job_description)
    
    # Save to Supabase
    try:
        supabase.table("negotiations").insert({
            "job_id": data.job_id,
            "candidate_id": data.candidate_id,
            "chat_log": chat_log,
            "status": judgment["decision"],
            "agreed_salary": judgment["score"] # Hack: storing score in salary col for now
        }).execute()
    except Exception as e:
        print(f"Database Error: {e}")

    return {
        "status": judgment["decision"],
        "score": judgment["score"],
        "reason": judgment["reason"],
        "log": chat_log
    }

@app.post("/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    print(f"📄 Receiving file: {file.filename}")
    try:
        contents = await file.read()
        pdf_file = io.BytesIO(contents)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return {"filename": file.filename, "text": text}
    except Exception as e:
        return {"error": str(e), "text": ""}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)