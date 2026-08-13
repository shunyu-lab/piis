"""Layer 1 — Raw Content.

Internet payload before claims are extracted. This is not knowledge.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from piis.models.enums import SourceType


class Content(BaseModel):
    id: str
    source_url: str
    source_type: SourceType
    title: str
    author: str | None = None
    published_at: datetime | None = None
    raw_text: str
    language: str = "und"
    metadata: dict[str, Any] = Field(default_factory=dict)


class NormalizedContent(BaseModel):
    """Cleaned text derived from Content. Still not a claim and not knowledge."""

    content_id: str
    text: str
    language: str
    title: str
    source_url: str
    metadata: dict[str, Any] = Field(default_factory=dict)
