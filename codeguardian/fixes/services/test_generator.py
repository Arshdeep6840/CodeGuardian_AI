import os
import google.generativeai as genai

def generate_tests(code_content, file_path=""):
    """
    Generate pytest unit test cases for the provided code content using the Gemini API.
    Returns the python code containing the test suite.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return (
            "# AI Test Case Generator unavailable.\n"
            "# Please configure the GEMINI_API_KEY environment variable in your .env file."
        )

    if not code_content:
        return "# No code content provided to generate test cases for."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3.5-flash")
        
        prompt = f"""
You are CodeGuardian AI, a senior QA and Python developer.
Write a comprehensive unit test suite using `pytest` for the code block below.

File Location: {file_path or 'code_file.py'}
Source Code:
```python
{code_content}
```

Guidelines:
1. Structure the test suite using `pytest` framework best practices.
2. Implement test cases for standard happy paths, error boundaries, and input validations.
3. If this code references Django models, views, or endpoints, use mocks or standard django test client mocks.
4. Mock any outbound HTTP requests or filesystem operations.
5. Provide ONLY the final python test code. Do not include markdown code block formatting (like ```python) or any other conversational text. Return only the valid python source.
"""
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean markdown code blocks if returned
        if text.startswith("```python"):
            text = text[9:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()
        
    except Exception as e:
        return f"# Failed to generate pytest test suite: {str(e)}"
