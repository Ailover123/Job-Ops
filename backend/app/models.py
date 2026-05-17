from pydantic import BaseModel, Field


class SeedJob(BaseModel):
    external_id: str
    title: str
    company_name: str
    description: str
    location: str
    city: str | None = None
    state: str | None = None
    country: str | None = None
    is_remote: bool = False
    job_type: str
    experience_min: int | None = None
    experience_max: int | None = None
    skills: list[str] = Field(default_factory=list)
    apply_url: str
    source_name: str
    posted_at: str | None = None
    is_active: bool = True


class CandidateProfile(BaseModel):
    preferred_roles: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    preferred_locations: list[str] = Field(default_factory=list)
    remote_preference: str = "remote_or_hybrid"
    job_types: list[str] = Field(default_factory=lambda: ["internship", "full_time"])
    experience_level: str = "fresher"
    willing_to_relocate: bool = False



class Recommendation(BaseModel):
    job: SeedJob
    skill_score: float
    fresher_score: float
    location_score: float
    experience_score: float
    quality_score: float
    final_score: int
    score_label: str
    explanation: str

