import json
from functools import lru_cache
from pathlib import Path
from typing import List

from app.models import SeedJob


ROOT_DIR = Path(__file__).resolve().parents[2]
SEED_JOBS_PATH = ROOT_DIR / "data" / "seed_jobs.json"
IMPORTED_JOBS_PATH = ROOT_DIR / "data" / "imported_jobs.json"


@lru_cache
def load_seed_jobs() -> List[SeedJob]:
    with SEED_JOBS_PATH.open("r", encoding="utf-8") as file:
        rows = json.load(file)
    return [SeedJob.model_validate(row) for row in rows]


def load_imported_jobs() -> List[SeedJob]:
    """Load collected jobs from the JSON cache file."""
    if not IMPORTED_JOBS_PATH.exists():
        return []
    try:
        with IMPORTED_JOBS_PATH.open("r", encoding="utf-8") as file:
            rows = json.load(file)
        return [SeedJob.model_validate(row) for row in rows]
    except Exception:
        return []


def load_all_jobs() -> List[SeedJob]:
    """Merge seed jobs and imported jobs with deduplication by external_id."""
    seen_ids = set()
    all_jobs = []
    
    # 1. Load seed jobs
    for job in load_seed_jobs():
        if job.external_id not in seen_ids:
            seen_ids.add(job.external_id)
            all_jobs.append(job)
            
    # 2. Load imported jobs
    for job in load_imported_jobs():
        if job.external_id not in seen_ids:
            seen_ids.add(job.external_id)
            all_jobs.append(job)
            
    return all_jobs


def save_imported_jobs(new_jobs: List[SeedJob]) -> int:
    """
    Save new_jobs to the JSON cache. Merges with existing imported jobs,
    deduplicates by external_id, and returns the number of newly added jobs.
    """
    existing_jobs = load_imported_jobs()
    existing_by_id = {j.external_id: j for j in existing_jobs}
    
    added_count = 0
    for job in new_jobs:
        if job.external_id not in existing_by_id:
            added_count += 1
        existing_by_id[job.external_id] = job
        
    # Serialize to JSON dicts
    serialized = [j.model_dump() for j in existing_by_id.values()]
    
    # Ensure parent data/ directory exists
    IMPORTED_JOBS_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with IMPORTED_JOBS_PATH.open("w", encoding="utf-8") as file:
        json.dump(serialized, file, indent=2, ensure_ascii=False)
        
    return added_count

