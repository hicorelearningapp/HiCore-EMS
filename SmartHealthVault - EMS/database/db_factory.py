from database.enums import DBType
from database.concrete.user_db import UserDatabase
from database.concrete.doctor_db import DoctorDatabase
from database.concrete.record_db import RecordDatabase
from database.concrete.ai_ml_db import AIMLDatabase
from database.concrete.insurance_db import InsuranceDatabase
from database.concrete.notification_db import NotificationDatabase
from database.concrete.telemedicine_db import TelemedicineDatabase

class DatabaseFactory:
    @staticmethod
    def create_database(db_type: DBType):
        if db_type == DBType.USER_DB:
            return UserDatabase()
        if db_type == DBType.DOCTOR_DB:
            return DoctorDatabase()
        if db_type == DBType.RECORD_DB:
            return RecordDatabase()
        if db_type == DBType.AI_ML_DB:
            return AIMLDatabase()
        if db_type == DBType.INSURANCE_DB:
            return InsuranceDatabase()
        if db_type == DBType.NOTIFICATION_DB:
            return NotificationDatabase()
        if db_type == DBType.TELEMEDICINE_DB:
            return TelemedicineDatabase()
        raise ValueError(f"Unsupported DBType: {db_type}")
