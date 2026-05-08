import json
from functools import lru_cache
from pathlib import Path

from app.models import SeedJob


ROOT_DIR = Path(__file__).resolve().parents[2]
SEED_JOBS_PATH = ROOT_DIR / "data" / "seed_jobs.json"


@lru_cache
def load_seed_jobs() -> list[SeedJob]:
    with SEED_JOBS_PATH.open("r", encoding="utf-8") as file:
        rows = json.load(file)
    return [SeedJob.model_validate(row) for row in rows]
