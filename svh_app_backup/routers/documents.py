import os
import sys
from pathlib import Path

# Add the parent directory to Python path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import FileResponse
from typing import List
import shutil
from sqlalchemy.orm import Session

# Now use absolute imports from the project root
from services.document_processor import DocumentProcessor
from models.user_model import User
from database.db_manager import get_db_session

router = APIRouter(
    prefix="/api/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}},
)

# Ensure upload directories exist
UPLOAD_DIR = "uploads/raw"
PROCESSED_DIR = "uploads/processed"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Get database session generator
get_db = get_db_session()

def get_current_user():
    # This is a simplified version - you should implement proper token validation
    db = next(get_db)
    try:
        user = db.query(User).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    finally:
        try:
            next(get_db)  # This will execute the finally block in get_db_session
        except StopIteration:
            pass

@router.post("/upload/", response_model=dict)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a document and process it with OCR to create a searchable PDF.
    """
    try:
        # Validate file type
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.pdf'}
        file_ext = Path(file.filename).suffix.lower() if file.filename else ''
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Save original file with user ID prefix
        file_path = os.path.join(UPLOAD_DIR, f"{current_user.id}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the file to create searchable PDF
        processor = DocumentProcessor()
        
        # If it's a PDF, we'd need to convert pages to images first
        # For now, we'll handle image files
        if file_ext in {'.png', '.jpg', '.jpeg', '.tiff', '.bmp'}:
            # Reset file pointer to the beginning for processing
            await file.seek(0)
            processed_path = processor.image_to_searchable_pdf(file, PROCESSED_DIR)
        else:
            # For PDFs, we'd need additional processing (can be implemented later)
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="PDF processing is not yet implemented. Please upload an image file."
            )
        
        return {
            "status": "success",
            "original_file": file.filename,
            "processed_file": os.path.basename(processed_path),
            "download_url": f"/api/documents/download/{os.path.basename(processed_path)}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )

@router.get("/download/{filename}")
async def download_document(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Download a processed document.
    """
    file_path = os.path.join(PROCESSED_DIR, filename)
    
    # Security check: Ensure the filename is safe and exists
    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Additional security: Verify the user has access to this file
    if not filename.startswith(f"{current_user.id}_"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return FileResponse(
        file_path,
        media_type='application/pdf',
        filename=f"searchable_{filename}"
    )

@router.get("/user-documents/")
async def list_user_documents(
    current_user: User = Depends(get_current_user)
):
    """
    List all documents uploaded by the current user.
    """
    user_files = []
    
    # Check processed files directory
    if os.path.exists(PROCESSED_DIR):
        for filename in os.listdir(PROCESSED_DIR):
            if filename.startswith(f"{current_user.id}_"):
                file_path = os.path.join(PROCESSED_DIR, filename)
                user_files.append({
                    "filename": filename,
                    "size": os.path.getsize(file_path),
                    "created_at": os.path.getctime(file_path),
                    "download_url": f"/api/documents/download/{filename}"
                })
    
    return {
        "status": "success",
        "documents": user_files
    }

# Export the router
__all__ = ["router"]
