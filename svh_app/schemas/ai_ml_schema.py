from models.ai_ml_model import AIResultModel
from parsers.ai_ml_parser import AIRequest, AIResponse
import json

class AIParser:
    @staticmethod
    def parse_result(user_id: str, result: dict, explanation: str = None) -> AIResultModel:
        return AIResultModel(user_id=user_id, result=json.dumps(result), explanation=explanation)

    @staticmethod
    def to_response(model: AIResultModel) -> AIResponse:
        res = {}
        try:
            import json as _json
            res = _json.loads(model.result) if model.result else {}
        except Exception:
            res = {}
        return AIResponse(id=model.id, user_id=model.user_id, result=res, explanation=model.explanation, created_at=model.created_at)
