import os
from dotenv import load_dotenv
load_dotenv()

def generate_heuristic_explanation(issue_title, issue_desc, code_snippet=""):
    """Generates an intelligent heuristic explanation when AI API is unavailable."""
    title_lower = (issue_title or "").lower()
    desc_lower = (issue_desc or "").lower()

    if "bare except" in title_lower or "bare_except" in desc_lower or "ast001" in title_lower:
        bug = "Catching bare `except:` intercepts all exceptions, including system exits (`SystemExit`), keyboard interrupts (`KeyboardInterrupt`), and memory errors, hiding critical runtime defects."
        risks = "Can lead to infinite loops, unkillable processes, swallowed syntax errors, and extreme difficulty in debugging production failures."
        remediation = "Replace `except:` with specific exception classes (e.g., `except (ValueError, KeyError) as e:`) or at minimum `except Exception as e:` with appropriate error logging."
    elif "eval" in title_lower or "exec" in title_lower or "ast002" in title_lower:
        bug = "Using `eval()` or `exec()` executes arbitrary string input directly within the Python interpreter runtime."
        risks = "Allows arbitrary Remote Code Execution (RCE) if any part of the evaluated string originates from untrusted user input or external parameters."
        remediation = "Use safer alternatives such as `ast.literal_eval()` for evaluating literals, or rewrite logic using standard dictionary mappings, parsers, or JSON decoders."
    elif "secret" in title_lower or "key" in title_lower or "token" in title_lower:
        bug = "Sensitive credentials or API access tokens are stored directly in plaintext source code."
        risks = "Exposure of secret keys in version control or build artifacts allows unauthorized actors to compromise cloud infrastructure, databases, or third-party APIs."
        remediation = "Migrate credentials into environment variables (e.g., via `python-decouple` or `os.environ`), and load them securely from `.env` files that are ignored by version control (`.gitignore`)."
    elif "long function" in title_lower or "ast003" in title_lower:
        bug = "The function exceeds 50 lines of code, violating Single Responsibility principles."
        risks = "High cyclomatic complexity, increased defect density, reduced unit testability, and difficult code reviews."
        remediation = "Decompose the large function into smaller, single-purpose helper functions with explicit inputs and return types."
    elif "argument" in title_lower or "ast004" in title_lower:
        bug = "The function accepts more than 6 parameters, creating an overly complex calling signature."
        risks = "Increased chance of passing arguments in wrong positions, tight coupling, and brittle API contracts."
        remediation = "Refactor related parameters into a dataclass, dictionary, Pydantic model, or kwargs configuration object."
    else:
        bug = f"{issue_title}: {issue_desc or 'Identified code defect or security vulnerability in the scanned file.'}"
        risks = "May cause unexpected application crashes, performance degradation, or security weaknesses in production."
        remediation = "Refactor the affected code section following Python PEP 8 standards and secure coding best practices."

    return (
        f"### 1. **Explain the Bug**\n{bug}\n\n"
        f"### 2. **Risks**\n{risks}\n\n"
        f"### 3. **Remediation**\n{remediation}"
    )

def explain_issue(issue_title, issue_desc, code_snippet=None):
    """
    Generate an explanation and remediation guide for an issue using the Gemini API.
    Falls back to a structured heuristic rule engine if the API key is not configured.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return generate_heuristic_explanation(issue_title, issue_desc, code_snippet)

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Try primary model, fallback if needed
        for model_name in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]:
            try:
                model = genai.GenerativeModel(model_name)
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
                if response and response.text:
                    return response.text.strip()
            except Exception:
                continue

        return generate_heuristic_explanation(issue_title, issue_desc, code_snippet)
    except Exception:
        return generate_heuristic_explanation(issue_title, issue_desc, code_snippet)

