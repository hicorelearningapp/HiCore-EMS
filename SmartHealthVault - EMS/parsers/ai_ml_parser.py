from models.ai_ml_model import AIResultModel
from schemas.ai_ml_schema import AIResultCreate, AIResultResponse
from datetime import datetime

class AIMLParser:
    @staticmethod
    def parse_create(result: AIResultCreate) -> AIResultModel:
        return AIResultModel(
            user_id=result.user_id,
            result=result.result,
            explanation=result.explanation,
            created_at=datetime.utcnow()
        )

    @staticmethod
    def to_json(result: AIResultModel) -> AIResultResponse:
        return AIResultResponse.from_orm(result)
