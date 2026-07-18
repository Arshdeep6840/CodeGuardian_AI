import re
import os

SECRET_PATTERNS = {
    "AWS Access Key ID": r"AKIA[0-9A-Z]{16}",
    "Slack Token": r"xox[bapr]-[0-9]{12}-[a-zA-Z0-9]{24}",
    "Google API Key": r"AIza[0-9A-Za-z-_]{35}",
    "Generic Credentials/Secrets": r"(?i)(api[-_]?key|secret|token|password|passwd|auth|private[-_]?key)[ \t]*=[ \t]*['\"]([a-zA-Z0-9_\-\.\~\+\/=]{12,})['\"]"
}

# Substrings that indicate false positives / placeholders
PLACEHOLDERS = [
    "placeholder",
    "your_api_key",
    "your-api-key",
    "my_api_key",
    "test_key",
    "dummy",
    "example",
    "secret-key",
    "django-insecure-w8" # ignore default template key to avoid cluttering settings
]

def scan_file_for_secrets(file_path):
    """
    Scan a file line-by-line for potential secrets matching patterns.
    Returns a list of issue dicts.
    """
    if not os.path.exists(file_path):
        return []

    issues = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return []

    for i, line in enumerate(lines):
        line_num = i + 1
        
        for name, pattern in SECRET_PATTERNS.items():
            matches = re.finditer(pattern, line)
            for match in matches:
                matched_str = match.group(0)
                
                # Check for placeholders
                if any(p in matched_str.lower() for p in PLACEHOLDERS):
                    continue
                
                issues.append({
                    "issue_type": "security",
                    "severity": "critical",
                    "title": f"Hardcoded credential found ({name})",
                    "description": f"A hardcoded credential matching the pattern for '{name}' was detected. Credentials should be stored in environment variables rather than source code.",
                    "line_number": line_num,
                    "column_number": match.start() + 1,
                    "code_snippet": line.strip(),
                    "rule_id": "SEC001"
                })
                # Break to avoid logging multiple patterns for the same line
                break

    return issues
