from abc import ABC, abstractmethod

from piis.models.content import NormalizedContent


class Normalizer(ABC):
    @abstractmethod
    def normalize(
        self,
        *,
        content_id: str,
        title: str,
        source_url: str,
        text: str,
        language: str,
    ) -> NormalizedContent:
        """Clean extracted text. Does not produce claims or knowledge."""
