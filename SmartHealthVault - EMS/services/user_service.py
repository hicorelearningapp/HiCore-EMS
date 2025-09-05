from typing import Dict
from models.user_model import User
import uuid

class UserService:
    def __init__(self, store: Dict[str, User]):
        self.store = store

    def create_user(self, user: User) -> User:
        uid = user.id or str(uuid.uuid4())
        user.id = uid
        self.store[uid] = user
        return user

    def get_user(self, user_id: str):
        return self.store.get(user_id)

    def list_users(self):
        return list(self.store.values())

    def update_user(self, user_id: str, patch: Dict):
        user = self.store.get(user_id)
        if not user:
            return None
        updated = user.copy(update=patch)
        self.store[user_id] = updated
        return updated

    def delete_user(self, user_id: str):
        return self.store.pop(user_id, None)
