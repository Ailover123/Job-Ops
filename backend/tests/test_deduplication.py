import pytest
from app.models import SeedJob
from app.seed_loader import (
    normalize_text,
    normalize_company,
    normalize_location,
    normalize_url,
    deduplicate_jobs,
)

def test_text_normalization():
    # Noise stripping, lowercasing, punctuation and space collapse
    assert normalize_text("Software Engineer - Remote") == "software engineer"
    assert normalize_text("Junior React Developer [Full-Time]") == "junior react developer"
    assert normalize_text("QA Specialist (Hybrid/Part-Time)") == "qa specialist"
    assert normalize_text("Python Developer onsite!!!") == "python developer"
    assert normalize_text("") == ""

def test_company_normalization():
    # Suffix stripping, lowercasing, space collapse
    assert normalize_company("Stripe Inc.") == "stripe"
    assert normalize_company("Google, LLC") == "google"
    assert normalize_company("OpenAI corp") == "openai"
    assert normalize_company("Microsoft Limited") == "microsoft"
    assert normalize_company("") == ""

def test_location_normalization():
    # Remote folds to "remote", punctuation/space collapse
    assert normalize_location("Remote, US") == "remote"
    assert normalize_location("USA Remote") == "remote"
    assert normalize_location("San Francisco, CA") == "san francisco ca"
    assert normalize_location("Anywhere") == "remote"
    assert normalize_location("") == ""

def test_url_normalization():
    # Scheme/domain lowercasing, trailing slash strip, tracking/query params stripped
    assert normalize_url("HTTPS://Boards.Greenhouse.Io/Stripe/") == "https://boards.greenhouse.io/stripe"
    assert normalize_url("http://jobs.lever.co/figma/123?utm=source") == "http://jobs.lever.co/figma/123"
    assert normalize_url("") == ""

def test_deduplicate_by_external_id():
    job1 = SeedJob(
        external_id="id-123",
        title="Software Engineer",
        company_name="Google",
        description="A cool python role.",
        location="Mountain View",
        is_remote=False,
        job_type="full_time",
        skills=["Python"],
        apply_url="https://google.com/jobs/1",
        source_name="seed",
        is_active=True
    )
    job2 = SeedJob(
        external_id="id-123",  # duplicate ID
        title="Different Title",
        company_name="Different Company",
        description="Different description.",
        location="Different Location",
        is_remote=False,
        job_type="full_time",
        skills=[],
        apply_url="https://google.com/jobs/2",
        source_name="greenhouse",
        is_active=True
    )
    
    deduped = deduplicate_jobs([job1, job2])
    assert len(deduped) == 1
    assert deduped[0].title == "Software Engineer"

def test_deduplicate_by_apply_url():
    job1 = SeedJob(
        external_id="id-1",
        title="Software Engineer",
        company_name="Google",
        description="Python development",
        location="Mountain View",
        is_remote=False,
        job_type="full_time",
        skills=["Python"],
        apply_url="https://Google.com/jobs/apply-here/",  # URL that normalizes to identical
        source_name="seed",
        is_active=True
    )
    job2 = SeedJob(
        external_id="id-2",
        title="FastAPI Engineer",
        company_name="Alphabet",
        description="FastAPI development",
        location="Remote",
        is_remote=True,
        job_type="full_time",
        skills=["FastAPI"],
        apply_url="https://google.com/jobs/apply-here",  # Duplicate normalized URL
        source_name="lever",
        is_active=True
    )
    
    deduped = deduplicate_jobs([job1, job2])
    assert len(deduped) == 1
    assert deduped[0].external_id == "id-1"

def test_deduplicate_by_fallback_company_title_location():
    job1 = SeedJob(
        external_id="id-1",
        title="Senior Python Engineer [Full-Time]",
        company_name="Google Inc.",
        description="Python backend",
        location="Mountain View, CA",
        is_remote=False,
        job_type="full_time",
        skills=["Python"],
        apply_url="https://google.com/apply-1",
        source_name="seed",
        is_active=True
    )
    job2 = SeedJob(
        external_id="id-2",
        title="Senior Python Engineer - Remote",  # Normalizes to identical (except remote, which is stripped)
        company_name="Google, LLC",                 # Normalizes to identical
        description="Different description text",
        location="Mountain View CA",                 # Normalizes to identical
        is_remote=False,
        job_type="full_time",
        skills=["Python"],
        apply_url="https://google.com/apply-2",      # Different URL
        source_name="greenhouse",
        is_active=True
    )
    
    deduped = deduplicate_jobs([job1, job2])
    assert len(deduped) == 1
    assert deduped[0].external_id == "id-1"

def test_deduplicate_by_fallback_company_content_hash():
    job1 = SeedJob(
        external_id="id-1",
        title="Frontend Specialist",
        company_name="Stripe",
        description="React and TypeScript frontend application work. Focus on developer experience.",
        location="San Francisco",
        is_remote=False,
        job_type="full_time",
        skills=["React"],
        apply_url="https://stripe.com/apply-1",
        source_name="seed",
        is_active=True
    )
    job2 = SeedJob(
        external_id="id-2",
        title="React Software Dev",             # Different title
        company_name="Stripe Inc.",                # Same company (normalized)
        description="  React  and   TypeScript frontend application work.   Focus on developer experience.  ",  # Same description with whitespace differences
        location="Remote",                          # Different location
        is_remote=True,
        job_type="full_time",
        skills=["React"],
        apply_url="https://stripe.com/apply-2",     # Different URL
        source_name="greenhouse",
        is_active=True
    )
    
    deduped = deduplicate_jobs([job1, job2])
    assert len(deduped) == 1
    assert deduped[0].external_id == "id-1"
