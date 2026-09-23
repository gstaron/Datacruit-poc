import pytest
from rest_framework import status
from rest_framework.test import APIClient

from jobs.models import Job

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


class TestMatchScoreAPI:
    def test_score_with_explicit_requirements(self, client):
        payload = {
            "resume_text": "Python and Django developer with PostgreSQL experience.",
            "must_have": ["Python", "Django", "PostgreSQL"],
            "nice_to_have": ["Redis"],
        }
        response = client.post("/api/matching/score/", payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["score"] == 75
        assert response.data["matched_must_have"] == ["Python", "Django", "PostgreSQL"]

    def test_score_against_a_stored_job(self, client):
        job = Job.objects.create(
            title="Backend Engineer",
            department="Engineering",
            location="Prague",
            must_have=["Python", "Django"],
            nice_to_have=["Redis"],
        )
        response = client.post(
            "/api/matching/score/",
            {"resume_text": "Python and Django developer, also used Redis.", "job_id": job.id},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["score"] == 100

    def test_missing_job_returns_404(self, client):
        response = client.post(
            "/api/matching/score/",
            {"resume_text": "Python developer.", "job_id": 999999},
            format="json",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_missing_resume_text_returns_400(self, client):
        response = client.post("/api/matching/score/", {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "resume_text" in response.data
