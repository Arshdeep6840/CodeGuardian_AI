import os
import google.generativeai as genai

def explain_issue(issue_title, issue_desc, code_snippet=None):
    """
    Generate an explanation and remediation guide for an issue using the Gemini API.
    Returns the explanation string.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return (
            "AI explanation unavailable. Please configure the GEMINI_API_KEY "
            "environment variable in your .env file to enable AI reviews."
        )

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
You are CodeGuardian AI, an expert code reviewer and security engineer.
Provide a clear, detailed, yet concise explanation for the following issue.

Issue: {issue_title}
Description: {issue_desc}
Code Snippet:
```python
{code_snippet or '# Snippet not available.'}
```

Format your response in three clearly labeled sections:
1. **Explain the Bug**: What the problem is and why it happens.
2. **Risks**: The potential runtime failures or security risks if not fixed.
3. **Remediation**: Step-by-step instructions on how to correct it.
"""
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Failed to retrieve explanation from Gemini API: {str(e)}"
