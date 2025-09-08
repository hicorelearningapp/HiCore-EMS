from database.base import SessionLocal
from database.interfaces import IDatabase
from models.insurance_model import InsuranceModel
from sqlalchemy.orm import Session

class InsuranceDatabase(IDatabase):
    def __init__(self):
        self.session: Session = SessionLocal()

    def execute_query(self, query: str, params: dict = None):
        return self.session.execute(query, params)

    def add_insurance(self, insurance: InsuranceModel):
        self.session.add(insurance)
        self.session.commit()
        self.session.refresh(insurance)
        return insurance

    def get_insurance(self, insurance_id: str):
        return self.session.query(InsuranceModel).filter(InsuranceModel.id == insurance_id).first()

    def list_insurances(self):
        return self.session.query(InsuranceModel).all()

    def update_insurance(self, insurance_id: str, updates: dict):
        insurance = self.get_insurance(insurance_id)
        if not insurance:
            return None
        for k, v in updates.items():
            setattr(insurance, k, v)
        self.session.commit()
        self.session.refresh(insurance)
        return insurance

    def delete_insurance(self, insurance_id: str):
        insurance = self.get_insurance(insurance_id)
        if not insurance:
            return None
        self.session.delete(insurance)
        self.session.commit()
        return True
