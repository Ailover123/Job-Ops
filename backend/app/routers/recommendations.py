from fastapi import APIRouter, Depends
from sqlmodel import Session, select, desc

from app.matching import rank_jobs
from app.models import CandidateProfile, Recommendation
from app.seed_loader import load_seed_jobs, load_all_jobs
from app.database import get_session
from app.db_models import Profile, Preferences

router = APIRouter(tags=["recommendations"])


@router.post("/recommendations", response_model=list[Recommendation])
def recommendations(profile: CandidateProfile) -> list[Recommendation]:
    return rank_jobs(profile, load_all_jobs())



@router.get("/recommendations/latest-profile")
async def recommendations_from_latest_profile(session: Session = Depends(get_session)):
    """
    Fetch the latest profile and return recommendations.
    """
    statement = select(Profile).order_by(desc(Profile.created_at)).limit(1)
    results = session.exec(statement)
    db_profile = results.first()

    statement_pref = select(Preferences).order_by(desc(Preferences.updated_at)).limit(1)
    results_pref = session.exec(statement_pref)
    db_pref = results_pref.first()

    if not db_profile and not db_pref:
        return {"status": "no_profile", "items": []}

    # Extract info from profile if exists
    extracted_skills = []
    preferred_locations = []
    preferred_roles = []
    
    if db_profile:
        extracted_skills = [s.get("name") for s in db_profile.skills if s.get("name")]
        if db_profile.location and db_profile.location.get("city"):
            preferred_locations.append(db_profile.location.get("city"))
        preferred_roles = db_profile.suggested_roles or []

    # Apply preference overrides if available
    remote_pref = "remote_or_hybrid"
    job_types = ["internship", "full_time"]
    willing_to_relocate = False

    if db_pref:
        if db_pref.preferred_roles:
            preferred_roles = db_pref.preferred_roles
        if db_pref.preferred_locations:
            preferred_locations = db_pref.preferred_locations
        if db_pref.preferred_tech_stack:
            # Merge tech stack skills with profile skills
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

    recs = rank_jobs(candidate, load_all_jobs())
    return {"status": "personalized", "items": recs}


@router.get("/jobs")
def jobs():
    return load_all_jobs()

