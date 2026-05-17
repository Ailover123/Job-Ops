from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlmodel import Session, select, desc
from datetime import datetime, timezone
from typing import List, Optional
from app.database import get_session
from app.db_models import Preferences

router = APIRouter(tags=["preferences"])

class PreferencesRequest(BaseModel):
    preferred_roles: List[str] = Field(default_factory=list)
    preferred_locations: List[str] = Field(default_factory=list)
    remote_preference: str = "remote_or_hybrid"
    job_types: List[str] = Field(default_factory=list)
    preferred_tech_stack: List[str] = Field(default_factory=list)
    willing_to_relocate: bool = False

class PreferencesResponse(BaseModel):
    id: Optional[int]
    preferred_roles: List[str]
    preferred_locations: List[str]
    remote_preference: str
    job_types: List[str]
    preferred_tech_stack: List[str]
    willing_to_relocate: bool
    created_at: datetime
    updated_at: datetime

@router.post("/preferences", response_model=PreferencesResponse)
def save_preferences(req: PreferencesRequest, session: Session = Depends(get_session)):
    pref = Preferences(
        preferred_roles=req.preferred_roles,
        preferred_locations=req.preferred_locations,
        remote_preference=req.remote_preference,
        job_types=req.job_types,
        preferred_tech_stack=req.preferred_tech_stack,
        willing_to_relocate=req.willing_to_relocate,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    session.add(pref)
    session.commit()
    session.refresh(pref)
    return pref

@router.get("/preferences/latest", response_model=Optional[PreferencesResponse])
def get_latest_preferences(session: Session = Depends(get_session)):
    statement = select(Preferences).order_by(desc(Preferences.updated_at)).limit(1)
    results = session.exec(statement)
    db_pref = results.first()
    return db_pref
