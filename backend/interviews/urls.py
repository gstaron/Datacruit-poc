from rest_framework.routers import DefaultRouter

from .views import InterviewViewSet

router = DefaultRouter()
router.register("interviews", InterviewViewSet, basename="interview")

urlpatterns = router.urls
