from pathlib import Path

from piis.knowledge.json_repository import JsonKnowledgeRepository
from piis.models.enums import KnowledgeStore


class PrimarySourceRepository(JsonKnowledgeRepository):
    def __init__(self, directory: Path) -> None:
        super().__init__(directory, KnowledgeStore.PRIMARY)
