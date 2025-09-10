from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from models.user_model import UserModel

class UserDatabase:
    def __init__(self, db: Session):
        self.db = db

    def execute_query(self, query: str, params: Any = None):
        return self.db.execute(query, params).fetchall()

    def insert(self, user: UserModel) -> UserModel:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, id: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.id == id).first()

    def get_by_email(self, email: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def list_all(self, filters: Dict = None) -> List[UserModel]:
        q = self.db.query(UserModel)
        return q.all()

    def update(self, id: str, updates: Dict) -> Optional[UserModel]:
        u = self.get_by_id(id)
        if not u:
            return None
        for k, v in updates.items():
            setattr(u, k, v)
        self.db.commit()
        self.db.refresh(u)
        return u

    def delete(self, id: str) -> bool:
        u = self.get_by_id(id)
        if not u:
            return False
        self.db.delete(u)
        self.db.commit()
        return True
