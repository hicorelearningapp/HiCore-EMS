from fastapi import FastAPI
from database.base import Base, engine
from routers import user_router, doctor_router, record_router, ai_ml_router, insurance_router, notification_router, telemedicine_router

app = FastAPI(title="SmartHealthVault - Backend (FastAPI)")

app.include_router(user_router.router)
app.include_router(doctor_router.router)
app.include_router(record_router.router)
app.include_router(ai_ml_router.router)
app.include_router(insurance_router.router)
app.include_router(notification_router.router)
app.include_router(telemedicine_router.router)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "SmartHealthVault API running"}
