from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AIResultCreate(BaseModel):
    user_id: str
    result: Optional[str] = None
    explanation: Optional[str] = None

class AIResultResponse(BaseModel):
    id: str
    user_id: str
    result: Optional[str]
    explanation: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True
