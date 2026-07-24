import os
from django.utils import timezone
from django.conf import settings
from accounts.models import Scan, CodeFile, Issue
from scanner.services import ast_parser, bandit_runner, secret_detector, ruff_runner

def run_project_scan(scan_id):
    """
    Run AST parser, Bandit, and Secret Detector on all files associated with a scan.
    Aggregates findings, calculates metrics and scores, and updates the scan status.
    """
    try:
        scan = Scan.objects.get(id=scan_id)
    except Scan.DoesNotExist:
        return False, "Scan not found"

    scan.status = "running"
    scan.started_at = timezone.now()
    scan.save()

    project = scan.project
    extracted_path = project.extracted_path

    if not extracted_path or not os.path.exists(extracted_path):
        scan.status = "failed"
        scan.error_message = f"Project extracted path does not exist: {extracted_path}"
        scan.completed_at = timezone.now()
        scan.save()
        return False, "Project extracted path not found"

    # Get all code files indexed in DB
    code_files = CodeFile.objects.filter(project=project)
    python_files = code_files.filter(extension=".py")
    
    # 1. Run Bandit (Security scanner on project folder)
    bandit_issues = bandit_runner.run_bandit(extracted_path)
    
    # Run Ruff (Code Quality scanner on project folder)
    ruff_issues = ruff_runner.run_ruff(extracted_path)
    
    # 2. Run AST and Secret Scanners file-by-file
    file_specific_issues = []
    
    for code_file in code_files:
        absolute_file_path = os.path.join(extracted_path, code_file.file_path)
        
        # Only run AST parser on Python files
        if code_file.extension == ".py":
            ast_issues = ast_parser.analyze_file(absolute_file_path)
            for issue in ast_issues:
                issue["code_file"] = code_file
                file_specific_issues.append(issue)

        # Run Secret Detector on all code files
        secret_issues = secret_detector.scan_file_for_secrets(absolute_file_path)
        for issue in secret_issues:
            issue["code_file"] = code_file
            file_specific_issues.append(issue)

    # 3. Create Issue records in database
    db_issues = []

    # Map Bandit issues back to CodeFile models in database
    for raw in bandit_issues:
        rel_path = raw.get("file_path", "")
        # Try to find corresponding CodeFile
        code_file = code_files.filter(file_path=rel_path).first()
        
        issue_obj = Issue(
            scan=scan,
            code_file=code_file,
            issue_type=raw.get("issue_type", "security"),
            severity=raw.get("severity", "low"),
            title=raw.get("title", "Security Vulnerability"),
            description=raw.get("description", ""),
            file_path=rel_path,
            line_number=raw.get("line_number"),
            column_number=raw.get("column_number", 0),
            code_snippet=raw.get("code_snippet"),
            tool_name="bandit",
            rule_id=raw.get("rule_id")
        )
        db_issues.append(issue_obj)

    # Map Ruff issues back to CodeFile models in database
    for raw in ruff_issues:
        rel_path = raw.get("file_path", "")
        code_file = code_files.filter(file_path=rel_path).first()
        rule_id = raw.get("rule_id", "")
        issue_type = "security" if rule_id.upper().startswith("S") else "code_quality"
        
        issue_obj = Issue(
            scan=scan,
            code_file=code_file,
            issue_type=issue_type,
            severity=raw.get("severity", "low"),
            title=raw.get("title", "Code Quality Issue"),
            description=raw.get("description", ""),
            file_path=rel_path,
            line_number=raw.get("line_number"),
            column_number=raw.get("column_number", 0),
            code_snippet=raw.get("code_snippet"),
            tool_name="ruff",
            rule_id=rule_id
        )
        db_issues.append(issue_obj)

    # Create file-specific issues (AST + Secrets)
    for raw in file_specific_issues:
        code_file = raw.get("code_file")
        tool_name = "ai" if raw.get("rule_id", "").startswith("AI") else "custom_rule"
        
        issue_obj = Issue(
            scan=scan,
            code_file=code_file,
            issue_type=raw.get("issue_type", "code_quality"),
            severity=raw.get("severity", "low"),
            title=raw.get("title", "Code Issue"),
            description=raw.get("description", ""),
            file_path=code_file.file_path,
            line_number=raw.get("line_number"),
            column_number=raw.get("column_number", 0),
            code_snippet=raw.get("code_snippet"),
            tool_name=tool_name,
            rule_id=raw.get("rule_id")
        )
        db_issues.append(issue_obj)

    # Bulk create issues in DB
    Issue.objects.bulk_create(db_issues)

    # 4. Calculate Scores
    critical_cnt = 0
    high_cnt = 0
    medium_cnt = 0
    low_cnt = 0

    security_deductions = 0
    quality_deductions = 0
    maintainability_deductions = 0

    all_issues = Issue.objects.filter(scan=scan)
    total_issues_found = all_issues.count()

    for issue in all_issues:
        sev = issue.severity.lower()
        if sev == "critical":
            critical_cnt += 1
            deduction = 15
        elif sev == "high":
            high_cnt += 1
            deduction = 10
        elif sev == "medium":
            medium_cnt += 1
            deduction = 5
        else:
            low_cnt += 1
            deduction = 2

        if issue.issue_type == "security":
            security_deductions += deduction
        elif issue.issue_type in ["code_quality", "style", "bug"]:
            quality_deductions += deduction
        
        # AST rule or Ruff complexity check for maintainability (complexity, too long, too many arguments)
        if issue.rule_id in ["AST003", "AST004"] or (issue.rule_id and (issue.rule_id.startswith("C9") or issue.rule_id.startswith("PLR09"))):
            maintainability_deductions += deduction

    # Deduct from base of 100
    security_score = max(0.0, 100.0 - security_deductions)
    code_quality_score = max(0.0, 100.0 - quality_deductions)
    maintainability_score = max(0.0, 100.0 - maintainability_deductions)
    
    # Overall score is a weighted average of individual scores
    overall_score = max(0.0, 100.0 - (15 * critical_cnt + 10 * high_cnt + 5 * medium_cnt + 2 * low_cnt))

    # Update scan results
    scan.status = "completed"
    scan.completed_at = timezone.now()
    scan.total_files_scanned = python_files.count()
    scan.total_issues_found = total_issues_found
    scan.critical_issues = critical_cnt
    scan.high_issues = high_cnt
    scan.medium_issues = medium_cnt
    scan.low_issues = low_cnt
    
    scan.security_score = security_score
    scan.code_quality_score = code_quality_score
    scan.maintainability_score = maintainability_score
    scan.overall_score = overall_score
    scan.scan_log = f"Scan execution succeeded. Scanned {python_files.count()} Python files. Found {total_issues_found} issues."
    scan.save()

    return True, "Scan aggregation completed successfully"
