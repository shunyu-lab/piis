"""Layer 4 — Reasoning / Analysis Result.

Outputs of comparing Claims against Knowledge. These must never be written
back as KnowledgeItem records by the pipeline.

Embedding similarity is an intermediate signal, not the analysis itself.
"""

from pydantic import BaseModel, Field, computed_field

from piis.models.enums import (
    AnalysisMethod,
    ClaimType,
    KnowledgeStore,
    RelationLabel,
    VerificationStatus,
)


class KnowledgeRelation(BaseModel):
    """One Claim compared with one KnowledgeItem — a reasoning edge."""

    source_id: str
    target_id: str
    relation: RelationLabel
    similarity: float | None = Field(
        default=None,
        description="Embedding similarity used as a feature, never as the verdict.",
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the relation label, not in the truth of either statement.",
    )
    store: KnowledgeStore
    rationale: str = ""
    method: AnalysisMethod = AnalysisMethod.HEURISTIC

    @computed_field
    @property
    def claim_id(self) -> str:
        return self.source_id

    @computed_field
    @property
    def knowledge_id(self) -> str:
        return self.target_id

    @computed_field
    @property
    def label(self) -> RelationLabel:
        return self.relation


class ClaimAnalysis(BaseModel):
    claim_id: str
    claim_type: ClaimType
    statement: str
    relations: list[KnowledgeRelation] = Field(default_factory=list)
    novelty_score: float = Field(ge=0.0, le=1.0)
    supporting_score: float = Field(ge=0.0, le=1.0)
    related_score: float = Field(ge=0.0, le=1.0)
    conflict_score: float = Field(ge=0.0, le=1.0)
    redundancy_score: float = Field(ge=0.0, le=1.0)
    evidence_gap_score: float = Field(ge=0.0, le=1.0)
    evidence_gap: str | None = None
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    primary_label: RelationLabel
    method: AnalysisMethod
    notes: str = ""


class SemanticDiffResult(BaseModel):
    content_id: str
    claim_analyses: list[ClaimAnalysis]
    novelty: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    related: list[str] = Field(default_factory=list)
    redundancies: list[str] = Field(default_factory=list)
    evidence_gaps: list[str] = Field(default_factory=list)
    novelty_score: float = Field(ge=0.0, le=1.0)
    supporting_score: float = Field(ge=0.0, le=1.0)
    conflict_score: float = Field(ge=0.0, le=1.0)
    redundancy_score: float = Field(ge=0.0, le=1.0)
    evidence_gap_score: float = Field(ge=0.0, le=1.0)
    method: AnalysisMethod
    engine: str


class EvidenceAnalysis(BaseModel):
    content_id: str
    notes: list[str] = Field(default_factory=list)
    claim_gaps: dict[str, str] = Field(default_factory=dict)
