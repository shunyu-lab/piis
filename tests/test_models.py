from datetime import UTC, datetime

from piis.models.analysis import ClaimAnalysis, SemanticDiffResult
from piis.models.claim import Claim, EvidenceSpan
from piis.models.content import Content, NormalizedContent
from piis.models.enums import (
    AnalysisMethod,
    ClaimType,
    EvidenceLevel,
    KnowledgeStore,
    KnowledgeType,
    RelationLabel,
    SourceType,
    VerificationStatus,
)
from piis.models.knowledge import KnowledgeItem, PersonalBelief


def test_content_is_not_a_claim() -> None:
    content = Content(
        id="c1",
        source_url="https://example.com/demo",
        source_type=SourceType.VIDEO,
        title="t",
        raw_text="body",
    )
    assert content.raw_text == "body"
    assert not hasattr(content, "claim_type")


def test_normalized_content_is_still_not_a_claim() -> None:
    normalized = NormalizedContent(
        content_id="c1",
        text="body",
        language="en",
        title="t",
        source_url="https://example.com/demo",
    )
    assert not hasattr(normalized, "claim_type")
    assert not hasattr(normalized, "knowledge_type")


def test_fact_claim_is_framing_not_truth() -> None:
    claim = Claim(
        id="cl1",
        content="The sky is green.",
        claim_type=ClaimType.FACT,
        source_content_id="c1",
        confidence=0.9,
        metadata={"extractor": "mock"},
    )
    assert claim.claim_type is ClaimType.FACT
    assert not hasattr(claim, "verification_status")
    assert "Not P(the proposition is true)" in (Claim.model_fields["confidence"].description or "")


def test_evidence_level_is_source_class_not_truth() -> None:
    span = EvidenceSpan(text="quote", credibility=EvidenceLevel.CREATOR_CONTENT)
    assert span.evidence_level is EvidenceLevel.CREATOR_CONTENT
    dumped = span.model_dump()
    assert dumped["evidence_level"] == "CREATOR_CONTENT"
    assert "credibility" not in dumped


def test_knowledge_item_has_no_embedding_slot() -> None:
    item = KnowledgeItem(
        id="d1",
        content="Python exists",
        knowledge_type=KnowledgeType.DOMAIN_KNOWLEDGE,
        store=KnowledgeStore.DOMAIN,
    )
    assert "embedding" not in item.model_dump()
    assert "embedding" not in KnowledgeItem.model_fields


def test_personal_belief_is_not_domain_knowledge() -> None:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    belief = PersonalBelief(
        id="p1",
        content="Sample belief",
        source="user",
        confidence=0.65,
        created_at=now,
        updated_at=now,
    )
    assert belief.knowledge_type is KnowledgeType.PERSONAL_BELIEF
    assert belief.store is KnowledgeStore.PERSONAL
    item = KnowledgeItem(
        id="d1",
        content="Python exists",
        knowledge_type=KnowledgeType.DOMAIN_KNOWLEDGE,
        store=KnowledgeStore.DOMAIN,
    )
    assert item.knowledge_type is not belief.knowledge_type


def test_fact_framing_is_independent_of_verification() -> None:
    analysis = ClaimAnalysis(
        claim_id="cl1",
        claim_type=ClaimType.FACT,
        statement="The sky is green.",
        novelty_score=0.5,
        supporting_score=0.0,
        related_score=0.0,
        conflict_score=0.0,
        redundancy_score=0.0,
        evidence_gap_score=0.2,
        verification_status=VerificationStatus.UNVERIFIED,
        primary_label=RelationLabel.UNRELATED,
        method=AnalysisMethod.HEURISTIC,
    )
    assert analysis.claim_type is ClaimType.FACT
    assert analysis.verification_status is VerificationStatus.UNVERIFIED


def test_analysis_result_is_not_knowledge() -> None:
    result = SemanticDiffResult(
        content_id="c1",
        claim_analyses=[
            ClaimAnalysis(
                claim_id="cl1",
                claim_type=ClaimType.OPINION,
                statement="x",
                novelty_score=0.8,
                supporting_score=0.1,
                related_score=0.0,
                conflict_score=0.0,
                redundancy_score=0.0,
                evidence_gap_score=0.2,
                verification_status=VerificationStatus.UNVERIFIED,
                primary_label=RelationLabel.UNRELATED,
                method=AnalysisMethod.HYBRID,
            )
        ],
        novelty=["cl1"],
        novelty_score=0.8,
        supporting_score=0.1,
        conflict_score=0.0,
        redundancy_score=0.0,
        evidence_gap_score=0.2,
        method=AnalysisMethod.HYBRID,
        engine="test",
    )
    dumped = result.model_dump()
    assert "knowledge_type" not in dumped
    assert result.claim_analyses[0].verification_status is VerificationStatus.UNVERIFIED
