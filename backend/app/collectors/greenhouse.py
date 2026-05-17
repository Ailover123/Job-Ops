import logging
import httpx
from typing import List, Dict, Any
from app.models import SeedJob
from app.collectors.utils import clean_html, extract_skills, parse_experience

logger = logging.getLogger(__name__)

class GreenhouseCollector:
    """Collector for public job listings from Greenhouse job boards."""

    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def fetch_jobs(self, board_token: str) -> List[Dict[str, Any]]:
        """
        Fetch public job postings from a Greenhouse board token.
        Endpoint: https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true
        """
        url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
        params = {"content": "true"}
        
        try:
            logger.info(f"Fetching Greenhouse jobs for board: {board_token}")
            response = httpx.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data.get("jobs", [])
        except Exception as e:
            logger.error(f"Error fetching Greenhouse board '{board_token}': {e}")
            raise RuntimeError(f"Failed to fetch Greenhouse board '{board_token}': {e}")

    def normalize(self, job: Dict[str, Any], board_token: str) -> SeedJob:
        """
        Normalize raw Greenhouse job posting dict into SeedJob pydantic model.
        """
        job_id = str(job.get("id"))
        external_id = f"greenhouse-{board_token}-{job_id}"
        
        title = job.get("title", "").strip() or "Untitled Role"
        
        # Format company name from token
        company_name = board_token.replace("-", " ").replace("_", " ").title()
        
        # Raw html description
        raw_description = job.get("content", "")
        description = clean_html(raw_description)
        
        # Parse location
        location_data = job.get("location", {})
        location_name = location_data.get("name", "Unknown").strip() if location_data else "Unknown"
        
        # Analyze remote preference (strict title and location only, using word boundary regexes)
        is_remote = False
        location_lower = location_name.lower()
        title_lower = title.lower()
        
        import re
        remote_pattern = re.compile(r'\b(remote|wfh|anywhere)\b')
        if remote_pattern.search(location_lower) or remote_pattern.search(title_lower):
            is_remote = True
            
        # Parse job type: default to full_time unless 'intern' or 'contract' is in title (using word boundaries)
        job_type = "full_time"
        intern_pattern = re.compile(r'\b(intern|internship|co-op|coop)\b')
        contract_pattern = re.compile(r'\b(contract|contractor|temp|temporary)\b')
        
        if intern_pattern.search(title_lower):
            job_type = "internship"
        elif contract_pattern.search(title_lower):
            job_type = "contract"
            
        # Parse experience ranges
        exp_min, exp_max = parse_experience(description)
        
        # Extract skills
        skills = extract_skills(title + " " + description)
        
        # Setup application URLs
        apply_url = job.get("absolute_url") or f"https://boards.greenhouse.io/{board_token}/jobs/{job_id}"
        
        # Setup post date
        posted_at = job.get("updated_at")
        
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
            source_name="greenhouse",
            posted_at=posted_at,
            is_active=True
        )

    def collect_and_normalize(self, board_token: str) -> List[SeedJob]:
        """Fetch, normalize, and return all active job postings for the given board token."""
        raw_jobs = self.fetch_jobs(board_token)
        normalized_jobs = []
        for raw_job in raw_jobs:
            try:
                normalized = self.normalize(raw_job, board_token)
                normalized_jobs.append(normalized)
            except Exception as e:
                logger.error(f"Error normalizing Greenhouse job {raw_job.get('id')}: {e}")
        return normalized_jobs
