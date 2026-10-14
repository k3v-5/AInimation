"""
AST Scanner for Zero-Any Policy & Strict Typing in backend/ and src/
Audits:
- Usage of typing.Any or Any in type annotations in Python
- Untyped function parameters or missing return annotations in Python
- 'any' type usage in TypeScript/TSX files
"""
import ast
import os
import re
import sys
from pathlib import Path

def scan_python_file(file_path: Path):
    violations = []
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))
    except Exception as e:
        return [f"PARSE_ERROR in {file_path}: {e}"]

    class TypeVisitor(ast.NodeVisitor):
        def __init__(self):
            self.imported_any = False

        def visit_ImportFrom(self, node):
            if node.module == "typing":
                for alias in node.names:
                    if alias.name == "Any":
                        self.imported_any = True
                        violations.append(f"{file_path}:{node.lineno}: 'Any' imported from typing")
            self.generic_visit(node)

        def visit_Import(self, node):
            for alias in node.names:
                if alias.name == "typing":
                    pass
            self.generic_visit(node)

        def check_annotation(self, node, lineno, context):
            if node is None:
                violations.append(f"{file_path}:{lineno}: Missing type annotation on {context}")
                return
            for sub in ast.walk(node):
                if isinstance(sub, ast.Name) and sub.id == "Any":
                    violations.append(f"{file_path}:{lineno}: Forbidden 'Any' used in {context}")
                elif isinstance(sub, ast.Attribute) and sub.attr == "Any":
                    violations.append(f"{file_path}:{lineno}: Forbidden 'typing.Any' used in {context}")

        def visit_FunctionDef(self, node):
            self.check_function(node)
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node):
            self.check_function(node)
            self.generic_visit(node)

        def check_function(self, node):
            # Check return annotation unless __init__
            if node.name != "__init__":
                if node.returns is None:
                    violations.append(f"{file_path}:{node.lineno}: Function '{node.name}' missing return type annotation")
                else:
                    self.check_annotation(node.returns, node.lineno, f"return type of '{node.name}'")
            elif node.returns is not None:
                self.check_annotation(node.returns, node.lineno, f"return type of '__init__'")

            # Check arguments
            args = node.args
            all_args = args.posonlyargs + args.args + args.kwonlyargs
            for arg in all_args:
                if arg.arg in ("self", "cls"):
                    continue
                if arg.annotation is None:
                    violations.append(f"{file_path}:{arg.lineno}: Parameter '{arg.arg}' of function '{node.name}' missing type annotation")
                else:
                    self.check_annotation(arg.annotation, arg.lineno, f"parameter '{arg.arg}' of '{node.name}'")

            if args.vararg:
                if args.vararg.annotation is None:
                    violations.append(f"{file_path}:{args.vararg.lineno}: *{args.vararg.arg} missing type annotation in '{node.name}'")
                else:
                    self.check_annotation(args.vararg.annotation, args.vararg.lineno, f"*{args.vararg.arg} in '{node.name}'")

            if args.kwarg:
                if args.kwarg.annotation is None:
                    violations.append(f"{file_path}:{args.kwarg.lineno}: **{args.kwarg.arg} missing type annotation in '{node.name}'")
                else:
                    self.check_annotation(args.kwarg.annotation, args.kwarg.lineno, f"**{args.kwarg.arg} in '{node.name}'")

    visitor = TypeVisitor()
    visitor.visit(tree)
    return violations

def scan_ts_file(file_path: Path):
    violations = []
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        # Look for : any, as any, <any>, Promise<any>, Array<any>, Record<..., any>
        any_patterns = [
            re.compile(r":\s*any\b"),
            re.compile(r"\bas\s+any\b"),
            re.compile(r"<\s*any\s*>"),
            re.compile(r"Promise<\s*any\s*>"),
            re.compile(r"Record<[^,]+,\s*any\s*>"),
            re.compile(r"\bany\[\]"),
        ]
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            for pat in any_patterns:
                if pat.search(line):
                    violations.append(f"{file_path}:{i}: TS forbidden 'any' detected: {line.strip()}")
                    break
    except Exception as e:
        violations.append(f"TS_READ_ERROR in {file_path}: {e}")
    return violations

def main():
    backend_dir = Path(r"e:\Disco F\Dev\IANIMATION\backend")
    src_dir = Path(r"e:\Disco F\Dev\IANIMATION\src")

    py_violations = []
    for py_file in backend_dir.rglob("*.py"):
        v = scan_python_file(py_file)
        py_violations.extend(v)

    ts_violations = []
    for ts_file in src_dir.rglob("*"):
        if ts_file.suffix in (".ts", ".tsx"):
            v = scan_ts_file(ts_file)
            ts_violations.extend(v)

    print(f"=== ZERO-ANY SCAN RESULTS ===")
    print(f"Backend Python violations: {len(py_violations)}")
    for v in py_violations[:50]:
        print(f"  PY: {v}")
    if len(py_violations) > 50:
        print(f"  ... and {len(py_violations) - 50} more")

    print(f"\nFrontend TypeScript violations: {len(ts_violations)}")
    for v in ts_violations:
        print(f"  TS: {v}")

    if py_violations or ts_violations:
        sys.exit(1)
    else:
        print("\nAll files 100% compliant with Zero-Any Policy!")
        sys.exit(0)

if __name__ == "__main__":
    main()
