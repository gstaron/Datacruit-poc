"""Datacruit AI matching microservice.

Deliberately separate from the Django monolith: this is the shape an
in-house AI inference service takes — FastAPI + SQLAlchemy, backed by
Redis for result caching, reading job requirements straight out of the
same Postgres database Django writes to. No candidate data is ever sent
to a third-party AI API; scoring runs entirely on this process, on our
own infrastructure.
"""

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from core.matching import score_candidate

from .cache import get_cached_score, set_cached_score
from .db import JobRow, get_db

app = FastAPI(
    title="Datacruit AI Matching Service",
    description=(
        "In-house resume/job match scoring. Runs on our own AI cluster — "
        "no external AI API calls, no candidate data leaves our infrastructure."
    ),
    version="1.0.0",
)


class MatchRequest(BaseModel):
    resume_text: str = Field(..., min_length=1)
    skills: list[str] = Field(default_factory=list)


class MatchResponse(BaseModel):
    score: int
    matched_must_have: list[str]
    missing_must_have: list[str]
    matched_nice_to_have: list[str]
    summary: str
    cached: bool


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/jobs/{job_id}/match", response_model=MatchResponse)
def match_candidate_to_job(job_id: int, payload: MatchRequest, db: Session = Depends(get_db)) -> MatchResponse:
    job = db.get(JobRow, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    cached = get_cached_score(job_id, payload.resume_text)
    if cached is not None:
        return MatchResponse(**cached, cached=True)

    breakdown = score_candidate(payload.resume_text, payload.skills, job.must_have or [], job.nice_to_have or [])
    result = breakdown.to_dict()
    set_cached_score(job_id, payload.resume_text, result)
    return MatchResponse(**result, cached=False)
