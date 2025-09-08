import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum

# Dependencies
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from passlib.context import CryptContext
from jose import JWTError, jwt

# ===== Configuration =====
DATABASE_URL = "sqlite:///./smarthealthvault.db"
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ===== Database Setup =====
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ===== Password Hashing =====
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ===== Models =====
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_doctor = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def verify_password(self, password: str):
        return pwd_context.verify(password, self.hashed_password)

class MedicalRecord(Base):
    __tablename__ = "medical_records"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    record_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User")

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(String, ForeignKey("users.id"), nullable=False)
    appointment_time = Column(DateTime, nullable=False)
    status = Column(String, default="scheduled")  # scheduled, completed, cancelled
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    patient = relationship("User", foreign_keys=[patient_id])
    doctor = relationship("User", foreign_keys=[doctor_id])

# Create all tables
Base.metadata.create_all(bind=engine)

# ===== Pydantic Models =====
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: str
    is_active: bool
    is_doctor: bool
    created_at: datetime

    class Config:
        orm_mode = True

class MedicalRecordBase(BaseModel):
    title: str
    description: Optional[str] = None
    record_type: Optional[str] = None

class MedicalRecordCreate(MedicalRecordBase):
    pass

class MedicalRecord(MedicalRecordBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class AppointmentBase(BaseModel):
    doctor_id: str
    appointment_time: datetime
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    id: str
    patient_id: str
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

# ===== Authentication Functions =====
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_user(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(SessionLocal)):
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

# ===== Database Dependency =====
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===== FastAPI App =====
app = FastAPI(title="SmartHealthVault API", version="1.0.0")

# ===== API Endpoints =====
@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
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

@app.post("/users/", response_model=UserInDB)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_doctor=user.is_doctor if hasattr(user, 'is_doctor') else False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/me/", response_model=UserInDB)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/records/", response_model=MedicalRecord)
def create_record(
    record: MedicalRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_record = MedicalRecord(**record.dict(), user_id=current_user.id)
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@app.get("/records/", response_model=List[MedicalRecord])
def read_records(
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    records = db.query(MedicalRecord).filter(MedicalRecord.user_id == current_user.id).offset(skip).limit(limit).all()
    return records

@app.post("/appointments/", response_model=Appointment)
def create_appointment(
    appointment: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if doctor exists and is actually a doctor
    doctor = db.query(User).filter(
        User.id == appointment.doctor_id,
        User.is_doctor == True
    ).first()
    
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    db_appointment = Appointment(
        **appointment.dict(),
        patient_id=current_user.id,
        status="scheduled"
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@app.get("/appointments/", response_model=List[Appointment])
def read_appointments(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.is_doctor:
        # Doctors can see all their appointments
        appointments = db.query(Appointment).filter(
            Appointment.doctor_id == current_user.id
        ).offset(skip).limit(limit).all()
    else:
        # Patients can only see their own appointments
        appointments = db.query(Appointment).filter(
            Appointment.patient_id == current_user.id
        ).offset(skip).limit(limit).all()
    
    return appointments

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to SmartHealthVault API"}

# Run with: uvicorn smarthealthvault_mono:app --reload
