# schemas/user_schema.py
from pydantic import BaseModel, EmailStr
from typing import Optional
import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    gender: Optional[str] = None
    age: Optional[int] = None
    dob: Optional[datetime.date] = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    gender: Optional[str] = None
    age: Optional[int] = None
    dob: Optional[datetime.date] = None

    class Config:
        orm_mode = True
