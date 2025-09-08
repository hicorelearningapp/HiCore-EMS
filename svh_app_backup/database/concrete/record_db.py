from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from models.record_model import RecordModel

class RecordDatabase:
    def __init__(self, db: Session):
        self.db = db

    def execute_query(self, query: str, params: Any = None):
        return self.db.execute(query, params).fetchall()

    def insert(self, model: RecordModel) -> RecordModel:
        self.db.add(model); self.db.commit(); self.db.refresh(model); return model

    def get_by_id(self, id: str) -> Optional[RecordModel]:
        return self.db.query(RecordModel).filter(RecordModel.id == id).first()

    def list_all(self, filters: Dict = None) -> List[RecordModel]:
        q = self.db.query(RecordModel)
        if filters:
            if "user_id" in filters: q = q.filter(RecordModel.user_id == filters["user_id"])
        return q.all()

    def update(self, id: str, updates: Dict) -> Optional[RecordModel]:
        r = self.get_by_id(id)
        if not r: return None
        for k, v in updates.items(): setattr(r, k, v)
        self.db.commit(); self.db.refresh(r); return r

    def delete(self, id: str) -> bool:
        r = self.get_by_id(id)
        if not r: return False
        self.db.delete(r); self.db.commit(); return True
