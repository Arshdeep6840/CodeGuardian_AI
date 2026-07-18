import os
import json
import difflib
import google.generativeai as genai

def generate_fix(issue_title, issue_desc, original_code, file_path=""):
    """
    Generate corrected code and unified diff patch for an issue using the Gemini API.
    Returns a dict with: fixed_code, explanation, and diff_patch.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {
            "fixed_code": original_code,
            "explanation": "AI fix generation unavailable. Please configure the GEMINI_API_KEY in your .env file.",
            "diff_patch": ""
        }

    if not original_code:
        return {
            "fixed_code": "",
            "explanation": "No original code snippet provided to fix.",
            "diff_patch": ""
        }

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
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
        
    except Exception as e:
        return {
            "fixed_code": original_code,
            "explanation": f"Failed to generate AI auto-fix: {str(e)}",
            "diff_patch": ""
        }
