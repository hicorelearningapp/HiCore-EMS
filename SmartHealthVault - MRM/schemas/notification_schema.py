from models.notification_model import NotificationModel
from parsers.notification_parser import NotificationCreate, NotificationResponse
from datetime import datetime

class NotificationParser:
    @staticmethod
    def parse_create(notification: NotificationCreate) -> NotificationModel:
        return NotificationModel(
            user_id=notification.user_id,
            title=notification.title,
            message=notification.message,
            created_at=datetime.utcnow()
        )

    @staticmethod
    def to_json(notification: NotificationModel) -> NotificationResponse:
        return NotificationResponse.from_orm(notification)
