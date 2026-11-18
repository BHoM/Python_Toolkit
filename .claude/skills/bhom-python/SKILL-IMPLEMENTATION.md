---
name: BHoM Python Implementation
description: Package layout, packaging, environments and code style for writing Python in Python_Toolkit.
version: 0.2.7
parent_skill: bhom-python
author: DRAFT - for QA
tags: [BHoM, Python, structure, style, packaging]
---

# BHoM Python Implementation

> **Use when:** adding or changing Python in Python_Toolkit - a new module, function or class, or packaging/environment changes.
> **Authority:** `Python_Engine/Python/README.md` ("BHoM/Python specific style guidance") is the published standard. Where it is silent, PEP 8 applies. Rules stricter than the README are marked **(proposed)** for QA.

---

## Quick Navigation

- [Most Common Task: Add a Function](#most-common-task-add-a-function)
- [Package Layout](#package-layout)
- [Packaging and Environments](#packaging-and-environments)
- [Style Rules](#style-rules)
- [Errors and Validation](#errors-and-validation)
- [Performance and Data](#performance-and-data)
- [Security and Privacy](#security-and-privacy)
- [Checklist](#checklist)

---

## Most Common Task: Add a Function

`src/python_toolkit/helpers/degree_days.py`:

```python
"""Heating and cooling degree-day calculations."""

import pandas as pd

from python_toolkit.bhom.analytics import bhom_analytics
from python_toolkit.bhom.logging import CONSOLE_LOGGER
from python_toolkit.helpers.timeseries import validate_timeseries


@bhom_analytics()
def heating_degree_days(air_temperature: pd.Series, base_temperature: float = 15.5) -> float:
    """Calculate heating degree days from an hourly air temperature series.

    Args:
        air_temperature (pd.Series):
            Hourly dry-bulb air temperature in degC, with a DatetimeIndex.
        base_temperature (float, optional):
            Base temperature in degC below which heating is required. Defaults to 15.5 (CIBSE TM41).

    Returns:
        float:
            Heating degree days in K.day.

    Raises:
        TypeError: If air_temperature is not a pandas Series with a DatetimeIndex.
        ValueError: If air_temperature is empty.
    """
    validate_timeseries(air_temperature, is_hourly=True)
    if air_temperature.empty:
        raise ValueError("air_temperature is empty - provide at least one day of hourly data.")

    if air_temperature.isna().any():
        CONSOLE_LOGGER.warning("air_temperature contains NaN values; these hours are ignored.")

    deficit = (base_temperature - air_temperature).clip(lower=0)
    return float(deficit.sum() / 24)
```

The BHoM copyright header goes above the module docstring (S21); it is left out of the examples in this skill for length.

What this shows: one public function per file, file named after it, module docstring, absolute imports grouped stdlib / third-party / python_toolkit, full type hints, Google docstring with units and `Raises`, validation at entry, a specific exception with a fix-it message, a warning via `CONSOLE_LOGGER`, analytics on the public entry point, vectorised pandas, a plain `float` return (not `numpy.float64`).

If C# needs to call it, add a thin wrapper under `bhom/wrapped/` - see [SKILL-FRAMEWORK.md](./SKILL-FRAMEWORK.md#c-callable-methods-bhom_callable--run_wrapped). Then add tests - see [SKILL-TESTING.md](./SKILL-TESTING.md).

---

## Package Layout

```
Python_Toolkit/
├── Python_Engine/                 # C#: BH.Engine.Python (environments, RunCommandStdout, ...)
│   └── Python/
│       ├── README.md              # published BHoM Python guidance
│       ├── pyproject.toml
│       ├── setup.py               # reads VERSION.txt written by the build
│       ├── Dockerfile
│       ├── run_tests.bat
│       ├── src/python_toolkit/
│       │   ├── __init__.py        # package constants
│       │   ├── bhom/              # BHoM integration
│       │   │   ├── analytics.py, util.py, bhom_object.py, installer_info.py
│       │   │   ├── logging/       # CONSOLE_LOGGER, ANALYTICS_LOGGER
│       │   │   ├── decorators/    # bhom_wrapper.bhom_callable
│       │   │   ├── wrapped/       # ALL C#-callable methods, and nothing else
│       │   │   └── run_wrapped.py # the single C# entry point
│       │   ├── bhom_tkinter/      # BHoM-styled tkinter windows and widgets
│       │   ├── helpers/           # general helpers (time series, decay, cardinality)
│       │   ├── plot/              # matplotlib plots
│       │   └── units/             # unit conversion enums
│       └── tests/
└── Python_oM/                     # C#: BH.oM.Python (PythonEnvironment, PythonVersion)
```

Rules:

- **One public function or class per file**, file named in snake_case after it (`AThing` -> `a_thing.py`, `do_stuff` -> `do_stuff.py`). Private helpers used only by that function may sit in the same file with a leading `_` (README).
- Organise by domain into sub-packages; general helpers go in `helpers/` (README).
- **C#-callable methods live in `bhom/wrapped/` and nowhere else; `bhom/wrapped/` holds only C#-callable methods** - thin wrappers calling into the domain sub-packages.
- Keep `__init__.py` files light: constants, re-exports and small setup are fine, but nothing heavy or surprising happens on import (see S20).
- New sub-packages need an `__init__.py` and, if they ship non-`.py` files, an entry in `[tool.setuptools.package-data]`.

---

## Packaging and Environments

| Item | Rule |
|------|------|
| Python version | Base environment default is `PythonVersion.v3_10` (`Compute.BasePythonEnvironment`). Code must run on 3.10 - no 3.11+ syntax or stdlib (`tomllib`, `ExceptionGroup`, `typing.Self`). |
| `requires-python` | **(proposed)** Add `requires-python = ">=3.10"` to `pyproject.toml` (currently absent). |
| Version number | Never hard-code. `setup.py` reads `VERSION.txt`, written by the `Python_Engine.csproj` build step from the assembly `FileVersion`. |
| Dependencies | `[project] dependencies` in `pyproject.toml`. Pin a package only with a stated reason (comment) - every BHoM toolkit environment installs python_toolkit first, so tight pins here constrain all of them. |
| Test/dev tools | `[dependency-groups] dev`. **(proposed)** `pytest`, `pytest-cov` and `pytest-order` are currently runtime dependencies - move them. `jupyterlab` stays a runtime dependency: notebooks are expected to work in non-dev environments. |
| Package data | Non-`.py` files (`.mplstyle`, `.tcl`, `.png`) must be listed in `[tool.setuptools.package-data]` or they are missing after install. Currently only `*.mplstyle` is listed - check `.tcl` theme files and `bhom/assets/*.png` are covered. |
| Paths | C# side: `BH.Engine.Python.Query.*`. Python side: `BHOM_LOG_FOLDER`, `os.environ["PROGRAMDATA"]`, `Path(__file__)` - never literal `C:\...` paths. |
| Deploying | Build `Python_Engine` (post-build copy to `%ProgramData%\BHoM\Extensions\PythonCode\Python_Toolkit`), then `UpdateBHoMPackages`. `run_tests.bat` tests that deployed copy. |
| Notebooks | Fine for local exploration (`%load_ext autoreload` / `%autoreload 2`), but **never committed** - `*.ipynb` is in `.gitignore`. Anything worth keeping moves into the package or a pytest test. |

---

## Style Rules

Formatting is mechanical: **black** (installed in every BHoM environment). Do not hand-argue formatting in review.

### Required (README)

| # | Rule |
|---|------|
| S1 | PEP 8, formatted with `black`. |
| S2 | **Absolute imports** - `from python_toolkit.plot.heatmap import heatmap`, not `from ..plot import heatmap`. (Much of `bhom/` still uses relative imports - fix when touched.) |
| S3 | **Type hints on every function and method** - all parameters and the return (`-> None` included). |
| S4 | **Google-style docstrings** on every module, class and function/method (dunders excepted). Methods of a documented class need at least a one-line description. |
| S5 | Give a sensible default wherever a typical user would not know what to enter (settings, tolerances, styling). Leave the default off only for inputs the user must supply (e.g. the data being processed). **Document every default in the docstring** ("Defaults to 15.5."). The README words this more strictly ("If in doubt do not include a default"); this is the agreed reading. |
| S6 | Real defaults in the signature, not `x=None` then `if x is None: x = ...` - **except mutable or call-evaluated defaults**, which must use `None` (S10). |
| S7 | One public function/class per file; snake_case file names. |

### Required (proposed)

| # | Rule |
|---|------|
| S8 | **British English** in names, docstrings, messages and comments (`colour`, `normalise`, `analyse`) - as [bhom-coding-standards](../bhom-coding-standards/SKILL.md). Third-party API names keep their spelling (`cmap`, `color=`). Existing exports such as `lighten_color` stay for compatibility. |
| S9 | `snake_case` functions/variables/modules, `PascalCase` classes, `UPPER_SNAKE` module constants, `_leading` for private. No single-letter names outside comprehensions and maths. |
| S10 | **No mutable or call-evaluated defaults** - not `[]`, `{}`, `uuid.uuid4()`, `datetime.now()`, `pd.Series()` in a signature or dataclass field. Use `None` or `field(default_factory=...)`. |
| S11 | `pathlib.Path` for paths; accept `str | Path` and convert once at entry. Text files opened with explicit `encoding="utf-8"`. |
| S12 | f-strings for message text. |
| S13 | No `print()` - use `CONSOLE_LOGGER` ([SKILL-FRAMEWORK.md](./SKILL-FRAMEWORK.md#logging)). |
| S14 | No `import *`, unused imports, commented-out code blocks, or `TODO` without an issue link. |
| S15 | Units in names or docstrings for every physical quantity (`air_temperature` "in degC"); SI by default, as BHoM. |
| S16 | Magic numbers named as module constants with their source (`TM52_CRITERION_1_K = 1.0  # CIBSE TM52 criterion 1`). |
| S17 | Typing compatible with 3.10: `list[str]`, `X | None` are fine; one style per file (don't mix with `Optional`/`List`). |
| S18 | `# pylint: disable=...` only with the specific code and a reason; no blanket disables around import blocks. |
| S19 | UTF-8 **without BOM** (24 files in `src` currently start with a BOM). |
| S20 | No work at import time in package modules: no network, `atexit`, environment-variable changes, or `sys.path` edits. Modules in `bhom/wrapped/` are imported on every `run_wrapped` call - keep them especially light. |
| S21 | **BHoM copyright header** at the very top of every `.py` file, source and tests, as `#` comments above the module docstring; end year = current year, updated whenever the file is modified. Template: [SKILL-REVIEW.md](./SKILL-REVIEW.md#copyright-for-python-files). |

### Docstring template (Google)

```python
def function_name(param_a: int, param_b: str | None = None) -> list[str]:
    """One-line summary in the imperative mood.

    Optional longer description: method, assumptions, references (standard + clause).

    Args:
        param_a (int):
            What it is, units, valid range.
        param_b (str | None, optional):
            What it is. Defaults to None, meaning ...

    Returns:
        list[str]:
            What comes back.

    Raises:
        ValueError: When and why.
    """
```

`bhom/analytics.py` uses numpy-style sections (`Returns\n-------`) - legacy; new code uses Google style. Placeholder docstrings (`"""_"""`) fail review.

---

## Errors and Validation

README: errors are handled gracefully; the user is told **what went wrong and how to fix it**; specific exceptions are preferred; errors are captured at the lowest possible level.

- Validate inputs at public entry points (types, ranges, lengths, index alignment), as C# BHoM does.
- Raise specific built-ins (`ValueError`, `TypeError`, `FileNotFoundError`, `KeyError`), or a package exception that subclasses one (`class TimeseriesError(ValueError)`), so callers can catch either.
- Message = what + how to fix: `f"EPW file not found: {path}. Check the path exists."`.
- **No bare `except:`.** `except Exception` only at a boundary (UI callback, analytics wrapper), logged with `exc_info=True`, then re-raised or turned into an explicit error - never `pass`, never a silent `None`.
- Chain causes: `raise ValueError("...") from exc`.
- No `assert` for runtime validation (stripped under `-O`).
- Caveats on a result -> `CONSOLE_LOGGER.warning`. `warnings.warn` only for genuine deprecations.
- **Wrapped methods:** let exceptions propagate - the process exits non-zero and C# receives the traceback as stderr. Do not return a traceback string as the "result".

---

## Performance and Data

BHoM priority order: **performance, security, maintainability, readability** ([bhom-coding-standards](../bhom-coding-standards/SKILL.md#priority-order)).

- Vectorise with numpy/pandas; no Python loops over 8760-row series where an array operation exists.
- Do not mutate inputs (`df = df.copy()` first) unless the function is documented as in-place. Wrapped methods in `bhom/wrapped/` are the exception (see [SKILL-FRAMEWORK.md](./SKILL-FRAMEWORK.md#c-callable-methods-bhom_callable--run_wrapped)).
- Return plain Python types at public and C# boundaries where practical (`float(x)`, not `numpy.float64`).
- `with` for files; `plt.close(fig)` for figures created in non-interactive code.
- `functools.lru_cache` only for pure functions with hashable, immutable inputs.

---

## Security and Privacy

- No credentials, tokens, connection strings or API keys in code, tests or notebooks.
- No project names, client names, job numbers or personal data in code, test assets or log messages (PR template warning).
- `subprocess` with an argument list - never `shell=True` with interpolated input.
- No `eval`/`exec` on external input; `pickle` only for trusted local files.
- Validate paths received from C# or the UI before deleting or overwriting.

---

## Checklist

- [ ] Right sub-package; one public function/class per file; snake_case file name
- [ ] BHoM copyright header with the current end year
- [ ] Module docstring; Google docstrings with units and `Raises`
- [ ] Type hints on all parameters and returns; 3.10-compatible
- [ ] Absolute imports, grouped stdlib / third-party / python_toolkit
- [ ] No mutable or call-evaluated defaults
- [ ] Inputs validated; specific exceptions with fix-it messages; no bare `except`
- [ ] `CONSOLE_LOGGER`, not `print`; `@bhom_analytics()` on public entry points
- [ ] C#-callable? Thin `@bhom_wrapper.bhom_callable` wrapper in `bhom/wrapped/`, returning objects
- [ ] `pathlib`; no hard-coded machine paths
- [ ] Dependencies and package data declared
- [ ] British English; no secrets or project data
- [ ] `black` clean; tests added ([SKILL-TESTING.md](./SKILL-TESTING.md))
