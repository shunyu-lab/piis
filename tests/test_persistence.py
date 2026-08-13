from pathlib import Path

from piis.config.settings import Settings
from piis.models.enums import JobStatus
from piis.persistence.repositories import JobStore
from piis.runtime import build_pipeline

ROOT = Path(__file__).resolve().parents[1]
DEMO = "https://example.com/demo"


def test_job_and_report_survive_new_session(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    db_url = f"sqlite:///{(runtime / 'piis.db').as_posix()}"
    settings = Settings(
        knowledge_dir=ROOT / "examples" / "sample_data",
        data_dir=tmp_path,
        database_url=db_url,
    )
    pipeline = build_pipeline(settings)
    report = pipeline.process_url(DEMO)
    assert report.job_id is not None
    assert report.markdown_path
    assert report.json_path

    store = JobStore(db_url)
    job = store.get_job(report.job_id)
    assert job is not None
    assert job.status is JobStatus.COMPLETED
    assert job.report_id == report.id
    path = store.get_report_json_path(report.id)
    assert path is not None
    assert path.exists()
    assert path.read_text(encoding="utf-8")
