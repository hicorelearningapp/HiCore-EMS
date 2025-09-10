from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from models.telemedicine_model import AppointmentModel

class TelemedicineDatabase:
    def __init__(self, db: Session):
        self.db = db

    def execute_query(self, query: str, params: Any = None):
        return self.db.execute(query, params).fetchall()

    def insert(self, model: AppointmentModel) -> AppointmentModel:
        self.db.add(model); self.db.commit(); self.db.refresh(model); return model

    def get_by_id(self, id: str) -> Optional[AppointmentModel]:
        return self.db.query(AppointmentModel).filter(AppointmentModel.id == id).first()

    def list_all(self, filters: Dict = None) -> List[AppointmentModel]:
        q = self.db.query(AppointmentModel)
        if filters:
            if "doctor_id" in filters: q = q.filter(AppointmentModel.doctor_id == filters["doctor_id"])
            if "user_id" in filters: q = q.filter(AppointmentModel.user_id == filters["user_id"])
        return q.all()

    def update(self, id: str, updates: Dict) -> Optional[AppointmentModel]:
        a = self.get_by_id(id)
        if not a: return None
        for k, v in updates.items(): setattr(a, k, v)
        self.db.commit(); self.db.refresh(a); return a

    def delete(self, id: str) -> bool:
        a = self.get_by_id(id)
        if not a: return False
        self.db.delete(a); self.db.commit(); return True
