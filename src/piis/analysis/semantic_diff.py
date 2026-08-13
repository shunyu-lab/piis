"""Semantic Diff Engine.

Pipeline inside the engine (stable for V0.2+):

    Claim + retrieved Knowledge
        → embed both (EmbeddingProvider)          # signal
        → classify each pair (RelationClassifier) # decision
        → aggregate ClaimAnalysis                 # analysis result

The engine never writes KnowledgeItem records.
"""

from collections.abc import Sequence
from statistics import mean

from piis.analysis.base import SemanticDiffEngine
from piis.analysis.classifier import RelationClassifier
from piis.embedding.base import EmbeddingProvider
from piis.models.analysis import ClaimAnalysis, KnowledgeRelation, SemanticDiffResult
from piis.models.claim import Claim
from piis.models.content import Content
from piis.models.enums import AnalysisMethod, RelationLabel, VerificationStatus
from piis.models.knowledge import KnowledgeItem, RelatedKnowledge

_LABEL_PRIORITY = (
    RelationLabel.CONFLICTING,
    RelationLabel.REDUNDANT,
    RelationLabel.SUPPORTING,
    RelationLabel.RELATED,
    RelationLabel.UNRELATED,
    RelationLabel.UNKNOWN,
)


class HybridSemanticDiffEngine(SemanticDiffEngine):
    def __init__(
        self,
        embeddings: EmbeddingProvider,
        classifier: RelationClassifier,
    ) -> None:
        self._embeddings = embeddings
        self._classifier = classifier

    @property
    def name(self) -> str:
        return f"hybrid:{self._embeddings.name}+{self._classifier.method.value}"

    def diff(
        self,
        *,
        content: Content,
        claims: Sequence[Claim],
        related: RelatedKnowledge,
    ) -> SemanticDiffResult:
        items = related.all_items()
        item_vectors = {
            item.id: vec
            for item, vec in zip(
                items,
                self._embeddings.embed([item.content for item in items]) if items else [],
                strict=True,
            )
        }
        analyses = [self._analyze_claim(claim, items, item_vectors) for claim in claims]
        method = (
            AnalysisMethod.HYBRID
            if self._classifier.method != AnalysisMethod.LLM
            else AnalysisMethod.LLM
        )
        return SemanticDiffResult(
            content_id=content.id,
            claim_analyses=analyses,
            novelty=_ids(analyses, RelationLabel.UNRELATED),
            conflicts=_ids(analyses, RelationLabel.CONFLICTING),
            related=_ids(analyses, RelationLabel.RELATED, RelationLabel.SUPPORTING),
            redundancies=_ids(analyses, RelationLabel.REDUNDANT),
            evidence_gaps=[],
            novelty_score=_mean([a.novelty_score for a in analyses], default=0.0),
            supporting_score=_max([a.supporting_score for a in analyses], default=0.0),
            conflict_score=_max([a.conflict_score for a in analyses], default=0.0),
            redundancy_score=_max([a.redundancy_score for a in analyses], default=0.0),
            evidence_gap_score=0.0,
            method=method,
            engine=self.name,
        )

    def _analyze_claim(
        self,
        claim: Claim,
        items: list[KnowledgeItem],
        item_vectors: dict[str, list[float]],
    ) -> ClaimAnalysis:
        claim_vec = self._embeddings.embed_one(claim.content)
        relations: list[KnowledgeRelation] = []
        for item in items:
            similarity = _cosine(claim_vec, item_vectors[item.id])
            relations.append(self._classifier.classify(claim, item, similarity=similarity))
        return _to_claim_analysis(claim, relations, self._classifier.method)


def _to_claim_analysis(
    claim: Claim,
    relations: list[KnowledgeRelation],
    method: AnalysisMethod,
) -> ClaimAnalysis:
    if not relations:
        return ClaimAnalysis(
            claim_id=claim.id,
            claim_type=claim.claim_type,
            statement=claim.content,
            relations=[],
            novelty_score=1.0,
            supporting_score=0.0,
            related_score=0.0,
            conflict_score=0.0,
            redundancy_score=0.0,
            evidence_gap_score=0.0,
            verification_status=VerificationStatus.UNVERIFIED,
            primary_label=RelationLabel.UNRELATED,
            method=method,
            notes="No retrieved knowledge to compare against.",
        )

    by_label = {label: 0.0 for label in RelationLabel}
    for rel in relations:
        by_label[rel.relation] = max(by_label[rel.relation], rel.confidence)

    primary = next(
        (label for label in _LABEL_PRIORITY if any(r.relation == label for r in relations)),
        RelationLabel.UNKNOWN,
    )
    return ClaimAnalysis(
        claim_id=claim.id,
        claim_type=claim.claim_type,
        statement=claim.content,
        relations=relations,
        novelty_score=_novelty(primary, relations),
        supporting_score=by_label[RelationLabel.SUPPORTING],
        related_score=by_label[RelationLabel.RELATED],
        conflict_score=by_label[RelationLabel.CONFLICTING],
        redundancy_score=by_label[RelationLabel.REDUNDANT],
        evidence_gap_score=0.0,
        verification_status=VerificationStatus.UNVERIFIED,
        primary_label=primary,
        method=method,
        notes=_notes(primary),
    )


def _novelty(primary: RelationLabel, relations: list[KnowledgeRelation]) -> float:
    if primary == RelationLabel.REDUNDANT:
        return 0.08
    if primary == RelationLabel.SUPPORTING:
        return 0.2
    if primary == RelationLabel.RELATED:
        return 0.35
    if primary == RelationLabel.CONFLICTING:
        return 0.45
    if all(rel.relation == RelationLabel.UNRELATED for rel in relations):
        return 0.88
    return 0.6


def _notes(primary: RelationLabel) -> str:
    if primary == RelationLabel.CONFLICTING:
        return (
            "Potential conflict with existing knowledge or a personal belief. "
            "This is a re-evaluation cue, not a truth verdict. "
            "Personal beliefs are never auto-modified."
        )
    if primary == RelationLabel.REDUNDANT:
        return "Appears to restate knowledge already held."
    if primary == RelationLabel.UNRELATED:
        return "No close match in retrieved knowledge — candidate novel information."
    if primary == RelationLabel.SUPPORTING:
        return "Same-direction overlap with retrieved knowledge; still UNVERIFIED."
    if primary == RelationLabel.RELATED:
        return "Topically related to retrieved knowledge; not a duplicate and not a verdict."
    return "Relation uncertain in V0.1."


def _ids(analyses: list[ClaimAnalysis], *labels: RelationLabel) -> list[str]:
    return [a.claim_id for a in analyses if a.primary_label in labels]


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    return float(sum(x * y for x, y in zip(a, b, strict=False)))


def _mean(values: list[float], default: float) -> float:
    return float(mean(values)) if values else default


def _max(values: list[float], default: float) -> float:
    return float(max(values)) if values else default
