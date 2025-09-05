from typing import Dict
from models.telemedicine_model import Appointment
import uuid

class TelemedicineService:
    def __init__(self, store: Dict[str, Appointment]):
        self.store = store

    def schedule(self, appointment: Appointment):
        aid = appointment.id or str(uuid.uuid4())
        appointment.id = aid
        self.store[aid] = appointment
        return appointment

    def get_appointment(self, appointment_id: str):
        return self.store.get(appointment_id)

    def list_for_user(self, user_id: str):
        return [a for a in self.store.values() if a.user_id == user_id]

    def cancel(self, appointment_id: str):
        a = self.store.get(appointment_id)
        if a:
            a.status = "canceled"
            self.store[appointment_id] = a
        return a
