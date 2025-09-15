from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database.base import Base, engine
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Verify OpenAI API key is set
if not os.getenv("OPENAI_API_KEY"):
    print("WARNING: OPENAI_API_KEY environment variable is not set")

# Import routers
from routers.user_router import router as user_router
from routers.doctor_router import router as doctor_router
from routers.record_router import router as record_router
from routers.ai_ml_router import router as ai_ml_router
from routers.insurance_router import router as insurance_router
from routers.notification_router import router as notification_router
from routers.telemedicine_router import router as telemedicine_router
from routers.pdf_router import router as pdf_router  # PDF analysis router

app = FastAPI(title="SmartHealthVault - Backend (FastAPI)")

# Include all routers
app.include_router(user_router)
app.include_router(doctor_router)
app.include_router(record_router)
app.include_router(ai_ml_router)
app.include_router(insurance_router)
app.include_router(notification_router)
app.include_router(telemedicine_router)
app.include_router(pdf_router)  # Add PDF router

# Serve static files for uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.on_event("startup")
def on_startup():
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Create necessary directories if they don't exist
    os.makedirs("uploads/raw", exist_ok=True)
    os.makedirs("uploads/processed", exist_ok=True)

@app.get("/")
def root():
    return {"message": "SmartHealthVault API running"}
