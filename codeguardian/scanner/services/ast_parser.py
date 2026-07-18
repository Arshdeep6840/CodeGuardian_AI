import ast
import os

class CodeGuardianASTVisitor(ast.NodeVisitor):
    def __init__(self, code_content):
        self.code_content = code_content
        self.lines = code_content.splitlines()
        self.issues = []

    def get_snippet(self, start_line, end_line):
        if not self.lines:
            return ""
        s_idx = max(0, start_line - 1)
        e_idx = min(len(self.lines), end_line)
        return "\n".join(self.lines[s_idx:e_idx])

    def visit_ExceptHandler(self, node):
        if node.type is None:
            self.issues.append({
                "issue_type": "code_quality",
                "severity": "medium",
                "title": "Bare except clause detected",
                "description": "Using a bare 'except:' clause catches all exceptions, including SystemExit and KeyboardInterrupt, which can hide active bugs and make debugging very difficult.",
                "line_number": node.lineno,
                "column_number": node.col_offset,
                "code_snippet": self.get_snippet(node.lineno, getattr(node, "end_lineno", node.lineno)),
                "rule_id": "AST001"
            })
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in ["eval", "exec"]:
                self.issues.append({
                    "issue_type": "security",
                    "severity": "critical",
                    "title": f"Use of dangerous function '{func_name}'",
                    "description": f"The '{func_name}' function compiles and runs arbitrary code dynamically, causing a severe security risk if user-supplied input is passed.",
                    "line_number": node.lineno,
                    "column_number": node.col_offset,
                    "code_snippet": self.get_snippet(node.lineno, getattr(node, "end_lineno", node.lineno)),
                    "rule_id": "AST002"
                })
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # Check function length
        start = node.lineno
        end = getattr(node, "end_lineno", start)
        length = end - start + 1
        if length > 50:
            self.issues.append({
                "issue_type": "code_quality",
                "severity": "medium",
                "title": f"Function '{node.name}' is too long",
                "description": f"Function '{node.name}' is {length} lines long. Functions exceeding 50 lines should be split into smaller, modular helper functions for readability.",
                "line_number": node.lineno,
                "column_number": node.col_offset,
                "code_snippet": self.get_snippet(node.lineno, min(node.lineno + 5, end)),
                "rule_id": "AST003"
            })

        # Check argument count
        args_count = len(node.args.args)
        if args_count > 6:
            self.issues.append({
                "issue_type": "code_quality",
                "severity": "low",
                "title": f"Function '{node.name}' has too many arguments",
                "description": f"Function '{node.name}' has {args_count} parameters. Functions with more than 6 arguments are hard to test and maintain.",
                "line_number": node.lineno,
                "column_number": node.col_offset,
                "code_snippet": self.get_snippet(node.lineno, getattr(node, "end_lineno", node.lineno)),
                "rule_id": "AST004"
            })
        self.generic_visit(node)


def analyze_file(file_path):
    """Analyze a single Python file using AST and return a list of issue dicts."""
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()

        tree = ast.parse(code, filename=file_path)
        visitor = CodeGuardianASTVisitor(code)
        visitor.visit(tree)
        return visitor.issues
    except Exception as e:
        return [{
            "issue_type": "bug",
            "severity": "high",
            "title": "Syntax error / AST parsing failed",
            "description": f"Failed to parse file due to a syntax error or file read issue: {str(e)}",
            "line_number": 1,
            "column_number": 0,
            "code_snippet": "",
            "rule_id": "AST_PARSE_ERR"
        }]
