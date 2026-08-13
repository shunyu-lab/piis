from abc import ABC, abstractmethod

from piis.models.content import Content


class Extractor(ABC):
    @abstractmethod
    def extract(self, content: Content) -> str:
        """Return extracted text (transcript, article body, ...). Not claims."""
