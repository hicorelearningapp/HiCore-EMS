from pydantic import BaseModel
from typing import Optional

class DoctorCreate(BaseModel):
    name: str
    specialization: Optional[str] = None
    qualifications: Optional[str] = None
    languages: Optional[str] = None
    clinic_address: Optional[str] = None

    class Config:
        from_attributes = True

class DoctorResponse(BaseModel):
    id: str
    name: str
    specialization: Optional[str] = None
    qualifications: Optional[str] = None
    languages: Optional[str] = None
    clinic_address: Optional[str] = None

    class Config:
        from_attributes = True
        orm_mode = True
