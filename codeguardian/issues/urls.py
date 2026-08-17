from django.urls import path
from .views import IssueListView, IssueDetailView, issue_list_page

urlpatterns = [
    path("api/issues/", IssueListView.as_view(), name="issue-list"),
    path("api/issues/<int:id>/", IssueDetailView.as_view(), name="issue-detail"),
    path("issues/", issue_list_page, name="issue-list-page"),
]
