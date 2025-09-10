from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from models.notification_model import NotificationModel

class NotificationDatabase:
    def __init__(self, db: Session):
        self.db = db

    def execute_query(self, query: str, params: Any = None):
        return self.db.execute(query, params).fetchall()

    def insert(self, model: NotificationModel) -> NotificationModel:
        self.db.add(model); self.db.commit(); self.db.refresh(model); return model

    def get_by_id(self, id: str) -> Optional[NotificationModel]:
        return self.db.query(NotificationModel).filter(NotificationModel.id == id).first()

    def list_all(self, filters: Dict = None) -> List[NotificationModel]:
        q = self.db.query(NotificationModel)
        if filters and "user_id" in filters: q = q.filter(NotificationModel.user_id == filters["user_id"])
        return q.all()

    def update(self, id: str, updates: Dict) -> Optional[NotificationModel]:
        n = self.get_by_id(id)
        if not n: return None
        for k, v in updates.items(): setattr(n, k, v)
        self.db.commit(); self.db.refresh(n); return n

    def delete(self, id: str) -> bool:
        n = self.get_by_id(id)
        if not n: return False
        self.db.delete(n); self.db.commit(); return True
