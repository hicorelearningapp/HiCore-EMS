from sqlalchemy import Column, String, DateTime
from database.base import Base
import uuid
from datetime import datetime

class RecordModel(Base):
    __tablename__ = "records"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    doctor_id = Column(String, nullable=True)
    category = Column(String, nullable=True)
    title = Column(String, nullable=True)
    content = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    extra_metadata = Column(String, nullable=True)  # ✅ renamed
    created_at = Column(DateTime, default=datetime.utcnow)
