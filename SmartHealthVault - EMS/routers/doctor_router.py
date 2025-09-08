from fastapi import APIRouter, HTTPException
from services.doctor_manager import DoctorManager
from schemas.doctor_schema import DoctorCreate, DoctorResponse
from typing import List

router = APIRouter(prefix="/doctors", tags=["Doctors"])
manager = DoctorManager()

@router.post("/", response_model=DoctorResponse)
def create_doctor(doctor: DoctorCreate):
    return manager.create_doctor(doctor)

@router.get("/", response_model=List[DoctorResponse])
def list_doctors():
    return manager.list_doctors()

@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor(doctor_id: str):
    d = manager.get_doctor(doctor_id)
    if not d:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return d

@router.put("/{doctor_id}", response_model=DoctorResponse)
def update_doctor(doctor_id: str, updates: dict):
    d = manager.update_doctor(doctor_id, updates)
    if not d:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return d

@router.delete("/{doctor_id}")
def delete_doctor(doctor_id: str):
    ok = manager.delete_doctor(doctor_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return {"message": "Doctor deleted"}
