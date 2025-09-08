from abc import ABC, abstractmethod

class IDatabase(ABC):
    @abstractmethod
    def execute_query(self, query: str, params: dict = None):
        pass
