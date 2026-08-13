from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass

from piis.models.enums import KnowledgeStore


@dataclass(frozen=True)
class VectorHit:
    item_id: str
    store: KnowledgeStore
    score: float


class VectorStore(ABC):
    """Derived index over knowledge ids. Rebuildable; never the knowledge SoT."""

    @abstractmethod
    def add(
        self,
        item_id: str,
        vector: Sequence[float],
        store: KnowledgeStore,
    ) -> None: ...

    def upsert(
        self,
        item_id: str,
        vector: Sequence[float],
        store: KnowledgeStore,
    ) -> None:
        self.add(item_id, vector, store)

    @abstractmethod
    def query(
        self,
        vector: Sequence[float],
        *,
        store: KnowledgeStore | None = None,
        top_k: int = 5,
    ) -> list[VectorHit]: ...
