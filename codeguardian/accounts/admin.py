from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Project, CodeFile, Scan, Issue, Fix, Report


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "role",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "role",
        "is_staff",
        "is_active",
    )

    fieldsets = UserAdmin.fieldsets + (
        ("Custom Fields", {"fields": ("role",)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Custom Fields", {"fields": ("role",)}),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "upload_type", "status", "total_files", "total_python_files", "created_at")
    list_filter = ("upload_type", "status", "language")
    search_fields = ("name", "user__email", "user__username", "github_url")
    ordering = ("-created_at",)


@admin.register(CodeFile)
class CodeFileAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "file_name", "file_path", "extension", "lines_of_code", "file_size")
    list_filter = ("extension", "project")
    search_fields = ("file_name", "file_path", "project__name")


@admin.register(Scan)
class ScanAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "project",
        "scan_name",
        "status",
        "total_files_scanned",
        "total_issues_found",
        "overall_score",
        "started_at",
        "completed_at",
    )
    list_filter = ("status", "project")
    search_fields = ("scan_name", "project__name")
    ordering = ("-created_at",)


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "scan",
        "code_file",
        "issue_type",
        "severity",
        "title",
        "file_path",
        "line_number",
        "is_fixed",
        "is_false_positive",
    )
    list_filter = ("issue_type", "severity", "tool_name", "is_fixed", "is_false_positive")
    search_fields = ("title", "description", "file_path", "scan__project__name")
    ordering = ("-created_at",)


@admin.register(Fix)
class FixAdmin(admin.ModelAdmin):
    list_display = ("id", "issue", "fix_title", "confidence_score", "status", "created_at")
    list_filter = ("status", "ai_model_used")
    search_fields = ("fix_title", "explanation", "issue__title")
    ordering = ("-created_at",)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "scan", "title", "report_format", "total_issues", "total_fixed", "final_score", "generated_at")
    list_filter = ("report_format",)
    search_fields = ("title", "summary", "scan__project__name")
    ordering = ("-generated_at",)