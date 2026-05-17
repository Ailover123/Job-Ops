import io
import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session

# Setup in-memory SQLite for testing to avoid hitting live Postgres
# This is a common pattern for fast unit tests.
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

def test_upload_resume_success(client: TestClient):
    # Use the downloaded sample.pdf for extraction test
    pdf_path = os.path.join(os.path.dirname(__file__), "sample.pdf")
    
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_content = f.read()
    else:
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Title (Test) >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"

    file_name = "test_resume.pdf"
    
    response = client.post(
        "/api/v1/onboarding/resume",
        files={"file": (file_name, io.BytesIO(pdf_content), "application/pdf")}
    )
    
    if not os.path.exists(pdf_path):
        assert response.status_code == 400
    else:
        assert response.status_code == 200
        data = response.json()
        assert data["file_name"] == file_name
        assert data["status"] == "uploaded"
        assert "extracted_text" in data

def test_save_and_fetch_profile(client: TestClient):
    # 1. Save profile
    profile_data = {
        "full_name": "Test User",
        "email": "test@example.com",
        "phone": "1234567890",
        "location": {"city": "Bangalore", "state": "KA", "country": "India"},
        "education": [],
        "skills": [{"name": "Python", "type": "technical", "confidence": 1.0}],
        "projects": [],
        "certifications": [],
        "suggested_roles": ["Developer"],
        "preferred_domains": []
    }
    
    save_response = client.post("/api/v1/profile", json=profile_data)
    assert save_response.status_code == 200
    assert save_response.json()["status"] == "success"
    
    # 2. Fetch latest
    fetch_response = client.get("/api/v1/profile/latest")
    assert fetch_response.status_code == 200
    data = fetch_response.json()
    assert data["full_name"] == "Test User"
    assert data["email"] == "test@example.com"
    assert data["skills"][0]["name"] == "Python"

def test_upload_resume_invalid_type(client: TestClient):
    text_content = b"This is a text file, not a PDF."
    response = client.post(
        "/api/v1/onboarding/resume",
        files={"file": ("test.txt", io.BytesIO(text_content), "text/plain")}
    )
    assert response.status_code == 400

def test_extract_profile_endpoints(client: TestClient):
    # Test canonical route
    response_canonical = client.post(
        "/api/v1/onboarding/profile/extract",
        json={"resume_text": "John Doe, Python, Javascript"}
    )
    assert response_canonical.status_code == 200
    data_c = response_canonical.json()
    assert "profile" in data_c
    assert data_c["extraction_method"] in ["gemini", "fallback"]

    # Test alias route
    response_alias = client.post(
        "/api/v1/profile/extract",
        json={"resume_text": "John Doe, Python, Javascript"}
    )
    assert response_alias.status_code == 200
    data_a = response_alias.json()
    assert "profile" in data_a
    assert data_a["extraction_method"] in ["gemini", "fallback"]

def test_extract_profile_empty_text(client: TestClient):
    response = client.post(
        "/api/v1/onboarding/profile/extract",
        json={"resume_text": ""}
    )
    assert response.status_code == 400
    assert "Resume text is required" in response.json()["detail"]
