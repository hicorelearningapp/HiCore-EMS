from database.db_manager import DatabaseManager
from database.enums import DBType
from schemas.record_schema import RecordParser
from parsers.record_parser import RecordCreate
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

    def get_records_by_patient(self, patient_id: str) -> List[dict]:
        """
        Get all records for a specific patient
        
        Args:
            patient_id: ID of the patient whose records to retrieve
            
        Returns:
            List of record objects for the specified patient
        """
        # Get all records and filter by patient_id
        all_records = self.db.list_all()
        patient_records = [r for r in all_records if str(r.user_id) == str(patient_id)]
        return [RecordParser.to_json(record) for record in patient_records]
