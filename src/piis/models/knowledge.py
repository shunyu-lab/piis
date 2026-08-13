"""Layer 3 — Knowledge.

Items stored in a knowledge base. Distinct from Content, Claim, and Analysis.
PERSONAL_BELIEF is the user's current cognitive state, not a fact.

Embeddings are not part of this model. They are derived at runtime in VectorStore.
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from piis.models.enums import KnowledgeStore, KnowledgeType


class KnowledgeItem(BaseModel):
    """Authoritative knowledge record. No embedding vectors — those are derived data."""

    id: str
    content: str
    knowledge_type: KnowledgeType
    store: KnowledgeStore
    source: str | None = None
    topics: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class BeliefRevision(BaseModel):
    at: datetime
    statement: str
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="How strongly the user held this version of the belief, not P(true).",
    )
    note: str | None = None


class PersonalBelief(KnowledgeItem):
    knowledge_type: Literal[KnowledgeType.PERSONAL_BELIEF] = KnowledgeType.PERSONAL_BELIEF
    store: Literal[KnowledgeStore.PERSONAL] = KnowledgeStore.PERSONAL
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="User's self-rated strength of this belief. Not a truth probability.",
    )
    created_at: datetime
    updated_at: datetime
    supporting_evidence: list[str] = Field(default_factory=list)
    opposing_evidence: list[str] = Field(default_factory=list)
    related_ids: list[str] = Field(default_factory=list)
    revisions: list[BeliefRevision] = Field(default_factory=list)


class RelatedKnowledge(BaseModel):
    """Retrieval bundle. Still knowledge, not an analysis result."""

    domain: list[KnowledgeItem] = Field(default_factory=list)
    primary: list[KnowledgeItem] = Field(default_factory=list)
    personal: list[KnowledgeItem] = Field(default_factory=list)
    external: list[KnowledgeItem] = Field(default_factory=list)

    def all_items(self) -> list[KnowledgeItem]:
        return [*self.domain, *self.primary, *self.personal, *self.external]
