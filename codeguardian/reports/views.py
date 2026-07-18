from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.files.base import ContentFile
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.models import Scan, Report
from accounts.serializers import ReportSerializer
from reports.services.pdf_generator import generate_pdf_report

class ReportRetrieveOrCreateView(APIView):
    """Retrieve an existing report for a scan, or generate it dynamically on-demand."""
    permission_classes = (IsAuthenticated,)

    def get(self, request, scan_id, *args, **kwargs):
        scan = get_object_or_404(Scan, id=scan_id)
        
        # Check if report already exists
        report = Report.objects.filter(scan=scan).first()
        if not report:
            # Generate the PDF binary bytes
            try:
                pdf_bytes = generate_pdf_report(scan)
            except Exception as e:
                return Response(
                    {"error": f"Failed to generate PDF report: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Create report metadata record
            report = Report.objects.create(
                scan=scan,
                title=f"Report - {scan.scan_name}",
                summary=f"Automated code review report for project '{scan.project.name}' scan '{scan.scan_name}'.",
                report_format="pdf",
                total_issues=scan.total_issues_found,
                total_fixed=scan.issues.filter(is_fixed=True).count(),
                total_pending=scan.issues.filter(is_fixed=False).count(),
                final_score=scan.overall_score,
                recommendations="AI recommendation overview: review critical SQL injections and hardcoded credentials first."
            )
            
            # Save PDF file to FileField
            report_filename = f"scan_{scan.id}_report.pdf"
            report.report_file.save(report_filename, ContentFile(pdf_bytes), save=True)
            
        serializer = ReportSerializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReportDownloadView(APIView):
    """Download the generated PDF report file directly."""
    permission_classes = (IsAuthenticated,)

    def get(self, request, id, *args, **kwargs):
        report = get_object_or_404(Report, id=id)
        
        if not report.report_file or not os_file_exists(report.report_file.path):
            # If the database has the record but the file is missing from disk, regenerate it
            try:
                pdf_bytes = generate_pdf_report(report.scan)
                report_filename = f"scan_{report.scan.id}_report.pdf"
                report.report_file.save(report_filename, ContentFile(pdf_bytes), save=True)
            except Exception as e:
                return Response(
                    {"error": f"Failed to regenerate missing PDF report file: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        # Open and stream file
        try:
            with open(report.report_file.path, "rb") as f:
                response = HttpResponse(f.read(), content_type="application/pdf")
                response["Content-Disposition"] = f"attachment; filename={os.path.basename(report.report_file.name)}"
                return response
        except Exception as e:
            return Response(
                {"error": f"Failed to read report file from disk: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

def os_file_exists(path):
    import os
    return os.path.exists(path)
