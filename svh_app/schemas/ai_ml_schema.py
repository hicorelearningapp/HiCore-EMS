from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime

class AIRequest(BaseModel):
    user_id: str
    record_ids: Optional[List[str]] = []
    prompt: Optional[str] = None
    inputs: Optional[Dict] = None

class AIResponse(BaseModel):
    id: str
    user_id: str
    result: Optional[Dict] = {}
    explanation: Optional[str] = None
    created_at: datetime = None

    class Config:
        orm_mode = True
