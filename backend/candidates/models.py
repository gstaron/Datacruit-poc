from django.db import models


class Candidate(models.Model):
    class Source(models.TextChoices):
        LINKEDIN = "linkedin", "LinkedIn"
        JOB_BOARD = "job_board", "Job Board"
        REFERRAL = "referral", "Referral"
        CAREER_SITE = "career_site", "Career Site"
        AGENCY = "agency", "Agency"

    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True, default="")
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.CAREER_SITE)
    resume_text = models.TextField()
    skills = models.JSONField(default=list, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name
