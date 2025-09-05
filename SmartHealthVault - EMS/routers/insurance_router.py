from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.insurance_model import InsurancePlan
from services.insurance_service import InsuranceService
from database import get_db

router = APIRouter()

def _service(db=Depends(get_db)):
    return InsuranceService(db.insurance_policies)

@router.post("/policies/", response_model=InsurancePlan)
def create_policy(policy: InsurancePlan, svc: InsuranceService = Depends(_service)):
    return svc.create_policy(policy)

@router.get("/policies/{policy_id}", response_model=InsurancePlan)
def get_policy(policy_id: str, svc: InsuranceService = Depends(_service)):
    p = svc.get_policy(policy_id)
    if not p:
        raise HTTPException(status_code=404, detail="Policy not found")
    return p

@router.get("/policies/patient/{patient_id}", response_model=List[InsurancePlan])
def get_patient_policies(patient_id: str, svc: InsuranceService = Depends(_service)):
    return [p for p in svc.store.values() if p.details.get("patient_id") == patient_id]

@router.post("/claims/")
def submit_claim(claim: dict):
    return {"claim_id": "12345", "status": "submitted", "details": claim}

@router.get("/claims/{claim_id}")
def get_claim(claim_id: str):
    return {"claim_id": claim_id, "status": "in-progress"}
