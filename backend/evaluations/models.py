from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Evaluation(models.Model):
    class Recommendation(models.TextChoices):
        HIRE = "hire", "Hire"
        MAYBE = "maybe", "Maybe"
        NO_HIRE = "no_hire", "No hire"

    application = models.ForeignKey(
        "pipeline.Application", related_name="evaluations", on_delete=models.CASCADE
    )
    evaluator_name = models.CharField(max_length=200)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    recommendation = models.CharField(
        max_length=10, choices=Recommendation.choices, default=Recommendation.MAYBE
    )
    comments = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.evaluator_name} on {self.application}: {self.recommendation}"
