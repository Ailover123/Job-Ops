import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from google import genai

from app.database import get_session
from app.db_models import Profile
from app.seed_loader import load_seed_jobs

router = APIRouter(tags=["roadmap"])

# Proper casings for a premium UI feel
SKILL_CASING = {
    "python": "Python",
    "sql": "SQL",
    "html": "HTML",
    "css": "CSS",
    "javascript": "JavaScript",
    "java": "Java",
    "c++": "C++",
    "git": "Git",
    "bash": "Bash",
    "react": "React",
    "next.js": "Next.js",
    "tailwind": "TailwindCSS",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "express": "Express",
    "node.js": "Node.js",
    "node": "Node.js",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scikit-learn": "Scikit-Learn",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "keras": "Keras",
    "machine learning": "Machine Learning",
    "data analysis": "Data Analysis",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "aws": "AWS",
    "gcp": "GCP",
    "azure": "Azure"
}

# Skill learning stages logic
SKILL_STAGES = {
    # Stage 1: Fundamentals
    "python": 1, "sql": 1, "html": 1, "css": 1, "javascript": 1, "java": 1, "c++": 1, "git": 1, "bash": 1,
    # Stage 2: Frameworks & Stores
    "react": 2, "next.js": 2, "tailwind": 2, "fastapi": 2, "django": 2, "flask": 2, "express": 2, "node.js": 2, "node": 2, "postgresql": 2, "mysql": 2, "mongodb": 2,
    # Stage 3: Data / Science / Ops
    "pandas": 3, "numpy": 3, "scikit-learn": 3, "tensorflow": 3, "pytorch": 3, "keras": 3, "machine learning": 3, "data analysis": 3, "docker": 3, "kubernetes": 3, "aws": 3, "gcp": 3, "azure": 3
}

class SkillGapRequest(BaseModel):
    desired_role: str

class SkillGapResponse(BaseModel):
    desired_role: str
    existing_skills: List[str]
    missing_skills: List[str]
    recommended_learning_order: List[str]
    suggested_project_ideas: List[str]
    matching_jobs_used_count: int
    explanation: str

@router.post("/roadmap/skill-gap", response_model=SkillGapResponse)
def get_skill_gap_roadmap(request: SkillGapRequest, session: Session = Depends(get_session)):
    desired_role = request.desired_role.strip()
    if not desired_role:
        raise HTTPException(status_code=400, detail="Desired role is required")

    # 1. Fetch latest profile skills
    statement = select(Profile).order_by(Profile.created_at.desc()).limit(1)
    results = session.exec(statement)
    db_profile = results.first()

    user_skills = []
    if db_profile and db_profile.skills:
        for s in db_profile.skills:
            name = s.get("name")
            if name:
                user_skills.append(name.strip())

    user_skills_lower = {s.lower() for s in user_skills}

    # 2. Match seed jobs
    seed_jobs = load_seed_jobs()
    matched_jobs = []
    
    desired_lower = desired_role.lower()
    
    # Check exact case-insensitive substring match
    for job in seed_jobs:
        if desired_lower in job.title.lower():
            matched_jobs.append(job)

    # Fallback to token-based matching if no exact matches found
    if not matched_jobs:
        generic_stopwords = {
            "intern", "fresher", "developer", "engineer", "trainee", "junior", 
            "senior", "lead", "associate", "software", "support", "role", 
            "position", "analyst", "in"
        }
        tokens = [t for t in desired_lower.replace("-", " ").replace("/", " ").split() if t not in generic_stopwords]
        
        if tokens:
            for job in seed_jobs:
                title_lower = job.title.lower()
                if any(token in title_lower for token in tokens):
                    matched_jobs.append(job)

    # 3. Aggregate common required skills from matched jobs
    common_skills = []
    skill_frequencies = {}

    for job in matched_jobs:
        for skill in job.skills:
            s_lower = skill.strip().lower()
            if s_lower:
                skill_frequencies[s_lower] = skill_frequencies.get(s_lower, 0) + 1

    # Sort common skills by frequency
    sorted_skills = sorted(skill_frequencies.keys(), key=lambda x: skill_frequencies[x], reverse=True)
    
    # Cap at top 8
    common_skills_lower = sorted_skills[:8]

    # Rule-based custom fallbacks if we matched no jobs or found no skills
    if not common_skills_lower:
        if any(w in desired_lower for w in ["ai", "ml", "machine", "learning", "science", "data"]):
            common_skills_lower = ["python", "machine learning", "pandas", "numpy", "pytorch", "scikit-learn", "sql", "git"]
        elif any(w in desired_lower for w in ["backend", "python", "django", "flask", "fastapi"]):
            common_skills_lower = ["python", "fastapi", "sql", "postgresql", "docker", "git", "aws", "redis"]
        elif any(w in desired_lower for w in ["frontend", "react", "next", "web", "html", "css", "js", "javascript"]):
            common_skills_lower = ["javascript", "react", "html", "css", "next.js", "tailwind", "git", "typescript"]
        else:
            common_skills_lower = ["python", "javascript", "git", "sql", "html", "css", "docker", "aws"]

    # Deduplicate and keep correct casings
    def get_cased_name(s_low: str) -> str:
        return SKILL_CASING.get(s_low, s_low.capitalize())

    # Map lower to cased
    existing_skills = []
    missing_skills = []

    for s_low in common_skills_lower:
        cased_name = get_cased_name(s_low)
        if s_low in user_skills_lower:
            existing_skills.append(cased_name)
        else:
            missing_skills.append(cased_name)

    # 4. Recommended Learning Order
    # Sort missing skills by stage ASC, then by frequency DESC (or just stage ASC)
    def get_stage_rank(skill_name: str) -> int:
        return SKILL_STAGES.get(skill_name.lower(), 4)

    recommended_learning_order = sorted(missing_skills, key=lambda x: get_stage_rank(x))

    # 5. Suggested Project Ideas
    suggested_project_ideas = []
    if any(w in desired_lower for w in ["ai", "ml", "machine", "learning", "science", "data"]):
        suggested_project_ideas = [
            "Build a personalized job recommendation engine utilizing Scikit-Learn and Pandas.",
            "Train a deep learning text classification model using PyTorch or TensorFlow.",
            "Deploy a robust prediction pipeline utilizing FastAPI and package it inside a Docker container."
        ]
    elif any(w in desired_lower for w in ["backend", "python", "django", "flask", "fastapi", "api"]):
        suggested_project_ideas = [
            "Build a comprehensive REST API using FastAPI with full SQLModel integration and JWT authentication.",
            "Design an asynchronous web scraping task queue leveraging Celery, Redis, and BeautifulSoup.",
            "Develop an optimized, relational e-commerce database system with complex query indexes."
        ]
    elif any(w in desired_lower for w in ["frontend", "react", "next", "web", "html", "css", "js", "javascript"]):
        suggested_project_ideas = [
            "Design a responsive candidate analytics dashboard featuring real-time interactive charts.",
            "Build a next-generation responsive developer portfolio with Next.js and static optimization.",
            "Implement a real-time multiplayer board game frontend using WebSockets and state-management."
        ]
    else:
        suggested_project_ideas = [
            "Build a full-stack job application tracker with dynamic status pipelines and search options.",
            "Create an E2E developer automation suite writing clean system logs to a database.",
            "Implement a CLI task organizer configured with user preferences and system reports."
        ]

    # 6. Optional Gemini Custom Tips
    explanation = ""
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        try:
            client = genai.Client(api_key=gemini_key)
            prompt = f"""
            Provide an inspiring, highly professional, 2-3 sentence personalized learning plan overview for a student pursuing a '{desired_role}' role.
            They already master: {', '.join(existing_skills) if existing_skills else 'none of the target skills yet'}.
            They should learn: {', '.join(missing_skills) if missing_skills else 'all target skills'}.
            Keep it extremely brief, actionable, encouraging, and direct. Do not include introductory or signature text.
            """
            response = client.models.generate_content(
                model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                contents=prompt,
            )
            explanation = response.text.strip()
        except Exception as e:
            # Fallback gracefully
            print(f"Gemini roadmap explanation failed: {e}")

    if not explanation:
        # High-quality fallback summary
        if existing_skills:
            explanation = f"Great start! You've already mastered key skills like {', '.join(existing_skills[:3])}. By picking up {', '.join(missing_skills[:3])} in the suggested order and building hands-on projects, you'll be highly competitive for '{desired_role}' roles."
        else:
            explanation = f"To land a '{desired_role}' role, starting with core skills like {', '.join(missing_skills[:3])} in our recommended learning order and building functional projects will give you an exceptional competitive edge."

    return SkillGapResponse(
        desired_role=desired_role,
        existing_skills=existing_skills,
        missing_skills=missing_skills,
        recommended_learning_order=recommended_learning_order,
        suggested_project_ideas=suggested_project_ideas,
        matching_jobs_used_count=len(matched_jobs),
        explanation=explanation
    )
