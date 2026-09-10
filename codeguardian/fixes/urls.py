from django.urls import path
from .views import (
    FixRetrieveOrGenerateView,
    FixStatusUpdateView,
    FixListAPIView,
    ScanPatchExportView,
    ScanFixedArchiveView,
    GenerateTestSuiteView,
    ScanTestSuiteDownloadView,
    CodeFileTestDownloadView,
    fix_list_page,
    test_suite_page,
)

urlpatterns = [
    path("api/fixes/", FixListAPIView.as_view(), name="fix-list"),
    path("api/fixes/issue/<int:issue_id>/", FixRetrieveOrGenerateView.as_view(), name="fix-retrieve-generate"),
    path("api/fixes/<int:id>/status/", FixStatusUpdateView.as_view(), name="fix-status-update"),
    path("api/scans/<int:scan_id>/patch/", ScanPatchExportView.as_view(), name="scan-patch-export"),
    path("api/scans/<int:scan_id>/download-fixed/", ScanFixedArchiveView.as_view(), name="scan-download-fixed"),
    path("api/codefiles/<int:code_file_id>/tests/", GenerateTestSuiteView.as_view(), name="generate-test-suite"),
    path("api/codefiles/<int:code_file_id>/tests/download/", CodeFileTestDownloadView.as_view(), name="download-file-tests"),
    path("api/scans/<int:scan_id>/tests/download/", ScanTestSuiteDownloadView.as_view(), name="download-scan-tests"),
    path("fixes/", fix_list_page, name="fix-list-page"),
    path("tests/", test_suite_page, name="test-suite-page"),
    path("tests/<int:scan_id>/", test_suite_page, name="test-suite-scan-page"),
]
