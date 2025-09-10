from database.db_manager import DatabaseManager
from database.enums import DBType
from schemas.insurance_schema import InsuranceParser
from parsers.insurance_parser import PolicyCreate, ClaimCreate
from typing import List
from sqlalchemy.orm import Session

class InsuranceManager:
    def __init__(self, db_session: Session):
        self.db = DatabaseManager(db_session).get_database(DBType.INSURANCE_DB)

    def create_policy(self, payload: PolicyCreate):
        m = InsuranceParser.parse_policy(payload)
        created = self.db.insert(m)
        return InsuranceParser.to_policy_response(created)

    def get_policy(self, policy_id: str):
        p = self.db.get_by_id(policy_id)
        return InsuranceParser.to_policy_response(p) if p else None

    def list_policies_for_patient(self, patient_id: str):
        rows = self.db.list_all({"patient_id": patient_id})
        return [InsuranceParser.to_policy_response(r) for r in rows]

    def submit_claim(self, payload: ClaimCreate):
        claim = InsuranceParser.parse_claim(payload)
        created = self.db.insert(claim)
        return {"claim_id": created.id, "status": created.status, "details": {"policy_id": created.policy_id, "amount": created.amount}}
