from sqlalchemy import Column, String, DateTime
from database.base import Base
import uuid
from datetime import datetime

class InsuranceModel(Base):
    __tablename__ = "insurance_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    provider = Column(String, nullable=False)         # Insurance provider name
    policy_number = Column(String, nullable=False)    # Policy ID
    coverage_details = Column(String, nullable=True)  # Coverage information
    valid_till = Column(String, nullable=True)        # Expiry date (as string for flexibility)
    created_at = Column(DateTime, default=datetime.utcnow)
