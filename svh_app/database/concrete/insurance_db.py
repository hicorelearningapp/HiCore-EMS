from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from models.insurance_model import PolicyModel, ClaimModel

class InsuranceDatabase:
    def __init__(self, db: Session):
        self.db = db

    def execute_query(self, query: str, params: Any = None):
        return self.db.execute(query, params).fetchall()

    def insert(self, model):
        self.db.add(model); self.db.commit(); self.db.refresh(model); return model

    def get_by_id(self, id: str):
        p = self.db.query(PolicyModel).filter(PolicyModel.id == id).first()
        if p: return p
        return self.db.query(ClaimModel).filter(ClaimModel.id == id).first()

    def list_all(self, filters: Dict = None):
        if filters and "patient_id" in filters:
            return self.db.query(PolicyModel).filter(PolicyModel.patient_id == filters["patient_id"]).all()
        return self.db.query(PolicyModel).all()

    def update(self, id: str, updates: Dict):
        p = self.db.query(PolicyModel).filter(PolicyModel.id == id).first()
        if not p: return None
        for k, v in updates.items(): setattr(p, k, v)
        self.db.commit(); self.db.refresh(p); return p

    def delete(self, id: str) -> bool:
        p = self.db.query(PolicyModel).filter(PolicyModel.id == id).first()
        if not p: return False
        self.db.delete(p); self.db.commit(); return True
