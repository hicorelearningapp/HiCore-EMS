from models.record_model import RecordModel
from parsers.record_parser import RecordCreate, RecordResponse
from datetime import datetime
import json

class RecordParser:
    @staticmethod
    def parse_create(record: RecordCreate) -> RecordModel:
        return RecordModel(
            user_id=record.user_id,
            doctor_id=record.doctor_id,
            category=record.category,
            title=record.title,
            content=record.content,
            file_path=record.file_path,
            extra_metadata=json.dumps(record.metadata) if record.metadata else None,
            created_at=datetime.utcnow()
        )

    @staticmethod
    def to_json(record: RecordModel) -> RecordResponse:
        # Parse the extra_metadata from JSON string to dict if it exists
        metadata = {}
        if record.extra_metadata:
            try:
                metadata = json.loads(record.extra_metadata)
            except (json.JSONDecodeError, TypeError):
                metadata = {}

        return RecordResponse.model_validate({
            'id': str(record.id),
            'user_id': record.user_id,
            'doctor_id': record.doctor_id,
            'category': record.category,
            'title': record.title,
            'content': record.content,
            'file_path': record.file_path,
            'metadata': metadata,
            'created_at': record.created_at
        })
