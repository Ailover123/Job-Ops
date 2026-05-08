import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_resume_success():
    # Create a dummy PDF content
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Title (Test) >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    file_name = "test_resume.pdf"
    
    response = client.post(
        "/api/v1/onboarding/resume",
        files={"file": (file_name, io.BytesIO(pdf_content), "application/pdf")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["file_name"] == file_name
    assert data["status"] == "uploaded"
    assert data["size_bytes"] == len(pdf_content)

def test_upload_resume_invalid_type():
    # Create a dummy text content
    text_content = b"This is a text file, not a PDF."
    file_name = "test_resume.txt"
    
    response = client.post(
        "/api/v1/onboarding/resume",
        files={"file": (file_name, io.BytesIO(text_content), "text/plain")}
    )
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are allowed."
