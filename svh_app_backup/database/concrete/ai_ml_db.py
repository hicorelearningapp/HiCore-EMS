from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from models.ai_ml_model import AIResultModel

class AIMLDatabase:
    def __init__(self, db: Session):
        self.db = db

    def execute_query(self, query: str, params: Any = None):
        return self.db.execute(query, params).fetchall()

    def insert(self, model: AIResultModel) -> AIResultModel:
        self.db.add(model); self.db.commit(); self.db.refresh(model); return model

    def get_by_id(self, id: str) -> Optional[AIResultModel]:
        return self.db.query(AIResultModel).filter(AIResultModel.id == id).first()

    def list_all(self, filters: Dict = None) -> List[AIResultModel]:
        return self.db.query(AIResultModel).all()

    def update(self, id: str, updates: Dict) -> Optional[AIResultModel]:
        m = self.get_by_id(id)
        if not m: return None
        for k, v in updates.items(): setattr(m, k, v)
        self.db.commit(); self.db.refresh(m); return m

    def delete(self, id: str) -> bool:
        m = self.get_by_id(id)
        if not m: return False
        self.db.delete(m); self.db.commit(); return True
