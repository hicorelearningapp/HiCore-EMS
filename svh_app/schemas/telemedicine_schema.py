from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    IN_PROGRESS = "in_progress"

class AppointmentType(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"
    IN_PERSON = "in_person"

class AppointmentCreate(BaseModel):
    doctor_id: str
    patient_id: str
    appointment_time: datetime
    duration_minutes: int = 30
    appointment_type: AppointmentType = AppointmentType.VIDEO
    reason: Optional[str] = None
    notes: Optional[str] = None

class AppointmentResponse(AppointmentCreate):
    id: str
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    created_at: datetime
    updated_at: datetime
    meeting_link: Optional[str] = None
    
    class Config:
        orm_mode = True

class AppointmentUpdate(BaseModel):
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None
    meeting_link: Optional[str] = None
    duration_minutes: Optional[int] = None

class PrescriptionItem(BaseModel):
    medicine_name: str
    dosage: str
    frequency: str
    duration: str
    instructions: Optional[str] = None

class PrescriptionCreate(BaseModel):
    appointment_id: str
    diagnosis: str
    notes: Optional[str] = None
    medicines: List[PrescriptionItem] = []

class PrescriptionResponse(PrescriptionCreate):
    id: str
    doctor_id: str
    patient_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
