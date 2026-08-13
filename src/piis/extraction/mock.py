from piis.extraction.base import Extractor
from piis.models.content import Content


class MockExtractionProvider(Extractor):
    """V0.1 stand-in for transcription: use Content.raw_text as-is."""

    def extract(self, content: Content) -> str:
        return content.raw_text


PlainTextExtractor = MockExtractionProvider
