"""Runtime job metadata. Stored in SQLite, not in the knowledge JSON stores."""

from datetime import datetime

from pydantic import BaseModel

from piis.models.enums import JobStatus


class Job(BaseModel):
    id: str
    url: str
    status: JobStatus
    report_id: str | None = None
    error: str | None = None
    created_at: datetime
