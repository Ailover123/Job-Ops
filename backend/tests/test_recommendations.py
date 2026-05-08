import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.db_models import Profile

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

def test_recommendations_no_profile(client: TestClient):
    """Test getting recommendations when no profile exists."""
    response = client.get("/api/v1/recommendations/latest-profile")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "no_profile"
    assert data["items"] == []

def test_recommendations_personalized(client: TestClient, session: Session):
    """Test getting recommendations based on a saved profile."""
    # Create a profile
    db_profile = Profile(
        full_name="Test User",
        skills=[{"name": "Python"}, {"name": "FastAPI"}],
        suggested_roles=["Backend Engineer"],
        location={"city": "Bangalore"}
    )
    session.add(db_profile)
    session.commit()

    response = client.get("/api/v1/recommendations/latest-profile")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "personalized"
    assert len(data["items"]) > 0
    # The first item should have some score
    assert data["items"][0]["final_score"] >= 0
