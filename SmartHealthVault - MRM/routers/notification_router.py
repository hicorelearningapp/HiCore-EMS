from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from database.db_manager import get_db_session
from services.notification_manager import NotificationManager
from parsers.notification_parser import NotificationCreate, NotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post("/", response_model=NotificationResponse)
def create_notification(payload: NotificationCreate, db: Session = Depends(get_db_session)):
    return NotificationManager(db).create_notification(payload)

@router.get("/user/{user_id}", response_model=List[NotificationResponse])
def user_notifications(user_id: str, db: Session = Depends(get_db_session)):
    return NotificationManager(db).list_notifications()

@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_read(notification_id: str, db: Session = Depends(get_db_session)):
    n = NotificationManager(db).mark_as_read(notification_id)
    if not n: raise HTTPException(status_code=404, detail="Notification not found")
    return n
