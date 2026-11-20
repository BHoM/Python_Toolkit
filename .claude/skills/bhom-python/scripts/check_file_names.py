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

"""Check Python file names against BHoM compliance rules PY-F03 and PY-F07.

PY-F03: a module holds one public class or function, and the file is named after it
in snake_case (``BHoMBaseWindow`` -> ``bhom_base_window.py``). This is the Python
equivalent of the C# ObjectNameMatchesFileName / MethodNameContainsFileName checks.

PY-F07: no file or folder name contains "error" (any case). Such names fail the
BHoMBot installer check on toolkits that depend on Python_Toolkit (issue #266), so
"Error" in a class name maps to "err" in its file name (``ColourScaleError`` ->
``colour_scale_err.py``).

Usage:
    python check_file_names.py PATH [PATH ...]

PATH is a ``.py`` file or a folder searched recursively. Exits with status 1 if any
check fails.
"""

import ast
import re
import sys
from pathlib import Path

SKIPPED_FILES = ("__init__.py", "conftest.py")


def _expected_stem(name: str) -> str:
    """Return the file stem a public class or function name should have.

    Args:
        name (str):
            The class or function name.

    Returns:
        str:
            The snake_case stem, with "BHoM" kept as one word and "error" shortened to "err".
    """
    name = name.replace("BHoM", "Bhom")
    snake = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
    return snake.replace("error", "err")


def _python_files(paths: list[str]) -> list[Path]:
    """Expand the given paths into a sorted list of Python files.

    Args:
        paths (list[str]):
            Files or folders to check.

    Returns:
        list[Path]:
            Every ``.py`` file found, excluding ``__pycache__`` folders.
    """
    found = []
    for raw in paths:
        path = Path(raw)
        candidates = path.rglob("*.py") if path.is_dir() else [path]
        found.extend(p for p in candidates if p.suffix == ".py" and "__pycache__" not in p.parts)
    return sorted(set(found))


def _check_file(path: Path) -> list[str]:
    """Return the PY-F03 and PY-F07 findings for one file.

    Args:
        path (Path):
            The Python file to check.

    Returns:
        list[str]:
            One message per finding; empty if the file passes.
    """
    findings = [
        f"{path}: PY-F07 '{part}' contains 'error'"
        for part in path.parts
        if "error" in part.lower()
    ]
    if path.name in SKIPPED_FILES or path.name.startswith("test_"):
        return findings

    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    public = [
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        and not node.name.startswith("_")
    ]
    stem = path.stem.lstrip("_")
    if len(public) > 1:
        findings.append(f"{path}: PY-F03 {len(public)} public definitions ({', '.join(public)})")
    elif len(public) == 1 and _expected_stem(public[0]) != stem:
        findings.append(f"{path}: PY-F03 defines {public[0]}, expected file {_expected_stem(public[0])}.py")
    return findings


def check_file_names(paths: list[str]) -> int:
    """Run the checks and print the findings.

    Args:
        paths (list[str]):
            Files or folders to check.

    Returns:
        int:
            The process exit status: 1 if any check failed, otherwise 0.
    """
    findings = [message for path in _python_files(paths) for message in _check_file(path)]
    print("\n".join(findings) if findings else "PY-F03/PY-F07: no findings.")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(check_file_names(sys.argv[1:]))
