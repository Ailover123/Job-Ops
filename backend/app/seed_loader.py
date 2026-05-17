import json
import re
import hashlib
from functools import lru_cache
from pathlib import Path
from typing import List
from urllib.parse import urlparse

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


def normalize_text(text: str) -> str:
    """Normalize general text by lowercasing, removing noise, removing punctuation, and collapsing space."""
    if not text:
        return ""
    t = text.lower()
    # Strip common location/type suffix noise from titles (e.g. "- Remote", "[Full-Time]")
    t = re.sub(r'\b(remote|hybrid|on-site|onsite|full-time|fulltime|part-time|parttime)\b', '', t)
    t = re.sub(r'[^\w\s]', ' ', t)
    return ' '.join(t.split())


def normalize_company(name: str) -> str:
    """Normalize company name by stripping common suffixes like LLC, Inc, Ltd, Corp."""
    if not name:
        return ""
    c = name.lower()
    c = re.sub(r'\b(inc\b\.?|llc\b\.?|ltd\b\.?|corp\b\.?|co\b\.?|corporation\b\.?|limited\b\.?)\b', '', c)
    c = re.sub(r'[^\w\s]', ' ', c)
    return ' '.join(c.split())


def normalize_location(loc: str) -> str:
    """Normalize location for robust duplicate comparison, folding remote variations to "remote"."""
    if not loc:
        return ""
    l = loc.lower()
    l = re.sub(r'[^\w\s]', ' ', l)
    l = ' '.join(l.split())
    if l in ["remote", "us remote", "usa remote", "anywhere", "remote us", "wfh"]:
        return "remote"
    return l


def normalize_url(url: str) -> str:
    """Normalize URL by lowercasing scheme, domain and path, and removing trailing slashes."""
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        path = parsed.path.lower().rstrip('/')
        return f"{scheme}://{netloc}{path}"
    except Exception:
        return url.strip().lower().rstrip('/')


def deduplicate_jobs(jobs: List[SeedJob]) -> List[SeedJob]:
    """
    Deduplicates a list of SeedJobs with multi-tier signals:
    1. Strong duplicate signal: external_id
    2. Strong duplicate signal: normalized apply_url
    3. Fallback duplicate signal: company + title + location key
    4. Fallback duplicate signal: company + content_hash (SHA256 of description)
    """
    seen_ids = set()
    seen_urls = set()
    seen_fallback_keys = set()
    seen_content_hashes = set()
    
    deduplicated = []
    
    for job in jobs:
        # 1. Exact external_id match
        if job.external_id in seen_ids:
            continue
            
        # 2. Exact normalized apply_url match
        normalized_url = normalize_url(job.apply_url)
        if normalized_url and normalized_url in seen_urls:
            continue
            
        # 3. Fallback duplicate match: normalized (company + title + location)
        norm_title = normalize_text(job.title)
        norm_company = normalize_company(job.company_name)
        norm_loc = normalize_location(job.location)
        fallback_key = (norm_company, norm_title, norm_loc)
        if fallback_key in seen_fallback_keys:
            continue
            
        # 4. Fallback duplicate match: same company + same cleaned description content_hash
        clean_desc = ' '.join(job.description.lower().split()) if job.description else ""
        c_hash = hashlib.sha256(clean_desc.encode('utf-8')).hexdigest() if clean_desc else ""
        company_content_key = (norm_company, c_hash)
        if c_hash and company_content_key in seen_content_hashes:
            continue
            
        # If all checks pass, record as seen and append to the output
        seen_ids.add(job.external_id)
        if normalized_url:
            seen_urls.add(normalized_url)
        seen_fallback_keys.add(fallback_key)
        if c_hash:
            seen_content_hashes.add(company_content_key)
            
        deduplicated.append(job)
        
    return deduplicated


def load_all_jobs() -> List[SeedJob]:
    """Merge seed jobs and imported jobs with robust multi-tier deduplication."""
    # Prioritize seed jobs (loaded first) over crawled/imported duplicate jobs
    seed_jobs = load_seed_jobs()
    imported_jobs = load_imported_jobs()
    return deduplicate_jobs(seed_jobs + imported_jobs)


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

