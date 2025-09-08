from database.enums import DBType
from database.db_factory import DatabaseFactory
from database.interfaces import IDatabase

class DatabaseManager:
    def __init__(self):
        self._cache = {}

    def get_database(self, db_type: DBType) -> IDatabase:
        if db_type not in self._cache:
            self._cache[db_type] = DatabaseFactory.create_database(db_type)
        return self._cache[db_type]
