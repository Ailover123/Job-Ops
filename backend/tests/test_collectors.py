import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.main import app
from app.database import get_session
from app.collectors import GreenhouseCollector, LeverCollector
from app.models import SeedJob
import app.seed_loader as seed_loader

# A clean, isolated environment using an in-memory python list mock
@pytest.fixture(autouse=True)
def mock_db_imported_jobs(monkeypatch):
    test_jobs_list = []
    
    def mock_load():
        return test_jobs_list
        
    def mock_save(new_jobs):
        added = 0
        for nj in new_jobs:
            if not any(x.external_id == nj.external_id for x in test_jobs_list):
                test_jobs_list.append(nj)
                added += 1
        return added
        
    monkeypatch.setattr("app.seed_loader.load_imported_jobs", mock_load)
    monkeypatch.setattr("app.seed_loader.save_imported_jobs", mock_save)
    monkeypatch.setattr("app.routers.internal.save_imported_jobs", mock_save)
    return test_jobs_list

from app.routers.internal import verify_internal_key

@pytest.fixture(name="client")
def client_fixture():
    # Simple TestClient fixture
    app.dependency_overrides[verify_internal_key] = lambda: None
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_greenhouse_collector_normalization():
    collector = GreenhouseCollector()
    mock_raw_job = {
        "id": 98765,
        "title": "Fresher React Developer (Intern)",
        "content": "<p>We are seeking a React developer. 1 to 2 years experience with JavaScript and CSS. </p>",
        "location": {"name": "Remote, US"},
        "absolute_url": "https://boards.greenhouse.io/test/jobs/98765",
        "updated_at": "2026-05-15T12:00:00Z"
    }

    normalized = collector.normalize(mock_raw_job, "cloudflare")
    
    assert isinstance(normalized, SeedJob)
    assert normalized.external_id == "greenhouse-cloudflare-98765"
    assert normalized.title == "Fresher React Developer (Intern)"
    assert normalized.company_name == "Cloudflare"
    assert "seeking a React developer" in normalized.description
    assert normalized.location == "Remote, US"
    assert normalized.is_remote is True
    assert normalized.job_type == "internship"
    assert normalized.experience_min == 1
    assert normalized.experience_max == 2
    assert "React" in normalized.skills
    assert "JavaScript" in normalized.skills
    assert "CSS" in normalized.skills
    assert normalized.apply_url == "https://boards.greenhouse.io/test/jobs/98765"
    assert normalized.source_name == "greenhouse"
    assert normalized.posted_at == "2026-05-15T12:00:00Z"

def test_lever_collector_normalization():
    collector = LeverCollector()
    mock_raw_job = {
        "id": "abc-123-xyz",
        "text": "Junior QA Engineer (Contractor)",
        "descriptionPlain": "Need someone to do manual testing with Python and Git. Experience range: 2+ years of QA.",
        "categories": {
            "location": "San Francisco, CA",
            "commitment": "Contract"
        },
        "workplaceType": "hybrid",
        "urls": {
            "apply": "https://jobs.lever.co/test/abc-123-xyz/apply"
        },
        "createdAt": 1778937600000  # Millisecond timestamp
    }

    normalized = collector.normalize(mock_raw_job, "lever")
    
    assert isinstance(normalized, SeedJob)
    assert normalized.external_id == "lever-lever-abc-123-xyz"
    assert normalized.title == "Junior QA Engineer (Contractor)"
    assert normalized.company_name == "Lever"
    assert "manual testing with Python" in normalized.description
    assert normalized.location == "San Francisco, CA"
    assert normalized.is_remote is False
    assert normalized.job_type == "contract"
    assert normalized.experience_min == 2
    assert normalized.experience_max is None
    assert "Python" in normalized.skills
    assert "Git" in normalized.skills
    assert normalized.apply_url == "https://jobs.lever.co/test/abc-123-xyz/apply"
    assert normalized.source_name == "lever"
    assert normalized.posted_at is not None

@patch("httpx.get")
def test_collect_greenhouse_api_endpoint(mock_get, client: TestClient):
    # Mock Greenhouse API response
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "jobs": [
            {
                "id": 111,
                "title": "Software Engineer",
                "content": "<p>Python backend developer role.</p>",
                "location": {"name": "Remote"},
                "absolute_url": "https://greenhouse.io/test/111"
            }
        ]
    }
    mock_get.return_value = mock_response

    payload = {"board_token": "stripe"}
    response = client.post("/api/v1/internal/collect/greenhouse", json=payload)
    
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    assert res_data["board_token"] == "stripe"
    assert res_data["fetched_count"] == 1
    assert res_data["new_jobs_added"] == 1
    assert res_data["source"] == "greenhouse"

    # Confirm job is saved in imported jobs JSON
    imported = seed_loader.load_imported_jobs()
    assert len(imported) == 1
    assert imported[0].external_id == "greenhouse-stripe-111"
    assert imported[0].title == "Software Engineer"
    assert "Python" in imported[0].skills

@patch("httpx.get")
def test_collect_lever_api_endpoint(mock_get, client: TestClient):
    # Mock Lever API response
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = [
        {
            "id": "222",
            "text": "Data Scientist",
            "description": "SQL and Python ML work.",
            "categories": {
                "location": "New York",
                "commitment": "Full Time"
            },
            "urls": {
                "apply": "https://lever.co/test/222"
            }
        }
    ]
    mock_get.return_value = mock_response

    payload = {"company_id": "figma"}
    response = client.post("/api/v1/internal/collect/lever", json=payload)
    
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    assert res_data["company_id"] == "figma"
    assert res_data["fetched_count"] == 1
    assert res_data["new_jobs_added"] == 1
    assert res_data["source"] == "lever"

    # Confirm job is saved in imported jobs JSON
    imported = seed_loader.load_imported_jobs()
    assert len(imported) == 1
    assert imported[0].external_id == "lever-figma-222"
    assert "SQL" in imported[0].skills

def test_jobs_endpoint_includes_imported_jobs(client: TestClient):
    # Create some mock imported jobs in our temporary test file
    mock_job = SeedJob(
        external_id="greenhouse-stripe-333",
        title="Frontend Specialist",
        company_name="Stripe",
        description="React and TypeScript",
        location="Remote",
        is_remote=True,
        job_type="full_time",
        skills=["React", "TypeScript"],
        apply_url="https://greenhouse.io/test/333",
        source_name="greenhouse",
        is_active=True
    )
    seed_loader.save_imported_jobs([mock_job])

    # Fetch jobs via GET /api/v1/jobs
    response = client.get("/api/v1/jobs")
    assert response.status_code == 200
    jobs_list = response.json()
    
    # Verify both seed jobs and imported jobs exist in the response
    assert len(jobs_list) > 1
    imported_job_results = [j for j in jobs_list if j["external_id"] == "greenhouse-stripe-333"]
    assert len(imported_job_results) == 1
    assert imported_job_results[0]["company_name"] == "Stripe"
