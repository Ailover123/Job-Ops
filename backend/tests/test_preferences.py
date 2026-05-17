import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.db_models import Profile, Preferences

# Setup in-memory SQLite for testing
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

def test_create_and_get_preferences(client: TestClient):
    """Test saving and retrieving preferences."""
    # Retrieve when no preferences saved yet
    response = client.get("/api/v1/preferences/latest")
    assert response.status_code == 200
    assert response.json() is None

    # Post new preferences
    pref_data = {
        "preferred_roles": ["Frontend Engineer", "React Developer"],
        "preferred_locations": ["Bangalore", "San Francisco"],
        "remote_preference": "remote_only",
        "job_types": ["full_time"],
        "preferred_tech_stack": ["React", "TypeScript", "Tailwind"],
        "willing_to_relocate": True
    }
    response = client.post("/api/v1/preferences", json=pref_data)
    assert response.status_code == 200
    data = response.json()
    assert data["preferred_roles"] == ["Frontend Engineer", "React Developer"]
    assert data["preferred_locations"] == ["Bangalore", "San Francisco"]
    assert data["remote_preference"] == "remote_only"
    assert data["job_types"] == ["full_time"]
    assert data["preferred_tech_stack"] == ["React", "TypeScript", "Tailwind"]
    assert data["willing_to_relocate"] is True
    assert "id" in data

    # Retrieve latest preferences
    response = client.get("/api/v1/preferences/latest")
    assert response.status_code == 200
    data = response.json()
    assert data["preferred_roles"] == ["Frontend Engineer", "React Developer"]
    assert data["willing_to_relocate"] is True

def test_recommendations_with_preferences_only(client: TestClient):
    """Test recommendations when only preferences exist (no profile)."""
    pref_data = {
        "preferred_roles": ["Python Developer"],
        "preferred_locations": ["Remote"],
        "remote_preference": "remote_only",
        "job_types": ["internship"],
        "preferred_tech_stack": ["Python"],
        "willing_to_relocate": False
    }
    client.post("/api/v1/preferences", json=pref_data)

    response = client.get("/api/v1/recommendations/latest-profile")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "personalized"
    assert len(data["items"]) > 0

def test_recommendations_with_merged_profile_and_preferences(client: TestClient, session: Session):
    """Test that recommendations correctly merge profile parsing and preference overrides."""
    # Create profile
    db_profile = Profile(
        full_name="Test Fresher",
        skills=[{"name": "Python"}],
        suggested_roles=["Data Analyst"],
        location={"city": "Pune"}
    )
    session.add(db_profile)
    session.commit()

    # Create preferences overriding roles & locations and adding tech skills
    pref_data = {
        "preferred_roles": ["ML Engineer"],
        "preferred_locations": ["Bangalore"],
        "remote_preference": "remote_or_hybrid",
        "job_types": ["full_time"],
        "preferred_tech_stack": ["PyTorch", "FastAPI"],
        "willing_to_relocate": True
    }
    client.post("/api/v1/preferences", json=pref_data)

    response = client.get("/api/v1/recommendations/latest-profile")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "personalized"
    # Verify items are returned
    assert len(data["items"]) > 0
