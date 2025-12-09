import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client

# Import the brains
from agents import get_candidate_agent, get_hr_agent

load_dotenv()

# Initialize Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")

# ERROR PREVENTION: Check if keys exist
if not url or not key:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env file")

supabase: Client = create_client(url, key)

# THIS IS THE LINE YOU WERE MISSING
app = FastAPI()

# Data Model
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

    # 1. Initialize the Agents
    candidate_agent = get_candidate_agent(data.resume_text, data.candidate_salary)
    hr_agent = get_hr_agent(data.job_description, data.hr_budget)

    # 2. The Conversation Log
    chat_log = []
    
    # 3. Start the Loop (HR speaks first)
    last_message = "I have reviewed your application. Briefly explain why you fit this role."
    chat_log.append({"sender": "HR", "message": last_message})
    
    status = "PENDING"
    
    # Max 4 turns each (8 total steps) to save time/money
    for _ in range(4):
        # -- Candidate Turn --
        response_c = candidate_agent.run(last_message)
        c_text = response_c.content
        chat_log.append({"sender": "Candidate", "message": c_text})
        
        if "AGREED" in c_text:
            status = "MATCH"
            break

        # -- HR Turn --
        response_hr = hr_agent.run(c_text)
        hr_text = response_hr.content
        chat_log.append({"sender": "HR", "message": hr_text})

        if "HIRED" in hr_text:
            status = "MATCH"
            break
        if "REJECTED" in hr_text:
            status = "REJECTED"
            break
        
        last_message = hr_text

    # 4. Save to Supabase
    try:
        supabase.table("negotiations").insert({
            "job_id": data.job_id,
            "candidate_id": data.candidate_id,
            "chat_log": chat_log,
            "status": status
        }).execute()
    except Exception as e:
        print(f"Database Error: {e}")

    return {
        "status": status,
        "log": chat_log
    }

@app.get("/")
def home():
    return {"status": "Agentic Negotiation System Online"}