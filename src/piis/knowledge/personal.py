from pathlib import Path

from piis.knowledge.json_repository import JsonKnowledgeRepository
from piis.models.enums import KnowledgeStore
from piis.models.knowledge import KnowledgeItem


class PersonalKnowledgeRepository(JsonKnowledgeRepository):
    """Read-only from the pipeline. Beliefs are never auto-updated."""

    def __init__(self, directory: Path) -> None:
        super().__init__(directory, KnowledgeStore.PERSONAL)

    def save(self, item: KnowledgeItem) -> None:
        raise PermissionError(
            "Personal knowledge is read-only during processing. "
            "The pipeline may retrieve and compare beliefs, not write them."
        )
