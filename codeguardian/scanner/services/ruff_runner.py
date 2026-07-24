import json
import subprocess
import shutil
import os

def map_severity(rule_code):
    """
    Map Ruff rule codes to CodeGuardian severity levels.
    """
    code = rule_code.upper()
    # Critical security issues or potential syntax/runtime blockers
    if code.startswith("E9") or code.startswith("F82") or code.startswith("F83"):
        return "critical"
    # Logic / High issues
    elif code.startswith("F8") or code.startswith("B00"):
        return "high"
    # Unused imports, unused variables, general style warnings (Medium)
    elif code.startswith("F4") or code.startswith("E") or code.startswith("W"):
        return "medium"
    # Style/formatting details (Low)
    return "low"

def run_ruff(target_dir):
    """
    Run Ruff check on the target directory and return parsed issues.
    """
    if not os.path.exists(target_dir):
        return []

    # Find ruff executable
    ruff_path = shutil.which("ruff")
    if not ruff_path:
        # Check standard virtualenv location
        venv_bin = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(target_dir))), "env", "Scripts", "ruff.exe")
        if os.path.exists(venv_bin):
            ruff_path = venv_bin
        else:
            print("Ruff executable not found. Skipping Ruff analysis.")
            return []

    try:
        # Run ruff check --format json <target_dir>
        # We ignore exit code because ruff returns non-zero if it finds issues
        result = subprocess.run(
            [ruff_path, "check", "--format", "json", target_dir],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
        
        stdout_content = result.stdout.strip()
        if not stdout_content:
            return []

        raw_issues = json.loads(stdout_content)
        issues = []
        for raw in raw_issues:
            rule_code = raw.get("code", "")
            severity = map_severity(rule_code)
            
            full_path = raw.get("filename", "")
            relative_path = os.path.relpath(full_path, target_dir) if os.path.isabs(full_path) else full_path
            
            location = raw.get("location", {})
            line_number = location.get("row", 1)
            column_number = location.get("column", 1)
            
            code_snippet = ""
            if os.path.exists(full_path):
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                        if 0 < line_number <= len(lines):
                            code_snippet = lines[line_number - 1].strip()
                except Exception:
                    pass
            
            issues.append({
                "issue_type": "code_quality",
                "severity": severity,
                "title": raw.get("message", "Code Quality Issue"),
                "description": f"Ruff Rule {rule_code}: {raw.get('message', '')}. More info: {raw.get('url', '') or 'https://docs.astral.sh/ruff/'}",
                "file_path": relative_path,
                "line_number": line_number,
                "column_number": column_number,
                "code_snippet": code_snippet,
                "rule_id": rule_code
            })
            
        return issues
        
    except Exception as e:
        print(f"Error running Ruff: {str(e)}")
        return []
