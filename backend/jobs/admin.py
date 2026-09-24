from django.contrib import admin

from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "department", "location", "status", "employment_type", "created_at")
    list_filter = ("status", "employment_type", "department")
    search_fields = ("title", "department", "location")
