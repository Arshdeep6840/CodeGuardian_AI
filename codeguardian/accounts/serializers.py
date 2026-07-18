from rest_framework import serializers
from .models import CustomUser, Project, CodeFile, Scan, Issue, Fix, Report

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "role", "created_at")
        read_only_fields = ("id", "created_at")

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "password", "role")
        read_only_fields = ("id",)

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role=validated_data.get("role", "user")
        )
        return user

class CodeFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeFile
        fields = (
            "id",
            "project",
            "file_name",
            "file_path",
            "extension",
            "lines_of_code",
            "file_size",
            "content_hash",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

class ProjectSerializer(serializers.ModelSerializer):
    code_files = CodeFileSerializer(many=True, read_only=True)
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "user",
            "name",
            "description",
            "upload_type",
            "zip_file",
            "github_url",
            "extracted_path",
            "language",
            "status",
            "total_files",
            "total_python_files",
            "code_files",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "extracted_path",
            "status",
            "total_files",
            "total_python_files",
            "created_at",
            "updated_at",
        )

class FixSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fix
        fields = (
            "id",
            "issue",
            "fix_title",
            "explanation",
            "original_code",
            "fixed_code",
            "patch_diff",
            "ai_model_used",
            "confidence_score",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

class IssueSerializer(serializers.ModelSerializer):
    fixes = FixSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = (
            "id",
            "scan",
            "code_file",
            "issue_type",
            "severity",
            "title",
            "description",
            "file_path",
            "line_number",
            "column_number",
            "code_snippet",
            "tool_name",
            "rule_id",
            "ai_explanation",
            "is_fixed",
            "is_false_positive",
            "fixes",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

class ScanSerializer(serializers.ModelSerializer):
    issues = IssueSerializer(many=True, read_only=True)

    class Meta:
        model = Scan
        fields = (
            "id",
            "project",
            "scan_name",
            "status",
            "started_at",
            "completed_at",
            "total_files_scanned",
            "total_issues_found",
            "critical_issues",
            "high_issues",
            "medium_issues",
            "low_issues",
            "security_score",
            "code_quality_score",
            "maintainability_score",
            "overall_score",
            "scan_log",
            "error_message",
            "issues",
            "created_at",
        )
        read_only_fields = (
            "id",
            "started_at",
            "completed_at",
            "total_files_scanned",
            "total_issues_found",
            "critical_issues",
            "high_issues",
            "medium_issues",
            "low_issues",
            "security_score",
            "code_quality_score",
            "maintainability_score",
            "overall_score",
            "scan_log",
            "error_message",
            "created_at",
        )

class ReportSerializer(serializers.ModelSerializer):
    scan = ScanSerializer(read_only=True)

    class Meta:
        model = Report
        fields = (
            "id",
            "scan",
            "title",
            "summary",
            "report_file",
            "report_format",
            "total_issues",
            "total_fixed",
            "total_pending",
            "final_score",
            "recommendations",
            "generated_at",
        )
        read_only_fields = ("id", "generated_at")
