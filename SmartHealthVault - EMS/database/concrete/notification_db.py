from database.base import SessionLocal
from database.interfaces import IDatabase
from models.notification_model import NotificationModel
from sqlalchemy.orm import Session

class NotificationDatabase(IDatabase):
    def __init__(self):
        self.session: Session = SessionLocal()

    def execute_query(self, query: str, params: dict = None):
        return self.session.execute(query, params)

    def add_notification(self, notification: NotificationModel):
        self.session.add(notification)
        self.session.commit()
        self.session.refresh(notification)
        return notification

    def get_notification(self, notification_id: str):
        return self.session.query(NotificationModel).filter(NotificationModel.id == notification_id).first()

    def list_notifications(self):
        return self.session.query(NotificationModel).all()

    def mark_as_read(self, notification_id: str):
        notification = self.get_notification(notification_id)
        if not notification:
            return None
        notification.read = True
        self.session.commit()
        self.session.refresh(notification)
        return notification

    def delete_notification(self, notification_id: str):
        notification = self.get_notification(notification_id)
        if not notification:
            return None
        self.session.delete(notification)
        self.session.commit()
        return True
