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

def test_roadmap_empty_profile(client: TestClient):
    response = client.post(
        "/api/v1/roadmap/skill-gap",
        json={"desired_role": "AI Engineer Intern"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["desired_role"] == "AI Engineer Intern"
    assert len(data["existing_skills"]) == 0
    assert len(data["missing_skills"]) > 0
    assert len(data["recommended_learning_order"]) > 0
    assert len(data["suggested_project_ideas"]) > 0
    assert "explanation" in data
    # Check fallback/GenAI text is present and informative
    assert len(data["explanation"]) > 0

def test_roadmap_with_profile(client: TestClient):
    # 1. Save profile with Python, SQL, and Git
    profile_data = {
        "full_name": "Test Candidate",
        "email": "candidate@example.com",
        "phone": "5551234",
        "location": {"city": "New York", "state": "NY", "country": "USA"},
        "education": [],
        "skills": [
            {"name": "Python", "type": "technical", "confidence": 1.0},
            {"name": "SQL", "type": "technical", "confidence": 0.9},
            {"name": "Git", "type": "technical", "confidence": 0.8}
        ],
        "projects": [],
        "certifications": [],
        "suggested_roles": ["Backend Developer"],
        "preferred_domains": []
    }
    save_response = client.post("/api/v1/profile", json=profile_data)
    assert save_response.status_code == 200

    # 2. Get roadmap for Backend Developer
    response = client.post(
        "/api/v1/roadmap/skill-gap",
        json={"desired_role": "Backend Developer"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["desired_role"] == "Backend Developer"
    
    # Python and Git should be listed under existing skills
    existing_skills_lower = [s.lower() for s in data["existing_skills"]]
    assert "python" in existing_skills_lower
    assert "git" in existing_skills_lower
    
    # Missing skills should be clean and not contain Python or Git
    missing_skills_lower = [s.lower() for s in data["missing_skills"]]
    assert "python" not in missing_skills_lower
    assert "git" not in missing_skills_lower

def test_roadmap_unknown_role(client: TestClient):
    response = client.post(
        "/api/v1/roadmap/skill-gap",
        json={"desired_role": "Interstellar Chef"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["desired_role"] == "Interstellar Chef"
    # Fallback to general tech stack
    assert len(data["missing_skills"]) > 0
    assert data["matching_jobs_used_count"] == 0

def test_roadmap_invalid_role(client: TestClient):
    response = client.post(
        "/api/v1/roadmap/skill-gap",
        json={"desired_role": ""}
    )
    assert response.status_code == 400
    assert "Desired role is required" in response.json()["detail"]
