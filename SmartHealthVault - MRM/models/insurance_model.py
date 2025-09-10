from sqlalchemy import Column, String, Integer, Float, DateTime
from database.base import Base
import uuid
from datetime import datetime

class PolicyModel(Base):
    __tablename__ = "policies"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    sum_insured = Column(Integer, nullable=False)
    premium = Column(Float, nullable=False)
    details = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ClaimModel(Base):
    __tablename__ = "claims"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    policy_id = Column(String, nullable=False)
    patient_id = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    reason = Column(String, nullable=True)
    status = Column(String, default="submitted")
    created_at = Column(DateTime, default=datetime.utcnow)
