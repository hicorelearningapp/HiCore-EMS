from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
import datetime

class RecordCreate(BaseModel):
    user_id: str = Field(..., min_length=1)
    doctor_id: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, max_length=100)
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    file_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "user_123",
                "doctor_id": "doctor_456",
                "category": "prescription",
                "title": "Annual Checkup",
                "content": "Patient's annual checkup results",
                "file_path": "/uploads/reports/checkup.pdf",
                "metadata": {"type": "pdf", "pages": 3}
            }
        }
    )

class RecordResponse(BaseModel):
    id: str
    user_id: str
    doctor_id: Optional[str] = None
    category: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    file_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime.datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "record_789",
                "user_id": "user_123",
                "doctor_id": "doctor_456",
                "category": "prescription",
                "title": "Annual Checkup",
                "content": "Patient's annual checkup results",
                "file_path": "/uploads/reports/checkup.pdf",
                "metadata": {"type": "pdf", "pages": 3},
                "created_at": "2023-01-01T12:00:00"
            }
        }
    )
