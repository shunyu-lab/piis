from abc import ABC, abstractmethod

from piis.models.enums import KnowledgeStore
from piis.models.knowledge import KnowledgeItem


class KnowledgeRepository(ABC):
    """Source of truth for one knowledge store. Implementations must not mix stores."""

    @property
    @abstractmethod
    def store(self) -> KnowledgeStore: ...

    @abstractmethod
    def list_items(self) -> list[KnowledgeItem]: ...

    @abstractmethod
    def get(self, item_id: str) -> KnowledgeItem | None: ...
