from database.db_manager import DatabaseManager
from database.enums import DBType
from parsers.telemedicine_parser import TelemedicineParser
from schemas.telemedicine_schema import AppointmentCreate
from typing import List
from sqlalchemy.orm import Session

class TelemedicineManager:
    def __init__(self, db_session: Session):
        self.db = DatabaseManager(db_session).get_database(DBType.TELEMEDICINE_DB)

    def schedule(self, payload: AppointmentCreate):
        model = TelemedicineParser.parse_create(payload)
        created = self.db.insert(model)
        return TelemedicineParser.to_json(created)

    def get_appointment(self, appointment_id: str):
        r = self.db.get_by_id(appointment_id)
        return TelemedicineParser.to_json(r) if r else None

    def list_appointments(self) -> List:
        return [TelemedicineParser.to_json(r) for r in self.db.list_all()]

    def update_appointment(self, appointment_id: str, updates: dict):
        r = self.db.update(appointment_id, updates)
        return TelemedicineParser.to_json(r) if r else None

    def cancel(self, appointment_id: str):
        return self.db.delete(appointment_id)
