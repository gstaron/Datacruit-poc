from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from candidates.models import Candidate
from core.matching import score_candidate
from jobs.models import Job

from .models import Application
from .serializers import ApplicationSerializer, ApplyToJobSerializer, MoveStageSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.select_related("job", "candidate").prefetch_related("stage_events")
    serializer_class = ApplicationSerializer
    filterset_fields = ["job", "stage", "candidate"]

    @action(detail=True, methods=["post"], url_path="move-stage")
    def move_stage(self, request, pk=None):
        application = self.get_object()
        serializer = MoveStageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application.move_to_stage(serializer.validated_data["stage"])
        # get_object()'s queryset prefetches stage_events; move_to_stage()
        # just inserted a new one via the related manager, which does not
        # update that cache, so reload before serializing the fresh state.
        application.refresh_from_db()
        return Response(ApplicationSerializer(application).data)


class ApplyToJobView(APIView):
    """`POST /api/jobs/<job_id>/apply/` — apply to a job and get an
    instant, explainable AI match score back, computed entirely
    in-process (see core.matching)."""

    def post(self, request, job_id):
        job = get_object_or_404(Job, pk=job_id)
        serializer = ApplyToJobSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        breakdown = score_candidate(data["resume_text"], [], job.must_have, job.nice_to_have)
        skills = list(dict.fromkeys(breakdown.matched_must_have + breakdown.matched_nice_to_have))

        candidate = Candidate.objects.create(
            name=data["name"],
            email=data["email"],
            phone=data.get("phone", ""),
            source=data["source"],
            resume_text=data["resume_text"],
            skills=skills,
            experience_years=data["experience_years"],
        )
        application = Application.objects.create(job=job, candidate=candidate)
        application.apply_match(breakdown)
        application.save()

        return Response(ApplicationSerializer(application).data, status=201)
