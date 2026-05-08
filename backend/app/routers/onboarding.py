from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["onboarding"])

class ResumeUploadResponse(BaseModel):
    file_name: str
    size_bytes: int
    status: str

@router.post("/onboarding/resume", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    # Validate PDF content type or extension
    if file.content_type != "application/pdf" and not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    # Read file to get size (for demo purposes)
    content = await file.read()
    size = len(content)
    
    # In a real scenario, we would save the file or process it
    # For this slice, we just return the success response
    
    return ResumeUploadResponse(
        file_name=file.filename,
        size_bytes=size,
        status="uploaded"
    )
