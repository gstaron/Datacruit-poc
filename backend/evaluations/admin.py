from django.contrib import admin

from .models import Evaluation


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ("application", "evaluator_name", "rating", "recommendation", "created_at")
    list_filter = ("recommendation",)
