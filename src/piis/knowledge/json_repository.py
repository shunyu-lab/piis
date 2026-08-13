import json
from pathlib import Path

from piis.knowledge.repository import KnowledgeRepository
from piis.models.enums import KnowledgeStore, KnowledgeType
from piis.models.knowledge import KnowledgeItem, PersonalBelief


class JsonKnowledgeRepository(KnowledgeRepository):
    """JSON files are the knowledge source of truth for V0.1."""

    def __init__(self, directory: Path, store: KnowledgeStore) -> None:
        self._directory = directory
        self._store = store
        self._items = _load(directory, store)

    @property
    def store(self) -> KnowledgeStore:
        return self._store

    def list_items(self) -> list[KnowledgeItem]:
        return list(self._items.values())

    def get(self, item_id: str) -> KnowledgeItem | None:
        return self._items.get(item_id)

    def save(self, item: KnowledgeItem) -> None:
        """Write-through to JSON. The processing pipeline must not call this on personal data."""
        if item.store != self._store:
            raise ValueError(f"item store {item.store} does not match repository {self._store}")
        self._items[item.id] = item
        path = self._directory / "items.json"
        payload = [source_of_truth_dict(row) for row in self._items.values()]
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def source_of_truth_dict(item: KnowledgeItem) -> dict:
    """JSON SoT payload. Derived fields such as embeddings must never appear here."""
    data = item.model_dump(mode="json")
    data.pop("embedding", None)
    return data


def _load(directory: Path, store: KnowledgeStore) -> dict[str, KnowledgeItem]:
    directory.mkdir(parents=True, exist_ok=True)
    loaded: dict[str, KnowledgeItem] = {}
    for path in sorted(directory.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload if isinstance(payload, list) else [payload]
        for row in rows:
            item = _parse(row, store)
            loaded[item.id] = item
    return loaded


def _parse(row: dict, store: KnowledgeStore) -> KnowledgeItem:
    row = {**row, "store": store.value}
    row.pop("embedding", None)
    knowledge_type = KnowledgeType(row["knowledge_type"])
    if knowledge_type == KnowledgeType.PERSONAL_BELIEF:
        return PersonalBelief.model_validate(row)
    return KnowledgeItem.model_validate(row)
