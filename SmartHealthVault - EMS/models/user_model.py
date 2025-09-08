# models/user_model.py
from sqlalchemy import Column, String, Integer, DateTime
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
    dob = Column(DateTime, nullable=True)
