from database.db_manager import DatabaseManager
from database.enums import DBType
from parsers.doctor_parser import DoctorParser
from schemas.doctor_schema import DoctorCreate
from typing import List

class DoctorManager:
    def __init__(self):
        self.db = DatabaseManager().get_database(DBType.DOCTOR_DB)

    def create_doctor(self, doctor_data: DoctorCreate):
        doctor = DoctorParser.parse_create(doctor_data)
        saved = self.db.add_doctor(doctor)
        return DoctorParser.to_json(saved)

    def get_doctor(self, doctor_id: str):
        d = self.db.get_doctor(doctor_id)
        return DoctorParser.to_json(d) if d else None

    def list_doctors(self) -> List:
        return [DoctorParser.to_json(d) for d in self.db.list_doctors()]

    def update_doctor(self, doctor_id: str, updates: dict):
        d = self.db.update_doctor(doctor_id, updates)
        return DoctorParser.to_json(d) if d else None

    def delete_doctor(self, doctor_id: str):
        return self.db.delete_doctor(doctor_id)
