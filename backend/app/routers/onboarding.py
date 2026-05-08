from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
import io
from pypdf import PdfReader

router = APIRouter(tags=["onboarding"])

class ResumeUploadResponse(BaseModel):
    file_name: str
    size_bytes: int
    status: str
    text_preview: str
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
        text_length=len(extracted_text)
    )
