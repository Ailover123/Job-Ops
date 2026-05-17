from datetime import datetime, timezone, timedelta
from app.models import SeedJob, CandidateProfile
from app.job_quality import classify_job_quality, passes_quality_gate

def test_senior_title_rejected_for_fresher():
    job = SeedJob(
        external_id="1",
        title="Senior Software Engineer",
        company_name="Test",
        description="Looking for an experienced engineer.",
        location="Remote",
        job_type="full_time",
        source_name="Test",
        apply_url="https://test.com"
    )
    profile = CandidateProfile(experience_level="fresher")
    
    quality = classify_job_quality(job)
    assert quality.is_senior_heavy is True
    assert quality.quality_score < 100
    
    assert passes_quality_gate(job, profile) is False

def test_internally_in_description_does_not_classify_as_internship():
    job = SeedJob(
        external_id="2",
        title="Software Engineer",
        company_name="Test",
        description="We promote internally.",
        location="Remote",
        job_type="full_time",
        source_name="Test",
        apply_url="https://test.com"
    )
    
    quality = classify_job_quality(job)
    assert quality.is_fresher_friendly is False
    assert quality.is_senior_heavy is False

def test_fresh_graduate_roles_boosted():
    job = SeedJob(
        external_id="3",
        title="New Grad Software Engineer",
        company_name="Test",
        description="Great for fresh graduates.",
        location="Remote",
        job_type="full_time",
        source_name="Test",
        apply_url="https://test.com"
    )
    
    quality = classify_job_quality(job)
    assert quality.is_fresher_friendly is True
    assert quality.quality_score > 100 or quality.quality_score == 100  # capped at 100
    assert "entry-level/fresher" in quality.reasons[0]

def test_experience_min_gte_4_rejected():
    job = SeedJob(
        external_id="4",
        title="Software Engineer",
        company_name="Test",
        description="Standard role.",
        location="Remote",
        job_type="full_time",
        experience_min=4,
        source_name="Test",
        apply_url="https://test.com"
    )
    profile = CandidateProfile(experience_level="fresher")
    
    quality = classify_job_quality(job)
    assert quality.is_senior_heavy is True
    assert passes_quality_gate(job, profile) is False

def test_stale_job_gets_warning_but_passes():
    old_date = (datetime.now(timezone.utc) - timedelta(days=50)).isoformat()
    job = SeedJob(
        external_id="5",
        title="Software Engineer",
        company_name="Test",
        description="Standard role.",
        location="Remote",
        job_type="full_time",
        posted_at=old_date,
        source_name="Test",
        apply_url="https://test.com"
    )
    profile = CandidateProfile(experience_level="fresher")
    
    quality = classify_job_quality(job)
    assert quality.is_stale is True
    assert quality.quality_score < 100
    assert passes_quality_gate(job, profile) is True

def test_valid_fresh_job_passes():
    job = SeedJob(
        external_id="6",
        title="Junior Developer",
        company_name="Test",
        description="Great entry role.",
        location="Remote",
        job_type="full_time",
        experience_min=1,
        source_name="Test",
        apply_url="https://test.com"
    )
    profile = CandidateProfile(experience_level="fresher")
    
    quality = classify_job_quality(job)
    assert quality.is_fresher_friendly is True
    assert quality.is_senior_heavy is False
    assert quality.quality_score == 100
    
    assert passes_quality_gate(job, profile) is True
