from rest_framework import serializers

from .models import Candidate


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = [
            "id", "name", "email", "phone", "source", "resume_text",
            "skills", "experience_years", "created_at",
        ]
        read_only_fields = ["id", "skills", "created_at"]
