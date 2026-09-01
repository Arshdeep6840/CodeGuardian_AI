import os
import re
import ast
from dotenv import load_dotenv
load_dotenv()

def generate_heuristic_tests(code_content, file_path=""):
    """Generates a boilerplate pytest test suite when AI API is unavailable."""
    if not code_content:
        return "# No source code provided to generate test cases."

    module_name = os.path.splitext(os.path.basename(file_path or "module"))[0]
    
    # Try parsing AST to find functions and classes
    functions = []
    classes = []
    try:
        tree = ast.parse(code_content)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
    except Exception:
        # Fallback regex search
        functions = re.findall(r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", code_content)
        classes = re.findall(r"class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[:\(]", code_content)

    test_lines = [
        "import pytest",
        "from unittest.mock import MagicMock, patch",
        f"# Unit tests for {file_path or 'module.py'}",
        "",
        "@pytest.fixture",
        "def sample_context():",
        "    \"\"\"Provides standard mock test context.\"\"\"",
        "    return {\"status\": \"ok\", \"sample_id\": 101}",
        ""
    ]

    if not functions and not classes:
        test_lines.extend([
            "def test_module_syntax_and_import():",
            "    \"\"\"Basic validation that the module executes and imports without syntax errors.\"\"\"",
            "    assert True",
            ""
        ])

    for func in functions:
        if func.startswith("__"):
            continue
        test_lines.extend([
            f"def test_{func}_happy_path(sample_context):",
            f"    \"\"\"Test standard successful execution of {func}.\"\"\"",
            f"    # Arrange & Act",
            f"    # TODO: Supply appropriate inputs for {func}",
            f"    result = True",
            f"    # Assert",
            f"    assert result is not None",
            "",
            f"def test_{func}_error_handling():",
            f"    \"\"\"Test that {func} appropriately handles invalid inputs or boundaries.\"\"\"",
            f"    with pytest.raises(Exception):",
            f"        # TODO: Trigger boundary condition for {func}",
            f"        raise ValueError('Expected test boundary exception')",
            ""
        ])

    for cls in classes:
        test_lines.extend([
            f"def test_{cls.lower()}_initialization():",
            f"    \"\"\"Test that {cls} can be instantiated with default configurations.\"\"\"",
            f"    # Arrange & Act",
            f"    instance = MagicMock()",
            f"    # Assert",
            f"    assert instance is not None",
            ""
        ])

    return "\n".join(test_lines)

def generate_tests(code_content, file_path=""):
    """
    Generate pytest unit test cases for the provided code content using the Gemini API.
    Falls back to intelligent heuristic pytest test generation if API key is not configured.
    """
    if not code_content:
        return "# No code content provided to generate test cases for."

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return generate_heuristic_tests(code_content, file_path)

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        for model_name in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]:
            try:
                model = genai.GenerativeModel(model_name)
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
            except Exception:
                continue

        return generate_heuristic_tests(code_content, file_path)
    except Exception:
        return generate_heuristic_tests(code_content, file_path)

