#
# This file is part of the Buildings and Habitats object Model (BHoM)
# Copyright (c) 2015 - 2026, the respective contributors. All rights reserved.
#
# Each contributor holds copyright over their respective contributions.
# The project versioning (Git) records all such contribution source information.
#
#
# The BHoM is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3.0 of the License, or
# (at your option) any later version.
#
# The BHoM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this code. If not, see <https://www.gnu.org/licenses/lgpl-3.0.html>.
#

"""Check Google-style docstrings against BHoM compliance rule PY-D05.

For every public function or method whose docstring has an ``Args:`` section:

- every parameter is documented (C# IsInputAttributePresent);
- every documented name is a parameter, unless the function takes ``**kwargs``
  (C# InputAttributeHasMatchingParameter);
- parameters are documented in signature order (C# InputAttributesAreInOrder);
- each description ends with punctuation (C# AttributeHasEndingPunctuation);
- a function annotated to return something has a ``Returns:`` section (C# HasOutputAttribute).

Missing docstrings and sections are left to pylint's docparams extension (PY-D02).

Usage:
    python check_docstrings.py PATH [PATH ...]

PATH is a ``.py`` file or a folder searched recursively. Exits with status 1 if any
check fails.
"""

import ast
import re
import sys
from pathlib import Path

SECTION = re.compile(r"^\s*(Args|Arguments|Returns|Yields|Raises|Attributes|Examples?|Notes?):\s*$")
ENTRY = re.compile(r"^\s+\**(\w+)\s*(\([^)]*\))?:\s*(.*)$")
ENDING_PUNCTUATION = ".!?:)`"


def _documented_args(doc: str) -> list[tuple[str, str]]:
    """Return the name and description of each entry in a docstring's Args section.

    Args:
        doc (str):
            The cleaned docstring.

    Returns:
        list[tuple[str, str]]:
            (name, description) pairs in the order they are documented.
    """
    lines = doc.expandtabs(4).splitlines()
    entries, indent, i = [], None, 0
    while i < len(lines):
        if lines[i].strip() in ("Args:", "Arguments:"):
            i += 1
            while i < len(lines) and not SECTION.match(lines[i]):
                line = lines[i]
                if line.strip():
                    depth = len(line) - len(line.lstrip())
                    indent = depth if indent is None else indent
                    match = ENTRY.match(line)
                    if depth == indent and match:
                        entries.append([match.group(1), match.group(3).strip(), False])
                    elif entries and depth > indent and not entries[-1][2]:
                        if match:  # nested "name (type):" entries, e.g. documented **kwargs, end the description
                            entries[-1][2] = True
                        else:
                            entries[-1][1] = f"{entries[-1][1]} {line.strip()}".strip()
                i += 1
            break
        i += 1
    return [(name, text) for name, text, _ in entries]


def _check_function(path: Path, node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    """Return the PY-D05 findings for one function or method.

    Args:
        path (Path):
            The file the function is in.
        node (ast.FunctionDef | ast.AsyncFunctionDef):
            The parsed function.

    Returns:
        list[str]:
            One message per finding; empty if the docstring passes.
    """
    doc = ast.get_docstring(node)
    if not doc or ("Args:" not in doc and "Arguments:" not in doc):
        return []

    arguments = node.args.posonlyargs + node.args.args
    arguments += [node.args.vararg] if node.args.vararg else []
    arguments += node.args.kwonlyargs
    params = [a.arg for a in arguments if a.arg not in ("self", "cls")]
    documented = _documented_args(doc)
    names = [name for name, _ in documented]
    where = f"{path}:{node.lineno} {node.name}: PY-D05"
    findings = []

    if missing := [p for p in params if p not in names]:
        findings.append(f"{where} parameters not documented: {', '.join(missing)}")
    extra = [n for n in names if n not in params and n not in ("args", "kwargs")]
    if extra and node.args.kwarg is None:
        findings.append(f"{where} documented but not parameters: {', '.join(extra)}")
    in_both = [n for n in names if n in params]
    if in_both != [p for p in params if p in in_both]:
        findings.append(f"{where} Args not in signature order")
    if unpunctuated := [n for n, text in documented if text and text[-1] not in ENDING_PUNCTUATION]:
        findings.append(f"{where} description without ending punctuation: {', '.join(unpunctuated)}")
    returns_value = node.returns is not None and not (isinstance(node.returns, ast.Constant) and node.returns.value is None)
    if returns_value and not re.search(r"^\s*(Returns|Yields):", doc, re.M):
        findings.append(f"{where} no Returns section")
    return findings


def check_docstrings(paths: list[str]) -> int:
    """Run the check and print the findings.

    Args:
        paths (list[str]):
            Files or folders to check.

    Returns:
        int:
            The process exit status: 1 if any check failed, otherwise 0.
    """
    files = set()
    for raw in paths:
        path = Path(raw)
        files.update(path.rglob("*.py") if path.is_dir() else [path])
    findings = []
    for path in sorted(files):
        if path.suffix != ".py" or "__pycache__" in path.parts or path.name.startswith("test_"):
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8-sig"))):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
                findings.extend(_check_function(path, node))
    print("\n".join(findings) if findings else "PY-D05: no findings.")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(check_docstrings(sys.argv[1:]))
