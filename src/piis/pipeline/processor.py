from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from piis.acquisition.base import AcquisitionProvider
from piis.analysis.base import SemanticDiffEngine
from piis.analysis.evidence import EvidenceAnalyzer
from piis.extraction.base import Extractor
from piis.extraction.claims import ClaimExtractor
from piis.ids import new_id
from piis.knowledge.retriever import KnowledgeRetriever
from piis.models.analysis import SemanticDiffResult
from piis.models.content import Content
from piis.models.report import Report
from piis.normalization.base import Normalizer
from piis.persistence.repositories import JobStore
from piis.reports.generator import ReportGenerator


class Pipeline:
    def __init__(
        self,
        *,
        acquisition: AcquisitionProvider,
        extractor: Extractor,
        normalizer: Normalizer,
        claim_extractor: ClaimExtractor,
        retriever: KnowledgeRetriever,
        diff_engine: SemanticDiffEngine,
        evidence_analyzer: EvidenceAnalyzer,
        report_generator: ReportGenerator,
        job_store: JobStore | None = None,
        on_step: Callable[[str], None] | None = None,
    ) -> None:
        self._acquisition = acquisition
        self._extractor = extractor
        self._normalizer = normalizer
        self._claim_extractor = claim_extractor
        self._retriever = retriever
        self._diff_engine = diff_engine
        self._evidence_analyzer = evidence_analyzer
        self._report_generator = report_generator
        self._job_store = job_store
        self._on_step = on_step or (lambda _msg: None)

    def process_url(self, url: str) -> Report:
        job = self._job_store.create(url) if self._job_store is not None else None
        try:
            content = self._acquisition.acquire(url)
            self._on_step("Content acquired")
            report = self.process(content, job_id=job.id if job else None)
            if job is not None and self._job_store is not None:
                self._job_store.complete(job.id, report.id)
            return report
        except Exception as exc:
            if job is not None and self._job_store is not None:
                self._job_store.fail(job.id, str(exc))
            raise

    def process(self, content: Content, *, job_id: str | None = None) -> Report:
        extracted = self._extractor.extract(content)
        self._on_step("Text extracted")
        normalized = self._normalizer.normalize(
            content_id=content.id,
            title=content.title,
            source_url=content.source_url,
            text=extracted,
            language=content.language,
        )
        self._on_step("Content normalized")
        claims = self._claim_extractor.extract(normalized)
        self._on_step("Claims extracted")
        related = self._retriever.retrieve(claims)
        self._on_step("Knowledge retrieved")
        diff = self._diff_engine.diff(content=content, claims=claims, related=related)
        self._on_step("Semantic diff completed")
        evidence = self._evidence_analyzer.analyze(content, claims)
        diff = self._evidence_analyzer.merge(diff, evidence)
        self._on_step("Evidence analysis completed")
        report = Report(
            id=new_id("report"),
            job_id=job_id,
            content=content,
            claims=claims,
            diff=diff,
            evidence=evidence,
            created_at=datetime.now(UTC),
            follow_ups=_follow_ups(diff),
        )
        saved = self._report_generator.write(report)
        if self._job_store is not None:
            self._job_store.save_report_meta(saved)
        self._on_step("Report generated")
        return saved

    def report_json_path(self, report_id: str) -> Path | None:
        if self._job_store is None:
            return None
        return self._job_store.get_report_json_path(report_id)


def _follow_ups(diff: SemanticDiffResult) -> list[str]:
    items: list[str] = []
    for analysis in diff.claim_analyses:
        if analysis.conflict_score >= 0.5:
            items.append(
                f"Re-evaluate personal or domain knowledge against: {analysis.statement}"
            )
        if analysis.evidence_gap_score >= 0.7:
            items.append(
                f"Look for primary sources supporting or challenging: {analysis.statement}"
            )
        if analysis.novelty_score >= 0.8:
            items.append(
                f"Decide whether to add as a hypothesis (not a belief): {analysis.statement}"
            )
    return items or ["No automatic follow-up. Judgment stays with the user."]
