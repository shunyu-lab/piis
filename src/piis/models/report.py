"""Presentation of analysis — not knowledge and not a claim."""

from datetime import datetime

from pydantic import BaseModel, Field

from piis.models.analysis import EvidenceAnalysis, SemanticDiffResult
from piis.models.claim import Claim
from piis.models.content import Content


class Report(BaseModel):
    id: str
    job_id: str | None = None
    content: Content
    claims: list[Claim]
    diff: SemanticDiffResult
    evidence: EvidenceAnalysis
    markdown_path: str | None = None
    json_path: str | None = None
    created_at: datetime
    follow_ups: list[str] = Field(default_factory=list)
