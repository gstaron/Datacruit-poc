from rest_framework import viewsets

from .models import Evaluation
from .serializers import EvaluationSerializer


class EvaluationViewSet(viewsets.ModelViewSet):
    queryset = Evaluation.objects.select_related("application")
    serializer_class = EvaluationSerializer
    filterset_fields = ["application", "recommendation"]
