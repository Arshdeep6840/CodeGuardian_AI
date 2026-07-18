from django.urls import path
from .views import IssueListView, IssueDetailView

urlpatterns = [
    path("api/issues/", IssueListView.as_view(), name="issue-list"),
    path("api/issues/<int:id>/", IssueDetailView.as_view(), name="issue-detail"),
]
