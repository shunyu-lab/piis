from piis.models.content import NormalizedContent
from piis.normalization.base import Normalizer


class DefaultNormalizer(Normalizer):
    def normalize(
        self,
        *,
        content_id: str,
        title: str,
        source_url: str,
        text: str,
        language: str,
    ) -> NormalizedContent:
        cleaned = "\n".join(line.rstrip() for line in text.strip().splitlines())
        return NormalizedContent(
            content_id=content_id,
            text=cleaned,
            language=language,
            title=title,
            source_url=source_url,
        )


PassthroughNormalizer = DefaultNormalizer
