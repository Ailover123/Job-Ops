from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from pydantic import BaseModel
import io
from pypdf import PdfReader
from sqlmodel import Session, select, desc
from app.schemas import ProfileExtractRequest, ProfileExtractResponse, ResumeProfile
from app.services.parser_service import extract_profile_from_text
from app.database import get_session
from app.db_models import Profile

router = APIRouter(tags=["onboarding"])

class ResumeUploadResponse(BaseModel):
    file_name: str
    size_bytes: int
    status: str
    text_preview: str
    extracted_text: str
    text_length: int

@router.post("/onboarding/resume", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    # Validate PDF content type or extension
    if file.content_type != "application/pdf" and not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    # Read file content
    content = await file.read()
    size = len(content)
    
    try:
        # Extract text from PDF
        pdf_file = io.BytesIO(content)
        reader = PdfReader(pdf_file)
        
        extracted_text = ""
        for page in reader.pages:
            extracted_text += page.extract_text() + "\n"
        
        extracted_text = extracted_text.strip()
        
        if not extracted_text:
            raise ValueError("No text could be extracted from the PDF.")
            
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Failed to extract text from PDF: {str(e)}"
        )
    
    return ResumeUploadResponse(
        file_name=file.filename,
        size_bytes=size,
        status="uploaded",
        text_preview=extracted_text[:500],
        extracted_text=extracted_text,
        text_length=len(extracted_text)
    )

@router.post("/onboarding/profile/extract", response_model=ProfileExtractResponse)
@router.post("/profile/extract", response_model=ProfileExtractResponse)
async def extract_profile(request: ProfileExtractRequest):
    if not request.resume_text or not request.resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text is required for extraction.")
    
    profile, method = extract_profile_from_text(request.resume_text)
    return ProfileExtractResponse(profile=profile, extraction_method=method)

@router.post("/profile")
async def save_user_profile(
    profile_data: ResumeProfile, 
    session: Session = Depends(get_session)
):
    """
    Step 2: Save the confirmed/edited profile to PostgreSQL.
    """
    db_profile = Profile(
        full_name=profile_data.full_name,
        email=profile_data.email,
        phone=profile_data.phone,
        location=profile_data.location.model_dump(),
        education=[e.model_dump() for e in profile_data.education],
        skills=[s.model_dump() for s in profile_data.skills],
        projects=[p.model_dump() for p in profile_data.projects],
        certifications=profile_data.certifications,
        suggested_roles=profile_data.suggested_roles,
        preferred_domains=profile_data.preferred_domains
    )
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    return {"status": "success", "profile_id": db_profile.id}

@router.get("/profile/latest")
async def fetch_latest_profile(session: Session = Depends(get_session)):
    """
    Fetch the most recently saved profile.
    """
    statement = select(Profile).order_by(desc(Profile.created_at)).limit(1)
    results = session.exec(statement)
    db_profile = results.first()
    
    if not db_profile:
        return {"status": "error", "message": "No profile found"}
        
    return db_profile
