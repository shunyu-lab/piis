"""Evidence analysis. V0.1 is heuristic and never claims verification."""

from abc import ABC, abstractmethod

from piis.models.analysis import EvidenceAnalysis, SemanticDiffResult
from piis.models.claim import Claim
from piis.models.content import Content
from piis.models.enums import ClaimType, VerificationStatus


class EvidenceAnalyzer(ABC):
    @abstractmethod
    def analyze(self, content: Content, claims: list[Claim]) -> EvidenceAnalysis: ...

    def merge(self, diff: SemanticDiffResult, evidence: EvidenceAnalysis) -> SemanticDiffResult:
        analyses = []
        for item in diff.claim_analyses:
            gap = evidence.claim_gaps.get(item.claim_id)
            score = 0.85 if gap else 0.15
            analyses.append(
                item.model_copy(
                    update={
                        "evidence_gap_score": score,
                        "evidence_gap": gap,
                        "verification_status": VerificationStatus.UNVERIFIED,
                    }
                )
            )
        gap_scores = [a.evidence_gap_score for a in analyses]
        return diff.model_copy(
            update={
                "claim_analyses": analyses,
                "evidence_gaps": [cid for cid in evidence.claim_gaps],
                "evidence_gap_score": max(gap_scores) if gap_scores else 0.0,
            }
        )


class HeuristicEvidenceAnalyzer(EvidenceAnalyzer):
    """Flags missing support. Does not decide truth."""

    def analyze(self, content: Content, claims: list[Claim]) -> EvidenceAnalysis:
        gaps: dict[str, str] = {}
        notes: list[str] = [
            "Verification status is UNVERIFIED for every claim in V0.1.",
            "ClaimType is framing only. Evidence level is not equivalent to truth.",
        ]
        for claim in claims:
            if claim.claim_type in {ClaimType.FACT, ClaimType.PREDICTION} and not claim.evidence:
                gaps[claim.id] = (
                    f"{claim.claim_type.value} + {VerificationStatus.UNVERIFIED.value}: "
                    "no evidence spans attached."
                )
        if gaps:
            notes.append(
                "Evidence gaps mean the source did not supply support, "
                "not that the proposition is false."
            )
        return EvidenceAnalysis(content_id=content.id, notes=notes, claim_gaps=gaps)
