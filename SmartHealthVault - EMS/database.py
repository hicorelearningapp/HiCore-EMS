from typing import Dict, Any
from fastapi import Depends

class InMemoryDB:
    """
    Simple in-memory database store.
    Each service gets its own dict.
    """
    def __init__(self):
        self.users: Dict[str, Any] = {}
        self.doctors: Dict[str, Any] = {}
        self.records: Dict[str, Any] = {}
        self.ai_results: Dict[str, Any] = {}
        self.insurance_policies: Dict[str, Any] = {}
        self.notifications: Dict[str, Any] = {}
        self.appointments: Dict[str, Any] = {}

# Dependency overrideable in tests/startup
_db_instance = InMemoryDB()
def get_db() -> InMemoryDB:
    return _db_instance
