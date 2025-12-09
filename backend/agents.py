from phi.agent import Agent
from phi.model.openai import OpenAIChat
from typing import List,Dict
import json

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
#############################NEW Interview Agent############################

def get_interviewer_agent(
    role: str,
    job_description: str,
    interview_type: str,
    difficulty: str = "medium",
    focus_skills: List[str] = None
):
    """
    Creates an AI interviewer agent tailored to specific roles and interview types.
    
    Args:
        role: Job role (e.g., "Software Engineer", "Product Manager", "Marketing Manager")
        job_description: Full JD text
        interview_type: "behavioral", "technical", "case_study", "system_design", "mixed"
        difficulty: "easy", "medium", "hard", "expert"
        focus_skills: Specific skills to probe (e.g., ["Python", "Leadership", "SQL"])
    """
    
    focus_context = ""
    if focus_skills:
        focus_context = f"\nFOCUS SKILLS TO PROBE: {', '.join(focus_skills)}"
    
    type_instructions = {
        "behavioral": [
            "Ask STAR-method friendly questions (Situation, Task, Action, Result).",
            "Probe for specific examples, not generic answers.",
            "Follow up if answers lack concrete details or metrics.",
            "Examples: 'Tell me about a time when...', 'Describe a situation where...'",
        ],
        "technical": [
            "Ask role-specific technical questions with increasing complexity.",
            "Request code snippets, algorithms, or technical explanations.",
            "Challenge assumptions and ask follow-up 'what if' scenarios.",
            "Verify depth of understanding, not just surface knowledge.",
        ],
        "case_study": [
            "Present a business problem or scenario relevant to the role.",
            "Ask how they would approach solving it step-by-step.",
            "Probe their analytical thinking, not just the final answer.",
            "Introduce constraints or new information mid-case.",
        ],
        "system_design": [
            "Ask to design a scalable system (e.g., URL shortener, ride-sharing app).",
            "Probe trade-offs, bottlenecks, and technology choices.",
            "Ask about scalability, fault tolerance, and data consistency.",
            "Challenge their design with real-world constraints.",
        ],
        "mixed": [
            "Combine behavioral and technical questions naturally.",
            "Start with behavioral warmup, then increase technical difficulty.",
            "Assess both soft skills and hard skills.",
        ]
    }
    
    difficulty_modifiers = {
        "easy": "Keep questions straightforward and foundational. Suitable for junior roles.",
        "medium": "Ask standard interview questions with moderate complexity.",
        "hard": "Introduce complex scenarios, edge cases, and trade-offs.",
        "expert": "Ask architect-level or expert-level questions with deep technical depth."
    }
    
    base_instructions = [
        f"You are interviewing for: {role}",
        f"Job Description: {job_description}",
        f"Interview Type: {interview_type.upper()}",
        f"Difficulty Level: {difficulty_modifiers[difficulty]}",
        focus_context,
        "\n=== CORE BEHAVIOR ===",
        "1. Ask ONE question at a time. Wait for the candidate's full response.",
        "2. Be professional but conversational, not robotic.",
        "3. If an answer is vague, ask clarifying follow-ups.",
        "4. Take notes mentally on: clarity, depth, examples, metrics, red flags.",
        "5. Adjust difficulty based on candidate performance.",
        "\n=== QUESTION STRATEGY ===",
    ]
    
    base_instructions.extend(type_instructions.get(interview_type, type_instructions["mixed"]))
    
    base_instructions.extend([
        "\n=== RESPONSE FORMAT ===",
        "Keep questions under 80 words.",
        "Be direct and clear.",
        "Do NOT give feedback during the interview—save that for the end.",
    ])
    
    return Agent(
        model=OpenAIChat(id="gpt-4o"),  # Use GPT-4 for better interview quality
        name=f"{role} Interviewer",
        instructions=base_instructions,
        markdown=True
    )


def get_feedback_agent():
    """
    Creates an agent that provides brutal, actionable feedback on interview answers.
    """
    return Agent(
        model=OpenAIChat(id="gpt-4o"),
        name="Interview Coach",
        instructions=[
            "You are a brutally honest interview coach.",
            "Your job is to analyze interview answers and give ACTIONABLE feedback.",
            "\n=== ANALYSIS FRAMEWORK ===",
            "1. STRUCTURE: Did they use STAR method (Situation, Task, Action, Result)?",
            "2. SPECIFICITY: Did they give concrete examples with metrics/numbers?",
            "3. RELEVANCE: Did they answer the actual question asked?",
            "4. CLARITY: Was the answer clear and concise, or rambling?",
            "5. IMPACT: Did they quantify results? (e.g., 'increased revenue by 30%')",
            "6. RED FLAGS: Generic answers, lying, contradictions, irrelevant stories.",
            "\n=== FEEDBACK FORMAT ===",
            "Provide feedback in this structure:",
            "- **STRENGTHS**: What they did well (be specific)",
            "- **WEAKNESSES**: What was missing or weak (be direct)",
            "- **MISSING KEYWORDS**: Skills/terms they should have mentioned",
            "- **CONFIDENCE SCORE**: 0-100 based on clarity and conviction",
            "- **IDEAL ANSWER**: Show them what a strong answer looks like",
            "- **REWRITE**: Rewrite their answer to be stronger",
            "\n=== TONE ===",
            "Be direct and tough, but not mean. Think 'tough love coach'.",
            "No corporate jargon. Use plain English.",
            "Call out BS. If they're being vague, say 'This is too generic.'",
        ],
        markdown=True
    )


def get_question_generator_agent(
    resume_text: str,
    job_description: str,
    role: str,
    skill_gaps: List[str] = None,
    difficulty: str = "medium"
):
    """
    Generates intelligent interview questions based on resume, JD, and skill gaps.
    """
    
    skill_gap_context = ""
    if skill_gaps:
        skill_gap_context = f"\nDETECTED SKILL GAPS (probe these harder): {', '.join(skill_gaps)}"
    
    return Agent(
        model=OpenAIChat(id="gpt-4o-mini"),
        name="Question Generator",
        instructions=[
            f"You are generating interview questions for a {role} role.",
            f"Candidate Resume: {resume_text}",
            f"Job Description: {job_description}",
            skill_gap_context,
            f"Difficulty: {difficulty}",
            "\n=== GENERATION RULES ===",
            "1. Generate questions that match the JD requirements.",
            "2. Probe skills mentioned in the resume to verify authenticity.",
            "3. If skill gaps detected, create questions to expose those gaps.",
            "4. Mix behavioral and technical questions.",
            "5. Increase difficulty progressively.",
            "\n=== OUTPUT FORMAT ===",
            "Return JSON array of questions:",
            '[{"question": "...", "type": "behavioral/technical", "skill": "...", "difficulty": "easy/medium/hard"}]',
        ],
        markdown=True
    )