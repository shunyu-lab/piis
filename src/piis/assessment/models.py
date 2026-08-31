"""Question-bank item schema. No scoring. No sample questions."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class CognitiveLevel(StrEnum):
    """Intended depth of an item. Not a linear intelligence score and not a grader."""

    RECOGNITION = "RECOGNITION"
    CONCEPTUAL_UNDERSTANDING = "CONCEPTUAL_UNDERSTANDING"
    APPLICATION = "APPLICATION"
    COMPARISON = "COMPARISON"
    CRITICAL_EVALUATION = "CRITICAL_EVALUATION"


class QuestionType(StrEnum):
    """Presentation form of an item. Not generation logic and not a rubric."""

    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    SHORT_ANSWER = "SHORT_ANSWER"
    OPEN_ENDED = "OPEN_ENDED"
    TRUE_FALSE = "TRUE_FALSE"
    SCENARIO = "SCENARIO"
    COMPARISON = "COMPARISON"
    OTHER = "OTHER"


class AssessmentItem(BaseModel):
    """One candidate question the system could ask later.

    This is not personal knowledge, not a belief, and not a Knowledge State record.
    """

    id: str
    topic: str
    difficulty: str | None = Field(
        default=None,
        description="Optional metadata label. Not a scoring algorithm.",
    )
    cognitive_level: CognitiveLevel
    question_type: QuestionType
    prompt: str
    metadata: dict[str, Any] = Field(default_factory=dict)
