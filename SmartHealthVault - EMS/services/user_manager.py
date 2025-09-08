# services/user_manager.py
from database.db_manager import DatabaseManager
from database.enums import DBType
from parsers.user_parser import UserParser
from schemas.user_schema import UserCreate
from typing import List, Optional
from sqlalchemy.orm import Session

class UserManager:
    def __init__(self, db_session: Session):
        self.db_manager = DatabaseManager(db_session)
        self.db = self.db_manager.get_database(DBType.USER_DB)

    def create_user(self, payload: UserCreate):
        # check uniqueness
        existing = self.db.get_by_id(payload.email) if False else None
        # Note: user_db has get_by_email, so call directly on adapter if present
        try:
            # if concrete adapter has get_by_email
            if hasattr(self.db, "get_by_email"):
                if self.db.get_by_email(payload.email):
                    raise ValueError("Email already registered")
        except Exception:
            pass

        model = UserParser.parse_create(payload)
        created = self.db.insert(model)
        return UserParser.to_response(created)

    def get_user(self, user_id: str):
        m = self.db.get_by_id(user_id)
        return UserParser.to_response(m) if m else None

    def list_users(self) -> List:
        rows = self.db.list_all()
        return [UserParser.to_response(r) for r in rows]

    def update_user(self, user_id: str, updates: dict):
        # handle password separately
        if "password" in updates:
            from passlib.hash import bcrypt
            updates["password_hash"] = bcrypt.hash(updates.pop("password"))
        updated = self.db.update(user_id, updates)
        return UserParser.to_response(updated) if updated else None

    def delete_user(self, user_id: str):
        return self.db.delete(user_id)
