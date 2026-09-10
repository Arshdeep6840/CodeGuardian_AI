import os
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.models import Issue, Fix, CodeFile
from accounts.serializers import FixSerializer
from fixes.services.fix_generator import generate_fix
from fixes.services.test_generator import generate_tests

class FixRetrieveOrGenerateView(APIView):
    """Retrieve an existing fix suggestion or generate a new AI-powered fix on-demand."""
    permission_classes = (IsAuthenticated,)

    def get(self, request, issue_id, *args, **kwargs):
        issue = get_object_or_404(Issue, id=issue_id)
        
        # Check if a fix already exists in the database
        fix = Fix.objects.filter(issue=issue).first()
        if not fix:
            # Generate new fix using the AI service
            res = generate_fix(
                issue.title,
                issue.description,
                issue.code_snippet or "",
                issue.file_path,
                issue.scan.project_id if issue.scan else None
            )
            
            fix = Fix.objects.create(
                issue=issue,
                fix_title=f"AI Fix: {issue.title}",
                explanation=res["explanation"],
                original_code=issue.code_snippet or "",
                fixed_code=res["fixed_code"],
                patch_diff=res["diff_patch"],
                ai_model_used="gemini-1.5-flash",
                confidence_score=0.90,
                status="suggested"
            )
            
        serializer = FixSerializer(fix)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FixStatusUpdateView(APIView):
    """Update the status of a fix suggestion (suggested, accepted, rejected, applied)."""
    permission_classes = (IsAuthenticated,)

    def patch(self, request, id, *args, **kwargs):
        fix = get_object_or_404(Fix, id=id)
        new_status = request.data.get("status")
        
        if new_status not in ["suggested", "accepted", "rejected", "applied"]:
            return Response(
                {"error": "Invalid status. Must be: suggested, accepted, rejected, or applied."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        fix.status = new_status
        fix.save()
        
        # If the fix is marked as applied, mark the parent issue as fixed too
        if new_status == "applied":
            issue = fix.issue
            issue.is_fixed = True
            issue.save()
            
        serializer = FixSerializer(fix)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GenerateTestSuiteView(APIView):
    """Generate a unit test suite for a code file using the AI test generator service."""
    permission_classes = (IsAuthenticated,)

    def get(self, request, code_file_id, *args, **kwargs):
        code_file = get_object_or_404(CodeFile, id=code_file_id)
        project = code_file.project
        
        # Build path to extracted file on disk
        file_path = os.path.join(project.extracted_path, code_file.file_path)
        if not os.path.exists(file_path):
            return Response(
                {"error": f"Source code file not found on disk at {code_file.file_path}"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                code_content = f.read()
        except Exception as e:
            return Response(
                {"error": f"Failed to read source file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
        # Call Gemini test case generator
        test_code = generate_tests(code_content, code_file.file_path)

        return Response({
            "code_file_id": code_file.id,
            "file_name": code_file.file_name,
            "test_code": test_code
        }, status=status.HTTP_200_OK)


import io
import zipfile
from django.http import HttpResponse
from django.shortcuts import render
from accounts.models import Scan, Project


class FixListAPIView(APIView):
    """API view to list all generated/suggested fixes with scan, project, and status filters."""
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        fixes = Fix.objects.select_related("issue", "issue__scan", "issue__code_file").all()
        scan_id = request.query_params.get("scan_id")
        project_id = request.query_params.get("project_id")
        status_filter = request.query_params.get("status")

        if scan_id:
            fixes = fixes.filter(issue__scan_id=scan_id)
        if project_id:
            fixes = fixes.filter(issue__scan__project_id=project_id)
        if status_filter:
            fixes = fixes.filter(status=status_filter.lower())

        serializer = FixSerializer(fixes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ScanPatchExportView(APIView):
    """Generate and export a unified Git .patch file containing all fixes for a scan."""
    permission_classes = ()

    def get(self, request, scan_id, *args, **kwargs):
        scan = get_object_or_404(Scan, id=scan_id)
        fixes = Fix.objects.filter(issue__scan=scan)
        
        status_filter = request.query_params.get("status")
        if status_filter:
            fixes = fixes.filter(status=status_filter)

        patch_lines = [
            f"# CodeGuardian AI Unified Patch",
            f"# Project: {scan.project.name}",
            f"# Scan ID: {scan.id}",
            f"# Date: {scan.completed_at or scan.created_at}",
            f"# Total Fixes Included: {fixes.count()}",
            "",
        ]

        for fix in fixes:
            file_rel_path = fix.issue.file_path if fix.issue else "unknown_file.py"
            patch_lines.append(f"diff --git a/{file_rel_path} b/{file_rel_path}")
            patch_lines.append(f"--- a/{file_rel_path}")
            patch_lines.append(f"+++ b/{file_rel_path}")
            if fix.patch_diff:
                patch_lines.append(fix.patch_diff.strip())
            else:
                patch_lines.append(f"# AI Fix: {fix.fix_title}")
                patch_lines.append(f"# Explanation: {fix.explanation}")
            patch_lines.append("")

        patch_content = "\n".join(patch_lines)
        response = HttpResponse(patch_content, content_type="text/x-diff; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="codeguardian_scan_{scan.id}.patch"'
        return response


class ScanFixedArchiveView(APIView):
    """Bundle the project source code with applied/selected fixes as a downloadable ZIP archive."""
    permission_classes = ()

    def get(self, request, scan_id, *args, **kwargs):
        scan = get_object_or_404(Scan, id=scan_id)
        project = scan.project

        if not project.extracted_path or not os.path.exists(project.extracted_path):
            return Response({"error": "Project source files not found on disk"}, status=status.HTTP_404_NOT_FOUND)

        # Map files to their latest applied or suggested fix
        fixes = Fix.objects.filter(issue__scan=scan)
        file_fixed_content = {}
        for fix in fixes:
            if fix.fixed_code and fix.issue and fix.issue.file_path:
                file_fixed_content[fix.issue.file_path] = fix.fixed_code

        # Create zip in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(project.extracted_path):
                # Exclude transient folders
                dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", "venv", "node_modules", ".pytest_cache"]]
                for file in files:
                    full_p = os.path.join(root, file)
                    rel_p = os.path.relpath(full_p, project.extracted_path).replace("\\", "/")
                    
                    if rel_p in file_fixed_content:
                        # Write fixed content
                        zf.writestr(rel_p, file_fixed_content[rel_p])
                    else:
                        zf.write(full_p, arcname=rel_p)

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="codeguardian_fixed_scan_{scan.id}.zip"'
        return response


class ScanTestSuiteDownloadView(APIView):
    """Download test cases for all Python files in a scan bundled as a ZIP package."""
    permission_classes = ()

    def get(self, request, scan_id, *args, **kwargs):
        scan = get_object_or_404(Scan, id=scan_id)
        project = scan.project
        code_files = CodeFile.objects.filter(project=project, extension=".py")

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # Add conftest.py
            conftest = (
                "# Pytest configuration generated by CodeGuardian AI\n"
                "import pytest\n"
                "import sys, os\n"
                "sys.path.insert(0, os.path.abspath('.'))\n"
            )
            zf.writestr("tests/conftest.py", conftest)

            for cf in code_files:
                file_path = os.path.join(project.extracted_path, cf.file_path)
                if os.path.exists(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            code_content = f.read()
                        test_code = generate_tests(code_content, cf.file_path)
                    except Exception:
                        test_code = f"# Failed to generate tests for {cf.file_name}\n"
                    
                    base_name = os.path.splitext(cf.file_name)[0]
                    zf.writestr(f"tests/test_{base_name}.py", test_code)

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="tests_scan_{scan.id}.zip"'
        return response


class CodeFileTestDownloadView(APIView):
    """Download the generated Pytest test suite for a single code file."""
    permission_classes = ()

    def get(self, request, code_file_id, *args, **kwargs):
        code_file = get_object_or_404(CodeFile, id=code_file_id)
        project = code_file.project
        file_path = os.path.join(project.extracted_path, code_file.file_path)

        if not os.path.exists(file_path):
            return Response({"error": "Source file not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                code_content = f.read()
            test_code = generate_tests(code_content, code_file.file_path)
        except Exception as e:
            test_code = f"# Error generating tests: {str(e)}"

        base_name = os.path.splitext(code_file.file_name)[0]
        response = HttpResponse(test_code, content_type="text/x-python; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="test_{base_name}.py"'
        return response


def fix_list_page(request):
    """Render the Fix Management UI page."""
    return render(request, "fix_list.html")


def test_suite_page(request, scan_id=None):
    """Render the AI Test Suite Generator UI page."""
    return render(request, "test_suite.html", {"scan_id": scan_id})
