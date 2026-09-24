from django.contrib import admin

from .models import Candidate


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "source", "experience_years", "created_at")
    list_filter = ("source",)
    search_fields = ("name", "email")
