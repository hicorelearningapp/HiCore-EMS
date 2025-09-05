from typing import Dict
from models.doctor_model import Doctor
import uuid

class DoctorService:
    def __init__(self, store: Dict[str, Doctor]):
        self.store = store

    def create_doctor(self, doctor: Doctor) -> Doctor:
        did = doctor.id or str(uuid.uuid4())
        doctor.id = did
        self.store[did] = doctor
        return doctor

    def get_doctor(self, doctor_id: str):
        return self.store.get(doctor_id)

    def list_doctors(self):
        return list(self.store.values())

    def update_doctor(self, doctor_id: str, patch: Dict):
        doc = self.store.get(doctor_id)
        if not doc:
            return None
        updated = doc.copy(update=patch)
        self.store[doctor_id] = updated
        return updated

    def delete_doctor(self, doctor_id: str):
        return self.store.pop(doctor_id, None)
