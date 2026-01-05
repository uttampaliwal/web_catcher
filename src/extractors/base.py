from abc import ABC, abstractmethod
from src.models import Document

class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, source: str) -> Document:
        pass
