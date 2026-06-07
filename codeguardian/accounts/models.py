from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.conf import settings


# -----------------------------User Model-----------------------------
class User(AbstractUser):
    ROLE_CHOICES = (
        ("user", "User"),
        ("admin", "Admin"),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="user")
    profile_image = models.ImageField(upload_to="profiles/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


# -----------------------------Project Model-----------------------------
class Project(models.Model):
    UPLOAD_TYPE_CHOICES = (
        ("zip", "ZIP Upload"),
        ("github", "GitHub Repository"),
        ("single_file", "Single Python File"),
    )

    STATUS_CHOICES = (
        ("uploaded", "Uploaded"),
        ("extracting", "Extracting"),
        ("ready", "Ready"),
        ("failed", "Failed"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects"
    )

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    upload_type = models.CharField(
        max_length=20,
        choices=UPLOAD_TYPE_CHOICES,
        default="zip"
    )

    zip_file = models.FileField(
        upload_to="project_zips/",
        validators=[FileExtensionValidator(allowed_extensions=["zip"])],
        null=True,
        blank=True
    )

    github_url = models.URLField(null=True, blank=True)

    extracted_path = models.CharField(max_length=500, null=True, blank=True)

    language = models.CharField(max_length=50, default="Python")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="uploaded"
    )

    total_files = models.IntegerField(default=0)
    total_python_files = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# ----------------------------- CodeFile Model -----------------------------
class CodeFile(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="code_files"
    )

    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)

    extension = models.CharField(max_length=20, default=".py")
    lines_of_code = models.IntegerField(default=0)
    file_size = models.IntegerField(default=0)

    content_hash = models.CharField(max_length=128, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_path


# ----------------------------- Scan Model -----------------------------
class Scan(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="scans"
    )

    scan_name = models.CharField(max_length=200, blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    total_files_scanned = models.IntegerField(default=0)
    total_issues_found = models.IntegerField(default=0)

    critical_issues = models.IntegerField(default=0)
    high_issues = models.IntegerField(default=0)
    medium_issues = models.IntegerField(default=0)
    low_issues = models.IntegerField(default=0)

    security_score = models.FloatField(default=100)
    code_quality_score = models.FloatField(default=100)
    maintainability_score = models.FloatField(default=100)
    overall_score = models.FloatField(default=100)

    scan_log = models.TextField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.name} - Scan {self.id}"


# ----------------------------- Issue Model -----------------------------
class Issue(models.Model):
    SEVERITY_CHOICES = (
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    )

    ISSUE_TYPE_CHOICES = (
        ("security", "Security"),
        ("bug", "Bug"),
        ("code_quality", "Code Quality"),
        ("performance", "Performance"),
        ("style", "Style"),
        ("complexity", "Complexity"),
        ("testing", "Testing"),
    )

    TOOL_CHOICES = (
        ("custom_rule", "Custom Rule"),
        ("bandit", "Bandit"),
        ("ruff", "Ruff"),
        ("pylint", "Pylint"),
        ("radon", "Radon"),
        ("ai", "AI Reviewer"),
    )

    scan = models.ForeignKey(
        Scan,
        on_delete=models.CASCADE,
        related_name="issues"
    )

    code_file = models.ForeignKey(
        CodeFile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issues"
    )

    issue_type = models.CharField(max_length=50, choices=ISSUE_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)

    title = models.CharField(max_length=255)
    description = models.TextField()

    file_path = models.CharField(max_length=500)
    line_number = models.IntegerField(null=True, blank=True)
    column_number = models.IntegerField(null=True, blank=True)

    code_snippet = models.TextField(blank=True, null=True)

    tool_name = models.CharField(
        max_length=50,
        choices=TOOL_CHOICES,
        default="custom_rule"
    )

    rule_id = models.CharField(max_length=100, null=True, blank=True)

    ai_explanation = models.TextField(blank=True, null=True)

    is_fixed = models.BooleanField(default=False)
    is_false_positive = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.severity}"


# ----------------------------- Fix Model -----------------------------
class Fix(models.Model):
    STATUS_CHOICES = (
        ("suggested", "Suggested"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("applied", "Applied"),
    )

    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="fixes"
    )

    fix_title = models.CharField(max_length=255)

    explanation = models.TextField()

    original_code = models.TextField(blank=True, null=True)
    fixed_code = models.TextField(blank=True, null=True)

    patch_diff = models.TextField(blank=True, null=True)

    ai_model_used = models.CharField(max_length=100, blank=True, null=True)

    confidence_score = models.FloatField(default=0.0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="suggested"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.fix_title


# ----------------------------- Report Model -----------------------------
class Report(models.Model):
    FORMAT_CHOICES = (
        ("pdf", "PDF"),
        ("json", "JSON"),
        ("html", "HTML"),
    )

    scan = models.OneToOneField(
        Scan,
        on_delete=models.CASCADE,
        related_name="report"
    )

    title = models.CharField(max_length=255)

    summary = models.TextField()

    report_file = models.FileField(
        upload_to="scan_reports/",
        null=True,
        blank=True
    )

    report_format = models.CharField(
        max_length=20,
        choices=FORMAT_CHOICES,
        default="pdf"
    )

    total_issues = models.IntegerField(default=0)
    total_fixed = models.IntegerField(default=0)
    total_pending = models.IntegerField(default=0)

    final_score = models.FloatField(default=100)

    recommendations = models.TextField(blank=True, null=True)

    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title