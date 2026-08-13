from piis.embedding.base import EmbeddingProvider
from piis.knowledge.base import KnowledgeRepository
from piis.models.claim import Claim
from piis.models.enums import KnowledgeStore
from piis.models.knowledge import KnowledgeItem, RelatedKnowledge
from piis.vectorstore.base import VectorStore

_STORES = (
    KnowledgeStore.DOMAIN,
    KnowledgeStore.PRIMARY,
    KnowledgeStore.PERSONAL,
    KnowledgeStore.EXTERNAL,
)


class KnowledgeRetriever:
    """Looks up related Knowledge for Claims. Does not produce analysis."""

    def __init__(
        self,
        repositories: dict[KnowledgeStore, KnowledgeRepository],
        embeddings: EmbeddingProvider,
        vectors: VectorStore,
        *,
        top_k: int = 4,
    ) -> None:
        self._repositories = repositories
        self._embeddings = embeddings
        self._vectors = vectors
        self._top_k = top_k
        self._index()

    def retrieve(self, claims: list[Claim]) -> RelatedKnowledge:
        by_store: dict[KnowledgeStore, dict[str, KnowledgeItem]] = {s: {} for s in _STORES}
        for claim in claims:
            vector = self._embeddings.embed_one(claim.content)
            for store in _STORES:
                if store not in self._repositories:
                    continue
                for hit in self._vectors.query(vector, store=store, top_k=self._top_k):
                    item = self._repositories[store].get(hit.item_id)
                    if item is not None:
                        by_store[store][item.id] = item
        return RelatedKnowledge(
            domain=list(by_store[KnowledgeStore.DOMAIN].values()),
            primary=list(by_store[KnowledgeStore.PRIMARY].values()),
            personal=list(by_store[KnowledgeStore.PERSONAL].values()),
            external=list(by_store[KnowledgeStore.EXTERNAL].values()),
        )

    def _index(self) -> None:
        for store, repo in self._repositories.items():
            items = repo.list_items()
            if not items:
                continue
            vectors = self._embeddings.embed([item.content for item in items])
            for item, vector in zip(items, vectors, strict=True):
                self._vectors.add(item.id, vector, store)
