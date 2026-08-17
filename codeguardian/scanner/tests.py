import io
import os
import zipfile
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Project, Scan, CodeFile
from scanner.services.file_extractor import detect_framework

User = get_user_model()

class ScannerTests(APITestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword"
        )
        self.client.force_authenticate(user=self.user)

        # Create an in-memory ZIP file for uploading
        self.zip_buffer = io.BytesIO()
        with zipfile.ZipFile(self.zip_buffer, "w") as zip_file:
            zip_file.writestr("app.py", "from flask import Flask\napp = Flask(__name__)")
            zip_file.writestr("utils.py", "def add(a, b):\n    return a + b")
            zip_file.writestr("README.md", "# My Application")
            # Ignored folder files
            zip_file.writestr("node_modules/index.js", "console.log('ignored');")
            zip_file.writestr("__pycache__/app.pyc", "binaries")
        self.zip_buffer.seek(0)
        self.zip_upload = SimpleUploadedFile("project.zip", self.zip_buffer.read(), content_type="application/zip")

    def test_project_zip_upload(self):
        """Test uploading a ZIP file to create a project."""
        url = reverse("project-upload")
        data = {
            "name": "Test Flask Project",
            "description": "A flask sample app",
            "upload_type": "zip",
            "file": self.zip_upload
        }
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 1)
        project = Project.objects.first()
        self.assertEqual(project.name, "Test Flask Project")
        self.assertEqual(project.status, "ready")
        self.assertEqual(project.total_python_files, 2)  # app.py, utils.py
        self.assertEqual(project.total_files, 3)  # app.py, utils.py, README.md (node_modules, pycache ignored)
        self.assertTrue("Flask" in project.language)
        
        # Verify CodeFile items are created
        self.assertEqual(CodeFile.objects.filter(project=project).count(), 3)
        code_file = CodeFile.objects.get(file_path="app.py")
        self.assertEqual(code_file.lines_of_code, 2)

    def test_project_single_file_upload(self):
        """Test uploading a single python file."""
        url = reverse("project-upload")
        single_file = SimpleUploadedFile("main.py", b"import fastapi\nprint('hello')", content_type="text/plain")
        data = {
            "name": "Single File",
            "upload_type": "single_file",
            "file": single_file
        }
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        project = Project.objects.first()
        self.assertEqual(project.total_python_files, 1)
        self.assertTrue("FastAPI" in project.language)

    @patch("scanner.views.download_github_repo")
    def test_github_import(self, mock_download):
        """Test importing a public GitHub repo."""
        # Mock download method to simulate writing mock zip to Project
        def mock_download_func(project_id):
            proj = Project.objects.get(id=project_id)
            # Create a mock zip
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w") as z:
                z.writestr("manage.py", "# Django startup\n")
                z.writestr("settings.py", "INSTALLED_APPS = []")
            buf.seek(0)
            proj.zip_file.save("mock_repo.zip", SimpleUploadedFile("mock_repo.zip", buf.read()), save=True)
            return True, "Mock download success"
        
        mock_download.side_effect = mock_download_func

        url = reverse("project-github-import")
        data = {
            "github_url": "https://github.com/django/django",
            "name": "Django Repo"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        project = Project.objects.first()
        self.assertEqual(project.upload_type, "github")
        self.assertEqual(project.status, "ready")
        self.assertTrue("Django" in project.language)
        self.assertEqual(project.total_python_files, 2)

    def test_start_scan_lifecycle(self):
        """Test starting a scan and checking status and results."""
        import tempfile
        temp_dir = tempfile.mkdtemp()
        # Setup an uploaded project first
        project = Project.objects.create(
            user=self.user,
            name="Manual Project",
            upload_type="zip",
            status="ready",
            extracted_path=temp_dir,
            total_python_files=5
        )
        for i in range(5):
            open(os.path.join(temp_dir, f"file_{i}.py"), "w").close()
            CodeFile.objects.create(
                project=project,
                file_name=f"file_{i}.py",
                file_path=f"file_{i}.py",
                extension=".py"
            )

        start_url = reverse("scan-start")
        data = {"project_id": project.id}
        response = self.client.post(start_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        scan_id = response.data["id"]
        scan = Scan.objects.get(id=scan_id)
        self.assertEqual(scan.status, "completed")
        self.assertEqual(scan.total_files_scanned, 5)
        self.assertEqual(scan.overall_score, 100.0)

        # Check status view
        status_url = reverse("scan-status", kwargs={"id": scan_id})
        response = self.client.get(status_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "completed")

        # Check results view
        results_url = reverse("scan-results", kwargs={"scan_id": scan_id})
        response = self.client.get(results_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0) # No issues detected in dummy scan

    @patch("scanner.services.ruff_runner.run_ruff")
    def test_ruff_scan_integration(self, mock_run_ruff):
        """Test that Ruff issues are correctly parsed, mapped to DB, and affect scores."""
        # Set up mock ruff results
        mock_run_ruff.return_value = [
            {
                "issue_type": "code_quality",
                "severity": "medium",
                "title": "Unused import: `sys`",
                "description": "Ruff Rule F401: `sys` imported but unused.",
                "file_path": "app.py",
                "line_number": 1,
                "column_number": 1,
                "code_snippet": "import sys",
                "rule_id": "F401"
            },
            {
                "issue_type": "code_quality",
                "severity": "high",
                "title": "Undefined name: `value`",
                "description": "Ruff Rule F821: Undefined name `value`.",
                "file_path": "utils.py",
                "line_number": 5,
                "column_number": 10,
                "code_snippet": "return value",
                "rule_id": "F821"
            }
        ]

        # Setup an uploaded project first
        import tempfile
        temp_dir = tempfile.mkdtemp()
        open(os.path.join(temp_dir, "app.py"), "w").close()
        open(os.path.join(temp_dir, "utils.py"), "w").close()
        
        project = Project.objects.create(
            user=self.user,
            name="Ruff Test Project",
            upload_type="zip",
            status="ready",
            extracted_path=temp_dir,
            total_python_files=2
        )
        # Create corresponding CodeFile objects in DB so the database references work
        CodeFile.objects.create(project=project, file_name="app.py", file_path="app.py", extension=".py")
        CodeFile.objects.create(project=project, file_name="utils.py", file_path="utils.py", extension=".py")

        start_url = reverse("scan-start")
        data = {"project_id": project.id}
        
        # Start scanning
        with patch("scanner.services.bandit_runner.run_bandit", return_value=[]), \
             patch("scanner.services.secret_detector.scan_file_for_secrets", return_value=[]), \
             patch("scanner.services.ast_parser.analyze_file", return_value=[]):
            response = self.client.post(start_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        scan_id = response.data["id"]
        scan = Scan.objects.get(id=scan_id)
        
        # Verify scan values
        self.assertEqual(scan.status, "completed")
        self.assertEqual(scan.total_issues_found, 2)
        # Undefined name (F821) is high severity -> deduction = 10
        # Unused import (F401) is medium severity -> deduction = 5
        # Total deduction = 15. Overall score = 100 - 15 = 85.0
        self.assertEqual(scan.overall_score, 85.0)
        self.assertEqual(scan.code_quality_score, 85.0)
        self.assertEqual(scan.security_score, 100.0) # No security issues
        
        # Check issues saved in DB
        self.assertEqual(scan.issues.count(), 2)
        issue1 = scan.issues.get(rule_id="F401")
        self.assertEqual(issue1.severity, "medium")
        self.assertEqual(issue1.tool_name, "ruff")
        self.assertEqual(issue1.file_path, "app.py")
