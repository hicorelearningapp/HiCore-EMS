from .user_router import router as user_router
from .doctor_router import router as doctor_router
from .record_router import router as record_router
from .ai_ml_router import router as ai_ml_router
from .insurance_router import router as insurance_router
from .notification_router import router as notification_router
from .telemedicine_router import router as telemedicine_router

__all__ = [
    'user_router',
    'doctor_router',
    'record_router',
    'ai_ml_router',
    'insurance_router',
    'notification_router',
    'telemedicine_router'
]