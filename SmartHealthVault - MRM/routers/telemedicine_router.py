from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from database.db_manager import get_db_session
from services.telemedicine_manager import TelemedicineManager
from parsers.telemedicine_parser import AppointmentCreate, AppointmentResponse

router = APIRouter(prefix="/appointments", tags=["Telemedicine"])

@router.post("/", response_model=AppointmentResponse)
def schedule(payload: AppointmentCreate, db: Session = Depends(get_db_session)):
    return TelemedicineManager(db).schedule(payload)

@router.get("/doctor/{doctor_id}", response_model=List[AppointmentResponse])
def doctor_appointments(doctor_id: str, db: Session = Depends(get_db_session)):
    return TelemedicineManager(db).list_appointments()

@router.get("/patient/{patient_id}", response_model=List[AppointmentResponse])
def patient_appointments(patient_id: str, db: Session = Depends(get_db_session)):
    return TelemedicineManager(db).list_appointments()

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: str, db: Session = Depends(get_db_session)):
    """
    Get details of a specific appointment by ID
    
    - **appointment_id**: The ID of the appointment to retrieve
    - Returns: The requested appointment details
    """
    appointment = TelemedicineManager(db).get_appointment(appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail=f"Appointment with ID {appointment_id} not found"
        )
    return appointment
