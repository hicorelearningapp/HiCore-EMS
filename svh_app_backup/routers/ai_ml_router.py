from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from database.db_manager import get_db_session
from services.ai_ml_manager import AIManager
from parsers.ai_ml_parser import AIRequest, AIResponse

router = APIRouter(prefix="/ai", tags=["AI/ML"])

@router.post("/analyze/", response_model=AIResponse)
def analyze(req: AIRequest, db: Session = Depends(get_db_session)):
    return AIManager(db).analyze(req)

@router.post("/predict/", response_model=AIResponse)
def predict(req: AIRequest, db: Session = Depends(get_db_session)):
    return AIManager(db).predict(req)

@router.get("/models/", response_model=List[str])
def models(db: Session = Depends(get_db_session)):
    return AIManager(db).list_models()
