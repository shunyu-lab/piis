"""Composition root. Swap providers here without touching the pipeline."""

from collections.abc import Callable

from piis.acquisition.mock import MockAcquisition
from piis.analysis.classifier import HeuristicRelationClassifier
from piis.analysis.evidence import HeuristicEvidenceAnalyzer
from piis.analysis.semantic_diff import HybridSemanticDiffEngine
from piis.config.settings import Settings
from piis.embedding.mock import MockEmbeddingProvider
from piis.extraction.claims import ClaimExtractor
from piis.extraction.mock import MockExtractionProvider
from piis.knowledge import KnowledgeRetriever, build_repositories
from piis.llm.mock import MockLLMProvider
from piis.normalization.default import DefaultNormalizer
from piis.persistence.repositories import JobStore
from piis.pipeline.processor import Pipeline
from piis.reports.generator import ReportGenerator
from piis.vectorstore.memory import MemoryVectorStore


def build_pipeline(
    settings: Settings | None = None,
    *,
    verbose: bool = False,
    on_step: Callable[[str], None] | None = None,
) -> Pipeline:
    settings = settings or Settings()
    settings.ensure_runtime_dirs()

    llm = _llm(settings)
    embeddings = _embeddings(settings)
    vectors = _vectors(settings)
    repositories = build_repositories(settings.knowledge_dir)

    step = on_step or (print if verbose else None)
    return Pipeline(
        acquisition=MockAcquisition(),
        extractor=MockExtractionProvider(),
        normalizer=DefaultNormalizer(),
        claim_extractor=ClaimExtractor(llm),
        retriever=KnowledgeRetriever(repositories, embeddings, vectors),
        diff_engine=HybridSemanticDiffEngine(embeddings, HeuristicRelationClassifier()),
        evidence_analyzer=HeuristicEvidenceAnalyzer(),
        report_generator=ReportGenerator(settings.processed_dir),
        job_store=JobStore(settings.database_url),
        on_step=step,
    )


def _llm(settings: Settings) -> MockLLMProvider:
    if settings.llm_provider != "mock":
        raise ValueError(
            f"LLM provider '{settings.llm_provider}' is not implemented in V0.1. Use mock."
        )
    return MockLLMProvider()


def _embeddings(settings: Settings) -> MockEmbeddingProvider:
    if settings.embedding_provider != "mock":
        raise ValueError(
            f"Embedding provider '{settings.embedding_provider}' is not implemented in V0.1. Use mock."
        )
    return MockEmbeddingProvider()


def _vectors(settings: Settings) -> MemoryVectorStore:
    if settings.vector_store != "memory":
        raise ValueError(
            f"Vector store '{settings.vector_store}' is not implemented in V0.1. Use memory."
        )
    return MemoryVectorStore()
