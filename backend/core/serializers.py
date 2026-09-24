from rest_framework import serializers


class MatchScoreRequestSerializer(serializers.Serializer):
    """Either pass `job_id` to score against a stored job's requirements,
    or pass `must_have`/`nice_to_have` directly for an ad-hoc score."""

    resume_text = serializers.CharField()
    job_id = serializers.IntegerField(required=False, allow_null=True)
    must_have = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    nice_to_have = serializers.ListField(child=serializers.CharField(), required=False, default=list)
