from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InsuranceCreate(BaseModel):
    user_id: str
    provider: str
    policy_number: str
    coverage_details: Optional[str] = None
    valid_till: Optional[str] = None

class InsuranceResponse(BaseModel):
    id: str
    user_id: str
    provider: str
    policy_number: str
    coverage_details: Optional[str]
    valid_till: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True
