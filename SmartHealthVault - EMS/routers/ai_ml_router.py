from fastapi import APIRouter, HTTPException
from services.ai_ml_manager import AIMLManager
from schemas.ai_ml_schema import AIResultCreate, AIResultResponse
from typing import List

router = APIRouter(prefix="/ai-results", tags=["AI/ML"])
manager = AIMLManager()

@router.post("/", response_model=AIResultResponse)
def create_result(result: AIResultCreate):
    return manager.create_result(result)

@router.get("/", response_model=List[AIResultResponse])
def list_results():
    return manager.list_results()

@router.get("/{result_id}", response_model=AIResultResponse)
def get_result(result_id: str):
    r = manager.get_result(result_id)
    if not r:
        raise HTTPException(status_code=404, detail="Result not found")
    return r

@router.put("/{result_id}", response_model=AIResultResponse)
def update_result(result_id: str, updates: dict):
    r = manager.update_result(result_id, updates)
    if not r:
        raise HTTPException(status_code=404, detail="Result not found")
    return r

@router.delete("/{result_id}")
def delete_result(result_id: str):
    ok = manager.delete_result(result_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Result not found")
    return {"message": "Result deleted"}
