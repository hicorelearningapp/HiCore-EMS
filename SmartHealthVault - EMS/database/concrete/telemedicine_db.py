from database.base import SessionLocal
from database.interfaces import IDatabase
from models.telemedicine_model import AppointmentModel
from sqlalchemy.orm import Session

class TelemedicineDatabase(IDatabase):
    def __init__(self):
        self.session: Session = SessionLocal()

    def execute_query(self, query: str, params: dict = None):
        return self.session.execute(query, params)

    def add_appointment(self, appointment: AppointmentModel):
        self.session.add(appointment)
        self.session.commit()
        self.session.refresh(appointment)
        return appointment

    def get_appointment(self, appointment_id: str):
        return self.session.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()

    def list_appointments(self):
        return self.session.query(AppointmentModel).all()

    def update_appointment(self, appointment_id: str, updates: dict):
        appointment = self.get_appointment(appointment_id)
        if not appointment:
            return None
        for k, v in updates.items():
            setattr(appointment, k, v)
        self.session.commit()
        self.session.refresh(appointment)
        return appointment

    def delete_appointment(self, appointment_id: str):
        appointment = self.get_appointment(appointment_id)
        if not appointment:
            return None
        self.session.delete(appointment)
        self.session.commit()
        return True
