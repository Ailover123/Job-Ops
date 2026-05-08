from fastapi import APIRouter

from app.matching import rank_jobs
from app.models import CandidateProfile, Recommendation
from app.seed_loader import load_seed_jobs

router = APIRouter(tags=["recommendations"])


@router.post("/recommendations", response_model=list[Recommendation])
def recommendations(profile: CandidateProfile) -> list[Recommendation]:
    return rank_jobs(profile, load_seed_jobs())


@router.get("/jobs")
def jobs():
    return load_seed_jobs()
