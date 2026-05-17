import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from sqlmodel import Session, select
from app.collectors import GreenhouseCollector, LeverCollector
from app.seed_loader import save_imported_jobs
from app.database import engine
from typing import List
from app.internal_schemas import CollectorSourceCreate, CollectorSourceUpdate, CollectorSourceResponse
from app.db_models import CollectorSource
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/internal", tags=["internal"])

class GreenhouseCollectRequest(BaseModel):
    board_token: str = "cloudflare"

class LeverCollectRequest(BaseModel):
    company_id: str = "lever"

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

@router.get("/sources", response_model=List[CollectorSourceResponse], dependencies=[Depends(verify_internal_key)])
def list_sources():
    """List all configured collector sources."""
    with Session(engine) as session:
        return session.exec(select(CollectorSource)).all()

@router.post("/sources", response_model=CollectorSourceResponse, dependencies=[Depends(verify_internal_key)])
def create_source(source_in: CollectorSourceCreate):
    """Add a new collector source config."""
    with Session(engine) as session:
        # Check for duplicates
        existing = session.exec(
            select(CollectorSource).where(
                CollectorSource.company_name == source_in.company_name,
                CollectorSource.enabled == True
            )
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Active source with this company name already exists")
        
        db_source = CollectorSource.model_validate(source_in.model_dump())
        session.add(db_source)
        session.commit()
        session.refresh(db_source)
        return db_source

@router.patch("/sources/{source_id}", response_model=CollectorSourceResponse, dependencies=[Depends(verify_internal_key)])
def update_source(source_id: int, source_in: CollectorSourceUpdate):
    """Update a collector source config."""
    with Session(engine) as session:
        db_source = session.get(CollectorSource, source_id)
        if not db_source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        update_data = source_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_source, key, value)
        
        db_source.updated_at = datetime.now(timezone.utc)
        session.add(db_source)
        session.commit()
        session.refresh(db_source)
        return db_source

@router.delete("/sources/{source_id}", response_model=CollectorSourceResponse, dependencies=[Depends(verify_internal_key)])
def delete_source(source_id: int):
    """Soft-disable a collector source."""
    with Session(engine) as session:
        db_source = session.get(CollectorSource, source_id)
        if not db_source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        db_source.enabled = False
        db_source.updated_at = datetime.now(timezone.utc)
        session.add(db_source)
        session.commit()
        session.refresh(db_source)
        return db_source



@router.post("/collect/greenhouse", dependencies=[Depends(verify_internal_key)])
async def collect_greenhouse(request: GreenhouseCollectRequest):
    """
    Trigger collection of job listings from Greenhouse for a specific board token.
    Uses public endpoints without auth/scraping logins.
    Ad-hoc endpoint - does not update CollectorSource audit fields.
    """
    board_token = request.board_token.strip()
    if not board_token:
        raise HTTPException(status_code=400, detail="Greenhouse board_token is required")

    try:
        collector = GreenhouseCollector()
        normalized_jobs = collector.collect_and_normalize(board_token)
        summary = save_imported_jobs(normalized_jobs)

        return {
            "status": "success",
            "board_token": board_token,
            "fetched_count": summary["fetched"],
            "new_jobs_added": summary["added"],
            "jobs_updated": summary["updated"],
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
    Ad-hoc endpoint - does not update CollectorSource audit fields.
    """
    company_id = request.company_id.strip()
    if not company_id:
        raise HTTPException(status_code=400, detail="Lever company_id is required")

    try:
        collector = LeverCollector()
        normalized_jobs = collector.collect_and_normalize(company_id)
        summary = save_imported_jobs(normalized_jobs)

        return {
            "status": "success",
            "company_id": company_id,
            "fetched_count": summary["fetched"],
            "new_jobs_added": summary["added"],
            "jobs_updated": summary["updated"],
            "source": "lever"
        }
    except Exception as e:
        logger.error(f"Lever collection failed for '{company_id}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collect/all", dependencies=[Depends(verify_internal_key)])
async def collect_all_sources():
    """
    Trigger collection for ALL enabled CollectorSource rows in the database.

    For each source:
    - Sets last_run_at immediately on attempt.
    - On success: updates last_success_at, last_fetched_count, last_saved_count, clears last_error.
    - On failure: stores last_error message, preserves previous last_success_at.

    Returns a per-source result list and aggregate totals.
    """
    with Session(engine) as session:
        sources = session.exec(
            select(CollectorSource).where(CollectorSource.enabled == True)
        ).all()

    if not sources:
        return {
            "status": "completed",
            "sources_attempted": 0,
            "sources_succeeded": 0,
            "sources_failed": 0,
            "total_fetched": 0,
            "total_added": 0,
            "total_updated": 0,
            "results": []
        }

    results = []
    total_fetched = 0
    total_added = 0
    total_updated = 0
    succeeded = 0
    failed = 0

    for source in sources:
        now = datetime.now(timezone.utc)
        source_result: dict = {
            "company": source.company_name,
            "source_type": source.source_type,
        }

        try:
            # Mark attempt time
            with Session(engine) as session:
                db_source = session.get(CollectorSource, source.id)
                if db_source:
                    db_source.last_run_at = now
                    session.add(db_source)
                    session.commit()

            # Dispatch to the correct collector
            if source.source_type == "greenhouse":
                if not source.board_token:
                    raise ValueError(f"CollectorSource id={source.id} has no board_token")
                collector = GreenhouseCollector()
                normalized_jobs = collector.collect_and_normalize(source.board_token)

            elif source.source_type == "lever":
                if not source.company_id:
                    raise ValueError(f"CollectorSource id={source.id} has no company_id")
                collector = LeverCollector()
                normalized_jobs = collector.collect_and_normalize(source.company_id)

            else:
                raise ValueError(f"Unknown source_type '{source.source_type}' for source id={source.id}")

            summary = save_imported_jobs(normalized_jobs)
            fetched = summary["fetched"]
            added = summary["added"]
            updated = summary["updated"]

            # Update status on success
            with Session(engine) as session:
                db_source = session.get(CollectorSource, source.id)
                if db_source:
                    db_source.last_success_at = datetime.now(timezone.utc)
                    db_source.last_error = None
                    db_source.last_fetched_count = fetched
                    db_source.last_saved_count = added + updated  # both new and refreshed jobs were persisted
                    session.add(db_source)
                    session.commit()

            total_fetched += fetched
            total_added += added
            total_updated += updated
            succeeded += 1

            source_result.update({
                "status": "success",
                "fetched": fetched,
                "added": added,
                "updated": updated,
            })
            logger.info(
                f"Collected {fetched} jobs from {source.company_name} "
                f"({source.source_type}): {added} new, {updated} updated"
            )

        except Exception as e:
            failed += 1
            error_msg = str(e)
            logger.error(
                f"Collection failed for {source.company_name} ({source.source_type}): {error_msg}"
            )

            # Store last_error; preserve last_success_at
            try:
                with Session(engine) as session:
                    db_source = session.get(CollectorSource, source.id)
                    if db_source:
                        db_source.last_error = error_msg
                        session.add(db_source)
                        session.commit()
            except Exception as db_err:
                logger.error(f"Failed to write last_error for source {source.id}: {db_err}")

            source_result.update({
                "status": "failed",
                "error": error_msg,
            })

        results.append(source_result)

    return {
        "status": "completed",
        "sources_attempted": len(sources),
        "sources_succeeded": succeeded,
        "sources_failed": failed,
        "total_fetched": total_fetched,
        "total_added": total_added,
        "total_updated": total_updated,
        "results": results,
    }
