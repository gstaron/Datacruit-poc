"""Celery tasks for the pipeline app.

Dispatched through Redis (the Celery broker — see config.settings) so
recomputation doesn't block the request/response cycle when a job's
requirements change.
"""

import logging

from django.core.cache import cache

from config.celery import app
from core.matching import score_candidate

logger = logging.getLogger(__name__)

MATCH_SCORE_CACHE_TTL_SECONDS = 60 * 60


def match_score_cache_key(application_id: int) -> str:
    return f"match-score:{application_id}"


@app.task(name="pipeline.recompute_job_matches")
def recompute_job_matches(job_id: int) -> int:
    """Recompute the AI match score for every application on a job.

    Called after a job's must-have/nice-to-have requirements change, so
    existing applications reflect the new requirements without asking
    candidates to re-apply. Returns the number of applications updated.
    """
    from jobs.models import Job
    from pipeline.models import Application

    try:
        job = Job.objects.get(pk=job_id)
    except Job.DoesNotExist:
        logger.warning("recompute_job_matches: job %s no longer exists", job_id)
        return 0

    updated = 0
    for application in Application.objects.filter(job=job).select_related("candidate"):
        breakdown = score_candidate(
            application.candidate.resume_text,
            application.candidate.skills,
            job.must_have,
            job.nice_to_have,
        )
        application.apply_match(breakdown)
        application.save(
            update_fields=[
                "match_score",
                "matched_must_have",
                "missing_must_have",
                "matched_nice_to_have",
                "match_summary",
                "updated_at",
            ]
        )
        cache.set(match_score_cache_key(application.id), breakdown.to_dict(), MATCH_SCORE_CACHE_TTL_SECONDS)
        updated += 1

    return updated
