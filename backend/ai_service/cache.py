"""Redis-backed cache for computed match results.

Uses redis-py directly (rather than Django's cache framework) since this
service runs as its own process. Isolated onto its own logical DB index
so it never collides with the Django app's cache keys on the same Redis
instance.
"""

import hashlib
import json
import os
from functools import lru_cache

import redis

CACHE_TTL_SECONDS = 60 * 60


def _redis_url() -> str:
    return os.environ.get("AI_SERVICE_REDIS_URL", "redis://localhost:6379/2")


@lru_cache
def get_client() -> "redis.Redis":
    return redis.from_url(_redis_url(), decode_responses=True)


def _cache_key(job_id: int, resume_text: str) -> str:
    digest = hashlib.sha256(resume_text.encode("utf-8")).hexdigest()
    return f"ai-match:{job_id}:{digest}"


def get_cached_score(job_id: int, resume_text: str) -> dict | None:
    raw = get_client().get(_cache_key(job_id, resume_text))
    return json.loads(raw) if raw else None


def set_cached_score(job_id: int, resume_text: str, result: dict) -> None:
    get_client().set(_cache_key(job_id, resume_text), json.dumps(result), ex=CACHE_TTL_SECONDS)
