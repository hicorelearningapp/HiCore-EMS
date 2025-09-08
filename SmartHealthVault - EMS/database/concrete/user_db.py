from database.base import SessionLocal
from database.interfaces import IDatabase
from models.user_model import UserModel
from sqlalchemy.orm import Session

class UserDatabase(IDatabase):
    def __init__(self):
        self.session: Session = SessionLocal()

    def execute_query(self, query: str, params: dict = None):
        return self.session.execute(query, params)

    def add_user(self, user: UserModel):
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_user(self, user_id: str):
        return self.session.query(UserModel).filter(UserModel.id == user_id).first()

    def list_users(self):
        return self.session.query(UserModel).all()

    def update_user(self, user_id: str, updates: dict):
        user = self.get_user(user_id)
        if not user:
            return None
        for k, v in updates.items():
            setattr(user, k, v)
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete_user(self, user_id: str):
        user = self.get_user(user_id)
        if not user:
            return None
        self.session.delete(user)
        self.session.commit()
        return True
