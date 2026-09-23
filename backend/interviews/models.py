from django.db import models


class Interview(models.Model):
    class Type(models.TextChoices):
        PHONE = "phone", "Phone"
        VIDEO = "video", "Video"
        ONSITE = "onsite", "Onsite"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    application = models.ForeignKey(
        "pipeline.Application", related_name="interviews", on_delete=models.CASCADE
    )
    scheduled_at = models.DateTimeField()
    interviewer = models.CharField(max_length=200)
    type = models.CharField(max_length=10, choices=Type.choices, default=Type.VIDEO)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SCHEDULED)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["scheduled_at"]

    def __str__(self) -> str:
        return f"{self.application} interview with {self.interviewer}"
