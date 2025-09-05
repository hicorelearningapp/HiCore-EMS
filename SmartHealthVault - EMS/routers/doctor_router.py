from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.doctor_model import Doctor
from services.doctor_service import DoctorService
from database import get_db

router = APIRouter()

def _service(db=Depends(get_db)):
    return DoctorService(db.doctors)

@router.post("/", response_model=Doctor)
def register_doctor(doctor: Doctor, svc: DoctorService = Depends(_service)):
    return svc.create_doctor(doctor)

@router.get("/", response_model=List[Doctor])
def list_doctors(svc: DoctorService = Depends(_service)):
    return svc.list_doctors()

@router.get("/{doctor_id}", response_model=Doctor)
def get_doctor(doctor_id: str, svc: DoctorService = Depends(_service)):
    d = svc.get_doctor(doctor_id)
    if not d:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return d

@router.get("/specialty/{specialty}", response_model=List[Doctor])
def find_by_specialty(specialty: str, svc: DoctorService = Depends(_service)):
    return [doc for doc in svc.list_doctors() if doc.specialization == specialty]
