import pytest
from fastapi.testclient import TestClient

from ai_service.main import app
from jobs.models import Job

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def client():
    return TestClient(app)


class TestHealth:
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestMatchEndpoint:
    def test_returns_404_for_unknown_job(self, client):
        response = client.post("/jobs/999999/match", json={"resume_text": "Python developer."})
        assert response.status_code == 404

    def test_computes_score_against_stored_job_requirements(self, client):
        job = Job.objects.create(
            title="Backend Engineer",
            department="Engineering",
            location="Prague",
            must_have=["Python", "Django", "PostgreSQL"],
            nice_to_have=["FastAPI", "SQLAlchemy", "Redis"],
        )

        response = client.post(
            f"/jobs/{job.id}/match",
            json={"resume_text": "Python and Django developer with PostgreSQL, FastAPI, SQLAlchemy and Redis skills."},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["score"] == 100
        assert set(data["matched_must_have"]) == {"Python", "Django", "PostgreSQL"}
        assert data["cached"] is False

    def test_second_identical_request_is_served_from_cache(self, client):
        job = Job.objects.create(
            title="Backend Engineer", department="Engineering", location="Prague", must_have=["Python"]
        )
        payload = {"resume_text": "Python developer."}

        first = client.post(f"/jobs/{job.id}/match", json=payload)
        second = client.post(f"/jobs/{job.id}/match", json=payload)

        assert first.json()["cached"] is False
        assert second.json()["cached"] is True
        assert second.json()["score"] == first.json()["score"]

    def test_missing_resume_text_returns_422(self, client):
        job = Job.objects.create(title="Backend Engineer", department="Engineering", location="Prague")
        response = client.post(f"/jobs/{job.id}/match", json={})
        assert response.status_code == 422

    def test_empty_resume_text_returns_422(self, client):
        job = Job.objects.create(title="Backend Engineer", department="Engineering", location="Prague")
        response = client.post(f"/jobs/{job.id}/match", json={"resume_text": ""})
        assert response.status_code == 422
