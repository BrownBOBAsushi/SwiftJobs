import os
import json
import io
from pathlib import Path
from dotenv import load_dotenv

# --- STEP 1: LOAD ENVIRONMENT VARIABLES FIRST ---
# We do this BEFORE importing anything else to ensure keys are ready.
# This fixes the issue where Python looks in the wrong folder.
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# --- STEP 2: VERIFY KEYS (Debug Check) ---
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")

if not supabase_key:
    print("❌ CRITICAL ERROR: SUPABASE_SERVICE_KEY is missing from backend/.env")
    print("   Make sure your .env file is inside the 'backend' folder and named correctly.")
else:
    print(f"✅ Loaded API Key starting with: {supabase_key[:10]}...")

# --- STEP 3: IMPORT LIBRARIES ---
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from pypdf import PdfReader
import openai

# Import the brains (Agents)
from agents import get_candidate_agent, get_hr_agent

# --- STEP 4: INITIALIZE APP & DB ---
app = FastAPI()

# Fix CORS to allow your Next.js frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase Client
# We use the keys we loaded in Step 1
if supabase_url and supabase_key:
    supabase: Client = create_client(supabase_url, supabase_key)
else:
    print("⚠️ Supabase client could not be initialized due to missing keys.")

# --- HELPER FUNCTIONS ---

def evaluate_match(chat_history, job_description):
    """
    Uses OpenAI to judge the negotiation and decide if the candidate is hired.
    """
    client = openai.OpenAI() # Uses OPENAI_API_KEY from .env automatically
    
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
    candidate_id: str = "anon_user"
    job_id: str
    resume_text: str
    job_description: str
    candidate_salary: str = "$5000"
    hr_budget: str = "$4500"

@app.post("/negotiate")
async def start_negotiation(data: NegotiationRequest):
    print(f"⚔️ Starting battle: Job {data.job_id} vs Candidate")

    # 1. Initialize Agents
    candidate_agent = get_candidate_agent(data.resume_text, data.candidate_salary)
    hr_agent = get_hr_agent(data.job_description, data.hr_budget)

    chat_log = []
    
    # 2. Initial Prompt
    last_message = "I have reviewed your application. Briefly explain why you fit this role."
    chat_log.append({"sender": "HR", "message": last_message})
    
    # 3. Run the Battle (Max 4 turns each)
    for i in range(4):
        # Candidate Turn
        print(f"   Turn {i+1}: Candidate thinking...")
        response_c = candidate_agent.run(last_message)
        c_text = response_c.content
        chat_log.append({"sender": "Candidate", "message": c_text})
        
        # HR Turn
        print(f"   Turn {i+1}: HR thinking...")
        response_hr = hr_agent.run(c_text)
        hr_text = response_hr.content
        chat_log.append({"sender": "HR", "message": hr_text})
        
        last_message = hr_text
        
        # Stop early if they agree/reject explicitly
        if "HIRED" in hr_text or "REJECTED" in hr_text:
            break

    # 4. Judgment Day
    print("👨‍⚖️ Calling the Judge...")
    judgment = evaluate_match(chat_log, data.job_description)
    print(f"⚖️ Verdict: {judgment['decision']} (Score: {judgment['score']})")
    
    # 5. Save to Supabase
    try:
        supabase.table("negotiations").insert({
            "job_id": data.job_id,
            "candidate_id": data.candidate_id,
            "chat_log": chat_log,
            "status": judgment["decision"],
            "agreed_salary": judgment["score"] # Storing score as int
        }).execute()
        print("✅ Saved to Database")
    except Exception as e:
        print(f"❌ Database Error: {e}")
        # We don't crash the app here, just print the error so the user still gets a result

    return {
        "status": judgment["decision"],
        "score": judgment["score"],
        "reason": judgment["reason"],
        "log": chat_log
    }

@app.post("/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    print(f"📄 Parsing PDF: {file.filename}")
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
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)