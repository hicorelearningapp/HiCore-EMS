from fastapi import APIRouter, HTTPException
from services.telemedicine_manager import TelemedicineManager
from schemas.telemedicine_schema import AppointmentCreate, AppointmentResponse
from typing import List

router = APIRouter(prefix="/appointments", tags=["Telemedicine"])
manager = TelemedicineManager()

@router.post("/", response_model=AppointmentResponse)
def create_appointment(appointment: AppointmentCreate):
    return manager.create_appointment(appointment)

@router.get("/", response_model=List[AppointmentResponse])
def list_appointments():
    return manager.list_appointments()

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: str):
    a = manager.get_appointment(appointment_id)
    if not a:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return a

@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(appointment_id: str, updates: dict):
    a = manager.update_appointment(appointment_id, updates)
    if not a:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return a

@router.delete("/{appointment_id}")
def delete_appointment(appointment_id: str):
    ok = manager.delete_appointment(appointment_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {"message": "Appointment deleted"}
