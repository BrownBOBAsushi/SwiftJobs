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


###############################NEW INTERVIEW SYSTEM##########################
class InterviewStartRequest(BaseModel):
    user_id: str
    role: str  # e.g., "Software Engineer", "Product Manager"
    job_description: str
    resume_text: str
    interview_type: str  # "behavioral", "technical", "case_study", "system_design", "mixed"
    difficulty: str = "medium"  # "easy", "medium", "hard", "expert"
    time_limit_minutes: Optional[int] = None  # For timed rounds
    enable_audio: bool = False  # Future: voice analysis


class InterviewAnswerRequest(BaseModel):
    interview_id: str
    answer_text: str
    audio_url: Optional[str] = None  # Future: S3/Supabase storage URL
    time_taken_seconds: Optional[int] = None


class FeedbackRequest(BaseModel):
    interview_id: str
    question_id: str


@app.post("/interview/start")
async def start_interview(data: InterviewStartRequest):
    """
    Start a new interview session.
    Returns the interview ID and first question.
    """
    print(f"🎤 Starting {data.interview_type} interview for {data.role}")
    
    # Analyze resume vs JD to detect skill gaps
    skill_gaps = await detect_skill_gaps(data.resume_text, data.job_description)
    
    # Generate question set
    questions = await generate_question_set(
        data.resume_text,
        data.job_description,
        data.role,
        data.interview_type,
        data.difficulty,
        skill_gaps
    )
    
    # Create interviewer agent
    interviewer = get_interviewer_agent(
        role=data.role,
        job_description=data.job_description,
        interview_type=data.interview_type,
        difficulty=data.difficulty,
        focus_skills=skill_gaps
    )
    
    # Save interview session to DB
    try:
        result = supabase.table("interviews").insert({
            "user_id": data.user_id,
            "role": data.role,
            "interview_type": data.interview_type,
            "difficulty": data.difficulty,
            "status": "in_progress",
            "questions": questions,
            "skill_gaps": skill_gaps,
            "time_limit_minutes": data.time_limit_minutes,
            "started_at": datetime.utcnow().isoformat(),
            "qa_log": []
        }).execute()
        
        interview_id = result.data[0]["id"]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create interview: {str(e)}")
    
    # Ask first question
    first_question = questions[0] if questions else "Tell me about yourself and why you're interested in this role."
    
    return {
        "interview_id": interview_id,
        "current_question": first_question,
        "question_number": 1,
        "total_questions": len(questions),
        "skill_gaps_detected": skill_gaps,
        "time_limit_minutes": data.time_limit_minutes
    }


@app.post("/interview/answer")
async def submit_answer(data: InterviewAnswerRequest):
    """
    Submit an answer to the current question.
    Returns instant feedback + next question.
    """
    print(f"💬 Answer submitted for interview {data.interview_id}")
    
    # Fetch interview session
    try:
        result = supabase.table("interviews").select("*").eq("id", data.interview_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        interview = result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Get current question
    qa_log = interview.get("qa_log", [])
    current_q_index = len(qa_log)
    questions = interview.get("questions", [])
    
    if current_q_index >= len(questions):
        return {"message": "Interview complete", "has_next": False}
    
    current_question = questions[current_q_index]
    
    # Analyze audio if provided (future feature)
    audio_analysis = None
    if data.audio_url:
        audio_analysis = await analyze_audio(data.audio_url)
    
    # Generate instant feedback
    feedback = await generate_feedback(
        question=current_question,
        answer=data.answer_text,
        interview_type=interview["interview_type"],
        role=interview["role"]
    )
    
    # Save Q&A to log
    qa_entry = {
        "question": current_question,
        "answer": data.answer_text,
        "feedback": feedback,
        "time_taken_seconds": data.time_taken_seconds,
        "audio_analysis": audio_analysis,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    qa_log.append(qa_entry)
    
    # Update database
    supabase.table("interviews").update({
        "qa_log": qa_log
    }).eq("id", data.interview_id).execute()
    
    # Check if more questions
    next_q_index = current_q_index + 1
    has_next = next_q_index < len(questions)
    
    response = {
        "feedback": feedback,
        "has_next": has_next,
        "question_number": next_q_index + 1 if has_next else None,
        "total_questions": len(questions)
    }
    
    if has_next:
        response["next_question"] = questions[next_q_index]
    else:
        # Interview complete - generate final report
        final_report = await generate_final_report(data.interview_id, interview)
        response["final_report"] = final_report
        
        # Mark as complete
        supabase.table("interviews").update({
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "final_report": final_report
        }).eq("id", data.interview_id).execute()
    
    return response


@app.get("/interview/{interview_id}/report")
async def get_interview_report(interview_id: str):
    """
    Get the full interview report with analytics.
    """
    try:
        result = supabase.table("interviews").select("*").eq("id", interview_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        interview = result.data[0]
        
        if interview["status"] != "completed":
            return {"message": "Interview not yet completed"}
        
        return {
            "interview_id": interview_id,
            "role": interview["role"],
            "interview_type": interview["interview_type"],
            "difficulty": interview["difficulty"],
            "started_at": interview["started_at"],
            "completed_at": interview.get("completed_at"),
            "qa_log": interview["qa_log"],
            "final_report": interview.get("final_report"),
            "skill_gaps": interview.get("skill_gaps")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= HELPER FUNCTIONS =============

async def detect_skill_gaps(resume_text: str, job_description: str) -> List[str]:
    """
    Analyze resume vs JD to find missing skills.
    """
    client = openai.OpenAI()
    
    prompt = f"""
    Compare this resume against the job description and identify SKILL GAPS.
    
    Resume:
    {resume_text}
    
    Job Description:
    {job_description}
    
    Return ONLY a JSON array of missing skills that are in the JD but not clearly in the resume.
    Example: ["Python", "Leadership", "SQL", "Public Speaking"]
    
    Keep it to top 5 most important gaps.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        return result.get("skills", [])
    except Exception as e:
        print(f"Skill gap detection error: {e}")
        return []


async def generate_question_set(
    resume_text: str,
    job_description: str,
    role: str,
    interview_type: str,
    difficulty: str,
    skill_gaps: List[str]
) -> List[str]:
    """
    Generate intelligent questions based on context.
    """
    client = openai.OpenAI()
    
    skill_context = f"Focus on these skill gaps: {', '.join(skill_gaps)}" if skill_gaps else ""
    
    prompt = f"""
    Generate 8-10 interview questions for a {role} position.
    
    Interview Type: {interview_type}
    Difficulty: {difficulty}
    {skill_context}
    
    Resume:
    {resume_text[:1000]}
    
    Job Description:
    {job_description[:1000]}
    
    Rules:
    1. Mix easy warmup questions with harder technical/behavioral questions
    2. Probe skills mentioned in resume to verify authenticity
    3. Ask questions that expose skill gaps
    4. Use STAR-method friendly questions for behavioral
    5. Include follow-up depth questions
    
    Return ONLY a JSON array of question strings.
    Example: ["Tell me about yourself", "Describe a time when...", "How would you design..."]
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        return result.get("questions", [
            "Tell me about yourself and your background.",
            "Why are you interested in this role?",
            "What's your greatest professional achievement?"
        ])
    except Exception as e:
        print(f"Question generation error: {e}")
        return ["Tell me about yourself.", "Why this role?", "Tell me about a challenge you faced."]


async def generate_feedback(question: str, answer: str, interview_type: str, role: str) -> dict:
    """
    Generate brutal, actionable feedback using the feedback agent.
    """
    feedback_agent = get_feedback_agent()
    
    prompt = f"""
    Interview Type: {interview_type}
    Role: {role}
    
    QUESTION: {question}
    
    CANDIDATE ANSWER: {answer}
    
    Analyze this answer and provide feedback in this JSON format:
    {{
        "strengths": ["point 1", "point 2"],
        "weaknesses": ["point 1", "point 2"],
        "missing_keywords": ["keyword1", "keyword2"],
        "confidence_score": 0-100,
        "clarity_score": 0-100,
        "relevance_score": 0-100,
        "star_method_used": true/false,
        "quantified_impact": true/false,
        "ideal_answer": "Example of a strong answer",
        "rewrite_suggestion": "Improved version of their answer",
        "overall_grade": "A/B/C/D/F",
        "brutal_truth": "Direct, honest assessment"
    }}
    """
    
    try:
        response = feedback_agent.run(prompt)
        feedback_text = response.content
        
        # Try to parse as JSON, fallback to text
        try:
            return json.loads(feedback_text)
        except:
            return {
                "raw_feedback": feedback_text,
                "confidence_score": 70
            }
    except Exception as e:
        print(f"Feedback generation error: {e}")
        return {
            "error": "Feedback generation failed",
            "confidence_score": 50
        }


async def generate_final_report(interview_id: str, interview: dict) -> dict:
    """
    Generate comprehensive final report with benchmarking.
    """
    client = openai.OpenAI()
    
    qa_log = interview.get("qa_log", [])
    
    prompt = f"""
    Generate a comprehensive interview performance report.
    
    Role: {interview['role']}
    Interview Type: {interview['interview_type']}
    Difficulty: {interview['difficulty']}
    
    Q&A Log:
    {json.dumps(qa_log, indent=2)}
    
    Provide analysis in JSON format:
    {{
        "overall_score": 0-100,
        "overall_grade": "A/B/C/D/F",
        "hire_recommendation": "Strong Hire/Hire/Maybe/No Hire",
        "strengths": ["strength 1", "strength 2"],
        "weaknesses": ["weakness 1", "weakness 2"],
        "skill_verification": {{"skill": "verified/not_verified"}},
        "star_method_usage": "Excellent/Good/Poor",
        "communication_clarity": 0-100,
        "technical_depth": 0-100,
        "behavioral_maturity": 0-100,
        "red_flags": ["flag 1", "flag 2"],
        "standout_moments": ["moment 1"],
        "improvement_areas": ["area 1", "area 2"],
        "benchmark_percentile": 0-100,
        "summary": "2-3 sentence overall assessment"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Report generation error: {e}")
        return {"error": "Report generation failed"}


async def analyze_audio(audio_url: str) -> dict:
    """
    Future: Analyze voice recording for tone, pace, filler words.
    Placeholder for now.
    """
    # TODO: Integrate with speech-to-text + audio analysis API
    return {
        "tone": "confident",
        "pace": "medium",
        "filler_words_count": 3,
        "clarity_score": 85,
        "transcript": "Audio analysis coming soon"
    }


# ============= ADMIN/ANALYTICS ENDPOINTS =============

@app.get("/analytics/user/{user_id}")
async def get_user_analytics(user_id: str):
    """
    Get user's interview history and progress analytics.
    """
    try:
        result = supabase.table("interviews").select("*").eq("user_id", user_id).execute()
        interviews = result.data
        
        # Calculate stats
        total_interviews = len(interviews)
        completed = len([i for i in interviews if i["status"] == "completed"])
        
        avg_score = 0
        if completed > 0:
            scores = [i.get("final_report", {}).get("overall_score", 0) for i in interviews if i["status"] == "completed"]
            avg_score = sum(scores) / len(scores) if scores else 0
        
        return {
            "user_id": user_id,
            "total_interviews": total_interviews,
            "completed_interviews": completed,
            "average_score": round(avg_score, 1),
            "interviews": interviews
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

