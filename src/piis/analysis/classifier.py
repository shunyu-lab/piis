"""Relation classification: Claim × KnowledgeItem → reasoning label.

V0.1 ships a heuristic classifier. V0.2 can swap LLMRelationClassifier
without changing SemanticDiffEngine.
"""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from difflib import SequenceMatcher

from piis.llm.base import LLMProvider
from piis.models.analysis import KnowledgeRelation
from piis.models.claim import Claim
from piis.models.enums import AnalysisMethod, RelationLabel
from piis.models.knowledge import KnowledgeItem

_CLASSIFY_SYSTEM = (
    "Classify the relation between a CLAIM and a KNOWLEDGE item. "
    "Return JSON with keys label and rationale. "
    "label must be one of: supporting, conflicting, related, redundant, unrelated, unknown. "
    "Do not decide whether the claim is true. Similarity is a feature, not agreement."
)


class RelationClassifier(ABC):
    @property
    @abstractmethod
    def method(self) -> AnalysisMethod: ...

    @abstractmethod
    def classify(
        self,
        claim: Claim,
        item: KnowledgeItem,
        *,
        similarity: float | None,
    ) -> KnowledgeRelation:
        """Decide the relation. `similarity` is an optional feature, not the answer."""


class HeuristicRelationClassifier(RelationClassifier):
    """Transparent V0.1 rules. Labeled heuristic so it cannot be mistaken for NLI."""

    @property
    def method(self) -> AnalysisMethod:
        return AnalysisMethod.HEURISTIC

    def classify(
        self,
        claim: Claim,
        item: KnowledgeItem,
        *,
        similarity: float | None,
    ) -> KnowledgeRelation:
        label, rationale, confidence = _heuristic(claim.content, item.content, similarity)
        return KnowledgeRelation(
            source_id=claim.id,
            target_id=item.id,
            relation=label,
            store=item.store,
            confidence=confidence,
            similarity=similarity,
            rationale=rationale,
            method=self.method,
        )


class LLMRelationClassifier(RelationClassifier):
    """Future path: same signature, LLM decides the label using similarity as context."""

    def __init__(self, llm: LLMProvider) -> None:
        self._llm = llm

    @property
    def method(self) -> AnalysisMethod:
        return AnalysisMethod.LLM

    def classify(
        self,
        claim: Claim,
        item: KnowledgeItem,
        *,
        similarity: float | None,
    ) -> KnowledgeRelation:
        prompt = (
            f"CLAIM: {claim.content}\n"
            f"KNOWLEDGE: {item.content}\n"
            f"KNOWLEDGE_TYPE: {item.knowledge_type.value}\n"
            f"SIMILARITY_FEATURE: {similarity if similarity is not None else 'n/a'}\n"
        )
        payload = json.loads(self._llm.generate(prompt, system=_CLASSIFY_SYSTEM))
        label = RelationLabel(payload["label"])
        return KnowledgeRelation(
            source_id=claim.id,
            target_id=item.id,
            relation=label,
            store=item.store,
            confidence=0.6,
            similarity=similarity,
            rationale=str(payload.get("rationale", "")),
            method=self.method,
        )


def _heuristic(
    claim_text: str,
    knowledge_text: str,
    similarity: float | None,
) -> tuple[RelationLabel, str, float]:
    a = _norm(claim_text)
    b = _norm(knowledge_text)
    overlap = SequenceMatcher(None, a, b).ratio()

    if _opposing_polarity(a, b):
        return (
            RelationLabel.CONFLICTING,
            "Heuristic: shared topic with opposing polarity "
            "(e.g. replace vs will not replace). "
            "Similarity is not used as the verdict.",
            0.8,
        )

    if a == b or overlap >= 0.88:
        return (
            RelationLabel.REDUNDANT,
            "Heuristic: near-duplicate wording. String overlap is used only for redundancy.",
            0.95,
        )

    if similarity is not None and similarity < 0.28:
        return (
            RelationLabel.UNRELATED,
            "Heuristic: low embedding similarity and no polarity clash — treated as unrelated.",
            0.7,
        )

    if overlap >= 0.62 or (similarity is not None and similarity >= 0.62):
        return (
            RelationLabel.SUPPORTING,
            "Heuristic: same-direction paraphrase / strong neighborhood. Not a truth verdict.",
            0.65,
        )

    if overlap >= 0.40 or (similarity is not None and similarity >= 0.40):
        return (
            RelationLabel.RELATED,
            "Heuristic: topical neighborhood without duplicate wording or detected opposition.",
            0.55,
        )

    return (
        RelationLabel.UNRELATED,
        "Heuristic: insufficient relatedness signals.",
        0.45,
    )


def _opposing_polarity(a: str, b: str) -> bool:
    pairs = (
        (_ELIMINATE, _CHANGE_NOT_ELIMINATE),
        (_REPLACE, _NOT_REPLACE),
        (_BAN, _NO_BAN),
    )
    for positive, negative in pairs:
        if (positive.search(a) and negative.search(b)) or (
            positive.search(b) and negative.search(a)
        ):
            return True
    return False


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


_ELIMINATE = re.compile(r"completely eliminate|eliminate the need|wipe out|replace all")
_CHANGE_NOT_ELIMINATE = re.compile(
    r"rather than (simply )?eliminate|change the structure|more likely to change"
)
_REPLACE = re.compile(r"\bwill replace\b|\breplace programmers\b|\breplace software engineers\b")
_NOT_REPLACE = re.compile(r"\bwill not replace\b|\bwon't replace\b|\bnot replace\b")
_BAN = re.compile(r"ban all|should ban")
_NO_BAN = re.compile(r"should not ban|must not ban|do not ban")
