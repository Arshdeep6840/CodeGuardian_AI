from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg
from accounts.models import Project, Scan, Issue

def dashboard_page(request):
    """View to serve the static dashboard HTML template."""
    return render(request, "dashboard.html")

class DashboardStatsView(APIView):
    """API view to aggregate security and code quality stats across all user projects."""
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        
        projects = Project.objects.filter(user=user)
        total_projects = projects.count()
        
        scans = Scan.objects.filter(project__user=user)
        total_scans = scans.count()
        
        issues = Issue.objects.filter(scan__project__user=user)
        total_issues = issues.count()
        
        # Severity breakdowns
        severity_counts = {
            "critical": issues.filter(severity="critical").count(),
            "high": issues.filter(severity="high").count(),
            "medium": issues.filter(severity="medium").count(),
            "low": issues.filter(severity="low").count(),
        }
        
        # Issue type breakdowns
        type_counts = {}
        for item in issues.values("issue_type").annotate(count=Count("id")):
            type_counts[item["issue_type"]] = item["count"]
            
        # Average health scores from completed scans
        completed_scans = scans.filter(status="completed")
        avg_scores = completed_scans.aggregate(
            avg_overall=Avg("overall_score"),
            avg_security=Avg("security_score"),
            avg_quality=Avg("code_quality_score"),
            avg_maintainability=Avg("maintainability_score")
        )
        
        avg_overall = avg_scores.get("avg_overall") or 100.0
        avg_security = avg_scores.get("avg_security") or 100.0
        avg_quality = avg_scores.get("avg_quality") or 100.0
        avg_maintainability = avg_scores.get("avg_maintainability") or 100.0
        
        # Recent scans list
        recent_scans = []
        for s in scans.order_by("-created_at")[:5]:
            recent_scans.append({
                "scan_id": s.id,
                "project_name": s.project.name,
                "scan_name": s.scan_name,
                "status": s.status,
                "total_issues": s.total_issues_found,
                "score": s.overall_score,
                "created_at": s.created_at
            })
            
        # Top 5 most risky files (files with the most critical or high severity issues)
        risky_files = []
        file_counts = (
            issues.exclude(severity="low")
            .values("file_path", "scan__project__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )
        for f in file_counts:
            risky_files.append({
                "file_path": f["file_path"],
                "project_name": f["scan__project__name"],
                "issue_count": f["count"]
            })
            
        return Response({
            "total_projects": total_projects,
            "total_scans": total_scans,
            "total_issues": total_issues,
            "severity_counts": severity_counts,
            "issue_type_counts": type_counts,
            "scores": {
                "overall": round(avg_overall, 1),
                "security": round(avg_security, 1),
                "code_quality": round(avg_quality, 1),
                "maintainability": round(avg_maintainability, 1),
            },
            "recent_scans": recent_scans,
            "risky_files": risky_files
        }, status=status.HTTP_200_OK)
