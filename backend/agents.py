from phi.agent import Agent
from phi.model.openai import OpenAIChat

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

def get_hr_agent(job_description: str, max_budget: str):
    return Agent(
        # OLD: model=OpenAIChat(id="gpt-4o"),
        # NEW:
        model=OpenAIChat(id="gpt-4o-mini"),
        name="HR Recruiter",
        instructions=[
            f"You are hiring for: {job_description}",
            f"Your HARD LIMIT budget is {max_budget}.",
            "1. First, verify they actually have the specific skills in the Job Description. Ask a technical question.",
            "2. If they are good, try to sell them on the 'Company Culture' or 'Growth' instead of just paying more.",
            "3. If you must pay more, ask for something in return (e.g., 'Can you start immediately?').",
            "4. Be polite but firm on the budget cap.",
            "5. Keep responses conversational and under 60 words."
        ],
        markdown=True
    )