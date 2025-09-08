from database.db_manager import DatabaseManager
from database.enums import DBType
from parsers.insurance_parser import InsuranceParser
from schemas.insurance_schema import InsuranceCreate
from typing import List

class InsuranceManager:
    def __init__(self):
        self.db = DatabaseManager().get_database(DBType.INSURANCE_DB)

    def create_insurance(self, insurance_data: InsuranceCreate):
        insurance = InsuranceParser.parse_create(insurance_data)
        saved = self.db.add_insurance(insurance)
        return InsuranceParser.to_json(saved)

    def get_insurance(self, insurance_id: str):
        i = self.db.get_insurance(insurance_id)
        return InsuranceParser.to_json(i) if i else None

    def list_insurances(self) -> List:
        return [InsuranceParser.to_json(i) for i in self.db.list_insurances()]

    def update_insurance(self, insurance_id: str, updates: dict):
        i = self.db.update_insurance(insurance_id, updates)
        return InsuranceParser.to_json(i) if i else None

    def delete_insurance(self, insurance_id: str):
        return self.db.delete_insurance(insurance_id)
