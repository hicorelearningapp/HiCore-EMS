from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional
from sqlalchemy.orm import Session
from database.db_manager import get_db_session
from services.record_manager import RecordManager
import shutil, os
from uuid import uuid4
from schemas.record_schema import RecordCreate, RecordResponse

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/records", tags=["Records"])

@router.post("/", response_model=RecordResponse)
def upload_record(
    user_id: str = Form(...),
    doctor_id: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db_session)
):
    file_path = None
    if file:
        filename = f"{uuid4().hex}_{file.filename}"
        path = os.path.join(UPLOAD_DIR, filename)
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_path = path
    payload = RecordCreate(user_id=user_id, doctor_id=doctor_id, category=category, title=title, file_path=file_path)
    return RecordManager(db).create_record(payload)
