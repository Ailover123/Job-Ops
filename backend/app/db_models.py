from datetime import datetime, timezone
from typing import List, Optional
from sqlmodel import SQLModel, Field, JSON, Column

class Profile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str = ""
    email: str = ""
    phone: str = ""
    
    # Store complex structures as JSON
    location: dict = Field(default_factory=dict, sa_column=Column(JSON))
    education: List[dict] = Field(default_factory=list, sa_column=Column(JSON))
    skills: List[dict] = Field(default_factory=list, sa_column=Column(JSON))
    projects: List[dict] = Field(default_factory=list, sa_column=Column(JSON))
    certifications: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    suggested_roles: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    preferred_domains: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SavedJob(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_external_id: str = Field(index=True, unique=True)
    job_title: str
    company_name: str
    location: str = "Unknown"
    source_name: str
    apply_url: str
    skills: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    saved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Application(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_external_id: str = Field(index=True, unique=True)
    job_title: str
    company_name: str
    location: str = "Unknown"
    source_name: str
    apply_url: str
    skills: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    status: str = "applied"  # e.g., applied, interviewing, offered, rejected
    applied_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: str = ""


class Preferences(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    preferred_roles: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    preferred_locations: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    remote_preference: str = "remote_or_hybrid"
    job_types: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    preferred_tech_stack: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    willing_to_relocate: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    external_id: str = Field(index=True, unique=True)
    title: str
    company_name: str
    description: str
    location: str
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    is_remote: bool = False
    job_type: str
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    skills: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    apply_url: str
    source_name: str
    posted_at: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CollectorSource(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company_name: str
    board_token: Optional[str] = None
    company_id: Optional[str] = None
    source_type: str  # greenhouse or lever
    enabled: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


