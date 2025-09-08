from database.db_manager import DatabaseManager
from database.enums import DBType
from parsers.notification_parser import NotificationParser
from schemas.notification_schema import NotificationCreate
from typing import List
from sqlalchemy.orm import Session

class NotificationManager:
    def __init__(self, db_session: Session):
        self.db = DatabaseManager(db_session).get_database(DBType.NOTIFICATION_DB)

    def create_notification(self, payload: NotificationCreate):
        m = NotificationParser.parse_create(payload)
        created = self.db.insert(m)
        return NotificationParser.to_json(created)

    def get_notification(self, notification_id: str):
        n = self.db.get_by_id(notification_id)
        return NotificationParser.to_json(n) if n else None

    def list_notifications(self) -> List:
        return [NotificationParser.to_json(n) for n in self.db.list_all()]

    def mark_as_read(self, notification_id: str):
        updated = self.db.update(notification_id, {"read": True})
        return NotificationParser.to_json(updated) if updated else None

    def delete_notification(self, notification_id: str):
        return self.db.delete(notification_id)
