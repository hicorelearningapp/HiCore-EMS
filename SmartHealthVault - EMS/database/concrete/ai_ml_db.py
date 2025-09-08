from database.base import SessionLocal
from database.interfaces import IDatabase
from models.ai_ml_model import AIResultModel
from sqlalchemy.orm import Session

class AIMLDatabase(IDatabase):
    def __init__(self):
        self.session: Session = SessionLocal()

    def execute_query(self, query: str, params: dict = None):
        return self.session.execute(query, params)

    def add_result(self, result: AIResultModel):
        self.session.add(result)
        self.session.commit()
        self.session.refresh(result)
        return result

    def get_result(self, result_id: str):
        return self.session.query(AIResultModel).filter(AIResultModel.id == result_id).first()

    def list_results(self):
        return self.session.query(AIResultModel).all()

    def update_result(self, result_id: str, updates: dict):
        result = self.get_result(result_id)
        if not result:
            return None
        for k, v in updates.items():
            setattr(result, k, v)
        self.session.commit()
        self.session.refresh(result)
        return result

    def delete_result(self, result_id: str):
        result = self.get_result(result_id)
        if not result:
            return None
        self.session.delete(result)
        self.session.commit()
        return True
