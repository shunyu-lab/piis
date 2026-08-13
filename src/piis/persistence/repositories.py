from datetime import UTC, datetime
from pathlib import Path

from piis.ids import new_id
from piis.models.enums import JobStatus
from piis.models.job import Job
from piis.models.report import Report
from piis.persistence.database import create_session_factory
from piis.persistence.models import JobRow, ReportRow


class JobStore:
    """SQLite runtime state for jobs and report metadata only."""

    def __init__(self, database_url: str) -> None:
        self._session = create_session_factory(database_url)

    def create(self, url: str) -> Job:
        job = Job(
            id=new_id("job"),
            url=url,
            status=JobStatus.RUNNING,
            created_at=datetime.now(UTC),
        )
        with self._session() as session:
            session.add(
                JobRow(
                    id=job.id,
                    url=job.url,
                    status=job.status.value,
                    created_at=job.created_at,
                )
            )
            session.commit()
        return job

    def complete(self, job_id: str, report_id: str) -> None:
        with self._session() as session:
            row = session.get(JobRow, job_id)
            if row is None:
                return
            row.status = JobStatus.COMPLETED.value
            row.report_id = report_id
            session.commit()

    def fail(self, job_id: str, error: str) -> None:
        with self._session() as session:
            row = session.get(JobRow, job_id)
            if row is None:
                return
            row.status = JobStatus.FAILED.value
            row.error = error
            session.commit()

    def save_report_meta(self, report: Report) -> None:
        if not report.markdown_path or not report.json_path:
            return
        with self._session() as session:
            session.merge(
                ReportRow(
                    id=report.id,
                    job_id=report.job_id,
                    content_id=report.content.id,
                    path_md=report.markdown_path,
                    path_json=report.json_path,
                    created_at=report.created_at,
                )
            )
            session.commit()

    def get_report_json_path(self, report_id: str) -> Path | None:
        with self._session() as session:
            row = session.get(ReportRow, report_id)
            if row is None:
                return None
            return Path(row.path_json)

    def get_job(self, job_id: str) -> Job | None:
        with self._session() as session:
            row = session.get(JobRow, job_id)
            if row is None:
                return None
            return Job(
                id=row.id,
                url=row.url,
                status=JobStatus(row.status),
                report_id=row.report_id,
                error=row.error,
                created_at=row.created_at,
            )
