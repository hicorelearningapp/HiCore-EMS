from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import datetime
from pydantic.config import ConfigDict

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    gender: Optional[str] = None
    age: Optional[int] = None
    dob: Optional[datetime.date] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None
    role: Optional[str] = "patient"

class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    gender: Optional[str] = None
    age: Optional[int] = None
    dob: Optional[datetime.date] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None
    role: str = "patient"

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "user_123",
                "name": "John Doe",
                "email": "john@example.com",
                "gender": "male",
                "age": 30,
                "dob": "1990-01-01",
                "blood_group": "A+",
                "address": "123 Main St",
                "role": "patient"
            }
        }
    )
