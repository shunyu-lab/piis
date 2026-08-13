from datetime import UTC, datetime
from pathlib import Path

import pytest

from piis.knowledge import build_repositories
from piis.knowledge.json_repository import JsonKnowledgeRepository
from piis.knowledge.personal import PersonalKnowledgeRepository
from piis.models.enums import KnowledgeStore, KnowledgeType
from piis.models.knowledge import KnowledgeItem, PersonalBelief

ROOT = Path(__file__).resolve().parents[1]


def test_sample_stores_are_separated() -> None:
    repos = build_repositories(ROOT / "examples" / "sample_data")
    domain_ids = {item.id for item in repos[KnowledgeStore.DOMAIN].list_items()}
    primary_ids = {item.id for item in repos[KnowledgeStore.PRIMARY].list_items()}
    personal_ids = {item.id for item in repos[KnowledgeStore.PERSONAL].list_items()}
    external_ids = {item.id for item in repos[KnowledgeStore.EXTERNAL].list_items()}
    assert domain_ids
    assert primary_ids
    assert personal_ids
    assert external_ids
    assert domain_ids.isdisjoint(primary_ids)
    assert domain_ids.isdisjoint(personal_ids)
    assert all(item.store is KnowledgeStore.DOMAIN for item in repos[KnowledgeStore.DOMAIN].list_items())
    assert all(item.store is KnowledgeStore.PERSONAL for item in repos[KnowledgeStore.PERSONAL].list_items())


def test_json_roundtrip(tmp_path: Path) -> None:
    repo = JsonKnowledgeRepository(tmp_path, KnowledgeStore.DOMAIN)
    item = KnowledgeItem(
        id="domain-test-1",
        content="Fictional domain note about programming tools.",
        knowledge_type=KnowledgeType.DOMAIN_KNOWLEDGE,
        store=KnowledgeStore.DOMAIN,
        source="test",
    )
    repo.save(item)
    raw = (tmp_path / "items.json").read_text(encoding="utf-8")
    assert '"embedding"' not in raw
    reloaded = JsonKnowledgeRepository(tmp_path, KnowledgeStore.DOMAIN)
    found = reloaded.get("domain-test-1")
    assert found is not None
    assert found.content == item.content
    assert found.store is KnowledgeStore.DOMAIN


def test_personal_save_is_rejected(tmp_path: Path) -> None:
    repo = PersonalKnowledgeRepository(tmp_path)
    now = datetime(2026, 1, 1, tzinfo=UTC)
    belief = PersonalBelief(
        id="p1",
        content="A fictional belief",
        source="test",
        confidence=0.5,
        created_at=now,
        updated_at=now,
    )
    with pytest.raises(PermissionError, match="read-only"):
        repo.save(belief)


def test_personal_repo_has_no_write_in_pipeline_contract() -> None:
    """Documented constraint: processing code must not call save on personal knowledge."""
    now = datetime(2026, 1, 1, tzinfo=UTC)
    assert now.tzinfo is UTC
    repos = build_repositories(ROOT / "examples" / "sample_data")
    personal = repos[KnowledgeStore.PERSONAL]
    assert not hasattr(type(personal), "update_belief")
    original = [item.model_dump() for item in personal.list_items()]
    again = [item.model_dump() for item in personal.list_items()]
    assert original == again
