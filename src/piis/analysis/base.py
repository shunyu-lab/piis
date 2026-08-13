from abc import ABC, abstractmethod
from collections.abc import Sequence

from piis.models.analysis import SemanticDiffResult
from piis.models.claim import Claim
from piis.models.content import Content
from piis.models.knowledge import RelatedKnowledge


class SemanticDiffEngine(ABC):
    """Reasoning port: compare extracted Claims against retrieved Knowledge.

    Implementations must return SemanticDiffResult (analysis), never KnowledgeItem.
    Embedding similarity may be used as a feature; it is not the relation label.
    """

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def diff(
        self,
        *,
        content: Content,
        claims: Sequence[Claim],
        related: RelatedKnowledge,
    ) -> SemanticDiffResult: ...
