from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class NotificationType(str, Enum):
    APPOINTMENT = "appointment"
    MEDICATION = "medication"
    SYSTEM = "system"
    BILLING = "billing"
    OTHER = "other"

class NotificationStatus(str, Enum):
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"

class NotificationCreate(BaseModel):
    user_id: str
    title: str
    message: str
    notification_type: NotificationType = NotificationType.SYSTEM
    related_entity_id: Optional[str] = None
    related_entity_type: Optional[str] = None

class NotificationResponse(NotificationCreate):
    id: str
    status: NotificationStatus = NotificationStatus.UNREAD
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class NotificationUpdate(BaseModel):
    status: Optional[NotificationStatus] = None
    read: Optional[bool] = None

class NotificationList(BaseModel):
    items: List[NotificationResponse]
    total: int
    page: int
    size: int
