from fastapi import APIRouter, HTTPException
from services.notification_manager import NotificationManager
from schemas.notification_schema import NotificationCreate, NotificationResponse
from typing import List

router = APIRouter(prefix="/notifications", tags=["Notifications"])
manager = NotificationManager()

@router.post("/", response_model=NotificationResponse)
def create_notification(notification: NotificationCreate):
    return manager.create_notification(notification)

@router.get("/", response_model=List[NotificationResponse])
def list_notifications():
    return manager.list_notifications()

@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(notification_id: str):
    n = manager.get_notification(notification_id)
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    return n

@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_as_read(notification_id: str):
    n = manager.mark_as_read(notification_id)
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    return n

@router.delete("/{notification_id}")
def delete_notification(notification_id: str):
    ok = manager.delete_notification(notification_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted"}
