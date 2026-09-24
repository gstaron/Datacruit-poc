from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from jobs.models import Job

from .matching import score_candidate
from .serializers import MatchScoreRequestSerializer


class MatchScoreView(APIView):
    """`POST /api/matching/score/` — ad-hoc, explainable AI match scoring.

    Runs entirely in-process (see core.matching) rather than calling an
    external AI provider, so resume text never leaves our infrastructure.
    """

    def post(self, request):
        serializer = MatchScoreRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        must_have = data["must_have"]
        nice_to_have = data["nice_to_have"]
        if data.get("job_id"):
            job = get_object_or_404(Job, pk=data["job_id"])
            must_have = job.must_have
            nice_to_have = job.nice_to_have

        breakdown = score_candidate(data["resume_text"], [], must_have, nice_to_have)
        return Response(breakdown.to_dict())
