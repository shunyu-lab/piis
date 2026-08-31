"""Question Bank facade: candidate items only, never user knowledge."""

from pathlib import Path

from piis.assessment.models import AssessmentItem
from piis.assessment.repository import AssessmentItemRepository, JsonAssessmentItemRepository


class QuestionBank:
    """A library of assessment items that a future engine may select from.

    Not a user profile. Not a knowledge base. Not an assessment result.
    """

    def __init__(self, repository: AssessmentItemRepository) -> None:
        self._repository = repository

    def get(self, item_id: str) -> AssessmentItem | None:
        return self._repository.get(item_id)

    def list_items(self) -> list[AssessmentItem]:
        return self._repository.list_items()


def question_bank_from_directory(directory: Path) -> QuestionBank:
    return QuestionBank(JsonAssessmentItemRepository(directory))
