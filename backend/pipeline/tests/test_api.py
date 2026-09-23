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


@pytest.fixture
def job():
    return Job.objects.create(
        title="Python Developer",
        department="Engineering",
        location="Prague",
        must_have=["Python", "Django", "PostgreSQL"],
        nice_to_have=["FastAPI", "SQLAlchemy", "Redis"],
    )


class TestApplyToJob:
    def test_apply_creates_candidate_and_scored_application(self, client, job):
        payload = {
            "name": "Jana Novakova",
            "email": "jana@example.com",
            "phone": "+420 601 111 222",
            "source": "linkedin",
            "experience_years": 5,
            "resume_text": "Python and Django developer with hands-on PostgreSQL, FastAPI, SQLAlchemy and Redis experience.",
        }
        response = client.post(f"/api/jobs/{job.id}/apply/", payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert Candidate.objects.count() == 1
        assert Application.objects.count() == 1

        data = response.data
        assert data["stage"] == "applied"
        assert data["match_score"] == 100
        assert set(data["matched_must_have"]) == {"Python", "Django", "PostgreSQL"}
        assert data["candidate"]["name"] == "Jana Novakova"
        assert data["job"]["title"] == "Python Developer"

    def test_apply_computes_partial_score_for_weak_resume(self, client, job):
        payload = {
            "name": "Weak Candidate",
            "email": "weak@example.com",
            "resume_text": "Experienced oil painter and muralist.",
        }
        response = client.post(f"/api/jobs/{job.id}/apply/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["match_score"] == 0

    def test_apply_to_missing_job_returns_404(self, client):
        response = client.post(
            "/api/jobs/999999/apply/",
            {"name": "A", "email": "a@example.com", "resume_text": "x"},
            format="json",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_apply_without_required_fields_returns_400(self, client, job):
        response = client.post(f"/api/jobs/{job.id}/apply/", {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data
        assert "email" in response.data
        assert "resume_text" in response.data


class TestApplicationAPI:
    def test_list_applications(self, client, job):
        candidate = Candidate.objects.create(name="A", email="a@example.com", resume_text="x")
        Application.objects.create(job=job, candidate=candidate)
        response = client.get("/api/applications/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_filter_applications_by_job_and_stage(self, client, job):
        candidate = Candidate.objects.create(name="A", email="a@example.com", resume_text="x")
        Application.objects.create(job=job, candidate=candidate)
        response = client.get(f"/api/applications/?job={job.id}&stage=applied")
        assert response.data["count"] == 1

        response = client.get(f"/api/applications/?job={job.id}&stage=hired")
        assert response.data["count"] == 0

    def test_move_stage_action(self, client, job):
        candidate = Candidate.objects.create(name="A", email="a@example.com", resume_text="x")
        application = Application.objects.create(job=job, candidate=candidate)

        response = client.post(
            f"/api/applications/{application.id}/move-stage/", {"stage": "screening"}, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["stage"] == "screening"
        assert [e["stage"] for e in response.data["stage_history"]] == ["applied", "screening"]

    def test_move_stage_rejects_invalid_stage(self, client, job):
        candidate = Candidate.objects.create(name="A", email="a@example.com", resume_text="x")
        application = Application.objects.create(job=job, candidate=candidate)

        response = client.post(
            f"/api/applications/{application.id}/move-stage/", {"stage": "not-a-stage"}, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_application_directly_succeeds_when_no_conflict(self, client, job):
        candidate = Candidate.objects.create(name="A", email="a@example.com", resume_text="x")
        response = client.post(
            "/api/applications/", {"job_id": job.id, "candidate_id": candidate.id}, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_updating_an_application_excludes_itself_from_the_duplicate_check(self, client, job):
        candidate = Candidate.objects.create(name="A", email="a@example.com", resume_text="x")
        application = Application.objects.create(job=job, candidate=candidate)

        response = client.patch(
            f"/api/applications/{application.id}/",
            {"job_id": job.id, "candidate_id": candidate.id},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK

    def test_empty_partial_update_skips_the_duplicate_check(self, client, job):
        candidate = Candidate.objects.create(name="A", email="a@example.com", resume_text="x")
        application = Application.objects.create(job=job, candidate=candidate)

        response = client.patch(f"/api/applications/{application.id}/", {}, format="json")
        assert response.status_code == status.HTTP_200_OK

    def test_duplicate_application_returns_400_not_500(self, client, job):
        candidate = Candidate.objects.create(name="A", email="a@example.com", resume_text="x")
        Application.objects.create(job=job, candidate=candidate)

        response = client.post(
            "/api/applications/",
            {"job_id": job.id, "candidate_id": candidate.id},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
