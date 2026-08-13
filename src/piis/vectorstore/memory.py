from collections.abc import Sequence

from piis.models.enums import KnowledgeStore
from piis.vectorstore.base import VectorHit, VectorStore


class MemoryVectorStore(VectorStore):
    def __init__(self) -> None:
        self._items: list[tuple[str, KnowledgeStore, list[float]]] = []

    def add(
        self,
        item_id: str,
        vector: Sequence[float],
        store: KnowledgeStore,
    ) -> None:
        self._items = [row for row in self._items if row[0] != item_id]
        self._items.append((item_id, store, list(vector)))

    def query(
        self,
        vector: Sequence[float],
        *,
        store: KnowledgeStore | None = None,
        top_k: int = 5,
    ) -> list[VectorHit]:
        scored: list[VectorHit] = []
        for item_id, item_store, stored in self._items:
            if store is not None and item_store != store:
                continue
            scored.append(
                VectorHit(item_id=item_id, store=item_store, score=_cosine(vector, stored))
            )
        scored.sort(key=lambda hit: hit.score, reverse=True)
        return scored[:top_k]


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    return float(sum(x * y for x, y in zip(a, b, strict=False)))
