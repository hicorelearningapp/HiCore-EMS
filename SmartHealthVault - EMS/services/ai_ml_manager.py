from database.db_manager import DatabaseManager
from database.enums import DBType
from parsers.ai_ml_parser import AIMLParser
from schemas.ai_ml_schema import AIResultCreate
from typing import List

class AIMLManager:
    def __init__(self):
        self.db = DatabaseManager().get_database(DBType.AI_ML_DB)

    def create_result(self, result_data: AIResultCreate):
        result = AIMLParser.parse_create(result_data)
        saved = self.db.add_result(result)
        return AIMLParser.to_json(saved)

    def get_result(self, result_id: str):
        r = self.db.get_result(result_id)
        return AIMLParser.to_json(r) if r else None

    def list_results(self) -> List:
        return [AIMLParser.to_json(r) for r in self.db.list_results()]

    def update_result(self, result_id: str, updates: dict):
        r = self.db.update_result(result_id, updates)
        return AIMLParser.to_json(r) if r else None

    def delete_result(self, result_id: str):
        return self.db.delete_result(result_id)
