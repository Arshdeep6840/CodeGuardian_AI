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
                issue.file_path
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
