import ast
import os
import math

class ComplexityVisitor(ast.NodeVisitor):
    """
    AST visitor to compute Cyclomatic Complexity and nesting depth for functions and methods.
    """
    def __init__(self, lines):
        self.lines = lines
        self.issues = []
        self.function_complexities = []
        self.current_depth = 0

    def _get_snippet(self, start_line, end_line):
        if not self.lines:
            return ""
        s = max(0, start_line - 1)
        e = min(len(self.lines), end_line)
        return "\n".join(self.lines[s:e])

    def _compute_node_complexity(self, func_node):
        """
        Calculates Cyclomatic Complexity (McCabe metric) for a given function AST node.
        Base complexity = 1.
        Increments for: if, for, while, except, with, assert, and/or expressions, ifexp.
        """
        complexity = 1
        max_depth = 0
        depth = 0

        for child in ast.walk(func_node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With, ast.Assert)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # 'and' and 'or' count as additional decision points
                complexity += max(1, len(child.values) - 1)
            elif isinstance(child, ast.IfExp):
                complexity += 1

        # Calculate max nesting depth
        def check_depth(node, cur):
            nonlocal max_depth
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                cur += 1
                if cur > max_depth:
                    max_depth = cur
            for c in ast.iter_child_nodes(node):
                check_depth(c, cur)

        check_depth(func_node, 0)
        return complexity, max_depth

    def visit_FunctionDef(self, node):
        self._analyze_func(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self._analyze_func(node)
        self.generic_visit(node)

    def _analyze_func(self, node):
        start = node.lineno
        end = getattr(node, "end_lineno", start)
        cc, max_depth = self._compute_node_complexity(node)
        self.function_complexities.append({
            "name": node.name,
            "lineno": start,
            "complexity": cc,
            "nesting_depth": max_depth,
            "lines": end - start + 1
        })

        # Check for critical complexity (CC > 15)
        if cc > 15:
            self.issues.append({
                "issue_type": "complexity",
                "severity": "high",
                "title": f"Critical Cyclomatic Complexity in '{node.name}' (CC: {cc})",
                "description": (
                    f"Function '{node.name}' has a Cyclomatic Complexity of {cc} (threshold: 10). "
                    "Functions with extremely high complexity are error-prone, hard to test, and difficult to maintain. "
                    "Refactor into smaller modular helper functions or simplify decision logic."
                ),
                "line_number": start,
                "column_number": node.col_offset,
                "code_snippet": self._get_snippet(start, min(start + 8, end)),
                "rule_id": "COMP002"
            })
        elif cc > 10:
            self.issues.append({
                "issue_type": "complexity",
                "severity": "medium",
                "title": f"High Cyclomatic Complexity in '{node.name}' (CC: {cc})",
                "description": (
                    f"Function '{node.name}' has a Cyclomatic Complexity of {cc} (threshold: 10). "
                    "Consider breaking complex condition chains into distinct routines."
                ),
                "line_number": start,
                "column_number": node.col_offset,
                "code_snippet": self._get_snippet(start, min(start + 8, end)),
                "rule_id": "COMP001"
            })

        # Check for deeply nested control flow (depth > 4)
        if max_depth > 4:
            self.issues.append({
                "issue_type": "complexity",
                "severity": "medium",
                "title": f"Deeply nested control structures in '{node.name}' (Depth: {max_depth})",
                "description": (
                    f"Function '{node.name}' has a nesting depth of {max_depth} levels (maximum recommended: 4). "
                    "Deep nesting reduces readability and increases cognitive load. Use early returns or guard clauses."
                ),
                "line_number": start,
                "column_number": node.col_offset,
                "code_snippet": self._get_snippet(start, min(start + 8, end)),
                "rule_id": "COMP003"
            })


def analyze_file_complexity(file_path):
    """
    Analyzes complexity metrics for a Python file.
    Returns:
      issues: list of issue dicts
      metrics: dict with total_functions, avg_complexity, max_complexity, maintainability_index
    """
    if not os.path.exists(file_path):
        return [], {"maintainability_index": 100.0, "avg_complexity": 1.0}

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()

        lines = code.splitlines()
        loc = max(1, len([l for l in lines if l.strip() and not l.strip().startswith("#")]))

        tree = ast.parse(code, filename=file_path)
        visitor = ComplexityVisitor(lines)
        visitor.visit(tree)

        funcs = visitor.function_complexities
        total_funcs = len(funcs)
        avg_cc = sum(f["complexity"] for f in funcs) / total_funcs if total_funcs > 0 else 1.0
        max_cc = max((f["complexity"] for f in funcs), default=1.0)

        # Normalized Maintainability Index (0 - 100)
        # Higher is better: 100 is pristine, < 50 is hard to maintain
        raw_mi = 171 - (0.23 * avg_cc) - (16.2 * math.log(loc))
        normalized_mi = max(0.0, min(100.0, (raw_mi * 100.0 / 171.0)))

        metrics = {
            "loc": loc,
            "total_functions": total_funcs,
            "avg_complexity": round(avg_cc, 1),
            "max_complexity": max_cc,
            "maintainability_index": round(normalized_mi, 1),
            "functions": funcs
        }

        return visitor.issues, metrics
    except Exception as e:
        return [], {"maintainability_index": 100.0, "avg_complexity": 1.0, "error": str(e)}
