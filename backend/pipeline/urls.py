from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ApplicationViewSet, ApplyToJobView

router = DefaultRouter()
router.register("applications", ApplicationViewSet, basename="application")

urlpatterns = [
    path("jobs/<int:job_id>/apply/", ApplyToJobView.as_view(), name="job-apply"),
] + router.urls
