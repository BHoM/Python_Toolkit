---
name: BHoM Python Compliance Review
description: Rule catalogue, severities, automated checks and report format for reviewing Python in Python_Toolkit.
version: 0.2.1
parent_skill: bhom-python
author: DRAFT - for QA
tags: [BHoM, Python, review, compliance, CI]
---

# BHoM Python Compliance Review

> **Use when:** asked to review, audit or compliance-check Python - a PR diff, a folder, or the whole package.
> **Scope:** BHoM CI (`.github/workflows/ci-beta.yml`, via `BHoM/CI_Toolkit`) runs build and compliance checks aimed at C#; **no Python linting, tests or copyright checks run in CI.** This review is currently the only gate for Python.

---

## Quick Navigation

- [Review Workflow](#review-workflow)
- [Automated Pass](#automated-pass)
- [Rule Catalogue](#rule-catalogue)
- [Report Format](#report-format)
- [Copyright for Python Files](#copyright-for-python-files)
- [Proposed Tool Configuration](#proposed-tool-configuration)

---

## Review Workflow

1. **Scope** - review the diff (`git diff develop...HEAD -- "*.py"`) unless asked for more. Issues on untouched lines are listed as "existing", never as blockers for the PR.
2. **Automated pass** - run the tools below in the Python_Toolkit environment; report counts, not raw dumps.
3. **Manual pass** - walk the [Rule Catalogue](#rule-catalogue) by severity. Read the code; grep hits are leads, not findings.
4. **Verify each finding** - `file:line`, the concrete failure (input -> wrong result/crash), and the fix. Drop anything you cannot substantiate.
5. **Tests** - check against [SKILL-TESTING.md](./SKILL-TESTING.md#checklist); missing tests for new public behaviour is **Major**.
6. **Report** in the [format below](#report-format). Do not edit code during a review unless asked.

Reviewer behaviour follows [bhom-coding-standards](../bhom-coding-standards/SKILL.md#ai-behavior-guidelines): concise, British English, no whitespace-only findings (black owns formatting), no suggestions where nothing needs to change.

---

## Automated Pass

From `Python_Engine/Python`, with the env's `python.exe`:

```bash
python -m black --check --diff src tests
python -m pylint src --disable=C0114 --output-format=parseable
python -m pytest tests -q --cov=python_toolkit --cov-report=term-missing
```

Greps (each hit needs a human look):

```bash
grep -rnE --include=*.py 'except\s*:' src                                   # PY-E01
grep -rnE --include=*.py '^\s*print\(' src                                  # PY-B05
grep -rnE --include=*.py 'def .*=\s*(\[\]|\{\}|[A-Za-z_.]+\(\))' src         # PY-C01 (single-line signatures only)
grep -rnE --include=*.py '(^|[^A-Za-z])[A-Z]:[/\\][^/\\]' src               # PY-S03 drive paths
grep -rnE --include=*.py 'shell=True|os\.system|eval\(|exec\(' src          # PY-S02
grep -rn  --include=*.py 'bhom_callable' src | grep -v 'bhom/wrapped/\|bhom/decorators/'   # PY-W02
python -c "import pathlib,sys; [print(p) for p in pathlib.Path(sys.argv[1]).rglob('*.py') if p.read_bytes()[:3]==b'\xef\xbb\xbf']" src   # PY-F04 BOM
```

pylint `W0102 dangerous-default-value` catches `[]`/`{}` defaults but **not** call defaults (`uuid.uuid4()`, `datetime.now()`) - check those by eye.

---

## Rule Catalogue

Severity: **Blocker** (fix before merge) / **Major** (fix in this PR unless the CI/CD lead agrees otherwise) / **Minor** (fix when touched) / **Info**.

### C#-callable methods

| ID | Sev | Rule |
|----|-----|------|
| PY-W01 | Blocker | C# calls Python **only** through `run_wrapped` (`-command <identifier> -in <json file>`). No C# code runs ad hoc scripts, `RunPythonString` snippets, or bespoke per-method CLI arguments. |
| PY-W02 | Blocker | Every C#-callable method has `@bhom_wrapper.bhom_callable("<identifier>", ...)` **and** lives under `python_toolkit/bhom/wrapped/`. A decorated method elsewhere is never registered. |
| PY-W03 | Major | `bhom/wrapped/` contains only C#-callable wrappers: thin, delegating to domain modules; module-level imports light and side-effect free (all are imported on every `run_wrapped` call). |
| PY-W04 | Major | Wrapped methods return Python objects and let `bhom_callable` encode them - no `json.dumps` in the method, and no `str` return when C# deserialises the result (strings are passed through unencoded). |
| PY-W05 | Blocker | No `print` (or other stdout output, including `CONSOLE_LOGGER.info`) in wrapped code paths - C# deserialises the whole of stdout. |
| PY-W06 | Major | Identifiers unique and stable; renaming one needs a C# deprecation path. |
| PY-W07 | Major | `argument_types` supplied for every argument that should arrive as a `BHoMObject` subclass; nested/list items converted explicitly. |
| PY-W08 | Major | Failures raise (non-zero exit, traceback on stderr, which C# detects) - no `try/except` that returns `traceback.format_exc()` or error text as the result. |

### Correctness and errors

| ID | Sev | Rule |
|----|-----|------|
| PY-C01 | Blocker | No mutable or call-evaluated defaults (`[]`, `{}`, `uuid.uuid4()`, `datetime.now()`) in signatures or dataclass fields |
| PY-C02 | Blocker | Logic does what its name/docstring says - check boolean conditions for always-true/false (e.g. `validate_timeseries` `is_annual`) |
| PY-C03 | Major | `dataclasses.field(default_factory=...)` is given a callable |
| PY-C04 | Major | Inputs not mutated unless documented in-place (the shipped `"test"` wrapped method mutates its input) |
| PY-C05 | Major | Floats compared with tolerance |
| PY-C06 | Major | Annotations match what is accepted/returned (`-> str` returning a dict; `x: str = None`) |
| PY-C07 | Minor | `is None` / `is not None`, never `== None` |
| PY-E01 | Blocker | No bare `except:` (`_bhom_callable_decorator.py`) |
| PY-E02 | Blocker | No swallowed errors: an `except` re-raises, or logs at `error` with `exc_info=True` *and* surfaces the failure |
| PY-E03 | Major | Specific exceptions, what-and-how-to-fix messages, chained with `from exc` |
| PY-E04 | Major | No `raise Exception(...)` |
| PY-E05 | Major | Inputs validated at public entry points |
| PY-E06 | Minor | No `assert` for runtime validation |

### BHoM integration

| ID | Sev | Rule |
|----|-----|------|
| PY-B02 | Major | BHoM objects use `BHoMObject`/`IObject` and `BHoMJSONEncoder`/`Decoder`; no hand-built `_t`/`BHoM_Guid` dicts or ad hoc key-case conversion |
| PY-B03 | Major | `_t` is the exact C# full type name, or `"BH.oM.Base.CustomObject"` when no C# type exists - never an invented name; attribute names round-trip to C# property names (test acronyms) |
| PY-B04 | Major | Public entry points (including wrapped methods) have `@bhom_analytics()` - with brackets, on functions/methods, not classes, private helpers or hot loops |
| PY-B05 | Major | `CONSOLE_LOGGER`, not `print`; no root-logger configuration; never log to `ANALYTICS_LOGGER` directly |
| PY-B06 | Major | No hard-coded BHoM paths where a constant or `Query` method exists; plot style via `plt.style.use("python_toolkit.bhom")` |
| PY-B07 | Major | `clr` only where needed, assemblies from `%ProgramData%\BHoM\Assemblies`, guarded for non-Windows |
| PY-B08 | Major | No import-time side effects (network, `atexit`, environment variables such as `HOME`, `sys.path`) |
| PY-B09 | Minor | Dependencies declared; pins justified; dev tools not in runtime dependencies |
| PY-B10 | Minor | Runs on the base environment's Python (3.10) |

### Security and privacy

| ID | Sev | Rule |
|----|-----|------|
| PY-S01 | Blocker | No secrets, tokens, connection strings, personal data, or project/client names in code, tests, assets or logs |
| PY-S02 | Blocker | No `eval`/`exec` on external input; no `shell=True`/`os.system` with interpolated values |
| PY-S03 | Major | No machine-specific absolute paths (`C:/Users/...`, network shares) |
| PY-S04 | Major | No committed artefacts: notebooks (`*.ipynb`), `.venv`, `__pycache__`, `.pytest_cache`, `.coverage`, `cov_html/`, data dumps |

### Documentation and style

| ID | Sev | Rule |
|----|-----|------|
| PY-D01 | Major | Type hints on every parameter and return of public functions/methods |
| PY-D02 | Major | Google-style docstrings on public modules, classes, functions; units for physical quantities; `Raises:` when it raises |
| PY-D03 | Minor | British English (third-party API names exempt) |
| PY-D04 | Minor | Docstrings match the signature; no placeholders or copy-paste |
| PY-F01 | Minor | `black`-clean (one finding, not per line) |
| PY-F02 | Minor | Absolute imports; no `import *`; no unused imports |
| PY-F03 | Minor | One public function/class per file; snake_case file names |
| PY-F04 | Minor | UTF-8 without BOM |
| PY-F05 | Info | No commented-out code; `TODO` has an issue link |

### Tests

| ID | Sev | Rule |
|----|-----|------|
| PY-T01 | Major | New/changed public behaviour has happy-path and failure-path tests |
| PY-T02 | Major | Bug fixes ship with a regression test |
| PY-T03 | Major | Wrapped methods tested on both faces (Python call and `__input_json__`) and registration |
| PY-T04 | Major | Tests independent, deterministic, no absolute paths or network; external tools skipped cleanly |
| PY-T05 | Minor | Meaningful assertions with clear messages |

---

## Report Format

```markdown
## Python review - Python_Toolkit <branch/PR>

**Scope:** <files / diff range>   **Automated:** black <n files>, pylint <score / n issues>, pytest <passed/failed, cov %>

### Blockers
1. **PY-W02** `src/python_toolkit/plot/heatmap_png.py:12` - `@bhom_callable` method outside `bhom/wrapped/`, so `run_wrapped("python_toolkit.plot.heatmap_png", ...)` raises `NotImplementedError`.
   Fix: move the wrapper to `bhom/wrapped/plot/heatmap_png.py`; keep the logic in `plot/`.

### Major
...

### Minor / Info
...

### Existing issues (not introduced by this PR)
...

### Verdict
Request changes | Approve with comments | Approve
```

- Order by severity, then file. One finding per root cause; group repeats ("PY-B05 x12 in `plot/`").
- If the tools could not be run, say so under **Automated** - never imply they passed.

---

## Copyright for Python Files

**Current state:** no `.py` file in Python_Toolkit has a copyright header, and CI does not check Python. [bhom-copyright](../bhom-copyright/SKILL.md) says the header is required for "all files in BHoM projects".

> **Decision needed (QA):** require the header on new `.py` files, or state that Python is exempt. Until decided, report missing headers as **Info**.

If required, the Python form keeps the C# text verbatim as `#` comments, above the module docstring:

```python
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

"""Module docstring."""
```

---

## Proposed Tool Configuration

Python_Toolkit has no lint or format config. **Proposal for QA** - add to `pyproject.toml` so people, Claude and a future CI job run the same checks:

```toml
[tool.black]
line-length = 120
target-version = ["py310"]

[tool.pylint.main]
py-version = "3.10"
load-plugins = ["pylint.extensions.docparams"]   # checks Args/Returns/Raises against signatures
disable = [
    "C0114",                                      # module docstring - matches the README's VS Code setting
    "R0902", "R0903", "R0904", "R0912", "R0913", "R0914", "R0915",  # "too many ..." design checks
]

[tool.pylint.basic]
good-names = ["i", "j", "k", "x", "y", "z", "df", "ax", "fig", "_"]

[tool.pylint.format]
max-line-length = 120

[tool.pytest.ini_options]
pythonpath = "src"
testpaths = ["tests"]
markers = [
    "slow: long-running tests excluded from the default run",
    "dotnet: needs pythonnet and BHoM assemblies",
]
```

Plus a CI step (Windows runner) running `black --check`, `pylint --fail-under=<agreed>` and `pytest` on `Python_Engine/Python` when `*.py` changes - to raise with the CI/CD lead as an addition to `BHoM/CI_Toolkit`.
