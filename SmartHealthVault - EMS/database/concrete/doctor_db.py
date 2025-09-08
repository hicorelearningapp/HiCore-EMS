from database.base import SessionLocal
from database.interfaces import IDatabase
from models.doctor_model import DoctorModel
from sqlalchemy.orm import Session

class DoctorDatabase(IDatabase):
    def __init__(self):
        self.session: Session = SessionLocal()

    def execute_query(self, query: str, params: dict = None):
        return self.session.execute(query, params)

    def add_doctor(self, doctor: DoctorModel):
        self.session.add(doctor)
        self.session.commit()
        self.session.refresh(doctor)
        return doctor

    def get_doctor(self, doctor_id: str):
        return self.session.query(DoctorModel).filter(DoctorModel.id == doctor_id).first()

    def list_doctors(self):
        return self.session.query(DoctorModel).all()

    def update_doctor(self, doctor_id: str, updates: dict):
        doctor = self.get_doctor(doctor_id)
        if not doctor:
            return None
        for k, v in updates.items():
            setattr(doctor, k, v)
        self.session.commit()
        self.session.refresh(doctor)
        return doctor

    def delete_doctor(self, doctor_id: str):
        doctor = self.get_doctor(doctor_id)
        if not doctor:
            return None
        self.session.delete(doctor)
        self.session.commit()
        return True
