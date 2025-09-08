from typing import Generator
from .base import SessionLocal
from .db_factory import create_database
from .enums import DBType

def get_db_session() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DatabaseManager:
    def __init__(self, db_session):
        self.db_session = db_session

    def get_database(self, db_type: DBType):
        return create_database(db_type, self.db_session)
