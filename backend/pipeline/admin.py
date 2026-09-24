from django.contrib import admin

from .models import Application, StageEvent


class StageEventInline(admin.TabularInline):
    model = StageEvent
    extra = 0
    readonly_fields = ("stage", "at")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("candidate", "job", "stage", "match_score", "created_at")
    list_filter = ("stage", "job")
    search_fields = ("candidate__name", "job__title")
    inlines = [StageEventInline]
