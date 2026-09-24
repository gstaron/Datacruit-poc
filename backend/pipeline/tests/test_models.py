import pytest
from django.db import IntegrityError

from candidates.models import Candidate
from core.matching import MatchBreakdown
from jobs.models import Job
from pipeline.models import Application, StageEvent

pytestmark = pytest.mark.django_db


@pytest.fixture
def job():
    return Job.objects.create(
        title="Backend Engineer",
        department="Engineering",
        location="Prague",
        must_have=["Python", "Django", "PostgreSQL"],
        nice_to_have=["FastAPI", "Redis"],
    )


@pytest.fixture
def candidate():
    return Candidate.objects.create(
        name="Jana Novakova", email="jana@example.com", resume_text="Python and Django developer."
    )


class TestApplicationModel:
    def test_create_defaults_to_applied_stage(self, job, candidate):
        application = Application.objects.create(job=job, candidate=candidate)
        assert application.stage == Application.Stage.APPLIED
        assert application.match_score == 0

    def test_creating_application_logs_initial_stage_event(self, job, candidate):
        application = Application.objects.create(job=job, candidate=candidate)
        events = list(application.stage_events.order_by("at"))
        assert len(events) == 1
        assert events[0].stage == Application.Stage.APPLIED

    def test_one_application_per_job_candidate_pair(self, job, candidate):
        Application.objects.create(job=job, candidate=candidate)
        with pytest.raises(IntegrityError):
            Application.objects.create(job=job, candidate=candidate)

    def test_apply_match_stores_breakdown_fields(self, job, candidate):
        application = Application.objects.create(job=job, candidate=candidate)
        breakdown = MatchBreakdown(
            score=80,
            matched_must_have=["Python", "Django"],
            missing_must_have=["PostgreSQL"],
            matched_nice_to_have=["Redis"],
            summary="Strong match.",
        )
        application.apply_match(breakdown)
        application.save()
        application.refresh_from_db()
        assert application.match_score == 80
        assert application.matched_must_have == ["Python", "Django"]
        assert application.missing_must_have == ["PostgreSQL"]
        assert application.matched_nice_to_have == ["Redis"]
        assert application.match_summary == "Strong match."

    def test_move_to_stage_updates_stage_and_logs_event(self, job, candidate):
        application = Application.objects.create(job=job, candidate=candidate)
        application.move_to_stage(Application.Stage.SCREENING)
        assert application.stage == Application.Stage.SCREENING
        stages = list(application.stage_events.order_by("at").values_list("stage", flat=True))
        assert stages == [Application.Stage.APPLIED, Application.Stage.SCREENING]

    def test_move_to_same_stage_does_not_duplicate_event(self, job, candidate):
        application = Application.objects.create(job=job, candidate=candidate)
        application.move_to_stage(Application.Stage.APPLIED)
        assert application.stage_events.count() == 1

    def test_str_representation(self, job, candidate):
        application = Application.objects.create(job=job, candidate=candidate)
        assert str(application) == "Jana Novakova -> Backend Engineer (applied)"


class TestStageEventModel:
    def test_str_representation(self, job, candidate):
        application = Application.objects.create(job=job, candidate=candidate)
        event = application.stage_events.first()
        assert str(event) == f"{application} @ applied"
