import json
import subprocess
import shutil
import os

def map_severity(bandit_severity, test_id):
    """Map Bandit's severity to CodeGuardian severity levels."""
    bs = bandit_severity.lower()
    if bs == "high":
        # Upgrade highly dangerous security issues to Critical
        if test_id in ["B608", "B105", "B106", "B309", "B506"]:
            return "critical"
        return "high"
    elif bs == "medium":
        return "medium"
    return "low"

def run_bandit(target_dir):
    """
    Run Bandit security scanner on the target directory.
    Returns a list of issue dicts.
    """
    if not os.path.exists(target_dir):
        return []

    # Check if bandit is installed and available
    bandit_path = shutil.which("bandit")
    if not bandit_path:
        # Fall back to trying just "bandit" command or searching standard env scripts path
        # Try checking if there's a bandit in the virtual env
        venv_bin = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(target_dir))), "env", "Scripts", "bandit.exe")
        if os.path.exists(venv_bin):
            bandit_path = venv_bin
        else:
            # If not found anywhere, log a warning and return empty
            print("Bandit executable not found. Skipping Bandit analysis.")
            return []

    # Run bandit -r <dir> -f json -q
    # We ignore the exit code because bandit returns non-zero when issues are found
    try:
        result = subprocess.run(
            [bandit_path, "-r", target_dir, "-f", "json", "-q"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
        
        stdout_content = result.stdout.strip()
        if not stdout_content:
            return []

        data = json.loads(stdout_content)
        raw_issues = data.get("results", [])
        
        issues = []
        for raw in raw_issues:
            test_id = raw.get("test_id", "")
            severity = map_severity(raw.get("issue_severity", "LOW"), test_id)
            
            # Get path relative to the target directory
            full_path = raw.get("filename", "")
            relative_path = os.path.relpath(full_path, target_dir) if os.path.isabs(full_path) else full_path
            
            issues.append({
                "issue_type": "security",
                "severity": severity,
                "title": raw.get("issue_text", "Security Vulnerability"),
                "description": f"Bandit Rule {test_id}: {raw.get('issue_text', '')}. More info: {raw.get('more_info', '')}",
                "line_number": raw.get("line_number"),
                "column_number": 0,
                "code_snippet": raw.get("code", ""),
                "rule_id": test_id
            })
            
        return issues
        
    except Exception as e:
        print(f"Error running Bandit: {str(e)}")
        return []
