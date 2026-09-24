import pytest
from django.utils import timezone

from candidates.models import Candidate
from interviews.models import Interview
from jobs.models import Job
from pipeline.models import Application

pytestmark = pytest.mark.django_db


@pytest.fixture
def application():
    job = Job.objects.create(title="Backend Engineer", department="Engineering", location="Prague")
    candidate = Candidate.objects.create(name="Jana Novakova", email="jana@example.com", resume_text="x")
    return Application.objects.create(job=job, candidate=candidate)


class TestInterviewModel:
    def test_create_with_defaults(self, application):
        interview = Interview.objects.create(
            application=application,
            scheduled_at=timezone.now(),
            interviewer="Petr Malek",
        )
        assert interview.type == Interview.Type.VIDEO
        assert interview.status == Interview.Status.SCHEDULED
        assert interview.notes == ""

    def test_str_representation(self, application):
        when = timezone.now()
        interview = Interview.objects.create(
            application=application, scheduled_at=when, interviewer="Petr Malek"
        )
        assert str(interview) == f"{application} interview with Petr Malek"

    def test_ordering_is_by_scheduled_at(self, application):
        later = Interview.objects.create(
            application=application,
            scheduled_at=timezone.now() + timezone.timedelta(days=2),
            interviewer="A",
        )
        sooner = Interview.objects.create(
            application=application,
            scheduled_at=timezone.now() + timezone.timedelta(days=1),
            interviewer="B",
        )
        assert list(Interview.objects.all()) == [sooner, later]
