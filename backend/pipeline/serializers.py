from rest_framework import serializers

from candidates.models import Candidate
from candidates.serializers import CandidateSerializer
from jobs.models import Job
from jobs.serializers import JobSerializer

from .models import Application


class StageEventSerializer(serializers.Serializer):
    stage = serializers.CharField()
    at = serializers.DateTimeField()


class ApplicationSerializer(serializers.ModelSerializer):
    candidate = CandidateSerializer(read_only=True)
    job = JobSerializer(read_only=True)
    job_id = serializers.PrimaryKeyRelatedField(source="job", queryset=Job.objects.all(), write_only=True)
    candidate_id = serializers.PrimaryKeyRelatedField(
        source="candidate", queryset=Candidate.objects.all(), write_only=True
    )
    stage_history = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            "id", "job", "candidate", "job_id", "candidate_id", "stage",
            "match_score", "matched_must_have", "missing_must_have",
            "matched_nice_to_have", "match_summary", "stage_history",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "stage", "match_score", "matched_must_have", "missing_must_have",
            "matched_nice_to_have", "match_summary", "created_at", "updated_at",
        ]

    def get_stage_history(self, obj: Application) -> list[dict]:
        return StageEventSerializer(obj.stage_events.all(), many=True).data


class MoveStageSerializer(serializers.Serializer):
    stage = serializers.ChoiceField(choices=Application.Stage.choices)


class ApplyToJobSerializer(serializers.Serializer):
    """Input for `POST /api/jobs/<id>/apply/` — a candidate applying to a job.

    Triggers automatic, in-house AI resume parsing + match scoring
    (see core.matching) rather than accepting a pre-computed score from
    the client.
    """

    name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=40, required=False, allow_blank=True, default="")
    source = serializers.ChoiceField(choices=Candidate.Source.choices, default=Candidate.Source.CAREER_SITE)
    experience_years = serializers.IntegerField(min_value=0, default=0)
    resume_text = serializers.CharField()
