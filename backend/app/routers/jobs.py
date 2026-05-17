from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, desc
from typing import List, Literal, Optional
from datetime import datetime, timezone
from pydantic import BaseModel

from app.database import get_session
from app.db_models import SavedJob, Application, Profile, Preferences
from app.seed_loader import load_seed_jobs, load_all_jobs
from app.matching import score_job
from app.models import CandidateProfile

router = APIRouter(tags=["jobs"])

class JobActionRequest(BaseModel):
    job_external_id: str
    job_title: str
    company_name: str
    location: str = "Unknown"
    source_name: str
    apply_url: str
    skills: List[str] = []

class ApplicationRequest(JobActionRequest):
    status: str = "applied"
    notes: str = ""

class ApplicationUpdateRequest(BaseModel):
    status: Optional[Literal["applied", "interviewing", "rejected", "offer", "withdrawn"]] = None
    notes: Optional[str] = None

@router.post("/saved-jobs")
async def save_job(request: JobActionRequest, session: Session = Depends(get_session)):
    """Save a job, idempotent."""
    statement = select(SavedJob).where(SavedJob.job_external_id == request.job_external_id)
    existing = session.exec(statement).first()
    
    if existing:
        return {"status": "success", "message": "already_saved", "item": existing}
    
    db_job = SavedJob(
        job_external_id=request.job_external_id,
        job_title=request.job_title,
        company_name=request.company_name,
        location=request.location,
        source_name=request.source_name,
        apply_url=request.apply_url,
        skills=request.skills
    )
    session.add(db_job)
    session.commit()
    session.refresh(db_job)
    return {"status": "success", "item": db_job}

@router.get("/saved-jobs")
async def list_saved_jobs(session: Session = Depends(get_session)):
    """List all saved jobs."""
    statement = select(SavedJob).order_by(SavedJob.saved_at.desc())
    results = session.exec(statement).all()
    return {"items": results}

@router.delete("/saved-jobs/{job_external_id}")
async def unsave_job(job_external_id: str, session: Session = Depends(get_session)):
    """Remove a saved job."""
    statement = select(SavedJob).where(SavedJob.job_external_id == job_external_id)
    job = session.exec(statement).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found in saved list")
    
    session.delete(job)
    session.commit()
    return {"status": "success", "message": "job_removed"}

@router.post("/applications")
async def record_application(request: ApplicationRequest, session: Session = Depends(get_session)):
    """Record a job application, idempotent."""
    statement = select(Application).where(Application.job_external_id == request.job_external_id)
    existing = session.exec(statement).first()
    
    if existing:
        # Update existing record if needed
        existing.status = request.status
        existing.notes = request.notes
        existing.applied_at = datetime.now(timezone.utc)
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return {"status": "success", "message": "application_updated", "item": existing}
    
    db_app = Application(
        job_external_id=request.job_external_id,
        job_title=request.job_title,
        company_name=request.company_name,
        location=request.location,
        source_name=request.source_name,
        apply_url=request.apply_url,
        skills=request.skills,
        status=request.status,
        notes=request.notes
    )
    session.add(db_app)
    session.commit()
    session.refresh(db_app)
    return {"status": "success", "item": db_app}

@router.get("/applications")
async def list_applications(session: Session = Depends(get_session)):
    """List all applications."""
    statement = select(Application).order_by(Application.applied_at.desc())
    results = session.exec(statement).all()
    return {"items": results}

@router.put("/applications/{job_external_id}")
async def update_application(
    job_external_id: str,
    request: ApplicationUpdateRequest,
    session: Session = Depends(get_session)
):
    """Update an application status or notes."""
    statement = select(Application).where(Application.job_external_id == job_external_id)
    db_app = session.exec(statement).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if request.status is not None:
        db_app.status = request.status
    if request.notes is not None:
        db_app.notes = request.notes
        
    session.add(db_app)
    session.commit()
    session.refresh(db_app)
    return {"status": "success", "item": db_app}


@router.get("/jobs/{external_id}")
async def get_job_detail(external_id: str, session: Session = Depends(get_session)):
    """Fetch job details and compute candidate compatibility scores."""
    # Find the job in seed jobs
    jobs = load_all_jobs()
    job = next((j for j in jobs if j.external_id == external_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Fetch latest profile and preferences
    db_profile = session.exec(select(Profile).order_by(desc(Profile.created_at)).limit(1)).first()
    db_pref = session.exec(select(Preferences).order_by(desc(Preferences.updated_at)).limit(1)).first()

    if not db_profile and not db_pref:
        return {
            "job": job,
            "has_profile": False,
            "match_score": None,
            "match_label": None,
            "match_explanation": None,
            "skill_score": None,
            "fresher_score": None,
            "location_score": None,
            "experience_score": None
        }

    # Construct the merged CandidateProfile
    extracted_skills = []
    preferred_locations = []
    preferred_roles = []

    if db_profile:
        extracted_skills = [s.get("name") for s in db_profile.skills if s.get("name")]
        if db_profile.location and db_profile.location.get("city"):
            preferred_locations.append(db_profile.location.get("city"))
        preferred_roles = db_profile.suggested_roles or []

    remote_pref = "remote_or_hybrid"
    job_types = ["internship", "full_time"]
    willing_to_relocate = False

    if db_pref:
        if db_pref.preferred_roles:
            preferred_roles = db_pref.preferred_roles
        if db_pref.preferred_locations:
            preferred_locations = db_pref.preferred_locations
        if db_pref.preferred_tech_stack:
            extracted_skills = list(set(extracted_skills + db_pref.preferred_tech_stack))
        remote_pref = db_pref.remote_preference
        job_types = db_pref.job_types or job_types
        willing_to_relocate = db_pref.willing_to_relocate

    candidate = CandidateProfile(
        preferred_roles=preferred_roles,
        skills=extracted_skills,
        preferred_locations=preferred_locations,
        remote_preference=remote_pref,
        job_types=job_types,
        experience_level="fresher",
        willing_to_relocate=willing_to_relocate
    )

    rec = score_job(candidate, job)

    return {
        "job": job,
        "has_profile": True,
        "match_score": rec.final_score,
        "match_label": rec.score_label,
        "match_explanation": rec.explanation,
        "skill_score": rec.skill_score,
        "fresher_score": rec.fresher_score,
        "location_score": rec.location_score,
        "experience_score": rec.experience_score
    }
