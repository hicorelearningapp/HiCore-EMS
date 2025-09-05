from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.notification_model import Notification
from services.notification_service import NotificationService
from database import get_db

router = APIRouter()

def _service(db=Depends(get_db)):
    return NotificationService(db.notifications)

@router.post("/", response_model=Notification)
def create_notification(notification: Notification, svc: NotificationService = Depends(_service)):
    return svc.send(notification)

@router.get("/{notification_id}", response_model=Notification)
def get_notification(notification_id: str, svc: NotificationService = Depends(_service)):
    n = svc.get(notification_id)
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    return n

@router.get("/user/{user_id}", response_model=List[Notification])
def get_user_notifications(user_id: str, svc: NotificationService = Depends(_service)):
    return [n for n in svc.store.values() if n.user_id == user_id]

@router.put("/{notification_id}/read", response_model=Notification)
def mark_as_read(notification_id: str, svc: NotificationService = Depends(_service)):
    n = svc.get(notification_id)
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    n.sent = True
    svc.store[notification_id] = n
    return n
