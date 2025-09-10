"""
CONSOLIDATED SMARTHEALTHVAULT APPLICATION
File: consolidated_app.py
This is a single-file version of the SmartHealthVault application that combines all components.
"""

# =============================================
# 1. IMPORTS AND CONFIGURATION
# =============================================
import os
import uuid
import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

# FastAPI and related imports
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# SQLAlchemy and database
from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey, Text, Boolean, Float, Enum as SQLAlchemyEnum
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from sqlalchemy.ext.declarative import DeclarativeMeta

# Pydantic models
from pydantic import BaseModel, EmailStr, validator, Field

# Security
from passlib.context import CryptContext
from jose import JWTError, jwt

# File processing
import shutil
from pathlib import Path
from typing import Optional

# =============================================
# 2. DATABASE CONFIGURATION
# =============================================
DATABASE_URL = "sqlite:///./svh.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base: DeclarativeMeta = declarative_base()

# =============================================
# 3. SECURITY CONFIGURATION
# =============================================
SECRET_KEY = "your-secret-key-here"  # In production, use environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# =============================================
# 4. MODELS
# =============================================
class UserRole(str, Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"

class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(SQLAlchemyEnum(UserRole), default=UserRole.PATIENT)
    gender = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    dob = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    records = relationship("MedicalRecordModel", back_populates="patient")
    doctor_appointments = relationship("AppointmentModel", foreign_keys="AppointmentModel.doctor_id", back_populates="doctor")
    patient_appointments = relationship("AppointmentModel", foreign_keys="AppointmentModel.patient_id", back_populates="patient")

class MedicalRecordModel(Base):
    __tablename__ = "medical_records"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("users.id"), nullable=False)
    record_type = Column(String, nullable=False)  # e.g., 'prescription', 'lab_result', 'diagnosis'
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    patient = relationship("UserModel", back_populates="records")

class AppointmentModel(Base):
    __tablename__ = "appointments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    doctor_id = Column(String, ForeignKey("users.id"), nullable=False)
    patient_id = Column(String, ForeignKey("users.id"), nullable=False)
    appointment_time = Column(DateTime, nullable=False)
    status = Column(String, default="scheduled")  # scheduled, completed, cancelled
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    doctor = relationship("UserModel", foreign_keys=[doctor_id], back_populates="doctor_appointments")
    patient = relationship("UserModel", foreign_keys=[patient_id], back_populates="patient_appointments")

# Create all tables
Base.metadata.create_all(bind=engine)

# =============================================
# 5. SCHEMAS (Pydantic Models)
# =============================================
class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: UserRole = UserRole.PATIENT
    
class UserCreate(UserBase):
    password: str
    gender: Optional[str] = None
    age: Optional[int] = None
    dob: Optional[datetime.date] = None

class UserResponse(UserBase):
    id: str
    created_at: datetime.datetime
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class MedicalRecordBase(BaseModel):
    record_type: str
    title: str
    description: Optional[str] = None

class MedicalRecordCreate(MedicalRecordBase):
    pass

class MedicalRecordResponse(MedicalRecordBase):
    id: str
    patient_id: str
    created_at: datetime.datetime
    
    class Config:
        orm_mode = True

class AppointmentBase(BaseModel):
    doctor_id: str
    patient_id: str
    appointment_time: datetime.datetime
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentResponse(AppointmentBase):
    id: str
    status: str
    created_at: datetime.datetime
    
    class Config:
        orm_mode = True

# =============================================
# 6. AUTHENTICATION UTILITIES
# =========================================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
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
    
    user = db.query(UserModel).filter(UserModel.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

# =============================================
# 7. DATABASE UTILITIES
# =========================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =============================================
# 8. FASTAPI APPLICATION
# =========================================
app = FastAPI(title="SmartHealthVault API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directories
os.makedirs("uploads/raw", exist_ok=True)
os.makedirs("uploads/processed", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# =============================================
# 9. AUTH ROUTES
# =========================================
@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        email=user.email,
        name=user.name,
        password_hash=hashed_password,
        role=user.role,
        gender=user.gender,
        age=user.age,
        dob=user.dob
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# =============================================
# 10. USER ROUTES
# =========================================
@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    return current_user

@app.put("/users/me", response_model=UserResponse)
async def update_user_me(
    name: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    age: Optional[int] = Form(None),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if name is not None:
        current_user.name = name
    if gender is not None:
        current_user.gender = gender
    if age is not None:
        current_user.age = age
    
    db.commit()
    db.refresh(current_user)
    return current_user

# =============================================
# 11. MEDICAL RECORDS ROUTES
# =========================================
@app.post("/records/", response_model=MedicalRecordResponse)
def create_medical_record(
    record_type: str = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    file_path = None
    if file:
        # Save the file
        file_extension = os.path.splitext(file.filename)[1]
        file_name = f"{uuid.uuid4()}{file_extension}"
        file_path = f"uploads/raw/{file_name}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    
    # Create record in database
    db_record = MedicalRecordModel(
        patient_id=current_user.id,
        record_type=record_type,
        title=title,
        description=description,
        file_path=file_path
    )
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@app.get("/records/me", response_model=List[MedicalRecordResponse])
def get_my_medical_records(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(MedicalRecordModel).filter(MedicalRecordModel.patient_id == current_user.id).all()

# =============================================
# 12. APPOINTMENT ROUTES
# =========================================
@app.post("/appointments/", response_model=AppointmentResponse)
def create_appointment(
    doctor_id: str = Form(...),
    appointment_time: datetime.datetime = Form(...),
    notes: Optional[str] = Form(None),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if doctor exists
    doctor = db.query(UserModel).filter(UserModel.id == doctor_id, UserModel.role == UserRole.DOCTOR).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Create appointment
    db_appointment = AppointmentModel(
        doctor_id=doctor_id,
        patient_id=current_user.id,
        appointment_time=appointment_time,
        notes=notes
    )
    
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@app.get("/appointments/me", response_model=List[AppointmentResponse])
def get_my_appointments(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == UserRole.DOCTOR:
        return db.query(AppointmentModel).filter(AppointmentModel.doctor_id == current_user.id).all()
    else:
        return db.query(AppointmentModel).filter(AppointmentModel.patient_id == current_user.id).all()

# =============================================
# 13. HEALTH CHECK
# =========================================
@app.get("/")
def read_root():
    return {"message": "SmartHealthVault API is running"}

# =============================================
# 14. MAIN ENTRY POINT
# =========================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
