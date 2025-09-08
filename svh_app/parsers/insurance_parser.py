from models.insurance_model import PolicyModel, ClaimModel
from schemas.insurance_schema import PolicyCreate, PolicyResponse, ClaimCreate
import json
from datetime import datetime

class InsuranceParser:
    @staticmethod
    def parse_policy(payload: PolicyCreate) -> PolicyModel:
        return PolicyModel(patient_id=payload.patient_id, name=payload.name,
                           sum_insured=payload.sum_insured, premium=payload.premium,
                           details=json.dumps(payload.details or {}), created_at=datetime.utcnow())

    @staticmethod
    def to_policy_response(m: PolicyModel) -> PolicyResponse:
        details = {}
        try:
            import json as _json
            details = _json.loads(m.details) if m.details else {}
        except Exception:
            details = {}
        return PolicyResponse(id=m.id, patient_id=m.patient_id, name=m.name,
                              sum_insured=m.sum_insured, premium=m.premium, details=details, created_at=m.created_at)

    @staticmethod
    def parse_claim(payload: ClaimCreate) -> ClaimModel:
        return ClaimModel(policy_id=payload.policy_id, patient_id=payload.patient_id,
                          amount=payload.amount, reason=payload.reason, created_at=datetime.utcnow())
