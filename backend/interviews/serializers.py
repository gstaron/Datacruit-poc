from rest_framework import serializers

from .models import Interview


class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ["id", "application", "scheduled_at", "interviewer", "type", "status", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]
