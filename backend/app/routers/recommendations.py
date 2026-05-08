from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.matching import rank_jobs
from app.models import CandidateProfile, Recommendation
from app.seed_loader import load_seed_jobs
from app.database import get_session
from app.db_models import Profile

router = APIRouter(tags=["recommendations"])


@router.post("/recommendations", response_model=list[Recommendation])
def recommendations(profile: CandidateProfile) -> list[Recommendation]:
    return rank_jobs(profile, load_seed_jobs())


@router.get("/recommendations/latest-profile")
async def recommendations_from_latest_profile(session: Session = Depends(get_session)):
    """
    Fetch the latest profile and return recommendations.
    """
    statement = select(Profile).order_by(Profile.created_at.desc()).limit(1)
    results = session.exec(statement)
    db_profile = results.first()

    if not db_profile:
        return {"status": "no_profile", "items": []}

    # Map DB Profile to CandidateProfile
    # Profile.skills is List[dict] like [{"name": "Python", "level": "Expert"}]
    # CandidateProfile.skills is List[str]
    extracted_skills = [s.get("name") for s in db_profile.skills if s.get("name")]
    
    # Profile.location is dict like {"city": "Bangalore", ...}
    # CandidateProfile.preferred_locations is List[str]
    preferred_locations = []
    if db_profile.location and db_profile.location.get("city"):
        preferred_locations.append(db_profile.location.get("city"))

    candidate = CandidateProfile(
        preferred_roles=db_profile.suggested_roles,
        skills=extracted_skills,
        preferred_locations=preferred_locations,
        # Keep defaults for now
        remote_preference="remote_or_hybrid",
        job_types=["internship", "full_time"],
        experience_level="fresher"
    )

    recs = rank_jobs(candidate, load_seed_jobs())
    return {"status": "personalized", "items": recs}


@router.get("/jobs")
def jobs():
    return load_seed_jobs()
