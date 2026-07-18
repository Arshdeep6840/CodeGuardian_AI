from django.urls import path
from .views import (
    FixRetrieveOrGenerateView,
    FixStatusUpdateView,
    GenerateTestSuiteView,
)

urlpatterns = [
    path("api/fixes/issue/<int:issue_id>/", FixRetrieveOrGenerateView.as_view(), name="fix-retrieve-generate"),
    path("api/fixes/<int:id>/status/", FixStatusUpdateView.as_view(), name="fix-status-update"),
    path("api/codefiles/<int:code_file_id>/tests/", GenerateTestSuiteView.as_view(), name="generate-test-suite"),
]
