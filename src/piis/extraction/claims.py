import json

from piis.ids import new_id
from piis.llm.base import LLMProvider
from piis.models.claim import Claim, EvidenceSpan
from piis.models.content import NormalizedContent
from piis.models.enums import ClaimType, EvidenceLevel

_EXTRACT_SYSTEM = (
    "Extract claims as JSON. Each claim is a proposition, not a summary. "
    "FACT means the author presented it as fact, not that it is verified."
)


class ClaimExtractor:
    """Turns NormalizedContent into Claims via an LLMProvider."""

    def __init__(self, llm: LLMProvider) -> None:
        self._llm = llm

    def extract(self, normalized: NormalizedContent) -> list[Claim]:
        prompt = (
            f"source_url={normalized.source_url}\n"
            f"title={normalized.title}\n"
            f"text=\n{normalized.text}\n"
        )
        raw = self._llm.generate(prompt, system=_EXTRACT_SYSTEM)
        payload = json.loads(raw)
        claims: list[Claim] = []
        for item in payload["claims"]:
            evidence = [
                EvidenceSpan(
                    text=span["text"],
                    source_content_id=normalized.content_id,
                    evidence_level=EvidenceLevel(
                        span.get("evidence_level", span.get("credibility", "UNKNOWN"))
                    ),
                )
                for span in item.get("evidence", [])
            ]
            claims.append(
                Claim(
                    id=new_id("claim"),
                    content=item["content"],
                    claim_type=ClaimType(item["claim_type"]),
                    source_content_id=normalized.content_id,
                    confidence=float(item.get("confidence", 0.5)),
                    evidence=evidence,
                    topics=list(item.get("topics", [])),
                )
            )
        return claims
