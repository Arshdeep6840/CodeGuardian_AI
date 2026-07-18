from django.urls import path
from .views import ReportRetrieveOrCreateView, ReportDownloadView

urlpatterns = [
    path("api/reports/scan/<int:scan_id>/", ReportRetrieveOrCreateView.as_view(), name="report-retrieve-create"),
    path("api/reports/<int:id>/download/", ReportDownloadView.as_view(), name="report-download"),
]
