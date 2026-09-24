from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from candidates.models import Candidate
from interviews.models import Interview
from jobs.models import Job
from pipeline.models import Application

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


class TestDashboardAPI:
    def test_empty_state(self, client):
        response = client.get("/api/dashboard/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["open_jobs"] == 0
        assert response.data["total_candidates"] == 0
        assert response.data["offers_extended"] == 0
        assert response.data["avg_time_to_hire_days"] is None
        assert response.data["avg_match_score"] == 0
        assert response.data["funnel"]["applied"] == 0
        assert response.data["source_breakdown"] == {}
        assert response.data["upcoming_interviews"] == []

    def test_counts_and_funnel(self, client):
        open_job = Job.objects.create(title="Open", department="Eng", location="Prague", status="open")
        Job.objects.create(title="Closed", department="Eng", location="Prague", status="closed")

        c1 = Candidate.objects.create(name="A", email="a@example.com", resume_text="x", source="linkedin")
        c2 = Candidate.objects.create(name="B", email="b@example.com", resume_text="x", source="linkedin")
        c3 = Candidate.objects.create(name="C", email="c@example.com", resume_text="x", source="referral")

        app1 = Application.objects.create(job=open_job, candidate=c1)
        app1.match_score = 80
        app1.save(update_fields=["match_score"])
        app1.move_to_stage(Application.Stage.SCREENING)

        app2 = Application.objects.create(job=open_job, candidate=c2)
        app2.match_score = 60
        app2.save(update_fields=["match_score"])
        app2.move_to_stage(Application.Stage.OFFER)

        Application.objects.create(job=open_job, candidate=c3)

        response = client.get("/api/dashboard/")
        assert response.data["open_jobs"] == 1
        assert response.data["total_candidates"] == 3
        assert response.data["offers_extended"] == 1
        assert response.data["avg_match_score"] == 47  # (80 + 60 + 0) / 3 rounded
        assert response.data["funnel"]["applied"] == 1
        assert response.data["funnel"]["screening"] == 1
        assert response.data["funnel"]["offer"] == 1
        assert response.data["source_breakdown"] == {"linkedin": 2, "referral": 1}

    def test_avg_time_to_hire_uses_applied_to_hired_gap(self, client):
        job = Job.objects.create(title="Backend", department="Eng", location="Prague")
        candidate = Candidate.objects.create(name="A", email="a@example.com", resume_text="x")
        application = Application.objects.create(job=job, candidate=candidate)

        first_event = application.stage_events.first()
        first_event.at = timezone.now() - timedelta(days=10)
        first_event.save(update_fields=["at"])

        application.move_to_stage(Application.Stage.HIRED)

        response = client.get("/api/dashboard/")
        assert response.data["avg_time_to_hire_days"] == 10

    def test_avg_time_to_hire_skips_hired_applications_with_incomplete_history(self, client):
        # Defensive case: historical/migrated data might be missing its
        # "applied" stage event. The average should just skip it rather
        # than crashing.
        job = Job.objects.create(title="Backend", department="Eng", location="Prague")
        candidate = Candidate.objects.create(name="A", email="a@example.com", resume_text="x")
        application = Application.objects.create(job=job, candidate=candidate)
        application.stage_events.filter(stage=Application.Stage.APPLIED).delete()
        application.move_to_stage(Application.Stage.HIRED)

        response = client.get("/api/dashboard/")
        assert response.data["avg_time_to_hire_days"] is None

    def test_upcoming_interviews_excludes_past_and_non_scheduled(self, client):
        job = Job.objects.create(title="Backend", department="Eng", location="Prague")
        candidate = Candidate.objects.create(name="A", email="a@example.com", resume_text="x")
        application = Application.objects.create(job=job, candidate=candidate)

        Interview.objects.create(
            application=application,
            scheduled_at=timezone.now() + timedelta(days=1),
            interviewer="Petr Malek",
            status="scheduled",
        )
        Interview.objects.create(
            application=application,
            scheduled_at=timezone.now() - timedelta(days=1),
            interviewer="Past",
            status="scheduled",
        )
        Interview.objects.create(
            application=application,
            scheduled_at=timezone.now() + timedelta(days=2),
            interviewer="Cancelled",
            status="cancelled",
        )

        response = client.get("/api/dashboard/")
        assert len(response.data["upcoming_interviews"]) == 1
        assert response.data["upcoming_interviews"][0]["interviewer"] == "Petr Malek"
        assert response.data["upcoming_interviews"][0]["candidate_name"] == "A"
        assert response.data["upcoming_interviews"][0]["job_title"] == "Backend"
