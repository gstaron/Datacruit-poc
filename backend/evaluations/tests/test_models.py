import pytest
from django.core.exceptions import ValidationError

from candidates.models import Candidate
from evaluations.models import Evaluation
from jobs.models import Job
from pipeline.models import Application

pytestmark = pytest.mark.django_db


@pytest.fixture
def application():
    job = Job.objects.create(title="Backend Engineer", department="Engineering", location="Prague")
    candidate = Candidate.objects.create(name="Jana Novakova", email="jana@example.com", resume_text="x")
    return Application.objects.create(job=job, candidate=candidate)


class TestEvaluationModel:
    def test_create_with_defaults(self, application):
        evaluation = Evaluation.objects.create(
            application=application, evaluator_name="Petr Malek", rating=5
        )
        assert evaluation.recommendation == Evaluation.Recommendation.MAYBE
        assert evaluation.comments == ""

    def test_str_representation(self, application):
        evaluation = Evaluation.objects.create(
            application=application, evaluator_name="Petr Malek", rating=5, recommendation=Evaluation.Recommendation.HIRE
        )
        assert str(evaluation) == f"Petr Malek on {application}: hire"

    @pytest.mark.parametrize("rating", [0, 6, -1])
    def test_rating_out_of_range_fails_validation(self, application, rating):
        evaluation = Evaluation(application=application, evaluator_name="Petr Malek", rating=rating)
        with pytest.raises(ValidationError):
            evaluation.full_clean()

    @pytest.mark.parametrize("rating", [1, 3, 5])
    def test_rating_in_range_passes_validation(self, application, rating):
        evaluation = Evaluation(application=application, evaluator_name="Petr Malek", rating=rating)
        evaluation.full_clean()
