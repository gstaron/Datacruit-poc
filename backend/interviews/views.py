from rest_framework import viewsets

from pipeline.models import Application

from .models import Interview
from .serializers import InterviewSerializer


class InterviewViewSet(viewsets.ModelViewSet):
    queryset = Interview.objects.select_related("application")
    serializer_class = InterviewSerializer
    filterset_fields = ["application", "status", "type"]

    def perform_create(self, serializer):
        interview = serializer.save()
        application = interview.application
        if application.stage == Application.Stage.APPLIED:
            application.move_to_stage(Application.Stage.SCREENING)
