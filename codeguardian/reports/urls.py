from django.urls import path
from .views import ReportRetrieveOrCreateView, ReportDownloadView, report_page

urlpatterns = [
    path("api/reports/scan/<int:scan_id>/", ReportRetrieveOrCreateView.as_view(), name="report-retrieve-create"),
    path("api/reports/<int:id>/download/", ReportDownloadView.as_view(), name="report-download"),
    path("reports/<int:scan_id>/", report_page, name="report-page"),
    path("report/<int:scan_id>/", report_page, name="report-page-short"),
    path("reports/", report_page, name="report-page-root"),
]
