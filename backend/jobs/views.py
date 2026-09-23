from rest_framework import viewsets

from pipeline.tasks import recompute_job_matches

from .models import Job
from .serializers import JobSerializer


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    filterset_fields = ["status", "department", "employment_type"]

    def perform_update(self, serializer):
        requirements_changed = (
            "must_have" in serializer.validated_data or "nice_to_have" in serializer.validated_data
        )
        job = serializer.save()
        if requirements_changed:
            recompute_job_matches.delay(job.id)
