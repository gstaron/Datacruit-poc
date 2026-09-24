import pytest
from rest_framework import status
from rest_framework.test import APIClient

from candidates.models import Candidate
from jobs.models import Job
from pipeline.models import Application

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


class TestJobAPI:
    def test_list_jobs(self, client):
        Job.objects.create(title="Backend Engineer", department="Engineering", location="Prague")
        response = client.get("/api/jobs/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_create_job(self, client):
        payload = {
            "title": "Python Developer",
            "department": "Engineering",
            "location": "Prague",
            "employment_type": "full_time",
            "must_have": ["Python", "Django", "PostgreSQL"],
            "nice_to_have": ["FastAPI", "SQLAlchemy", "Redis"],
        }
        response = client.post("/api/jobs/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert Job.objects.count() == 1
        assert Job.objects.get().must_have == ["Python", "Django", "PostgreSQL"]

    def test_retrieve_job(self, client):
        job = Job.objects.create(title="Backend Engineer", department="Engineering", location="Prague")
        response = client.get(f"/api/jobs/{job.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Backend Engineer"

    def test_update_job_status(self, client):
        job = Job.objects.create(title="Backend Engineer", department="Engineering", location="Prague")
        response = client.patch(f"/api/jobs/{job.id}/", {"status": "closed"}, format="json")
        assert response.status_code == status.HTTP_200_OK
        job.refresh_from_db()
        assert job.status == "closed"

    def test_delete_job(self, client):
        job = Job.objects.create(title="Backend Engineer", department="Engineering", location="Prague")
        response = client.delete(f"/api/jobs/{job.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Job.objects.count() == 0

    def test_updating_requirements_triggers_async_recompute_of_existing_applications(
        self, client, settings
    ):
        settings.CELERY_TASK_ALWAYS_EAGER = True
        job = Job.objects.create(
            title="Backend Engineer",
            department="Engineering",
            location="Prague",
            must_have=["Python"],
        )
        candidate = Candidate.objects.create(
            name="A", email="a@example.com", resume_text="Python and Django developer."
        )
        application = Application.objects.create(job=job, candidate=candidate)
        assert application.match_score == 0

        response = client.patch(
            f"/api/jobs/{job.id}/", {"must_have": ["Python", "Django"]}, format="json"
        )
        assert response.status_code == status.HTTP_200_OK

        application.refresh_from_db()
        assert application.match_score == 100

    def test_updating_unrelated_field_does_not_touch_applications(self, client, settings):
        settings.CELERY_TASK_ALWAYS_EAGER = True
        job = Job.objects.create(
            title="Backend Engineer", department="Engineering", location="Prague", must_have=["Python"]
        )
        candidate = Candidate.objects.create(name="A", email="a@example.com", resume_text="Painter.")
        application = Application.objects.create(job=job, candidate=candidate)
        application.match_score = 42
        application.save(update_fields=["match_score"])

        client.patch(f"/api/jobs/{job.id}/", {"location": "Remote"}, format="json")

        application.refresh_from_db()
        assert application.match_score == 42  # untouched — no requirements change

    def test_filter_by_status(self, client):
        Job.objects.create(title="Open role", department="Eng", location="Prague", status="open")
        Job.objects.create(title="Closed role", department="Eng", location="Prague", status="closed")
        response = client.get("/api/jobs/?status=open")
        assert response.data["count"] == 1
        assert response.data["results"][0]["title"] == "Open role"
