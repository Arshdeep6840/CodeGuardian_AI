import os
import re
import json
import difflib
from dotenv import load_dotenv
load_dotenv()

def generate_heuristic_fix(issue_title, issue_desc, original_code, file_path=""):
    """Generates an intelligent heuristic fix and unified diff when AI API is unavailable."""
    if not original_code:
        return {
            "fixed_code": "",
            "explanation": "No original code snippet provided to fix.",
            "diff_patch": ""
        }

    title_lower = (issue_title or "").lower()
    fixed_code = original_code
    explanation = "Applied standardized remediation pattern for the detected issue."

    # Heuristic: Bare except -> specific Exception
    if "bare except" in title_lower or "ast001" in title_lower:
        fixed_code = re.sub(r"except\s*:", "except Exception as e:", original_code)
        explanation = "Replaced bare `except:` clause with `except Exception as e:` to prevent swallowing critical system interrupts."
    # Heuristic: eval() / exec() -> ast.literal_eval
    elif "eval" in title_lower or "ast002" in title_lower:
        if "import ast" not in original_code:
            fixed_code = "import ast\n" + original_code.replace("eval(", "ast.literal_eval(")
        else:
            fixed_code = original_code.replace("eval(", "ast.literal_eval(")
        explanation = "Replaced unsafe `eval()` execution with safe literal evaluation via `ast.literal_eval()`."
    # Heuristic: Hardcoded secrets -> os.getenv
    elif "secret" in title_lower or "key" in title_lower or "token" in title_lower:
        if "import os" not in original_code:
            fixed_code = "import os\n" + re.sub(
                r'([A-Za-z0-9_]*(?:KEY|SECRET|TOKEN|PASSWORD)[A-Za-z0-9_]*)\s*=\s*["\'][^"\']+["\']',
                r'\1 = os.getenv("\1", "")',
                original_code,
                flags=re.IGNORECASE
            )
        else:
            fixed_code = re.sub(
                r'([A-Za-z0-9_]*(?:KEY|SECRET|TOKEN|PASSWORD)[A-Za-z0-9_]*)\s*=\s*["\'][^"\']+["\']',
                r'\1 = os.getenv("\1", "")',
                original_code,
                flags=re.IGNORECASE
            )
        explanation = "Replaced hardcoded plaintext credentials with secure environment variable lookups via `os.getenv()`."
    else:
        # Generic comment reminder
        fixed_code = f"# TODO: CodeGuardian Remediation: Verify fix for {issue_title}\n{original_code}"
        explanation = f"Flagged {issue_title} for manual review and refactoring according to best practices."

    # Generate unified diff
    orig_lines = original_code.splitlines(keepends=True)
    fixed_lines = fixed_code.splitlines(keepends=True)
    diff = difflib.unified_diff(
        orig_lines,
        fixed_lines,
        fromfile=f"a/{file_path or 'original_file.py'}",
        tofile=f"b/{file_path or 'fixed_file.py'}"
    )
    diff_patch = "".join(diff)

    return {
        "fixed_code": fixed_code,
        "explanation": explanation,
        "diff_patch": diff_patch
    }

def generate_fix(issue_title, issue_desc, original_code, file_path=""):
    """
    Generate corrected code and unified diff patch for an issue using the Gemini API.
    Falls back to intelligent heuristic fixes if API key is not configured or fails.
    """
    if not original_code:
        return {
            "fixed_code": "",
            "explanation": "No original code snippet provided to fix.",
            "diff_patch": ""
        }

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return generate_heuristic_fix(issue_title, issue_desc, original_code, file_path)

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        for model_name in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]:
            try:
                model = genai.GenerativeModel(model_name)
                prompt = f"""
You are CodeGuardian AI, an expert auto-fix helper.
Fix the code bug or security issue described below.

File: {file_path or 'code_file.py'}
Issue Title: {issue_title}
Issue Description: {issue_desc}

Original Code Block:
```python
{original_code}
```

Please fix the issue in the code block and return your response in the following JSON format:
{{
  "fixed_code": "Your fully corrected code block here. Make sure to preserve imports and indentations where necessary.",
  "explanation": "A concise explanation of the changes made."
}}

Do not include any preambles, greetings, or postscripts. Return ONLY the JSON object.
"""
                response = model.generate_content(prompt)
                text = response.text.strip()
                
                # Clean json backticks if present
                if text.startswith("```json"):
                    text = text[7:]
                elif text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
                
                data = json.loads(text)
                fixed_code = data.get("fixed_code", original_code)
                explanation = data.get("explanation", "Code corrected successfully.")
                
                # Generate Git-style unified diff patch
                orig_lines = original_code.splitlines(keepends=True)
                fixed_lines = fixed_code.splitlines(keepends=True)
                
                diff = difflib.unified_diff(
                    orig_lines,
                    fixed_lines,
                    fromfile=f"a/{file_path or 'original_file.py'}",
                    tofile=f"b/{file_path or 'fixed_file.py'}"
                )
                diff_patch = "".join(diff)
                
                return {
                    "fixed_code": fixed_code,
                    "explanation": explanation,
                    "diff_patch": diff_patch
                }
            except Exception:
                continue

        return generate_heuristic_fix(issue_title, issue_desc, original_code, file_path)
    except Exception:
        return generate_heuristic_fix(issue_title, issue_desc, original_code, file_path)

