from phi.agent import Agent
from phi.model.openai import OpenAIChat

def get_candidate_agent(resume_text: str, desired_salary: str):
    return Agent(
        model=OpenAIChat(id="gpt-4o"),
        name="Candidate Representative",
        instructions=[
            f"You represent a job seeker with this resume: {resume_text}",
            f"Your goal is to get the job, but your desired salary is {desired_salary}.",
            "1. Highlight skills that match the job description.",
            "2. If the budget is too low, negotiate politely but firmly.",
            "3. Keep your responses short (max 2 sentences).",
            "4. If the offer is good, say 'AGREED'."
        ],
        show_tool_calls=False,
        markdown=True
    )

def get_hr_agent(job_description: str, max_budget: str):
    return Agent(
        model=OpenAIChat(id="gpt-4o"),
        name="HR Recruiter",
        instructions=[
            f"You are hiring for this role: {job_description}",
            f"Your absolute maximum budget is {max_budget}. Try to get them cheaper.",
            "1. Assess if the candidate has the required skills.",
            "2. If they are unqualified, say 'REJECTED'.",
            "3. If they are qualified, negotiate salary.",
            "4. Keep your responses short (max 2 sentences).",
            "5. If you reach a deal, say 'HIRED'."
        ],
        show_tool_calls=False,
        markdown=True
    )