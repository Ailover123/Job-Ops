import logging
from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from app.collectors import GreenhouseCollector, LeverCollector
from app.seed_loader import save_imported_jobs
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/internal", tags=["internal"])

class GreenhouseCollectRequest(BaseModel):
    board_token: str = "cloudflare"  # Default token useful for testing

class LeverCollectRequest(BaseModel):
    company_id: str = "lever"  # Default company id useful for testing

def verify_internal_key(x_internal_api_key: str | None = Header(None, alias="X-Internal-API-Key")):
    """
    Verify the X-Internal-API-Key header matches the configured INTERNAL_API_KEY.
    If INTERNAL_API_KEY is missing, returns a 503 Service Unavailable.
    If header does not match, returns a 403 Forbidden.
    """
    if not settings.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Internal collection API is disabled because INTERNAL_API_KEY is not configured."
        )
    if x_internal_api_key != settings.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Invalid or missing X-Internal-API-Key header."
        )

@router.post("/collect/greenhouse", dependencies=[Depends(verify_internal_key)])
async def collect_greenhouse(request: GreenhouseCollectRequest):
    """
    Trigger collection of job listings from Greenhouse for a specific board token.
    Uses public endpoints without auth/scraping logins.
    """
    board_token = request.board_token.strip()
    if not board_token:
        raise HTTPException(status_code=400, detail="Greenhouse board_token is required")
        
    try:
        collector = GreenhouseCollector()
        normalized_jobs = collector.collect_and_normalize(board_token)
        new_added = save_imported_jobs(normalized_jobs)
        
        return {
            "status": "success",
            "board_token": board_token,
            "fetched_count": len(normalized_jobs),
            "new_jobs_added": new_added,
            "source": "greenhouse"
        }
    except Exception as e:
        logger.error(f"Greenhouse collection failed for '{board_token}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/collect/lever", dependencies=[Depends(verify_internal_key)])
async def collect_lever(request: LeverCollectRequest):
    """
    Trigger collection of job listings from Lever for a specific company id.
    Uses public endpoints without auth/scraping logins.
    """
    company_id = request.company_id.strip()
    if not company_id:
        raise HTTPException(status_code=400, detail="Lever company_id is required")
        
    try:
        collector = LeverCollector()
        normalized_jobs = collector.collect_and_normalize(company_id)
        new_added = save_imported_jobs(normalized_jobs)
        
        return {
            "status": "success",
            "company_id": company_id,
            "fetched_count": len(normalized_jobs),
            "new_jobs_added": new_added,
            "source": "lever"
        }
    except Exception as e:
        logger.error(f"Lever collection failed for '{company_id}': {e}")
        raise HTTPException(status_code=500, detail=str(e))
