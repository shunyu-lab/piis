"""Replaceable storage for AssessmentItem records. V0.1 ships an empty local bank."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from piis.assessment.models import AssessmentItem


class AssessmentItemRepository(Protocol):
    def get(self, item_id: str) -> AssessmentItem | None: ...

    def list_items(self) -> list[AssessmentItem]: ...


class JsonAssessmentItemRepository:
    """Load assessment items from JSON files in a directory.

    An empty directory (or a directory with no ``*.json`` files) is a valid bank.
    This class does not write items and does not store user responses.
    """

    def __init__(self, directory: Path) -> None:
        self._directory = directory
        self._items = _load(directory)

    def get(self, item_id: str) -> AssessmentItem | None:
        return self._items.get(item_id)

    def list_items(self) -> list[AssessmentItem]:
        return list(self._items.values())


def _load(directory: Path) -> dict[str, AssessmentItem]:
    loaded: dict[str, AssessmentItem] = {}
    if not directory.is_dir():
        return loaded
    for path in sorted(directory.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload if isinstance(payload, list) else [payload]
        for row in rows:
            item = AssessmentItem.model_validate(row)
            loaded[item.id] = item
    return loaded
