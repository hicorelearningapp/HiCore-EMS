from fastapi import APIRouter, HTTPException
from services.insurance_manager import InsuranceManager
from schemas.insurance_schema import InsuranceCreate, InsuranceResponse
from typing import List

router = APIRouter(prefix="/insurance", tags=["Insurance"])
manager = InsuranceManager()

@router.post("/", response_model=InsuranceResponse)
def create_insurance(insurance: InsuranceCreate):
    return manager.create_insurance(insurance)

@router.get("/", response_model=List[InsuranceResponse])
def list_insurances():
    return manager.list_insurances()

@router.get("/{insurance_id}", response_model=InsuranceResponse)
def get_insurance(insurance_id: str):
    i = manager.get_insurance(insurance_id)
    if not i:
        raise HTTPException(status_code=404, detail="Insurance record not found")
    return i

@router.put("/{insurance_id}", response_model=InsuranceResponse)
def update_insurance(insurance_id: str, updates: dict):
    i = manager.update_insurance(insurance_id, updates)
    if not i:
        raise HTTPException(status_code=404, detail="Insurance record not found")
    return i

@router.delete("/{insurance_id}")
def delete_insurance(insurance_id: str):
    ok = manager.delete_insurance(insurance_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Insurance record not found")
    return {"message": "Insurance record deleted"}
