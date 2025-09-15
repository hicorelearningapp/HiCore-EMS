from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from database.db_manager import get_db_session
from services.insurance_manager import InsuranceManager
from parsers.insurance_parser import PolicyCreate, PolicyResponse, ClaimCreate, ClaimResponse

router = APIRouter(prefix="/insurance", tags=["Insurance"])

@router.post("/policies/", response_model=PolicyResponse)
def create_policy(payload: PolicyCreate, db: Session = Depends(get_db_session)):
    return InsuranceManager(db).create_policy(payload)

@router.get("/policies/{policy_id}", response_model=PolicyResponse)
def get_policy(policy_id: str, db: Session = Depends(get_db_session)):
    p = InsuranceManager(db).get_policy(policy_id)
    if not p: raise HTTPException(status_code=404, detail="Policy not found")
    return p

@router.get("/policies/patient/{patient_id}", response_model=List[PolicyResponse])
def get_patient_policies(patient_id: str, db: Session = Depends(get_db_session)):
    """
    Get all insurance policies for a specific patient
    
    - **patient_id**: The ID of the patient whose policies to retrieve
    - Returns: List of insurance policies for the specified patient
    """
    policies = InsuranceManager(db).list_policies_for_patient(patient_id)
    if not policies:
        raise HTTPException(
            status_code=404,
            detail=f"No policies found for patient with ID: {patient_id}"
        )
    return policies

@router.post("/claims/", response_model=Dict[str, Any])
def submit_claim(payload: ClaimCreate, db: Session = Depends(get_db_session)):
    """
    Submit a new insurance claim
    
    - **policy_id**: ID of the insurance policy
    - **patient_id**: ID of the patient making the claim
    - **amount**: Claim amount
    - **reason**: Reason for the claim (optional)
    - Returns: Claim submission details
    """
    return InsuranceManager(db).submit_claim(payload)

@router.get("/claims/{claim_id}", response_model=ClaimResponse)
def get_claim(claim_id: str, db: Session = Depends(get_db_session)):
    """
    Get claim status and details by ID
    
    - **claim_id**: The ID of the claim to retrieve
    - Returns: Claim details including status
    
    Example response:
    ```json
    {
        "claim_id": "123e4567-e89b-12d3-a456-426614174000",
        "policy_id": "123e4567-e89b-12d3-a456-426614174000",
        "patient_id": "123e4567-e89b-12d3-a456-426614174000",
        "amount": 1500.0,
        "reason": "Annual checkup",
        "status": "submitted",
        "created_at": "2023-01-01T12:00:00"
    }
    ```
    """
    claim = InsuranceManager(db).get_claim(claim_id)
    if not claim:
        raise HTTPException(
            status_code=404,
            detail=f"Claim with ID {claim_id} not found"
        )
    return claim
