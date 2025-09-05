from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.telemedicine_model import Appointment
from services.telemedicine_service import TelemedicineService
from database import get_db

router = APIRouter()

def _service(db=Depends(get_db)):
    return TelemedicineService(db.appointments)

@router.post("/", response_model=Appointment)
def schedule_appointment(appt: Appointment, svc: TelemedicineService = Depends(_service)):
    return svc.schedule(appt)

@router.get("/{appointment_id}", response_model=Appointment)
def get_appointment(appointment_id: str, svc: TelemedicineService = Depends(_service)):
    a = svc.get_appointment(appointment_id)
    if not a:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return a

@router.get("/doctor/{doctor_id}", response_model=List[Appointment])
def doctor_appointments(doctor_id: str, svc: TelemedicineService = Depends(_service)):
    return [a for a in svc.store.values() if a.doctor_id == doctor_id]

@router.get("/patient/{patient_id}", response_model=List[Appointment])
def patient_appointments(patient_id: str, svc: TelemedicineService = Depends(_service)):
    return svc.list_for_user(patient_id)
