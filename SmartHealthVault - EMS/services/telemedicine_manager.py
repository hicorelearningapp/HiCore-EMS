from database.db_manager import DatabaseManager
from database.enums import DBType
from parsers.telemedicine_parser import TelemedicineParser
from schemas.telemedicine_schema import AppointmentCreate
from typing import List

class TelemedicineManager:
    def __init__(self):
        self.db = DatabaseManager().get_database(DBType.TELEMEDICINE_DB)

    def create_appointment(self, appointment_data: AppointmentCreate):
        appointment = TelemedicineParser.parse_create(appointment_data)
        saved = self.db.add_appointment(appointment)
        return TelemedicineParser.to_json(saved)

    def get_appointment(self, appointment_id: str):
        a = self.db.get_appointment(appointment_id)
        return TelemedicineParser.to_json(a) if a else None

    def list_appointments(self) -> List:
        return [TelemedicineParser.to_json(a) for a in self.db.list_appointments()]

    def update_appointment(self, appointment_id: str, updates: dict):
        a = self.db.update_appointment(appointment_id, updates)
        return TelemedicineParser.to_json(a) if a else None

    def delete_appointment(self, appointment_id: str):
        return self.db.delete_appointment(appointment_id)
