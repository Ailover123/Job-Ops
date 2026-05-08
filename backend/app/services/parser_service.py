import os
import json
import re
from typing import Optional
from google import genai
from pydantic import ValidationError
from app.schemas import ResumeProfile, LocationInfo, EducationEntry, SkillEntry, ProjectEntry

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Simple keyword sets for fallback extraction
TECH_SKILLS = {"python", "javascript", "react", "node", "fastapi", "sql", "git", "java", "c++", "aws", "docker"}
SOFT_SKILLS = {"communication", "leadership", "teamwork", "problem solving", "agile"}

def extract_profile_from_text(resume_text: str) -> (ResumeProfile, str):
    """
    Main entry point for profile extraction.
    Attempts Gemini extraction, falls back to deterministic extraction if needed.
    """
    if not resume_text or not resume_text.strip():
        return _extract_with_fallback(""), "fallback"

    # Try Gemini first if key is present
    if GEMINI_API_KEY:
        try:
            profile = _extract_with_gemini(resume_text)
            if profile:
                return profile, "gemini"
        except Exception as e:
            print(f"Gemini extraction failed: {e}")

    # Fallback
    return _extract_with_fallback(resume_text), "fallback"

def _extract_with_gemini(resume_text: str) -> Optional[ResumeProfile]:
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
    Extract the following information from the resume text and return it as a VALID JSON object.
    Follow the schema strictly. Do not add any text outside the JSON.
    
    Resume Text:
    {resume_text}
    
    JSON Schema:
    {{
      "full_name": "",
      "email": "",
      "phone": "",
      "location": {{ "city": "", "state": "", "country": "" }},
      "education": [{{ "degree": "", "institution": "", "year": "", "score": "" }}],
      "skills": [{{ "name": "", "type": "", "confidence": 1.0 }}],
      "projects": [{{ "title": "", "description": "", "tech_stack": [], "url": "" }}],
      "certifications": [],
      "suggested_roles": [],
      "preferred_domains": []
    }}
    """
    
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    
    try:
        # Clean up response text in case of markdown blocks
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3].strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:-3].strip()
            
        data = json.loads(raw_text)
        return ResumeProfile(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"Validation or Parse error on Gemini output: {e}")
        return None

def _extract_with_fallback(text: str) -> ResumeProfile:
    """
    Simple regex and keyword based extraction for fallback.
    """
    profile = ResumeProfile()
    
    if not text:
        return profile

    # Extract email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        profile.email = email_match.group(0)

    # Extract phone (basic pattern)
    phone_match = re.search(r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}', text)
    if phone_match:
        profile.phone = phone_match.group(0)

    # Extract skills by matching keywords using regex for word boundaries
    text_lower = text.lower()
    for skill in TECH_SKILLS:
        if re.search(rf'\b{re.escape(skill)}\b', text_lower):
            profile.skills.append(SkillEntry(name=skill.capitalize() if skill != 'sql' else 'SQL', type="technical", confidence=0.7))
    
    for skill in SOFT_SKILLS:
        if re.search(rf'\b{re.escape(skill)}\b', text_lower):
            profile.skills.append(SkillEntry(name=skill.capitalize(), type="soft", confidence=0.7))

    # Rough suggested roles
    found_tech = {s.name.lower() for s in profile.skills if s.type == "technical"}
    if found_tech:
        if "python" in found_tech or "fastapi" in found_tech:
            profile.suggested_roles.append("Python Developer")
        if "javascript" in found_tech or "react" in found_tech:
            profile.suggested_roles.append("Frontend Developer")
            
    return profile
