import pytest

from jobs.models import Job

pytestmark = pytest.mark.django_db


class TestJobModel:
    def test_create_job_with_defaults(self):
        job = Job.objects.create(title="Backend Engineer", department="Engineering", location="Prague")
        assert job.status == Job.Status.OPEN
        assert job.employment_type == Job.EmploymentType.FULL_TIME
        assert job.must_have == []
        assert job.nice_to_have == []
        assert job.created_at is not None

    def test_str_returns_title(self):
        job = Job.objects.create(title="Backend Engineer", department="Engineering", location="Prague")
        assert str(job) == "Backend Engineer"

    def test_must_have_and_nice_to_have_store_lists(self):
        job = Job.objects.create(
            title="Backend Engineer",
            department="Engineering",
            location="Prague",
            must_have=["Python", "Django", "PostgreSQL"],
            nice_to_have=["FastAPI", "SQLAlchemy", "Redis"],
        )
        job.refresh_from_db()
        assert job.must_have == ["Python", "Django", "PostgreSQL"]
        assert job.nice_to_have == ["FastAPI", "SQLAlchemy", "Redis"]

    def test_ordering_is_newest_first(self):
        older = Job.objects.create(title="Older", department="Eng", location="Prague")
        newer = Job.objects.create(title="Newer", department="Eng", location="Prague")
        assert list(Job.objects.all()) == [newer, older]
