from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from database.db_manager import get_db_session
from services.insurance_manager import InsuranceManager
from schemas.insurance_schema import PolicyCreate, PolicyResponse, ClaimCreate

router = APIRouter(prefix="/insurance", tags=["Insurance"])

@router.post("/policies/", response_model=PolicyResponse)
def create_policy(payload: PolicyCreate, db: Session = Depends(get_db_session)):
    return InsuranceManager(db).create_policy(payload)

@router.get("/policies/{policy_id}", response_model=PolicyResponse)
def get_policy(policy_id: str, db: Session = Depends(get_db_session)):
    p = InsuranceManager(db).get_policy(policy_id)
    if not p: raise HTTPException(status_code=404, detail="Policy not found")
    return p

@router.post("/claims/")
def submit_claim(payload: ClaimCreate, db: Session = Depends(get_db_session)):
    return InsuranceManager(db).submit_claim(payload)
