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
