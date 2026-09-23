from django.urls import include, path

urlpatterns = [
    path("", include("jobs.urls")),
    path("", include("candidates.urls")),
    path("", include("pipeline.urls")),
    path("", include("interviews.urls")),
    path("", include("evaluations.urls")),
    path("", include("analytics.urls")),
    path("", include("core.urls")),
]
