import logging
import httpx
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.models import SeedJob
from app.collectors.utils import clean_html, extract_skills, parse_experience

logger = logging.getLogger(__name__)

class LeverCollector:
    """Collector for public job listings from Lever postings boards."""

    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def fetch_jobs(self, company_id: str) -> List[Dict[str, Any]]:
        """
        Fetch public job postings from a Lever company ID.
        Endpoint: https://api.lever.co/v0/postings/{company_id}?mode=json
        """
        url = f"https://api.lever.co/v0/postings/{company_id}"
        params = {"mode": "json"}
        
        try:
            logger.info(f"Fetching Lever jobs for company: {company_id}")
            response = httpx.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list):
                return data
            return []
        except Exception as e:
            logger.error(f"Error fetching Lever company '{company_id}': {e}")
            raise RuntimeError(f"Failed to fetch Lever company '{company_id}': {e}")

    def normalize(self, job: Dict[str, Any], company_id: str) -> SeedJob:
        """
        Normalize raw Lever job posting dict into SeedJob pydantic model.
        """
        job_id = str(job.get("id"))
        external_id = f"lever-{company_id}-{job_id}"
        
        title = job.get("text", "").strip() or "Untitled Role"
        
        # Format company name from company_id
        company_name = company_id.replace("-", " ").replace("_", " ").title()
        
        # Raw description
        raw_description = job.get("descriptionPlain") or job.get("description", "")
        description = clean_html(raw_description)
        
        # Parse categories
        categories = job.get("categories", {}) or {}
        location_name = categories.get("location", "Unknown").strip()
        commitment = categories.get("commitment", "").strip()
        
        # Analyze remote preference (strict title, location, and workplaceType only, using word boundary regexes)
        is_remote = False
        workplace_type = str(job.get("workplaceType", "")).lower()
        location_lower = location_name.lower()
        title_lower = title.lower()
        
        import re
        remote_pattern = re.compile(r'\b(remote|wfh|anywhere)\b')
        if (
            workplace_type == "remote" or
            remote_pattern.search(location_lower) or 
            remote_pattern.search(title_lower)
        ):
            is_remote = True
            
        # Parse job type: check commitment or title (using word boundaries, eliminating description)
        job_type = "full_time"
        commitment_lower = commitment.lower()
        intern_pattern = re.compile(r'\b(intern|internship|co-op|coop)\b')
        contract_pattern = re.compile(r'\b(contract|contractor|temp|temporary)\b')
        
        if intern_pattern.search(title_lower) or intern_pattern.search(commitment_lower):
            job_type = "internship"
        elif contract_pattern.search(title_lower) or contract_pattern.search(commitment_lower):
            job_type = "contract"
            
        # Parse experience ranges
        exp_min, exp_max = parse_experience(description)
        
        # Extract skills
        skills = extract_skills(title + " " + description)
        
        # Setup application URLs
        urls = job.get("urls", {}) or {}
        apply_url = urls.get("apply") or urls.get("show") or f"https://jobs.lever.co/{company_id}/{job_id}"
        
        # Setup post date from createdAt timestamp (milliseconds)
        posted_at = None
        created_at_ms = job.get("createdAt")
        if created_at_ms:
            try:
                posted_at = datetime.fromtimestamp(created_at_ms / 1000.0, tz=timezone.utc).isoformat()
            except Exception:
                pass
        
        return SeedJob(
            external_id=external_id,
            title=title,
            company_name=company_name,
            description=description,
            location=location_name,
            city=None,
            state=None,
            country=None,
            is_remote=is_remote,
            job_type=job_type,
            experience_min=exp_min,
            experience_max=exp_max,
            skills=skills,
            apply_url=apply_url,
            source_name="lever",
            posted_at=posted_at,
            is_active=True
        )

    def collect_and_normalize(self, company_id: str) -> List[SeedJob]:
        """Fetch, normalize, and return all active job postings for the given Lever company ID."""
        raw_jobs = self.fetch_jobs(company_id)
        normalized_jobs = []
        for raw_job in raw_jobs:
            try:
                normalized = self.normalize(raw_job, company_id)
                normalized_jobs.append(normalized)
            except Exception as e:
                logger.error(f"Error normalizing Lever job {raw_job.get('id')}: {e}")
        return normalized_jobs
