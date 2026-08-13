from pathlib import Path

from fastapi.testclient import TestClient

from piis.config.settings import Settings
from piis.models.analysis import SemanticDiffResult
from piis.models.claim import Claim
from piis.models.content import Content
from piis.models.enums import RelationLabel
from piis.runtime import build_pipeline

ROOT = Path(__file__).resolve().parents[1]
DEMO = "https://example.com/demo"


def _settings(tmp_path: Path) -> Settings:
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    return Settings(
        knowledge_dir=ROOT / "examples" / "sample_data",
        data_dir=tmp_path,
        database_url=f"sqlite:///{(runtime / 'piis.db').as_posix()}",
    )


def test_pipeline_demo_url(tmp_path: Path) -> None:
    steps: list[str] = []
    pipeline = build_pipeline(_settings(tmp_path), on_step=steps.append)
    report = pipeline.process_url(DEMO)

    assert "Content acquired" in steps
    assert "Text extracted" in steps
    assert "Content normalized" in steps
    assert "Claims extracted" in steps
    assert "Knowledge retrieved" in steps
    assert "Semantic diff completed" in steps
    assert "Evidence analysis completed" in steps
    assert "Report generated" in steps

    assert isinstance(report.content, Content)
    assert all(isinstance(claim, Claim) for claim in report.claims)
    assert isinstance(report.diff, SemanticDiffResult)
    assert report.claims, "demo fixture should extract claims"
    assert Path(report.markdown_path or "").exists()

    labels = {item.primary_label for item in report.diff.claim_analyses}
    assert RelationLabel.CONFLICTING in labels
    assert RelationLabel.REDUNDANT in labels or RelationLabel.SUPPORTING in labels

    markdown = Path(report.markdown_path or "").read_text(encoding="utf-8")
    assert "Presented as fact" in markdown
    assert "UNVERIFIED" in markdown
    assert "will not change them" in markdown.lower() or "Belief left unchanged" in markdown


def test_unknown_provider_fails_fast(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    settings.llm_provider = "openai"
    try:
        build_pipeline(settings)
        raise AssertionError("expected fail-fast for unknown LLM provider")
    except ValueError as exc:
        assert "openai" in str(exc)
        assert "mock" in str(exc).lower()


def test_health_endpoint() -> None:
    from piis.api.main import app

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
