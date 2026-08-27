from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated

from accounts.models import Project, Scan, Issue, CustomUser
from accounts.serializers import ProjectSerializer, ScanSerializer, IssueSerializer
from scanner.services.file_extractor import extract_and_map_project
from scanner.services.github_downloader import download_github_repo
from scanner.services.issue_aggregator import run_project_scan

User = get_user_model()

def get_fallback_user(request):
    """Helper to return request.user or a default developer fallback user if unauthenticated."""
    if request.user and request.user.is_authenticated:
        return request.user
    
    # Try finding the first admin or user in DB
    default_user = User.objects.first()
    if not default_user:
        # Create a default user if none exists in database
        default_user = User.objects.create_superuser(
            username="developer",
            email="developer@codeguardian.ai",
            password="DeveloperPassword123"
        )
    return default_user


class ProjectUploadView(APIView):
    """API view to upload a python project ZIP or single .py file."""
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get("file")
        name = request.data.get("name")
        description = request.data.get("description", "")
        upload_type = request.data.get("upload_type", "zip") # "zip" or "single_file"

        if not file_obj:
            return Response(
                {"error": "No file uploaded. Please upload a file."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not name:
            # Generate a default name from filename
            name = file_obj.name.split(".")[0]

        if upload_type not in ["zip", "single_file"]:
            return Response(
                {"error": "Invalid upload type. Must be 'zip' or 'single_file'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Enforce file extension check
        ext = file_obj.name.split(".")[-1].lower()
        if upload_type == "zip" and ext != "zip":
            return Response(
                {"error": "File must be a ZIP archive when upload_type is 'zip'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif upload_type == "single_file" and ext != "py":
            return Response(
                {"error": "File must be a Python (.py) file when upload_type is 'single_file'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = get_fallback_user(request)

        # Create Project
        project = Project.objects.create(
            user=user,
            name=name,
            description=description,
            upload_type=upload_type,
            zip_file=file_obj,
            status="uploaded"
        )

        # Extract and Index
        success, message = extract_and_map_project(project.id)
        if not success:
            project.status = "failed"
            project.save()
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProjectSerializer(project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GitHubImportView(APIView):
    """API view to import a public GitHub repository."""

    def post(self, request, *args, **kwargs):
        github_url = request.data.get("github_url")
        name = request.data.get("name")
        description = request.data.get("description", "")

        if not github_url:
            return Response(
                {"error": "github_url parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not name:
            # Get repo name from URL
            parts = github_url.strip().rstrip("/").split("/")
            name = parts[-1].replace(".git", "") if parts else "GitHub Import"

        user = get_fallback_user(request)

        # Create Project in uploaded status
        project = Project.objects.create(
            user=user,
            name=name,
            description=description,
            upload_type="github",
            github_url=github_url,
            status="uploaded"
        )

        # Download ZIP from GitHub
        download_success, download_message = download_github_repo(project.id)
        if not download_success:
            return Response({"error": download_message}, status=status.HTTP_400_BAD_REQUEST)

        # Extract and index
        extract_success, extract_message = extract_and_map_project(project.id)
        if not extract_success:
            return Response({"error": extract_message}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProjectSerializer(project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StartScanView(APIView):
    """API view to start a new analysis scan on an indexed project."""

    def post(self, request, *args, **kwargs):
        project_id = request.data.get("project_id")
        scan_name = request.data.get("scan_name")

        if not project_id:
            return Response(
                {"error": "project_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        project = get_object_or_404(Project, id=project_id)
        if project.status != "ready":
            return Response(
                {"error": f"Project is not ready for scanning. Current status: {project.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not scan_name:
            scan_name = f"Scan_{timezone.now().strftime('%Y%m%d_%H%M%S')}"

        # Create Scan
        scan = Scan.objects.create(
            project=project,
            scan_name=scan_name,
            status="running",
            started_at=timezone.now()
        )

        # Trigger actual scan pipeline
        success, message = run_project_scan(scan.id)
        if not success:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

        # Refresh scan from database to load updated scores and details
        scan.refresh_from_db()

        serializer = ScanSerializer(scan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ScanStatusView(generics.RetrieveAPIView):
    """Retrieve scan execution status and summary metadata."""
    queryset = Scan.objects.all()
    serializer_class = ScanSerializer
    lookup_field = "id"


class ScanResultsView(APIView):
    """List issues found during a scan execution."""

    def get(self, request, scan_id, *args, **kwargs):
        scan = get_object_or_404(Scan, id=scan_id)
        issues = scan.issues.all()
        
        # Simple optional severity filter
        severity = request.query_params.get("severity")
        if severity:
            issues = issues.filter(severity=severity.lower())

        serializer = IssueSerializer(issues, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


def upload_page(request):
    """View to serve the static project upload page HTML template."""
    return render(request, "upload.html")


class ProjectListView(generics.ListAPIView):
    """API view to list all projects for the authenticated user."""
    permission_classes = (IsAuthenticated,)
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user).order_by("-created_at")

def projects_page(request):
    """View to serve the static projects page HTML template."""
    return render(request, "projects.html")