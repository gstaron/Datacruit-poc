from django.db.models import Avg, Count
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from candidates.models import Candidate
from interviews.models import Interview
from jobs.models import Job
from pipeline.models import Application


class DashboardView(APIView):
    """Aggregate recruiting metrics — the API behind the frontend dashboard."""

    def get(self, request):
        applications = Application.objects.all()

        funnel = {
            stage: applications.filter(stage=stage).count()
            for stage, _ in Application.Stage.choices
            if stage != Application.Stage.REJECTED
        }

        source_breakdown = {
            row["source"]: row["count"]
            for row in Candidate.objects.values("source").annotate(count=Count("id"))
        }

        avg_match_score = applications.aggregate(avg=Avg("match_score"))["avg"]

        upcoming_interviews = (
            Interview.objects.filter(status=Interview.Status.SCHEDULED, scheduled_at__gte=timezone.now())
            .select_related("application__candidate", "application__job")
            .order_by("scheduled_at")[:5]
        )

        return Response(
            {
                "open_jobs": Job.objects.filter(status=Job.Status.OPEN).count(),
                "total_candidates": Candidate.objects.count(),
                "offers_extended": applications.filter(
                    stage__in=[Application.Stage.OFFER, Application.Stage.HIRED]
                ).count(),
                "avg_time_to_hire_days": self._avg_time_to_hire_days(applications),
                "avg_match_score": round(avg_match_score) if avg_match_score is not None else 0,
                "funnel": funnel,
                "source_breakdown": source_breakdown,
                "upcoming_interviews": [
                    {
                        "candidate_name": i.application.candidate.name,
                        "job_title": i.application.job.title,
                        "scheduled_at": i.scheduled_at,
                        "interviewer": i.interviewer,
                        "type": i.type,
                    }
                    for i in upcoming_interviews
                ],
            }
        )

    @staticmethod
    def _avg_time_to_hire_days(applications):
        gaps = []
        hired = applications.filter(stage=Application.Stage.HIRED).prefetch_related("stage_events")
        for application in hired:
            events = {e.stage: e.at for e in application.stage_events.all()}
            applied_at = events.get(Application.Stage.APPLIED)
            hired_at = events.get(Application.Stage.HIRED)
            if applied_at and hired_at:
                gaps.append((hired_at - applied_at).days)
        return round(sum(gaps) / len(gaps)) if gaps else None
