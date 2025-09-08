from database.base import SessionLocal
from database.interfaces import IDatabase
from models.record_model import RecordModel
from sqlalchemy.orm import Session

class RecordDatabase(IDatabase):
    def __init__(self):
        self.session: Session = SessionLocal()

    def execute_query(self, query: str, params: dict = None):
        return self.session.execute(query, params)

    def add_record(self, record: RecordModel):
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def get_record(self, record_id: str):
        return self.session.query(RecordModel).filter(RecordModel.id == record_id).first()

    def list_records(self):
        return self.session.query(RecordModel).all()

    def update_record(self, record_id: str, updates: dict):
        record = self.get_record(record_id)
        if not record:
            return None
        for k, v in updates.items():
            setattr(record, k, v)
        self.session.commit()
        self.session.refresh(record)
        return record

    def delete_record(self, record_id: str):
        record = self.get_record(record_id)
        if not record:
            return None
        self.session.delete(record)
        self.session.commit()
        return True
