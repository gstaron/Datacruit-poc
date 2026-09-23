from django.db import models

from core.matching import MatchBreakdown


class Application(models.Model):
    """A candidate's application to a job — the pipeline/kanban card."""

    class Stage(models.TextChoices):
        APPLIED = "applied", "Applied"
        SCREENING = "screening", "Screening"
        INTERVIEW = "interview", "Interview"
        OFFER = "offer", "Offer"
        HIRED = "hired", "Hired"
        REJECTED = "rejected", "Rejected"

    job = models.ForeignKey("jobs.Job", related_name="applications", on_delete=models.CASCADE)
    candidate = models.ForeignKey(
        "candidates.Candidate", related_name="applications", on_delete=models.CASCADE
    )
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.APPLIED)

    match_score = models.PositiveSmallIntegerField(default=0)
    matched_must_have = models.JSONField(default=list, blank=True)
    missing_must_have = models.JSONField(default=list, blank=True)
    matched_nice_to_have = models.JSONField(default=list, blank=True)
    match_summary = models.CharField(max_length=200, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["job", "candidate"], name="unique_application_per_job_candidate")
        ]
        ordering = ["-match_score", "-created_at"]

    def __str__(self) -> str:
        return f"{self.candidate} -> {self.job} ({self.stage})"

    def save(self, *args, **kwargs) -> None:
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            self.stage_events.create(stage=self.stage)

    def apply_match(self, breakdown: MatchBreakdown) -> None:
        """Copy a computed :class:`MatchBreakdown` onto this application."""
        self.match_score = breakdown.score
        self.matched_must_have = breakdown.matched_must_have
        self.missing_must_have = breakdown.missing_must_have
        self.matched_nice_to_have = breakdown.matched_nice_to_have
        self.match_summary = breakdown.summary

    def move_to_stage(self, stage: str) -> None:
        """Update the pipeline stage and append a :class:`StageEvent`, unless unchanged."""
        if stage == self.stage and self.stage_events.exists():
            return
        self.stage = stage
        self.save(update_fields=["stage", "updated_at"])
        self.stage_events.create(stage=stage)


class StageEvent(models.Model):
    """One timestamped stage transition, used for pipeline/time-to-hire analytics."""

    application = models.ForeignKey(Application, related_name="stage_events", on_delete=models.CASCADE)
    stage = models.CharField(max_length=20, choices=Application.Stage.choices)
    at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["at"]

    def __str__(self) -> str:
        return f"{self.application} @ {self.stage}"
