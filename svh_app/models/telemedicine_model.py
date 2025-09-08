from sqlalchemy import Column, String, DateTime
from database.base import Base
import uuid
from datetime import datetime

class AppointmentModel(Base):
    __tablename__ = "appointments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    doctor_id = Column(String, nullable=False)
    appointment_time = Column(String, nullable=False)  # ✅ renamed
    mode = Column(String, default="video")
    status = Column(String, default="scheduled")
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)  # ✅ works now
