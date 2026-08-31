import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

from piis import __version__
from piis.config.settings import Settings
from piis.runtime import build_pipeline

settings = Settings()
pipeline = build_pipeline(settings)
app = FastAPI(
    title="PIIS",
    version=__version__,
    description="Personal Information Intelligence System",
)


class ProcessRequest(BaseModel):
    url: HttpUrl


class ProcessResponse(BaseModel):
    job_id: str
    status: str
    report_id: str


@app.get("/")
def root() -> dict[str, str]:
    return {"name": "PIIS", "version": __version__}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/process", response_model=ProcessResponse)
def process(body: ProcessRequest) -> ProcessResponse:
    report = pipeline.process_url(str(body.url))
    return ProcessResponse(
        job_id=report.job_id or "",
        status="completed",
        report_id=report.id,
    )


@app.get("/reports/{report_id}")
def get_report(report_id: str) -> dict:
    path = pipeline.report_json_path(report_id)
    if path is None or not path.exists():
        raise HTTPException(status_code=404, detail="report not found")
    return json.loads(path.read_text(encoding="utf-8"))
