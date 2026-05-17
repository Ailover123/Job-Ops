import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_save_job_success_and_duplicate(client: TestClient):
    job_data = {
        "job_external_id": "job_123",
        "job_title": "Software Engineer",
        "company_name": "Tech Corp",
        "location": "San Francisco",
        "source_name": "LinkedIn",
        "apply_url": "https://linkedin.com/jobs/123",
        "skills": ["Python", "React"]
    }
    
    # 1. Save job
    response = client.post("/api/v1/saved-jobs", json=job_data)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["item"]["job_external_id"] == "job_123"
    assert response.json()["item"]["location"] == "San Francisco"
    assert response.json()["item"]["skills"] == ["Python", "React"]
    
    # 2. Save duplicate
    response = client.post("/api/v1/saved-jobs", json=job_data)
    assert response.status_code == 200
    assert response.json()["message"] == "already_saved"
    
    # 3. List saved jobs
    response = client.get("/api/v1/saved-jobs")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1

def test_delete_saved_job(client: TestClient):
    job_data = {
        "job_external_id": "job_456",
        "job_title": "Data Scientist",
        "company_name": "Data AI",
        "location": "Remote",
        "source_name": "Indeed",
        "apply_url": "https://indeed.com/jobs/456",
        "skills": ["Python", "R"]
    }
    client.post("/api/v1/saved-jobs", json=job_data)
    
    # Delete existing
    response = client.delete("/api/v1/saved-jobs/job_456")
    assert response.status_code == 200
    assert response.json()["message"] == "job_removed"
    
    # Delete non-existing
    response = client.delete("/api/v1/saved-jobs/job_999")
    assert response.status_code == 404

def test_record_application_success_and_update(client: TestClient):
    app_data = {
        "job_external_id": "job_789",
        "job_title": "Frontend dev",
        "company_name": "Web Co",
        "location": "New York",
        "source_name": "Wellfound",
        "apply_url": "https://wellfound.com/jobs/789",
        "skills": ["JS", "CSS"]
    }
    
    # 1. Record application
    response = client.post("/api/v1/applications", json=app_data)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["item"]["status"] == "applied"
    assert response.json()["item"]["location"] == "New York"
    
    # 2. Record application (update status/notes)
    update_data = {**app_data, "status": "interviewing", "notes": "Got a call!"}
    response = client.post("/api/v1/applications", json=update_data)
    assert response.status_code == 200
    assert response.json()["message"] == "application_updated"
    assert response.json()["item"]["status"] == "interviewing"
    assert response.json()["item"]["notes"] == "Got a call!"
    
    # 3. List applications
    response = client.get("/api/v1/applications")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1

def test_empty_lists(client: TestClient):
    response = client.get("/api/v1/saved-jobs")
    assert response.status_code == 200
    assert response.json()["items"] == []
    
    response = client.get("/api/v1/applications")
    assert response.status_code == 200
    assert response.json()["items"] == []

def test_update_application_status_and_notes(client: TestClient):
    app_data = {
        "job_external_id": "job_abc",
        "job_title": "Software Engineer",
        "company_name": "Antigravity",
        "location": "Remote",
        "source_name": "GitHub",
        "apply_url": "https://github.com/careers/abc",
        "skills": ["Python"]
    }
    # Record application
    client.post("/api/v1/applications", json=app_data)
    
    # 1. Update both status and notes
    response = client.put(
        "/api/v1/applications/job_abc",
        json={"status": "interviewing", "notes": "Got a call!"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["item"]["status"] == "interviewing"
    assert response.json()["item"]["notes"] == "Got a call!"
    
    # 2. Update status only, notes must remain "Got a call!"
    response = client.put(
        "/api/v1/applications/job_abc",
        json={"status": "offer"}
    )
    assert response.status_code == 200
    assert response.json()["item"]["status"] == "offer"
    assert response.json()["item"]["notes"] == "Got a call!"
    
    # 3. Update notes only, status must remain "offer"
    response = client.put(
        "/api/v1/applications/job_abc",
        json={"notes": "Offer of 200k!"}
    )
    assert response.status_code == 200
    assert response.json()["item"]["status"] == "offer"
    assert response.json()["item"]["notes"] == "Offer of 200k!"

def test_update_application_validation_error(client: TestClient):
    app_data = {
        "job_external_id": "job_def",
        "job_title": "Software Engineer",
        "company_name": "Antigravity",
        "location": "Remote",
        "source_name": "GitHub",
        "apply_url": "https://github.com/careers/def",
        "skills": ["Python"]
    }
    client.post("/api/v1/applications", json=app_data)
    
    # Attempt update to invalid status value
    response = client.put(
        "/api/v1/applications/job_def",
        json={"status": "hired"}  # invalid
    )
    assert response.status_code == 422

def test_update_application_not_found(client: TestClient):
    response = client.put(
        "/api/v1/applications/non_existent_job",
        json={"status": "interviewing"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"


def test_get_job_detail_anonymous(client: TestClient):
    response = client.get("/api/v1/jobs/seed-001")
    assert response.status_code == 200
    data = response.json()
    assert data["job"]["external_id"] == "seed-001"
    assert data["has_profile"] is False
    assert data["match_score"] is None
    assert data["match_explanation"] is None


def test_get_job_detail_personalized(client: TestClient, session: Session):
    from app.db_models import Profile, Preferences
    
    profile = Profile(
        full_name="John Doe",
        email="john@example.com",
        skills=[{"name": "Python"}, {"name": "FastAPI"}],
        location={"city": "Remote"}
    )
    session.add(profile)
    
    pref = Preferences(
        preferred_roles=["Python Developer Intern"],
        preferred_locations=["Remote"],
        remote_preference="remote_only",
        job_types=["internship"]
    )
    session.add(pref)
    session.commit()
    
    response = client.get("/api/v1/jobs/seed-001")
    assert response.status_code == 200
    data = response.json()
    assert data["job"]["external_id"] == "seed-001"
    assert data["has_profile"] is True
    assert data["match_score"] is not None
    assert isinstance(data["match_score"], int)
    assert "Python" in data["match_explanation"] or "fastapi" in data["match_explanation"].lower()


def test_get_job_detail_not_found(client: TestClient):
    response = client.get("/api/v1/jobs/invalid-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"
