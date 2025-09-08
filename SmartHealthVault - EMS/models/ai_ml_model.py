from sqlalchemy import Column, String, DateTime
from database.base import Base
import uuid
from datetime import datetime

class AIResultModel(Base):
    __tablename__ = "ai_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    result = Column(String, nullable=True)
    explanation = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
