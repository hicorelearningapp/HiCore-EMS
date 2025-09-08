from .enums import DBType
from .concrete.user_db import UserDatabase
from .concrete.doctor_db import DoctorDatabase
from .concrete.record_db import RecordDatabase
from .concrete.insurance_db import InsuranceDatabase
from .concrete.notification_db import NotificationDatabase
from .concrete.telemedicine_db import TelemedicineDatabase
from .concrete.ai_ml_db import AIMLDatabase

def create_database(db_type: DBType, db_session):
    if db_type == DBType.USER_DB:
        return UserDatabase(db_session)
    if db_type == DBType.DOCTOR_DB:
        return DoctorDatabase(db_session)
    if db_type == DBType.RECORD_DB:
        return RecordDatabase(db_session)
    if db_type == DBType.INSURANCE_DB:
        return InsuranceDatabase(db_session)
    if db_type == DBType.NOTIFICATION_DB:
        return NotificationDatabase(db_session)
    if db_type == DBType.TELEMEDICINE_DB:
        return TelemedicineDatabase(db_session)
    if db_type == DBType.AI_ML_DB:
        return AIMLDatabase(db_session)
    raise ValueError(f"Unknown DBType: {db_type}")
