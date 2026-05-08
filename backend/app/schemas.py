from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

class LocationInfo(BaseModel):
    city: str = ""
    state: str = ""
    country: str = ""

class EducationEntry(BaseModel):
    degree: str = ""
    institution: str = ""
    year: str = ""
    score: str = ""

class SkillEntry(BaseModel):
    name: str = ""
    type: str = ""  # e.g., "technical", "soft", "tool"
    confidence: float = 1.0

class ProjectEntry(BaseModel):
    title: str = ""
    description: str = ""
    tech_stack: List[str] = Field(default_factory=list)
    url: str = ""

class ResumeProfile(BaseModel):
    full_name: str = ""
    email: str = ""
    phone: str = ""
    location: LocationInfo = Field(default_factory=LocationInfo)
    education: List[EducationEntry] = Field(default_factory=list)
    skills: List[SkillEntry] = Field(default_factory=list)
    projects: List[ProjectEntry] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    suggested_roles: List[str] = Field(default_factory=list)
    preferred_domains: List[str] = Field(default_factory=list)

class ProfileExtractRequest(BaseModel):
    resume_text: str

class ProfileExtractResponse(BaseModel):
    profile: ResumeProfile
    extraction_method: str  # "gemini" or "fallback"
