from rest_framework import serializers

from .models import Evaluation


class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = ["id", "application", "evaluator_name", "rating", "recommendation", "comments", "created_at"]
        read_only_fields = ["id", "created_at"]
