from sqlalchemy import Column, String
from database.base import Base
import uuid

class DoctorModel(Base):
    __tablename__ = "doctors"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    specialization = Column(String, nullable=True)
    qualifications = Column(String, nullable=True)
    languages = Column(String, nullable=True)
    clinic_address = Column(String, nullable=True)
