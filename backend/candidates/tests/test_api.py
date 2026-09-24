import pytest
from rest_framework import status
from rest_framework.test import APIClient

from candidates.models import Candidate

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


class TestCandidateAPI:
    def test_list_candidates(self, client):
        Candidate.objects.create(name="Jana Novakova", email="jana@example.com", resume_text="x")
        response = client.get("/api/candidates/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_create_candidate(self, client):
        payload = {
            "name": "Jana Novakova",
            "email": "jana@example.com",
            "resume_text": "Python and Django developer.",
            "source": "linkedin",
            "experience_years": 4,
        }
        response = client.post("/api/candidates/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert Candidate.objects.count() == 1

    def test_skills_field_is_read_only(self, client):
        payload = {
            "name": "Jana Novakova",
            "email": "jana@example.com",
            "resume_text": "x",
            "skills": ["Python"],
        }
        response = client.post("/api/candidates/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert Candidate.objects.get().skills == []

    def test_filter_by_source(self, client):
        Candidate.objects.create(name="A", email="a@example.com", resume_text="x", source="linkedin")
        Candidate.objects.create(name="B", email="b@example.com", resume_text="x", source="referral")
        response = client.get("/api/candidates/?source=linkedin")
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "A"
