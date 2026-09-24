import pytest
from rest_framework import status
from rest_framework.test import APIClient

from candidates.models import Candidate
from evaluations.models import Evaluation
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


class TestEvaluationAPI:
    def test_create_evaluation(self, client, application):
        payload = {
            "application": application.id,
            "evaluator_name": "Petr Malek",
            "rating": 5,
            "recommendation": "hire",
            "comments": "Great system design round.",
        }
        response = client.post("/api/evaluations/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert Evaluation.objects.count() == 1

    @pytest.mark.parametrize("rating", [0, 6])
    def test_rating_out_of_range_returns_400(self, client, application, rating):
        payload = {
            "application": application.id,
            "evaluator_name": "Petr Malek",
            "rating": rating,
        }
        response = client.post("/api/evaluations/", payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "rating" in response.data

    def test_filter_evaluations_by_application(self, client, application):
        Evaluation.objects.create(application=application, evaluator_name="A", rating=4)
        response = client.get(f"/api/evaluations/?application={application.id}")
        assert response.data["count"] == 1
