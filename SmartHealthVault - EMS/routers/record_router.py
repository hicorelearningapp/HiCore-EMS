from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form
from typing import List, Optional
from models.record_model import Record
from services.record_service import RecordService
from database import get_db

router = APIRouter()

def _service(db=Depends(get_db)):
    return RecordService(db.records)

@router.post("/", response_model=Record)
def upload_record(
    user_id: str = Form(...),
    doctor_id: Optional[str] = Form(None),
    category: Optional[str] = Form("prescription"),
    file: UploadFile = None,
    svc: RecordService = Depends(_service)
):
    record = Record(user_id=user_id, doctor_id=doctor_id, category=category, title=file.filename if file else None)
    return svc.create_record(record)

@router.get("/{record_id}", response_model=Record)
def get_record(record_id: str, svc: RecordService = Depends(_service)):
    r = svc.get_record(record_id)
    if not r:
        raise HTTPException(status_code=404, detail="Record not found")
    return r

@router.get("/patient/{patient_id}", response_model=List[Record])
def get_patient_records(patient_id: str, svc: RecordService = Depends(_service)):
    return svc.list_records_for_user(patient_id)

@router.delete("/{record_id}")
def delete_record(record_id: str, svc: RecordService = Depends(_service)):
    deleted = svc.delete_record(record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"message": "Record deleted successfully"}
