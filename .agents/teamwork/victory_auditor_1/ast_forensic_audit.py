import ast
import os
import re
from pathlib import Path

def run_ast_forensic_audit():
    project_root = Path(r"e:\Disco F\Dev\IANIMATION")
    backend_dir = project_root / "backend"
    src_dir = project_root / "src"
    
    print("=" * 70)
    print("PHASE 2: AST FORENSIC & INTEGRITY AUDIT")
    print("=" * 70)
    
    # Check 1: Zero-Any in Python (backend/)
    py_files = sorted(list(backend_dir.rglob("*.py")))
    any_violations = []
    
    class AnyVisitor(ast.NodeVisitor):
        def __init__(self, filename):
            self.filename = filename
            
        def visit_Import(self, node):
            for name in node.names:
                if name.name == "Any" or name.name.endswith(".Any"):
                    any_violations.append((self.filename, node.lineno, f"Import of {name.name}"))
            self.generic_visit(node)
            
        def visit_ImportFrom(self, node):
            if node.module in ("typing", "typing_extensions"):
                for name in node.names:
                    if name.name == "Any":
                        any_violations.append((self.filename, node.lineno, "ImportFrom Any"))
            self.generic_visit(node)
            
        def visit_Name(self, node):
            if node.id == "Any":
                any_violations.append((self.filename, node.lineno, "Name Any referenced"))
            self.generic_visit(node)
            
    for pf in py_files:
        try:
            content = pf.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(pf))
            visitor = AnyVisitor(str(pf.relative_to(project_root)))
            visitor.visit(tree)
        except Exception as e:
            print(f"Error parsing {pf}: {e}")
            
    print(f"\n[CHECK 1] Python Zero-Any AST Violations in backend/: {len(any_violations)}")
    for f, line, desc in any_violations:
        print(f"  FAILED: {f}:{line} - {desc}")
    if not any_violations:
        print("  PASSED: 0 Any references found in backend/ Python files.")

    # Check 2: Test fixture imports in production backend
    test_leak_violations = []
    for pf in py_files:
        content = pf.read_text(encoding="utf-8")
        rel_path = str(pf.relative_to(project_root))
        for lineno, line in enumerate(content.splitlines(), 1):
            if re.search(r"^\s*from\s+tests\b", line) or re.search(r"^\s*import\s+tests\b", line):
                test_leak_violations.append((rel_path, lineno, line.strip()))
                
    print(f"\n[CHECK 2] Production importing test fixtures: {len(test_leak_violations)}")
    for f, line, code in test_leak_violations:
        print(f"  FAILED: {f}:{line} - {code}")
    if not test_leak_violations:
        print("  PASSED: 0 test fixture imports in backend/ production code.")

    # Check 3: Facade & Hardcoded constant returns in backend
    print(f"\n[CHECK 3] Deep AST Inspection for Facades & Hardcoded constants")
    facade_flags = []
    for pf in py_files:
        rel_path = str(pf.relative_to(project_root))
        content = pf.read_text(encoding="utf-8")
        try:
            tree = ast.parse(content, filename=str(pf))
            for node in ast.walk(tree):
                # Check for functions returning constant string/number without any other logic
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    body = [n for n in node.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))] # exclude docstrings
                    if len(body) == 1 and isinstance(body[0], ast.Return):
                        ret_val = body[0].value
                        if isinstance(ret_val, ast.Constant):
                            # trivial constant return
                            facade_flags.append((rel_path, node.lineno, f"Function '{node.name}' only returns constant {repr(ret_val.value)}"))
                        elif isinstance(ret_val, (ast.List, ast.Dict, ast.Set)) and len(ret_val.elts if hasattr(ret_val, 'elts') else ret_val.keys) == 0:
                            facade_flags.append((rel_path, node.lineno, f"Function '{node.name}' only returns empty container"))
                    # Check for functions containing only pass or raise NotImplementedError
                    elif len(body) == 1 and isinstance(body[0], ast.Pass):
                        # Abstract methods or empty pass
                        pass
                    elif len(body) == 1 and isinstance(body[0], ast.Raise) and isinstance(body[0].exc, ast.Call):
                        if getattr(body[0].exc.func, 'id', None) == 'NotImplementedError':
                            facade_flags.append((rel_path, node.lineno, f"Function '{node.name}' raises NotImplementedError"))
        except Exception as e:
            print(f"Error checking {pf}: {e}")
            
    print(f"  Trivial/Facade candidates found: {len(facade_flags)}")
    for f, line, desc in facade_flags:
        print(f"  FLAG: {f}:{line} - {desc}")

    # Check 4: Specific previously flagged items
    print("\n[CHECK 4] Specific Previously Flagged Items:")
    # Check neural.py for queue_prompt
    neural_file = backend_dir / "ai" / "neural.py"
    if neural_file.exists():
        content = neural_file.read_text(encoding="utf-8")
        if "prompt_mock_id_12345" in content:
            print("  FAILED: neural.py still contains static 'prompt_mock_id_12345'")
        else:
            print("  PASSED: neural.py static prompt_mock_id_12345 was removed/replaced.")
            
    # Check mocap.py for hardcoded frame_count=90, duration=3.0
    mocap_file = backend_dir / "ai" / "mocap.py"
    if mocap_file.exists():
        content = mocap_file.read_text(encoding="utf-8")
        if "frame_count=90" in content:
            print("  FAILED: mocap.py still contains hardcoded frame_count=90")
        else:
            print("  PASSED: mocap.py dynamic calculation implemented.")

    # Check image_to_3d.py for hardcoded vertex_count=8, polygon_count=12
    img3d_file = backend_dir / "ai" / "image_to_3d.py"
    if img3d_file.exists():
        content = img3d_file.read_text(encoding="utf-8")
        if "vertex_count=8" in content and "polygon_count=12" in content:
            print("  WARNING/FLAG: image_to_3d.py contains vertex_count=8, polygon_count=12")
        else:
            print("  PASSED: image_to_3d.py counts.")

    # Check 5: TypeScript Zero-Any in src/
    ts_files = sorted(list(src_dir.rglob("*.ts")) + list(src_dir.rglob("*.tsx")))
    ts_any_violations = []
    # Match any keyword not in word, e.g. ": any", "<any>", "as any", "any[]"
    any_regex = re.compile(r"\bany\b")
    # comments regex
    for tf in ts_files:
        rel_path = str(tf.relative_to(project_root))
        content = tf.read_text(encoding="utf-8")
        for lineno, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            if any_regex.search(line):
                # verify it's not 'company', 'many', etc. \bany\b handles words,
                # but check if it's in string literal
                ts_any_violations.append((rel_path, lineno, line.strip()))
                
    print(f"\n[CHECK 5] TypeScript 'any' occurrences in src/: {len(ts_any_violations)}")
    for f, line, code in ts_any_violations:
        print(f"  FLAG: {f}:{line} - {code}")
    if not ts_any_violations:
        print("  PASSED: 0 'any' occurrences found in src/ TypeScript files.")

if __name__ == "__main__":
    run_ast_forensic_audit()
