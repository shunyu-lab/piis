from piis.analysis.classifier import HeuristicRelationClassifier, LLMRelationClassifier
from piis.analysis.semantic_diff import HybridSemanticDiffEngine
from piis.embedding.mock import MockEmbeddingProvider
from piis.llm.mock import MockLLMProvider
from piis.models.analysis import SemanticDiffResult
from piis.models.claim import Claim
from piis.models.content import Content
from piis.models.enums import (
    AnalysisMethod,
    ClaimType,
    KnowledgeStore,
    KnowledgeType,
    RelationLabel,
    SourceType,
)
from piis.models.knowledge import KnowledgeItem, RelatedKnowledge


def _content() -> Content:
    return Content(
        id="content-test",
        source_url="https://example.com/demo",
        source_type=SourceType.VIDEO,
        title="fixture",
        raw_text="unused",
    )


def _claim(cid: str, text: str, claim_type: ClaimType = ClaimType.FACT) -> Claim:
    return Claim(
        id=cid,
        content=text,
        claim_type=claim_type,
        source_content_id="content-test",
        confidence=0.7,
    )


def _item(iid: str, text: str, store: KnowledgeStore = KnowledgeStore.DOMAIN) -> KnowledgeItem:
    ktype = {
        KnowledgeStore.DOMAIN: KnowledgeType.DOMAIN_KNOWLEDGE,
        KnowledgeStore.PERSONAL: KnowledgeType.PERSONAL_BELIEF,
        KnowledgeStore.PRIMARY: KnowledgeType.PRIMARY_SOURCE,
        KnowledgeStore.EXTERNAL: KnowledgeType.EXTERNAL_CLAIM,
    }[store]
    return KnowledgeItem(id=iid, content=text, knowledge_type=ktype, store=store)


def _engine() -> HybridSemanticDiffEngine:
    return HybridSemanticDiffEngine(MockEmbeddingProvider(), HeuristicRelationClassifier())


def test_identical_is_redundant() -> None:
    text = "Python is a programming language created by Guido van Rossum."
    result = _engine().diff(
        content=_content(),
        claims=[_claim("c-same", text)],
        related=RelatedKnowledge(domain=[_item("k-same", text)]),
    )
    analysis = result.claim_analyses[0]
    assert analysis.primary_label is RelationLabel.REDUNDANT
    assert "c-same" in result.redundancies
    assert isinstance(result, SemanticDiffResult)


def test_paraphrase_same_direction_is_supporting() -> None:
    result = _engine().diff(
        content=_content(),
        claims=[_claim("c-rel", "LLMs help programmers write boilerplate code.")],
        related=RelatedKnowledge(
            domain=[_item("k-rel", "Large language models can assist programmers with boilerplate.")]
        ),
    )
    analysis = result.claim_analyses[0]
    assert analysis.primary_label in {RelationLabel.SUPPORTING, RelationLabel.RELATED, RelationLabel.REDUNDANT}
    assert analysis.primary_label is not RelationLabel.CONFLICTING


def test_related_is_not_redundant() -> None:
    result = _engine().diff(
        content=_content(),
        claims=[_claim("c-topic", "Software engineers still write and review production code.")],
        related=RelatedKnowledge(
            domain=[_item("k-rel", "Large language models can assist programmers with boilerplate.")]
        ),
    )
    analysis = result.claim_analyses[0]
    assert analysis.primary_label in {RelationLabel.RELATED, RelationLabel.UNRELATED, RelationLabel.SUPPORTING}
    assert analysis.primary_label is not RelationLabel.REDUNDANT


def test_conflict_is_not_string_similarity() -> None:
    """Opposite polarity on a shared topic must be CONFLICTING even if vectors are close."""
    claim = _claim(
        "c-conf",
        "AI will completely eliminate the need for software engineers within two years.",
        ClaimType.PREDICTION,
    )
    knowledge = _item(
        "k-conf",
        "AI is more likely to change the structure of programming work than simply eliminate programmers.",
        KnowledgeStore.PERSONAL,
    )
    embeddings = MockEmbeddingProvider()
    similarity = _cosine(
        embeddings.embed_one(claim.content),
        embeddings.embed_one(knowledge.content),
    )
    result = HybridSemanticDiffEngine(embeddings, HeuristicRelationClassifier()).diff(
        content=_content(),
        claims=[claim],
        related=RelatedKnowledge(personal=[knowledge]),
    )
    analysis = result.claim_analyses[0]
    relation = analysis.relations[0]
    assert similarity > 0.35, "fixture should share topical tokens so similarity is not 'low'"
    assert relation.similarity is not None and relation.similarity > 0.35
    assert relation.relation is RelationLabel.CONFLICTING
    assert analysis.primary_label is RelationLabel.CONFLICTING
    assert "c-conf" in result.conflicts


def test_high_similarity_replace_vs_not_replace_is_conflicting() -> None:
    claim = _claim("c-rep", "AI will replace programmers.")
    knowledge = _item("k-rep", "AI will not replace programmers.")
    embeddings = MockEmbeddingProvider()
    similarity = _cosine(
        embeddings.embed_one(claim.content),
        embeddings.embed_one(knowledge.content),
    )
    result = HybridSemanticDiffEngine(embeddings, HeuristicRelationClassifier()).diff(
        content=_content(),
        claims=[claim],
        related=RelatedKnowledge(domain=[knowledge]),
    )
    assert similarity > 0.5
    assert result.claim_analyses[0].primary_label is RelationLabel.CONFLICTING


def test_unrelated_topic_is_unrelated() -> None:
    result = _engine().diff(
        content=_content(),
        claims=[_claim("c-geo", "The capital of France is Paris.")],
        related=RelatedKnowledge(
            domain=[_item("k-ai", "Large language models can assist programmers with boilerplate.")]
        ),
    )
    analysis = result.claim_analyses[0]
    assert analysis.primary_label is RelationLabel.UNRELATED
    assert analysis.novelty_score > 0.7
    assert "c-geo" in result.novelty


def test_llm_classifier_is_a_drop_in_for_the_engine() -> None:
    claim = _claim(
        "c-llm",
        "AI will completely eliminate the need for software engineers within two years.",
        ClaimType.PREDICTION,
    )
    knowledge = _item(
        "k-llm",
        "AI is more likely to change the structure of programming work than simply eliminate programmers.",
        KnowledgeStore.PERSONAL,
    )
    engine = HybridSemanticDiffEngine(
        MockEmbeddingProvider(),
        LLMRelationClassifier(MockLLMProvider()),
    )
    result = engine.diff(
        content=_content(),
        claims=[claim],
        related=RelatedKnowledge(personal=[knowledge]),
    )
    assert result.claim_analyses[0].primary_label is RelationLabel.CONFLICTING
    assert result.method is AnalysisMethod.LLM


def _cosine(a: list[float], b: list[float]) -> float:
    return float(sum(x * y for x, y in zip(a, b, strict=False)))
