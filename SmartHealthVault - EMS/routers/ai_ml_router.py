from fastapi import APIRouter, Depends
from models.ai_ml_model import AIRequest, AIResponse
from services.ai_ml_service import AIService
from database import get_db
from typing import List

router = APIRouter()

def _service(db=Depends(get_db)):
    return AIService(db.ai_results)

@router.post("/analyze/", response_model=AIResponse)
def analyze(req: AIRequest, svc: AIService = Depends(_service)):
    return svc.analyze(req.user_id, req.dict())

@router.post("/predict/", response_model=AIResponse)
def predict(req: AIRequest, svc: AIService = Depends(_service)):
    return svc.analyze(req.user_id, req.dict())  # placeholder

@router.get("/models/", response_model=List[str])
def list_models():
    return ["diagnosis-risk-model", "treatment-suggestion-model"]

@router.post("/train/")
def train_model(data: dict):
    return {"status": "training started", "params": data}
