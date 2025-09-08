from database.db_manager import DatabaseManager
from database.enums import DBType
from parsers.ai_ml_parser import AIParser
from schemas.ai_ml_schema import AIRequest
from typing import List
from sqlalchemy.orm import Session

class AIManager:
    def __init__(self, db_session: Session):
        self.db = DatabaseManager(db_session).get_database(DBType.AI_ML_DB)

    def analyze(self, payload: AIRequest):
        result = {"summary": "placeholder summary", "risk_scores": {"diabetes": 0.1}}
        model = AIParser.parse_result(payload.user_id, result, explanation="placeholder")
        created = self.db.insert(model)
        return AIParser.to_response(created)

    def predict(self, payload: AIRequest):
        return self.analyze(payload)

    def get_result(self, result_id: str):
        m = self.db.get_by_id(result_id)
        return AIParser.to_response(m) if m else None

    def list_models(self) -> List[str]:
        return ["diagnosis-risk-model", "treatment-suggestion-model"]
