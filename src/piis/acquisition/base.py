from abc import ABC, abstractmethod

from piis.models.content import Content


class AcquisitionProvider(ABC):
    @abstractmethod
    def acquire(self, url: str) -> Content:
        """Fetch raw Content for a URL. Implementations must not extract claims."""
