import re
from datetime import datetime, timezone
from dataclasses import dataclass, field
from app.models import SeedJob, CandidateProfile

@dataclass
class JobQualityResult:
    is_fresher_friendly: bool
    is_senior_heavy: bool
    is_stale: bool
    quality_score: int
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

FRESHER_TITLE_PATTERN = re.compile(
    r"\b(intern|internship|fresher|graduate|new grad|entry level|junior|trainee|associate)\b", 
    re.IGNORECASE
)

SENIOR_TITLE_PATTERN = re.compile(
    r"\b(senior|sr|staff|principal|lead|manager|architect|director|head)\b", 
    re.IGNORECASE
)

def classify_job_quality(job: SeedJob) -> JobQualityResult:
    is_fresher_friendly = False
    is_senior_heavy = False
    is_stale = False
    score = 100
    reasons = []
    warnings = []

    title = job.title or ""
    
    # 1. Stale Check
    if job.posted_at:
        try:
            posted_date = datetime.fromisoformat(job.posted_at.replace('Z', '+00:00'))
            if posted_date.tzinfo is None:
                posted_date = posted_date.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            days_old = (now - posted_date).days
            if days_old > 45:
                is_stale = True
                score -= 30
                warnings.append(f"Job is stale ({days_old} days old)")
        except ValueError:
            pass

    # 2. Title Checks
    if FRESHER_TITLE_PATTERN.search(title):
        is_fresher_friendly = True
        score += 20
        reasons.append("Title indicates entry-level/fresher role")
    
    if SENIOR_TITLE_PATTERN.search(title):
        is_senior_heavy = True
        score -= 50
        warnings.append("Title indicates senior role")

    # 3. Experience Rules
    exp_min = job.experience_min
    if exp_min is not None:
        if exp_min >= 4:
            is_senior_heavy = True
            score -= 40
            warnings.append(f"Requires {exp_min} years minimum experience")
        elif exp_min == 3:
            score -= 20
            warnings.append(f"Requires {exp_min} years minimum experience (borderline)")
        elif exp_min in (0, 1, 2):
            is_fresher_friendly = True
            score += 20
            reasons.append(f"Experience requirement is low ({exp_min} years)")
            
    score = max(0, min(100, score))

    return JobQualityResult(
        is_fresher_friendly=is_fresher_friendly,
        is_senior_heavy=is_senior_heavy,
        is_stale=is_stale,
        quality_score=score,
        reasons=reasons,
        warnings=warnings
    )

def passes_quality_gate(job: SeedJob, profile: CandidateProfile) -> bool:
    quality = classify_job_quality(job)
    
    if profile.experience_level == "fresher" and quality.is_senior_heavy:
        return False
        
    return True
