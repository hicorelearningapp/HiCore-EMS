from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationCreate(BaseModel):
    user_id: str
    title: str
    message: str

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    read: bool
    created_at: datetime

    class Config:
        orm_mode = True
