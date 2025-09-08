from models.insurance_model import InsuranceModel
from schemas.insurance_schema import InsuranceCreate, InsuranceResponse
from datetime import datetime

class InsuranceParser:
    @staticmethod
    def parse_create(insurance: InsuranceCreate) -> InsuranceModel:
        return InsuranceModel(
            user_id=insurance.user_id,
            provider=insurance.provider,
            policy_number=insurance.policy_number,
            coverage_details=insurance.coverage_details,
            valid_till=insurance.valid_till,
            created_at=datetime.utcnow()
        )

    @staticmethod
    def to_json(insurance: InsuranceModel) -> InsuranceResponse:
        return InsuranceResponse.from_orm(insurance)
