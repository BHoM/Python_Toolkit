import ast
from pathlib import Path

root = Path("c:/GitHub_Files/Python_Toolkit/Python_Engine/Python/src/python_toolkit/bhom_tkinter")
files = sorted(root.rglob("*.py"))

for path in files:
    rel = path.relative_to(root)
    src = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(src)
    except SyntaxError as error:
        print(f"{rel}|SYNTAX_ERROR|{error}")
        continue

    issues = []

    if ast.get_docstring(tree) is None:
        issues.append(("module", "<module>"))

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_") and ast.get_docstring(node) is None:
                issues.append(("function", node.name))
        elif isinstance(node, ast.ClassDef):
            if not node.name.startswith("_") and ast.get_docstring(node) is None:
                issues.append(("class", node.name))
            for member in node.body:
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if member.name.startswith("_"):
                        continue
                    if ast.get_docstring(member) is None:
                        issues.append(("method", f"{node.name}.{member.name}"))

    for kind, name in issues:
        print(f"{rel}|{kind}|{name}")
