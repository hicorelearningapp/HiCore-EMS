from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from database.db_manager import get_db_session
from schemas.telemedicine_schema import TelemedicineParser
from parsers.telemedicine_parser import AppointmentCreate

router = APIRouter(prefix="/appointments", tags=["Telemedicine"])

@router.post("/", response_model=TelemedicineParser.to_response)
def schedule(payload: AppointmentCreate, db: Session = Depends(get_db_session)):
    return TelemedicineManager(db).schedule(payload)

@router.get("/doctor/{doctor_id}", response_model=List[AppointmentResponse])
def doctor_appointments(doctor_id: str, db: Session = Depends(get_db_session)):
    return TelemedicineManager(db).list_appointments()

@router.get("/patient/{patient_id}", response_model=List[AppointmentResponse])
def patient_appointments(patient_id: str, db: Session = Depends(get_db_session)):
    return TelemedicineManager(db).list_appointments()
