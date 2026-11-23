---
name: BHoM Python Compliance Review
description: Rule catalogue, severities, automated checks and report format for reviewing Python in Python_Toolkit.
version: 0.3.0
parent_skill: bhom-python
author: BHoM
tags: [BHoM, Python, review, compliance, CI]
---

# BHoM Python Compliance Review

> **Use when:** asked to review, audit or compliance-check Python - a PR diff, a folder, or the whole package.
> **Scope:** BHoM CI (`.github/workflows/ci-beta.yml`, via `BHoM/CI_Toolkit`) runs its code, copyright and documentation compliance on `*.cs` files only; **no Python linting, tests or copyright checks run in CI.** This review is currently the only gate for Python. One BHoMBot check does reach Python: the **installer** check on dependent toolkits fails when a Python file name contains "error" ([#266](https://github.com/BHoM/Python_Toolkit/issues/266)), which PY-F07 catches before the bot does.

---

## Quick Navigation

- [Review Workflow](#review-workflow)
- [Automated Pass](#automated-pass)
- [Rule Catalogue](#rule-catalogue)
- [BHoM Compliance Mapping](#bhom-compliance-mapping)
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
grep -rL --include=*.py 'Buildings and Habitats object Model (BHoM)' src tests   # PY-F06 files missing the header
find . -iname '*error*' -not -path '*/__pycache__/*'                          # PY-F07 any file or folder named "error"
```

BHoM compliance scripts shipped with this skill (paths relative to the repo root; exit status 1 on any finding). Pass folders for a full audit, or only the changed files for a PR review:

```bash
SKILL=.claude/skills/bhom-python/scripts
python $SKILL/check_file_names.py Python_Engine/Python/src Python_Engine/Python/tests   # PY-F03, PY-F07
python $SKILL/check_docstrings.py Python_Engine/Python/src                             # PY-D05
python $SKILL/check_file_names.py $(git diff --name-only develop...HEAD -- '*.py')      # changed files only
```

Calibration on `develop` at `45d527b`: PY-F07 none (fixed by #267), PY-F03 34 existing, PY-D05 9 existing. Before #267 the file-name check flagged `colour_scales/errors.py` under both PY-F07 and PY-F03. Use relative paths: PY-F07 inspects every folder in the path you pass.

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
| PY-C04 | Major | Inputs not mutated unless documented in-place. **Exception:** methods in `bhom/wrapped/` may modify their inputs, which are copies deserialised from C# JSON |
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
| PY-B11 | Major | `BHoMObject` subclasses declare real attributes for their data; `custom_data` is not used as a substitute for properties (C# `IsUsingCustomData`) |

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
| PY-D02 | Major | Google-style docstrings on public modules, classes, functions; units for physical quantities; every default value documented ("Defaults to ..."); `Raises:` when it raises |
| PY-D03 | Minor | British English (third-party API names exempt) |
| PY-D04 | Minor | No placeholder (`"""_"""`) or copy-pasted docstrings |
| PY-D05 | Major | `Args:` documents every parameter, only real parameters (unless `**kwargs`), in signature order; each description ends with punctuation; a function that returns a value has `Returns:` (`check_docstrings.py`) |
| PY-F01 | Minor | `black`-clean (one finding, not per line) |
| PY-F02 | Minor | Absolute imports; no `import *`; no unused imports |
| PY-F03 | Major | One public function/class per file, and the file is named after it in snake_case: `BHoMBaseWindow` -> `bhom_base_window.py`, `ColourScaleError` -> `colour_scale_err.py` (see PY-F07). Grab-bag names (`errors.py`, `utils.py`, `misc.py`, `common.py`) are not allowed for new files (`check_file_names.py`) |
| PY-F04 | Minor | UTF-8 without BOM |
| PY-F05 | Info | No commented-out code; `TODO` has an issue link |
| PY-F06 | Major | BHoM copyright header at the top of every new or changed `.py` file (source and tests), with the current end year ([template](#copyright-for-python-files)) |
| PY-F07 | Blocker | No file or folder under `Python_Engine/Python` (source, tests or assets) has "error" in its name, in any case. It fails the BHoMBot installer check on dependent toolkits ([#266](https://github.com/BHoM/Python_Toolkit/issues/266), fixed by renaming `errors.py` to `colour_scale_err.py` in #267). Use `err` or a specific name (`check_file_names.py`, `find`) |

### Tests

| ID | Sev | Rule |
|----|-----|------|
| PY-T01 | Major | New/changed public behaviour has success-path and failure-path tests |
| PY-T02 | Major | Bug fixes ship with a regression test |
| PY-T03 | Major | Wrapped methods tested on both faces (Python call and `__input_json__`) and registration |
| PY-T04 | Major | Tests independent, deterministic, no absolute paths or network; external tools skipped cleanly |
| PY-T05 | Minor | Meaningful assertions with clear messages |

---

## BHoM Compliance Mapping

BHoM's code compliance (`CodeComplianceTest_Engine` in `BHoM/Test_Toolkit`) is a set of C# checks. These are their Python equivalents in this skill. C# checks with no Python meaning (attributes, `static` classes, `virtual` properties, constructors, Convert/Create naming) are left out.

| BHoM check | Python rule | Automated by |
|------------|-------------|--------------|
| BHoMBot installer check (file names) | PY-F07 | `check_file_names.py`, `find` |
| `ObjectNameMatchesFileName`, `MethodNameContainsFileName` | PY-F03 | `check_file_names.py` |
| `HasValidCopyright` | PY-F06 | `grep -rL` |
| `IsInputAttributePresent`, `InputAttributeHasMatchingParameter`, `InputAttributesAreInOrder` | PY-D05 | `check_docstrings.py` |
| `AttributeHasEndingPunctuation` | PY-D05 | `check_docstrings.py` |
| `HasOutputAttribute` | PY-D05 | `check_docstrings.py` |
| `HasDescriptionAttribute` | PY-D02 | pylint `docparams` |
| `InputParameterStartsLower` | S9 (snake_case parameters) | pylint `invalid-name` |
| `IsUsingCustomData` | PY-B11 | manual |
| `HasValidPreviousVersionAttribute` (versioning) | PY-W06 (stable wrapped identifiers) | manual |

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

**Every `.py` file - source and tests - carries the BHoM copyright header**, as [bhom-copyright](../bhom-copyright/SKILL.md) requires for all BHoM files (PY-F06).

- **Form:** the C# header text verbatim, as `#` comments, at the very top of the file, above the module docstring (and so above any `from __future__` import).
- **Year:** `2015 - <current year>`. When you modify a file, update the end year to the current year, exactly as bhom-copyright describes.
- **Existing files:** no `.py` file in Python_Toolkit has the header yet. Add it to every new file and to every existing file a PR changes. Missing headers on untouched files go under "Existing issues", not as blockers.
- **CI:** the BHoM copyright check does not cover Python, so this review is what enforces it.

Template (use the current year):

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

Python_Toolkit has no lint or format config. **Proposal** - add to `pyproject.toml` so people, Claude and a future CI job run the same checks:

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
