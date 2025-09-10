from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime

class PolicyCreate(BaseModel):
    patient_id: str
    name: str
    sum_insured: int
    premium: float
    details: Optional[Dict] = None

class PolicyResponse(PolicyCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    status: str = "active"

    class Config:
        orm_mode = True

class ClaimCreate(BaseModel):
    policy_id: str
    amount: float
    description: str
    documents: Optional[List] = []

class ClaimResponse(ClaimCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    status: str = "pending"
    processed_at: Optional[datetime] = None
    processed_by: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        orm_mode = True
