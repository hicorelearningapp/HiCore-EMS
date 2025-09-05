from typing import Dict
from models.notification_model import Notification
import uuid

class NotificationService:
    def __init__(self, store: Dict[str, Notification]):
        self.store = store

    def send(self, notification: Notification):
        nid = notification.id or str(uuid.uuid4())
        notification.id = nid
        # placeholder: mark as sent True (in real app integrate with SMS/Push/Email)
        notification.sent = True
        self.store[nid] = notification
        return notification

    def get(self, notification_id: str):
        return self.store.get(notification_id)
