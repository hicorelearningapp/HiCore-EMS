from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from database.db_manager import get_db_session
from services.record_manager import RecordManager
import shutil, os
from uuid import uuid4
from parsers.record_parser import RecordCreate, RecordResponse
import mimetypes

# Define upload directories
UPLOAD_BASE_DIR = "./uploads/raw"
UPLOAD_IMAGE_DIR = os.path.join(UPLOAD_BASE_DIR, "images")
UPLOAD_PDF_DIR = os.path.join(UPLOAD_BASE_DIR, "pdfs")

# Create upload directories if they don't exist
os.makedirs(UPLOAD_IMAGE_DIR, exist_ok=True)
os.makedirs(UPLOAD_PDF_DIR, exist_ok=True)

# Allowed file types
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif"}
ALLOWED_PDF_TYPES = {"application/pdf"}
ALLOWED_TYPES = ALLOWED_IMAGE_TYPES.union(ALLOWED_PDF_TYPES)

router = APIRouter(prefix="/records", tags=["Records"])

def get_upload_dir(content_type: str) -> str:
    """Determine the upload directory based on file type"""
    if content_type in ALLOWED_IMAGE_TYPES:
        return UPLOAD_IMAGE_DIR
    elif content_type in ALLOWED_PDF_TYPES:
        return UPLOAD_PDF_DIR
    else:
        raise ValueError(f"Unsupported file type: {content_type}")

@router.post("/", response_model=RecordResponse)
async def upload_record(
    user_id: str = Form(...),
    doctor_id: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db_session)
):
    # Check if file is provided
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Get file content type
    content_type = file.content_type
    
    # Validate file type
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_TYPES)}"
        )
    
    try:
        # Determine upload directory based on file type
        upload_dir = get_upload_dir(content_type)
        
        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1]  # Get original extension
        filename = f"{uuid4().hex}{file_ext}"
        file_path = os.path.join(upload_dir, filename)
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create record in database
        payload = RecordCreate(
            user_id=user_id, 
            doctor_id=doctor_id, 
            category=category, 
            title=title or file.filename,
            file_path=file_path
        )
        return RecordManager(db).create_record(payload)
        
    except Exception as e:
        # Clean up file if there was an error
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/{record_id}", response_model=dict)
def get_record(record_id: str, db: Session = Depends(get_db_session)):
    """
    Get a specific record by ID, including its file content if available.
    
    - **record_id**: The ID of the record to retrieve
    - Returns: Record details and file content if available
    """
    record = RecordManager(db).get_record(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    # If the record has a file path, read the file content
    file_content = None
    if record.get('file_path') and os.path.exists(record['file_path']):
        try:
            with open(record['file_path'], 'rb') as file:
                file_content = file.read().decode('utf-8', errors='replace')
        except Exception as e:
            file_content = f"[Error reading file: {str(e)}]"
    
    return {
        "record": record,
        "file_content": file_content
    }

@router.get("/patient/{patient_id}", response_model=List[dict])
def get_patient_records(patient_id: str, db: Session = Depends(get_db_session)):
    """
    Get all records for a specific patient
    
    - **patient_id**: ID of the patient whose records to retrieve
    - Returns: List of record dictionaries for the specified patient
    """
    records = RecordManager(db).get_records_by_patient(patient_id)
    if not records:
        raise HTTPException(
            status_code=404,
            detail=f"No records found for patient with ID: {patient_id}"
        )
    # Convert Pydantic models to dictionaries
    return [record.model_dump() if hasattr(record, 'model_dump') else record 
            for record in records]

@router.delete("/{record_id}", response_model=dict)
def delete_record(record_id: str, db: Session = Depends(get_db_session)):
    """
    Delete a specific record by ID
    
    - **record_id**: The ID of the record to delete
    - Returns: Success message if deletion was successful
    """
    # First check if the record exists
    record = RecordManager(db).get_record(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    # If the record has an associated file, delete it
    if record.get('file_path') and os.path.exists(record['file_path']):
        try:
            os.remove(record['file_path'])
        except Exception as e:
            # Log the error but don't fail the request
            print(f"Warning: Could not delete file {record['file_path']}: {str(e)}")
    
    # Delete the record from the database
    success = RecordManager(db).delete_record(record_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete record")
    
    return {"message": "Record deleted successfully"}
