from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from models.doctor_model import DoctorModel

class DoctorDatabase:
    def __init__(self, db: Session):
        self.db = db

    def execute_query(self, query: str, params: Any = None):
        return self.db.execute(query, params).fetchall()

    def insert(self, model: DoctorModel) -> DoctorModel:
        self.db.add(model); self.db.commit(); self.db.refresh(model); return model

    def get_by_id(self, id: str) -> Optional[DoctorModel]:
        return self.db.query(DoctorModel).filter(DoctorModel.id == id).first()

    def list_all(self, filters: Dict = None) -> List[DoctorModel]:
        q = self.db.query(DoctorModel)
        if filters and "specialization" in filters:
            q = q.filter(DoctorModel.specialization == filters["specialization"])
        return q.all()

    def update(self, id: str, updates: Dict) -> Optional[DoctorModel]:
        d = self.get_by_id(id)
        if not d: return None
        for k, v in updates.items(): setattr(d, k, v)
        self.db.commit(); self.db.refresh(d); return d

    def delete(self, id: str) -> bool:
        d = self.get_by_id(id)
        if not d: return False
        self.db.delete(d); self.db.commit(); return True
