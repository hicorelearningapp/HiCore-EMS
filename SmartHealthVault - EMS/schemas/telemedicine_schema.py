from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AppointmentCreate(BaseModel):
    user_id: str
    doctor_id: str
    datetime: str
    mode: Optional[str] = "video"
    status: Optional[str] = "scheduled"
    notes: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: str
    user_id: str
    doctor_id: str
    datetime: str
    mode: str
    status: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True
