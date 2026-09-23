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


@pytest.fixture
def application():
    job = Job.objects.create(title="Backend Engineer", department="Engineering", location="Prague")
    candidate = Candidate.objects.create(name="Jana Novakova", email="jana@example.com", resume_text="x")
    return Application.objects.create(job=job, candidate=candidate)


class TestInterviewAPI:
    def test_create_interview_advances_applied_application_to_screening(self, client, application):
        assert application.stage == Application.Stage.APPLIED
        payload = {
            "application": application.id,
            "scheduled_at": timezone.now().isoformat(),
            "interviewer": "Petr Malek",
            "type": "video",
        }
        response = client.post("/api/interviews/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert Interview.objects.count() == 1

        application.refresh_from_db()
        assert application.stage == Application.Stage.SCREENING

    def test_create_interview_does_not_regress_a_later_stage(self, client, application):
        application.move_to_stage(Application.Stage.INTERVIEW)
        payload = {
            "application": application.id,
            "scheduled_at": timezone.now().isoformat(),
            "interviewer": "Petr Malek",
        }
        client.post("/api/interviews/", payload, format="json")

        application.refresh_from_db()
        assert application.stage == Application.Stage.INTERVIEW

    def test_filter_interviews_by_status(self, client, application):
        Interview.objects.create(
            application=application, scheduled_at=timezone.now(), interviewer="A", status="scheduled"
        )
        Interview.objects.create(
            application=application, scheduled_at=timezone.now(), interviewer="B", status="completed"
        )
        response = client.get("/api/interviews/?status=scheduled")
        assert response.data["count"] == 1
