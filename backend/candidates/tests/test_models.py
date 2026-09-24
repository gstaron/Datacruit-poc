import pytest

from candidates.models import Candidate

pytestmark = pytest.mark.django_db


class TestCandidateModel:
    def test_create_candidate_with_defaults(self):
        candidate = Candidate.objects.create(
            name="Elena Novak", email="elena@example.com", resume_text="Python developer."
        )
        assert candidate.source == Candidate.Source.CAREER_SITE
        assert candidate.experience_years == 0
        assert candidate.skills == []

    def test_str_returns_name(self):
        candidate = Candidate.objects.create(name="Elena Novak", email="elena@example.com", resume_text="x")
        assert str(candidate) == "Elena Novak"

    def test_skills_stores_list(self):
        candidate = Candidate.objects.create(
            name="Elena Novak",
            email="elena@example.com",
            resume_text="Python, Django",
            skills=["Python", "Django"],
        )
        candidate.refresh_from_db()
        assert candidate.skills == ["Python", "Django"]
