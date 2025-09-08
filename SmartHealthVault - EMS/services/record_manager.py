from database.db_manager import DatabaseManager
from database.enums import DBType
from parsers.record_parser import RecordParser
from schemas.record_schema import RecordCreate
from typing import List

class RecordManager:
    def __init__(self):
        self.db = DatabaseManager().get_database(DBType.RECORD_DB)

    def create_record(self, record_data: RecordCreate):
        record = RecordParser.parse_create(record_data)
        saved = self.db.add_record(record)
        return RecordParser.to_json(saved)

    def get_record(self, record_id: str):
        r = self.db.get_record(record_id)
        return RecordParser.to_json(r) if r else None

    def list_records(self) -> List:
        return [RecordParser.to_json(r) for r in self.db.list_records()]

    def update_record(self, record_id: str, updates: dict):
        r = self.db.update_record(record_id, updates)
        return RecordParser.to_json(r) if r else None

    def delete_record(self, record_id: str):
        return self.db.delete_record(record_id)
