from typing import Dict, List
from models.record_model import Record
import uuid

class RecordService:
    def __init__(self, store: Dict[str, Record]):
        self.store = store

    def create_record(self, record: Record) -> Record:
        rid = record.id or str(uuid.uuid4())
        record.id = rid
        self.store[rid] = record
        return record

    def get_record(self, record_id: str):
        return self.store.get(record_id)

    def list_records_for_user(self, user_id: str) -> List[Record]:
        return [r for r in self.store.values() if r.user_id == user_id]

    def update_record(self, record_id: str, patch: Dict):
        rec = self.store.get(record_id)
        if not rec:
            return None
        updated = rec.copy(update=patch)
        self.store[record_id] = updated
        return updated

    def delete_record(self, record_id: str):
        return self.store.pop(record_id, None)
