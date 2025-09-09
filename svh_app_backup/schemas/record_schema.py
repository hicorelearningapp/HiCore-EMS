from models.record_model import RecordModel
from parsers.record_parser import RecordCreate, RecordResponse
from datetime import datetime

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
            metadata=record.metadata,
            created_at=datetime.utcnow()
        )

    @staticmethod
    def to_json(record: RecordModel) -> RecordResponse:
        return RecordResponse.from_orm(record)
