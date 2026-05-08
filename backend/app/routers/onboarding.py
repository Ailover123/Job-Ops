from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
import io
from pypdf import PdfReader
from app.schemas import ProfileExtractRequest, ProfileExtractResponse
from app.services.parser_service import extract_profile_from_text

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
async def extract_profile(request: ProfileExtractRequest):
    if not request.resume_text or not request.resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text is required for extraction.")
    
    profile, method = extract_profile_from_text(request.resume_text)
    return ProfileExtractResponse(profile=profile, extraction_method=method)
