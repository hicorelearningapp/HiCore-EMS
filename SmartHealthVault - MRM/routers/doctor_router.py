from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from database.db_manager import get_db_session
from services.doctor_manager import DoctorManager
from parsers.doctor_parser import DoctorCreate, DoctorResponse

router = APIRouter(prefix="/doctors", tags=["Doctors"])

@router.post("/", response_model=DoctorResponse)
def create_doctor(payload: DoctorCreate, db: Session = Depends(get_db_session)):
    return DoctorManager(db).create_doctor(payload)

@router.get("/", response_model=List[DoctorResponse])
def list_doctors(db: Session = Depends(get_db_session)):
    return DoctorManager(db).list_doctors()

@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor(doctor_id: str, db: Session = Depends(get_db_session)):
    d = DoctorManager(db).get_doctor(doctor_id)
    if not d: raise HTTPException(status_code=404, detail="Doctor not found")
    return d

@router.get("/specialty/{specialty}", response_model=List[DoctorResponse])
def find_by_specialty(specialty: str, db: Session = Depends(get_db_session)):
    return DoctorManager(db).list_doctors(specialization=specialty)
