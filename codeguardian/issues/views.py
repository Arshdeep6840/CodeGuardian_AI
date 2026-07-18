from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.models import Issue
from accounts.serializers import IssueSerializer
from scanner.services.llm_agent import explain_issue

class IssueListView(APIView):
    """API view to list all scanned issues with filters for scan, severity, and issue type."""
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        issues = Issue.objects.all()
        scan_id = request.query_params.get("scan_id")
        severity = request.query_params.get("severity")
        issue_type = request.query_params.get("issue_type")

        # Filter by project if project_id is provided
        project_id = request.query_params.get("project_id")
        if project_id:
            issues = issues.filter(scan__project_id=project_id)

        if scan_id:
            issues = issues.filter(scan_id=scan_id)
        if severity:
            issues = issues.filter(severity=severity.lower())
        if issue_type:
            issues = issues.filter(issue_type=issue_type.lower())

        serializer = IssueSerializer(issues, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IssueDetailView(APIView):
    """API view to retrieve detailed issue information, including on-demand AI explanation generation."""
    permission_classes = (IsAuthenticated,)

    def get(self, request, id, *args, **kwargs):
        issue = get_object_or_404(Issue, id=id)

        # Generate AI explanation on-demand if it hasn't been set yet
        if not issue.ai_explanation:
            explanation = explain_issue(issue.title, issue.description, issue.code_snippet)
            issue.ai_explanation = explanation
            issue.save()

        serializer = IssueSerializer(issue)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, id, *args, **kwargs):
        """Allow users to mark issues as fixed or false positives."""
        issue = get_object_or_404(Issue, id=id)
        is_fixed = request.data.get("is_fixed")
        is_false_positive = request.data.get("is_false_positive")

        if is_fixed is not None:
            issue.is_fixed = bool(is_fixed)
        if is_false_positive is not None:
            issue.is_false_positive = bool(is_false_positive)

        issue.save()
        serializer = IssueSerializer(issue)
        return Response(serializer.data, status=status.HTTP_200_OK)
