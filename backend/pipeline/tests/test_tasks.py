import pytest
from django.core.cache import cache

from candidates.models import Candidate
from jobs.models import Job
from pipeline.models import Application
from pipeline.tasks import match_score_cache_key, recompute_job_matches

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def job():
    return Job.objects.create(
        title="Backend Engineer",
        department="Engineering",
        location="Prague",
        must_have=["Python", "Django", "PostgreSQL"],
        nice_to_have=["Redis"],
    )


class TestRecomputeJobMatches:
    def test_updates_match_score_for_every_application_on_the_job(self, job):
        candidate = Candidate.objects.create(
            name="Jana Novakova",
            email="jana@example.com",
            resume_text="Python and Django developer.",
        )
        application = Application.objects.create(job=job, candidate=candidate)
        assert application.match_score == 0  # never scored yet

        updated = recompute_job_matches(job.id)

        assert updated == 1
        application.refresh_from_db()
        assert application.match_score > 0
        assert application.matched_must_have == ["Python", "Django"]
        assert application.missing_must_have == ["PostgreSQL"]

    def test_caches_the_breakdown_in_redis(self, job):
        candidate = Candidate.objects.create(
            name="Jana Novakova", email="jana@example.com", resume_text="Python and Django developer."
        )
        application = Application.objects.create(job=job, candidate=candidate)

        recompute_job_matches(job.id)
        application.refresh_from_db()

        cached = cache.get(match_score_cache_key(application.id))
        assert cached is not None
        assert cached["score"] == application.match_score

    def test_returns_zero_for_a_job_that_no_longer_exists(self):
        assert recompute_job_matches(999999) == 0

    def test_returns_zero_when_job_has_no_applications(self, job):
        assert recompute_job_matches(job.id) == 0
