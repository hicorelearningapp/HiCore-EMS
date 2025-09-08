from database.db_manager import DatabaseManager
from database.enums import DBType
from parsers.notification_parser import NotificationParser
from schemas.notification_schema import NotificationCreate
from typing import List

class NotificationManager:
    def __init__(self):
        self.db = DatabaseManager().get_database(DBType.NOTIFICATION_DB)

    def create_notification(self, notification_data: NotificationCreate):
        notification = NotificationParser.parse_create(notification_data)
        saved = self.db.add_notification(notification)
        return NotificationParser.to_json(saved)

    def get_notification(self, notification_id: str):
        n = self.db.get_notification(notification_id)
        return NotificationParser.to_json(n) if n else None

    def list_notifications(self) -> List:
        return [NotificationParser.to_json(n) for n in self.db.list_notifications()]

    def mark_as_read(self, notification_id: str):
        n = self.db.mark_as_read(notification_id)
        return NotificationParser.to_json(n) if n else None

    def delete_notification(self, notification_id: str):
        return self.db.delete_notification(notification_id)
