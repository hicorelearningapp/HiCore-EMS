from database.db_manager import DatabaseManager
from database.enums import DBType
from parsers.record_parser import RecordParser
from schemas.record_schema import RecordCreate
from typing import List
from sqlalchemy.orm import Session

class RecordManager:
    def __init__(self, db_session: Session):
        self.db = DatabaseManager(db_session).get_database(DBType.RECORD_DB)

    def create_record(self, payload: RecordCreate):
        model = RecordParser.parse_create(payload)
        created = self.db.insert(model)
        return RecordParser.to_json(created)

    def get_record(self, record_id: str):
        r = self.db.get_by_id(record_id)
        return RecordParser.to_json(r) if r else None

    def list_records(self) -> List:
        return [RecordParser.to_json(r) for r in self.db.list_all()]

    def update_record(self, record_id: str, updates: dict):
        r = self.db.update(record_id, updates)
        return RecordParser.to_json(r) if r else None

    def delete_record(self, record_id: str):
        return self.db.delete(record_id)
