from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.model.groq import Groq

def get_candidate_agent(resume_text: str, desired_salary: str):
    return Agent(
        model=OpenAIChat(id="gpt-4o-mini"),
        name="Candidate Representative",
        instructions=[
            f"You represent a job seeker with this resume: {resume_text}",
            f"Your GOAL salary is {desired_salary}.",
            "1. INTEGRITY CHECK: You can ONLY claim skills listed in the resume. Do NOT lie.",
            "2. If asked about a skill you don't have, admit it, but say you are a fast learner.",
            "3. If the offer is low, ask for non-monetary benefits (Remote work, Equity).",
            "4. Be confident but grounded in the resume's reality.",
            "5. Keep responses conversational and under 60 words."
        ],
        markdown=True
    )

def get_hr_agent(job_description: str, budget: str):
    return Agent(
        name="HR Agent",
        # --- CHANGE THIS SECTION ---
        # Old: model=OpenAIChat(id="gpt-4o"),
        # New: Use Groq with Llama 3.3 (Fastest) or DeepSeek
        model=Groq(id="llama-3.3-70b-versatile"), 
        # ---------------------------
        role=f"You are a Hiring Manager negotiating a job offer. Job Description: {job_description}. Budget: {budget}.",
        instructions=[
            "Negotiate the salary fiercely but professionally.",
            "Do not agree to a salary higher than your budget.",
            "Keep responses short (under 2 sentences).", # Speed hack
            "If the candidate matches the budget and skills, say 'HIRED'.",
            "If they are too expensive or unqualified, say 'REJECTED'."
        ],
        markdown=True
    )