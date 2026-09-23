from django.urls import path

from .views import MatchScoreView

urlpatterns = [
    path("matching/score/", MatchScoreView.as_view(), name="matching-score"),
]
