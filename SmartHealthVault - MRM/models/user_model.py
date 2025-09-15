from sqlalchemy import Column, String, Integer, Date
from database.base import Base
import uuid

class UserModel(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    gender = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    dob = Column(Date, nullable=True)
    blood_group = Column(String, nullable=True)
    address = Column(String, nullable=True)
    role = Column(String, nullable=False, default="patient")
