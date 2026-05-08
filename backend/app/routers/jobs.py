from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import datetime, timezone
from pydantic import BaseModel

from app.database import get_session
from app.db_models import SavedJob, Application

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
