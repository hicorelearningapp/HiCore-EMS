from fastapi import APIRouter, HTTPException
from services.record_manager import RecordManager
from schemas.record_schema import RecordCreate, RecordResponse
from typing import List

router = APIRouter(prefix="/records", tags=["Records"])
manager = RecordManager()

@router.post("/", response_model=RecordResponse)
def create_record(record: RecordCreate):
    return manager.create_record(record)

@router.get("/", response_model=List[RecordResponse])
def list_records():
    return manager.list_records()

@router.get("/{record_id}", response_model=RecordResponse)
def get_record(record_id: str):
    r = manager.get_record(record_id)
    if not r:
        raise HTTPException(status_code=404, detail="Record not found")
    return r

@router.put("/{record_id}", response_model=RecordResponse)
def update_record(record_id: str, updates: dict):
    r = manager.update_record(record_id, updates)
    if not r:
        raise HTTPException(status_code=404, detail="Record not found")
    return r

@router.delete("/{record_id}")
def delete_record(record_id: str):
    ok = manager.delete_record(record_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"message": "Record deleted"}
