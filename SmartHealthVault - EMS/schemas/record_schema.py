from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RecordCreate(BaseModel):
    user_id: str
    doctor_id: Optional[str] = None
    category: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    file_path: Optional[str] = None
    metadata: Optional[str] = None

class RecordResponse(BaseModel):
    id: str
    user_id: str
    doctor_id: Optional[str] = None
    category: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    file_path: Optional[str] = None
    metadata: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
