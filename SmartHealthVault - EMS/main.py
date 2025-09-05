from fastapi import FastAPI, Depends
from routers import (
    user_router,
    doctor_router,
    record_router,
    ai_ml_router,
    insurance_router,
    notification_router,
    telemedicine_router,
)
from database import get_db, InMemoryDB

app = FastAPI(title="SmartHealthVault - Backend (FastAPI)")

# Include routers
app.include_router(user_router.router, prefix="/users", tags=["Users"])
app.include_router(doctor_router.router, prefix="/doctors", tags=["Doctors"])
app.include_router(record_router.router, prefix="/records", tags=["Records"])
app.include_router(ai_ml_router.router, prefix="/ai", tags=["AI/ML"])
app.include_router(insurance_router.router, prefix="/insurance", tags=["Insurance"])
app.include_router(notification_router.router, prefix="/notifications", tags=["Notifications"])
app.include_router(telemedicine_router.router, prefix="/telemedicine", tags=["Telemedicine"])


@app.on_event("startup")
async def startup_event():
    # Initialize DB or connections here if needed (for now in-memory)
    db = InMemoryDB()
    get_db.override(lambda: db)


@app.get("/")
def root():
    return {"message": "SmartHealthVault API running"}
