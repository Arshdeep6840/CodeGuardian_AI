from django.urls import path
from scanner import views

urlpatterns = [
    path("api/projects/", views.ProjectListView.as_view(), name="project-list"),
    path("api/projects/upload/", views.ProjectUploadView.as_view(), name="project-upload"),
    path("api/projects/github/", views.GitHubImportView.as_view(), name="project-github-import"),
    path("api/scans/start/", views.StartScanView.as_view(), name="scan-start"),
    path("api/scans/<int:id>/status/", views.ScanStatusView.as_view(), name="scan-status"),
    path("api/scans/<int:scan_id>/results/", views.ScanResultsView.as_view(), name="scan-results"),
    path("scan/upload/", views.upload_page, name="scan-upload-page"),
]