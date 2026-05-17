import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session, engine as app_engine
from app.collectors import GreenhouseCollector, LeverCollector
from app.db_models import CollectorSource
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
        updated = 0
        for nj in new_jobs:
            if not any(x.external_id == nj.external_id for x in test_jobs_list):
                test_jobs_list.append(nj)
                added += 1
            else:
                updated += 1
        return {"fetched": len(new_jobs), "added": added, "updated": updated}

    monkeypatch.setattr("app.seed_loader.load_imported_jobs", mock_load)
    monkeypatch.setattr("app.seed_loader.save_imported_jobs", mock_save)
    monkeypatch.setattr("app.routers.internal.save_imported_jobs", mock_save)
    return test_jobs_list


from app.routers.internal import verify_internal_key


@pytest.fixture(name="session")
def session_fixture():
    """Isolated in-memory SQLite session shared by client and test assertions."""
    test_engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """TestClient with auth bypassed and session overridden."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[verify_internal_key] = lambda: None

    # Patch the engine used by /collect/all to be the test engine
    import app.routers.internal as internal_mod
    original_engine = internal_mod.engine
    internal_mod.engine = session.get_bind()

    client = TestClient(app)
    yield client

    internal_mod.engine = original_engine
    app.dependency_overrides.clear()


@pytest.fixture(name="authed_client")
def authed_client_fixture(session: Session):
    """TestClient that does NOT bypass verify_internal_key."""
    app.dependency_overrides[get_session] = lambda: session
    app.dependency_overrides.pop(verify_internal_key, None)
    client = TestClient(app, raise_server_exceptions=False)
    yield client
    app.dependency_overrides.clear()


# --- Existing normalization tests ---

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

    # Confirm job is saved in imported jobs
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

    # Confirm job is saved in imported jobs
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


# --- New /collect/all tests ---

def test_collect_all_requires_auth(authed_client: TestClient):
    """POST /collect/all must reject requests without X-Internal-API-Key."""
    response = authed_client.post("/api/v1/internal/collect/all")
    # 503 when no INTERNAL_API_KEY set in test env, or 403 if wrong key
    assert response.status_code in (403, 503)


def test_collect_all_requires_auth_wrong_key(authed_client: TestClient):
    """POST /collect/all must return 403 for a wrong key."""
    import os
    from app.config import settings
    original = settings.INTERNAL_API_KEY
    settings.INTERNAL_API_KEY = "correct-key"
    try:
        response = authed_client.post(
            "/api/v1/internal/collect/all",
            headers={"X-Internal-API-Key": "wrong-key"}
        )
        assert response.status_code == 403
    finally:
        settings.INTERNAL_API_KEY = original


@patch("app.routers.internal.LeverCollector")
@patch("app.routers.internal.GreenhouseCollector")
def test_collect_all_success(MockGreenhouse, MockLever, client: TestClient, session: Session):
    """POST /collect/all with mocked collectors returns correct summary."""
    # Seed one enabled CollectorSource of each type
    gh_source = CollectorSource(
        company_name="TestCo GH", board_token="testco", source_type="greenhouse", enabled=True
    )
    lv_source = CollectorSource(
        company_name="TestCo LV", company_id="testco-lv", source_type="lever", enabled=True
    )
    session.add(gh_source)
    session.add(lv_source)
    session.commit()

    # Mock collector return values
    mock_gh_job = SeedJob(
        external_id="greenhouse-testco-1", title="GH Job", company_name="TestCo GH",
        description="desc", location="Remote", is_remote=True, job_type="full_time",
        skills=["Python"], apply_url="https://greenhouse.io/1", source_name="greenhouse", is_active=True
    )
    mock_lv_job = SeedJob(
        external_id="lever-testco-lv-1", title="LV Job", company_name="TestCo LV",
        description="desc", location="NYC", is_remote=False, job_type="full_time",
        skills=["React"], apply_url="https://lever.co/1", source_name="lever", is_active=True
    )

    MockGreenhouse.return_value.collect_and_normalize.return_value = [mock_gh_job]
    MockLever.return_value.collect_and_normalize.return_value = [mock_lv_job]

    response = client.post("/api/v1/internal/collect/all")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "completed"
    assert data["sources_attempted"] >= 2
    assert data["sources_succeeded"] >= 2
    assert data["sources_failed"] == 0
    assert data["total_fetched"] >= 2
    assert data["total_added"] >= 2

    # Check per-source results present
    result_companies = [r["company"] for r in data["results"]]
    assert "TestCo GH" in result_companies
    assert "TestCo LV" in result_companies


@patch("app.routers.internal.LeverCollector")
@patch("app.routers.internal.GreenhouseCollector")
def test_collect_all_updates_source_status(MockGreenhouse, MockLever, client: TestClient, session: Session):
    """After /collect/all, CollectorSource.last_success_at and counts must be set."""
    gh_source = CollectorSource(
        company_name="StatusTestCo", board_token="statustestco", source_type="greenhouse", enabled=True
    )
    session.add(gh_source)
    session.commit()
    session.refresh(gh_source)
    source_id = gh_source.id

    mock_job = SeedJob(
        external_id="greenhouse-statustestco-99", title="Status Job",
        company_name="StatusTestCo", description="desc", location="Remote",
        is_remote=True, job_type="full_time", skills=["Go"],
        apply_url="https://greenhouse.io/99", source_name="greenhouse", is_active=True
    )
    MockGreenhouse.return_value.collect_and_normalize.return_value = [mock_job]
    MockLever.return_value.collect_and_normalize.return_value = []

    response = client.post("/api/v1/internal/collect/all")
    assert response.status_code == 200

    # Verify DB status fields were updated
    session.expire_all()
    updated = session.get(CollectorSource, source_id)
    assert updated.last_run_at is not None
    assert updated.last_success_at is not None
    assert updated.last_error is None
    assert updated.last_fetched_count == 1
    assert updated.last_saved_count == 1


@patch("app.routers.internal.LeverCollector")
@patch("app.routers.internal.GreenhouseCollector")
def test_collect_all_handles_failed_source(MockGreenhouse, MockLever, client: TestClient, session: Session):
    """A failing source stores last_error and does not prevent other sources from running."""
    gh_source = CollectorSource(
        company_name="BrokenCo", board_token="brokenco", source_type="greenhouse", enabled=True
    )
    lv_source = CollectorSource(
        company_name="WorkingCo", company_id="workingco", source_type="lever", enabled=True
    )
    session.add(gh_source)
    session.add(lv_source)
    session.commit()
    session.refresh(gh_source)
    session.refresh(lv_source)
    broken_id = gh_source.id
    working_id = lv_source.id

    # Greenhouse raises; Lever succeeds
    MockGreenhouse.return_value.collect_and_normalize.side_effect = RuntimeError("Network timeout")
    mock_lv_job = SeedJob(
        external_id="lever-workingco-55", title="Working Job",
        company_name="WorkingCo", description="desc", location="Remote",
        is_remote=True, job_type="full_time", skills=["TypeScript"],
        apply_url="https://lever.co/55", source_name="lever", is_active=True
    )
    MockLever.return_value.collect_and_normalize.return_value = [mock_lv_job]

    response = client.post("/api/v1/internal/collect/all")
    assert response.status_code == 200

    data = response.json()
    assert data["sources_failed"] >= 1
    assert data["sources_succeeded"] >= 1

    # Broken source has last_error set
    session.expire_all()
    broken = session.get(CollectorSource, broken_id)
    assert broken.last_error is not None
    assert "Network timeout" in broken.last_error
    assert broken.last_success_at is None  # was never successful

    # Working source has no error
    working = session.get(CollectorSource, working_id)
    assert working.last_success_at is not None
    assert working.last_error is None


@patch("app.routers.internal.LeverCollector")
@patch("app.routers.internal.GreenhouseCollector")
def test_collect_all_save_failure_marks_source_failed(MockGreenhouse, MockLever, client: TestClient, session: Session, monkeypatch):
    """If save_imported_jobs raises, the source is marked failed with last_error set."""
    gh_source = CollectorSource(
        company_name="SaveFailCo", board_token="savefailco", source_type="greenhouse", enabled=True
    )
    lv_source = CollectorSource(
        company_name="SaveOkCo", company_id="saveokco", source_type="lever", enabled=True
    )
    session.add(gh_source)
    session.add(lv_source)
    session.commit()
    session.refresh(gh_source)
    session.refresh(lv_source)
    fail_id = gh_source.id
    ok_id = lv_source.id

    mock_gh_job = SeedJob(
        external_id="greenhouse-savefailco-1", title="Save Fail Job",
        company_name="SaveFailCo", description="desc", location="Remote",
        is_remote=True, job_type="full_time", skills=["Rust"],
        apply_url="https://greenhouse.io/1", source_name="greenhouse", is_active=True
    )
    mock_lv_job = SeedJob(
        external_id="lever-saveokco-2", title="Save Ok Job",
        company_name="SaveOkCo", description="desc", location="NYC",
        is_remote=False, job_type="full_time", skills=["Go"],
        apply_url="https://lever.co/2", source_name="lever", is_active=True
    )
    MockGreenhouse.return_value.collect_and_normalize.return_value = [mock_gh_job]
    MockLever.return_value.collect_and_normalize.return_value = [mock_lv_job]

    # Make save_imported_jobs raise on the first call (greenhouse) but succeed on the second (lever)
    original_save = seed_loader.save_imported_jobs
    call_count = {"n": 0}

    def patched_save(jobs):
        call_count["n"] += 1
        if call_count["n"] == 1:
            raise RuntimeError("DB connection lost")
        return original_save(jobs)

    monkeypatch.setattr("app.routers.internal.save_imported_jobs", patched_save)

    response = client.post("/api/v1/internal/collect/all")
    assert response.status_code == 200

    data = response.json()
    assert data["sources_failed"] >= 1
    assert data["sources_succeeded"] >= 1

    # Verify the greenhouse source was marked failed with last_error
    session.expire_all()
    fail_src = session.get(CollectorSource, fail_id)
    assert fail_src.last_error is not None
    assert "DB connection lost" in fail_src.last_error
    assert fail_src.last_success_at is None

    # Verify the lever source was still successful
    ok_src = session.get(CollectorSource, ok_id)
    assert ok_src.last_success_at is not None
    assert ok_src.last_error is None
