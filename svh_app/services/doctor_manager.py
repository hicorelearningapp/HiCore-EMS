from database.db_manager import DatabaseManager
from database.enums import DBType
from schemas.doctor_schema import DoctorParser
from parsers.doctor_parser import DoctorCreate
from typing import List
from sqlalchemy.orm import Session

class DoctorManager:
    def __init__(self, db_session: Session):
        self.db = DatabaseManager(db_session).get_database(DBType.DOCTOR_DB)

    def create_doctor(self, payload: DoctorCreate):
        model = DoctorParser.parse_create(payload)
        created = self.db.insert(model)
        return DoctorParser.to_json(created)

    def get_doctor(self, doctor_id: str):
        m = self.db.get_by_id(doctor_id)
        return DoctorParser.to_json(m) if m else None

    def list_doctors(self, specialization: str = None):
        filters = {"specialization": specialization} if specialization else None
        rows = self.db.list_all(filters)
        return [DoctorParser.to_json(r) for r in rows]
