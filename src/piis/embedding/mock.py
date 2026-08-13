import hashlib
import math
import re
from collections.abc import Sequence

from piis.embedding.base import EmbeddingProvider

_DIM = 64

# Collapse paraphrases so embedding similarity can be high even when polarity differs.
_CANON = {
    "llms": "language_model",
    "llm": "language_model",
    "programmers": "software_engineer",
    "programmer": "software_engineer",
    "engineers": "software_engineer",
    "engineer": "software_engineer",
    "coding": "code",
    "assistants": "assistant",
    "assistant": "assistant",
    "boilerplate": "boilerplate",
    "python": "python",
    "guido": "guido",
    "rossum": "rossum",
    "ai": "ai",
    "eliminate": "eliminate",
    "ban": "ban",
    "paris": "paris",
    "france": "france",
    "capital": "capital",
}


class MockEmbeddingProvider(EmbeddingProvider):
    """Hashed bag-of-words vectors. Similarity is a retrieval signal only."""

    @property
    def name(self) -> str:
        return "mock"

    @property
    def dimensions(self) -> int:
        return _DIM

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [_vector(text) for text in texts]


def _vector(text: str) -> list[float]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    vec = [0.0] * _DIM
    for token in tokens:
        canon = _CANON.get(token, token)
        bucket = int(hashlib.md5(canon.encode("utf-8"), usedforsecurity=False).hexdigest(), 16) % _DIM
        vec[bucket] += 1.0
    return _l2(vec)


def _l2(vec: list[float]) -> list[float]:
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]
