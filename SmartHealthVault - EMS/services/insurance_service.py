from typing import Dict, List
from models.insurance_model import InsurancePlan
import uuid

class InsuranceService:
    """
    Simple placeholder insurance logic: returns a few mock plans
    """
    def __init__(self, store: Dict[str, InsurancePlan]):
        self.store = store

    def recommend_plans(self, query: dict):
        # Create some sample plans (in real life consult DB / partner APIs)
        sample = [
            InsurancePlan(id=str(uuid.uuid4()), name="Basic Health Plan", sum_insured=300000, premium=4999.0, details={"type":"individual"}),
            InsurancePlan(id=str(uuid.uuid4()), name="Comprehensive Family Plan", sum_insured=1000000, premium=19999.0, details={"type":"family"}),
        ]
        # store them for reference
        for p in sample:
            self.store[p.id] = p
        return sample

    def get_plan(self, plan_id: str):
        return self.store.get(plan_id)
