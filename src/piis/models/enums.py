"""Shared enumerations. These are labels, not verdicts of truth."""

from enum import StrEnum


class SourceType(StrEnum):
    VIDEO = "video"
    ARTICLE = "article"
    POST = "post"
    PAPER = "paper"
    FORUM = "forum"
    UNKNOWN = "unknown"


class ClaimType(StrEnum):
    """How the author framed the proposition — not whether it is true."""

    FACT = "FACT"
    OPINION = "OPINION"
    PREDICTION = "PREDICTION"
    INTERPRETATION = "INTERPRETATION"
    VALUE_JUDGMENT = "VALUE_JUDGMENT"
    QUESTION = "QUESTION"
    UNKNOWN = "UNKNOWN"


class KnowledgeType(StrEnum):
    DOMAIN_KNOWLEDGE = "DOMAIN_KNOWLEDGE"
    PRIMARY_SOURCE = "PRIMARY_SOURCE"
    PERSONAL_BELIEF = "PERSONAL_BELIEF"
    PERSONAL_HYPOTHESIS = "PERSONAL_HYPOTHESIS"
    PERSONAL_QUESTION = "PERSONAL_QUESTION"
    EXTERNAL_CLAIM = "EXTERNAL_CLAIM"


class KnowledgeStore(StrEnum):
    DOMAIN = "domain"
    PRIMARY = "primary"
    PERSONAL = "personal"
    EXTERNAL = "external"


class EvidenceLevel(StrEnum):
    """Source class for an evidence span. Not equivalent to truth or verification."""

    PRIMARY_SOURCE = "PRIMARY_SOURCE"
    OFFICIAL_SOURCE = "OFFICIAL_SOURCE"
    ACADEMIC_SOURCE = "ACADEMIC_SOURCE"
    REPUTABLE_MEDIA = "REPUTABLE_MEDIA"
    EXPERT_ANALYSIS = "EXPERT_ANALYSIS"
    CREATOR_CONTENT = "CREATOR_CONTENT"
    FORUM = "FORUM"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    UNKNOWN = "UNKNOWN"


class AnalysisMethod(StrEnum):
    HEURISTIC = "heuristic"
    EMBEDDING = "embedding"
    LLM = "llm"
    HYBRID = "hybrid"


class RelationLabel(StrEnum):
    """How a claim relates to a knowledge item. A reasoning label, not knowledge."""

    SUPPORTING = "supporting"
    CONFLICTING = "conflicting"
    RELATED = "related"
    REDUNDANT = "redundant"
    UNRELATED = "unrelated"
    UNKNOWN = "unknown"


class VerificationStatus(StrEnum):
    """Distinct from ClaimType. V0.1 always leaves claims UNVERIFIED."""

    UNVERIFIED = "UNVERIFIED"
    SUPPORTED = "SUPPORTED"
    REFUTED = "REFUTED"


class JobStatus(StrEnum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
