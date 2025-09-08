from pydantic import BaseModel
from typing import Optional, Dict
import datetime

class RecordCreate(BaseModel):
    user_id: str
    doctor_id: Optional[str] = None
    category: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    file_path: Optional[str] = None
    metadata: Optional[Dict] = None

class RecordResponse(BaseModel):
    id: str
    user_id: str
    doctor_id: Optional[str] = None
    category: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    file_path: Optional[str] = None
    metadata: Optional[Dict] = None
    created_at: datetime.datetime

    class Config:
        orm_mode = True
