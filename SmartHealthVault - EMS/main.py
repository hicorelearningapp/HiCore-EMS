from fastapi import FastAPI
from database.base import Base, engine
from routers import (
    user_router,
    doctor_router,
    record_router,
    ai_ml_router,
    insurance_router,
    notification_router,
    telemedicine_router
)

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SmartHealthVault API")

# Routers
app.include_router(user_router.router, prefix="/users", tags=["Users"])
app.include_router(doctor_router.router, prefix="/doctors", tags=["Doctors"])
app.include_router(record_router.router, prefix="/records", tags=["Records"])
app.include_router(ai_ml_router.router, prefix="/ai-ml", tags=["AI/ML"])
app.include_router(insurance_router.router, prefix="/insurance", tags=["Insurance"])
app.include_router(notification_router.router, prefix="/notifications", tags=["Notifications"])
app.include_router(telemedicine_router.router, prefix="/appointments", tags=["Telemedicine"])

@app.get("/")
def root():
    return {"message": "SmartHealthVault API is running 🚀"}
