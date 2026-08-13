from pathlib import Path

from piis.knowledge.domain import DomainKnowledgeRepository
from piis.knowledge.external import ExternalKnowledgeRepository
from piis.knowledge.json_repository import JsonKnowledgeRepository
from piis.knowledge.personal import PersonalKnowledgeRepository
from piis.knowledge.primary import PrimarySourceRepository
from piis.knowledge.repository import KnowledgeRepository
from piis.knowledge.retriever import KnowledgeRetriever
from piis.models.enums import KnowledgeStore


def build_repositories(knowledge_dir: Path) -> dict[KnowledgeStore, KnowledgeRepository]:
    return {
        KnowledgeStore.DOMAIN: DomainKnowledgeRepository(knowledge_dir / "domain"),
        KnowledgeStore.PRIMARY: PrimarySourceRepository(knowledge_dir / "primary"),
        KnowledgeStore.PERSONAL: PersonalKnowledgeRepository(knowledge_dir / "personal"),
        KnowledgeStore.EXTERNAL: ExternalKnowledgeRepository(knowledge_dir / "external"),
    }


__all__ = [
    "DomainKnowledgeRepository",
    "ExternalKnowledgeRepository",
    "JsonKnowledgeRepository",
    "KnowledgeRepository",
    "KnowledgeRetriever",
    "PersonalKnowledgeRepository",
    "PrimarySourceRepository",
    "build_repositories",
]
