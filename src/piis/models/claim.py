"""Layer 2 — Extracted Claim.

A claim is a proposition taken from Content. FACT means the author
presented it as a fact, not that PIIS has verified it.
Verification lives on VerificationStatus (analysis), not on ClaimType.
"""

from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from piis.models.enums import ClaimType, EvidenceLevel


class EvidenceSpan(BaseModel):
    """A quoted span from source Content. Not a knowledge item."""

    model_config = ConfigDict(populate_by_name=True)

    text: str
    source_content_id: str | None = None
    evidence_level: EvidenceLevel = Field(
        default=EvidenceLevel.UNKNOWN,
        validation_alias=AliasChoices("evidence_level", "credibility"),
        description=(
            "Source class of this span (e.g. CREATOR_CONTENT vs ACADEMIC_SOURCE). "
            "Not a truth score and not verification."
        ),
    )


class Claim(BaseModel):
    id: str
    content: str
    claim_type: ClaimType
    source_content_id: str
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "Extractor confidence that this proposition was identified correctly. "
            "Not P(the proposition is true)."
        ),
    )
    evidence: list[EvidenceSpan] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    source_span: str | None = None
