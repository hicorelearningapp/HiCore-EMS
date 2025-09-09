"""
SmartHealthVault - Consolidated Application
This file combines all functionality from the SmartHealthVault project into a single file.
"""

import os
import uuid
import shutil
import tempfile
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

# Dependencies
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import sessionmaker, relationship, Session, declarative_base
from sqlalchemy.sql import func
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional
import json

# ==============================================
# Database Configuration
# ==============================================
DATABASE_URL = "sqlite:///./svh.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==============================================
# Security Configuration
# ==============================================
SECRET_KEY = "your-secret-key-here"  # In production, use environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ==============================================
# Models
# ==============================================
class UserModel(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    gender = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    dob = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_doctor = Column(Boolean, default=False)

    # Relationships
    records = relationship("RecordModel", back_populates="user")
    notifications = relationship("NotificationModel", back_populates="user")
    insurance_policies = relationship("InsuranceModel", back_populates="user")
    telemedicine_sessions = relationship("TelemedicineModel", back_populates="user")

class DoctorModel(UserModel):
    __tablename__ = "doctors"
    id = Column(String, ForeignKey('users.id'), primary_key=True)
    specialization = Column(String, nullable=False)
    license_number = Column(String, unique=True, nullable=False)
    hospital_affiliation = Column(String, nullable=True)
    consultation_fee = Column(Float, default=0.0)
    rating = Column(Float, default=0.0)
    experience_years = Column(Integer, default=0)
    
    # Relationships
    telemedicine_sessions = relationship("TelemedicineModel", back_populates="doctor")
    appointments = relationship("AppointmentModel", back_populates="doctor")

class RecordModel(Base):
    __tablename__ = "records"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    record_type = Column(String, nullable=False)  # e.g., 'prescription', 'lab_result', 'scan'
    file_path = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("UserModel", back_populates="records")
    analysis_results = relationship("AIMLResultModel", back_popuments="record")

class AIMLResultModel(Base):
    __tablename__ = "ai_ml_results"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    record_id = Column(String, ForeignKey('records.id'), nullable=False)
    model_used = Column(String, nullable=False)
    result_data = Column(Text, nullable=False)  # JSON string of results
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    record = relationship("RecordModel", back_populates="analysis_results")

class InsuranceModel(Base):
    __tablename__ = "insurance_policies"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    provider_name = Column(String, nullable=False)
    policy_number = Column(String, nullable=False, unique=True)
    coverage_details = Column(Text, nullable=True)  # JSON string
    expiry_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("UserModel", back_populates="insurance_policies")

class NotificationModel(Base):
    __tablename__ = "notifications"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    notification_type = Column(String, nullable=True)  # e.g., 'appointment', 'reminder', 'alert'
    
    # Relationships
    user = relationship("UserModel", back_populates="notifications")

class TelemedicineModel(Base):
    __tablename__ = "telemedicine_sessions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    doctor_id = Column(String, ForeignKey('doctors.id'), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    status = Column(String, default="scheduled")  # scheduled, in-progress, completed, cancelled
    notes = Column(Text, nullable=True)
    meeting_link = Column(String, nullable=True)
    
    # Relationships
    user = relationship("UserModel", back_populates="telemedicine_sessions")
    doctor = relationship("DoctorModel", back_populates="telemedicine_sessions")

class AppointmentModel(Base):
    __tablename__ = "appointments"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    doctor_id = Column(String, ForeignKey('doctors.id'), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    status = Column(String, default="scheduled")  # scheduled, completed, cancelled, no-show
    reason = Column(Text, nullable=True)
    diagnosis = Column(Text, nullable=True)
    prescription = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("UserModel")
    doctor = relationship("DoctorModel", back_populates="appointments")

# Create all tables
Base.metadata.create_all(bind=engine)

# ==============================================
# Pydantic Models (Schemas)
# ==============================================
class UserBase(BaseModel):
    email: EmailStr
    name: str
    
class UserCreate(UserBase):
    password: str
    
class User(UserBase):
    id: str
    is_active: bool
    is_doctor: bool = False
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class RecordBase(BaseModel):
    title: str
    record_type: str
    notes: Optional[str] = None

class RecordCreate(RecordBase):
    pass

class Record(RecordBase):
    id: str
    user_id: str
    file_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class AIMLResultBase(BaseModel):
    model_used: str
    result_data: str
    confidence: Optional[float] = None

class AIMLResultCreate(AIMLResultBase):
    record_id: str

class AIMLResult(AIMLResultBase):
    id: str
    created_at: datetime
    
    class Config:
        orm_mode = True

# ==============================================
# Authentication & Security
# =============================================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_user(db: Session, email: str):
    return db.query(UserModel).filter(UserModel.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user(db, email)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[datetime] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

# ==============================================
# File Handling
# ==============================================
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_upload_file(upload_file: UploadFile, destination: str) -> str:
    try:
        file_path = os.path.join(UPLOAD_DIR, destination)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()
    return file_path

# ==============================================
# FastAPI Application
# ==============================================
app = FastAPI(title="SmartHealthVault - Consolidated API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# ==============================================
# API Endpoints
# ==============================================
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        email=user.email,
        name=user.name,
        password_hash=hashed_password,
        is_doctor=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return current_user

@app.post("/records/", response_model=Record)
def create_record(
    record: RecordCreate,
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    file_path = None
    if file:
        file_extension = os.path.splitext(file.filename)[1]
        file_path = save_upload_file(file, f"records/{current_user.id}/{str(uuid.uuid4())}{file_extension}")
    
    db_record = RecordModel(
        user_id=current_user.id,
        title=record.title,
        record_type=record.record_type,
        notes=record.notes,
        file_path=file_path
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@app.get("/records/", response_model=List[Record])
def read_records(
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    records = db.query(RecordModel).filter(RecordModel.user_id == current_user.id).offset(skip).limit(limit).all()
    return records

@app.post("/ai/analyze/{record_id}", response_model=AIMLResult)
def analyze_record(
    record_id: str,
    model_name: str = "default",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # In a real app, this would call your AI/ML model
    # For now, we'll return a mock result
    record = db.query(RecordModel).filter(
        RecordModel.id == record_id,
        RecordModel.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    # Mock analysis result
    result_data = {
        "analysis": "This is a mock analysis result.",
        "findings": ["Finding 1", "Finding 2"],
        "confidence": 0.95,
        "recommendations": ["Recommendation 1", "Recommendation 2"]
    }
    
    db_result = AIMLResultModel(
        record_id=record_id,
        model_used=model_name,
        result_data=json.dumps(result_data),
        confidence=0.95
    )
    
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    
    return db_result

# ==============================================
# Main Entry Point
# ==============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
