---
name: BHoM Python Testing
description: How to write, organise and run pytest tests for Python_Toolkit, including serialisation round trips, wrapped (C#-callable) methods, plots, UI and pythonnet.
version: 0.2.6
parent_skill: bhom-python
author: BHoM
tags: [BHoM, Python, testing, pytest]
---

# BHoM Python Testing

> **Use when:** writing tests for new or changed Python, or judging whether a PR's tests are sufficient.
> **Policy (`Python_Engine/Python/README.md`):** everything that can reasonably be tested should be; a passing unit test is required for PR approval; the code author writes the tests and the reviewer judges their sufficiency. Dispensation only from the CI/CD lead with justification.

---

## Quick Navigation

- [Quick Start](#quick-start)
- [Where Tests Live](#where-tests-live)
- [Running Tests](#running-tests)
- [What to Test](#what-to-test)
- [Patterns by Code Type](#patterns-by-code-type)
- [Test Quality Rules](#test-quality-rules)
- [Checklist](#checklist)

---

## Quick Start

```python
"""Tests for python_toolkit.helpers.degree_days."""

import pandas as pd
import pytest

from python_toolkit.helpers.degree_days import heating_degree_days


def test_heating_degree_days_returns_expected_for_constant_temperature():
    # Arrange
    index = pd.date_range("2026-01-01", periods=48, freq="h")
    air_temperature = pd.Series(10.0, index=index)

    # Act
    result = heating_degree_days(air_temperature, base_temperature=15.5)

    # Assert
    assert result == pytest.approx(11.0)  # 5.5 K x 2 days


def test_heating_degree_days_raises_for_non_series():
    with pytest.raises(TypeError, match="pandas Series"):
        heating_degree_days([10.0, 11.0])
```

- Framework: **pytest** only.
- Name: `test_<unit>_<behaviour>_<condition>` - same intent as the C# `Method_Scenario_Expected` convention in [bhom-coding-standards](../bhom-coding-standards/SKILL.md#testing-standards).
- Arrange / Act / Assert, one behaviour per test.
- Every `raise` in the code gets a `pytest.raises(..., match=...)` test.

---

## Where Tests Live

`Python_Engine/Python/tests/`, mirroring the source tree:

```
tests/
├── __init__.py              # shared constants (current practice, e.g. TIMESERIES_COLLECTION)
├── conftest.py              # (proposed) fixtures, Agg backend, analytics off
├── assets/                  # small, licence-safe sample data
├── test_bhom_serialiser.py
├── test_plot.py
└── ...                      # test_<module>.py or test_<subpackage>/test_<module>.py
```

- Sample data in `tests/assets/`, loaded via `Path(__file__).parent / "assets" / ...` - never absolute, user or network paths.
- Test and asset file names follow the same BHoM rule as source: **no "error" in any name** (`tests/` is copied into the install with the rest of `Python_Engine/Python`). Use `test_colour_scale_err.py`, not `test_colour_scale_errors.py`.
- No project or client data in assets - public or synthetic only.
- **Open question:** the README says tests go in `.ci/unit_tests/python/`, which holds only an empty, misspelt `__init_.py`. Practice is `Python_Engine/Python/tests/`; this skill follows practice and the README should be updated.

---

## Running Tests

From the repo, against source (`pyproject.toml` sets `pythonpath = "src"`):

```bash
"C:/ProgramData/BHoM/Extensions/PythonEnvironments/Python_Toolkit/v3_10/python.exe" -m pytest Python_Engine/Python/tests --cov python_toolkit --cov-report term-missing -v
```

- `run_tests.bat` runs against the **deployed copy** in `%ProgramData%\BHoM\Extensions\PythonCode\Python_Toolkit` - rebuild `Python_Engine` first or you test stale code.
- Run with `DISABLE_BHOM_ANALYTICS=1` so tests do not write usage logs (set before any python_toolkit import).
- Coverage output (`.coverage`, `cov_html/`) and `.pytest_cache/` must not be committed; **(proposed)** add `cov_html/` to `.gitignore` (it ignores `htmlcov/` but `run_tests.bat` writes `cov_html`).

`conftest.py` starter **(proposed)**:

```python
"""Shared pytest configuration."""

import os

os.environ.setdefault("DISABLE_BHOM_ANALYTICS", "1")  # before python_toolkit imports

import matplotlib  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import pytest  # noqa: E402

matplotlib.use("Agg")  # headless; avoids tkinter backend errors under pytest


@pytest.fixture(autouse=True)
def _close_figures():
    yield
    plt.close("all")
```

---

## What to Test

Minimum per change (README policy, made explicit):

1. **Success path** returns the predefined expected result.
2. **Each raised error** is raised with the expected type and message fragment.
3. **Lowest-level functions first** in multi-step processes, so errors do not cascade untested.
4. **External programs** - assert availability first and `pytest.skip` with a reason if absent.
5. **Floating point / stochastic** - `pytest.approx` with deliberate `rel`/`abs`; never `==` on floats.
6. **Regression** - a bug fix ships with the test that would have caught it.

---

## Patterns by Code Type

### Wrapped (C#-callable) methods

Test both faces of the method:

```python
import json

import python_toolkit.bhom.wrapped  # noqa: F401 - registers every wrapped method, as run_wrapped does
from python_toolkit.bhom.decorators import bhom_wrapper
from python_toolkit.bhom.wrapped.plot.heatmap_png import heatmap_png


def test_heatmap_png_is_registered():
    assert bhom_wrapper.get_registered_method("python_toolkit.plot.heatmap_png") is not None


def test_heatmap_png_python_call_returns_path(tmp_path):
    out = heatmap_png(values=[1.0] * 48, start="2026-01-01T00:00", output_path=str(tmp_path / "h.png"))
    assert out.exists()


def test_heatmap_png_csharp_call_returns_bhom_json(tmp_path):
    payload = json.dumps({"values": [1.0] * 48, "start": "2026-01-01T00:00", "output_path": str(tmp_path / "h.png")})

    result = heatmap_png(__input_json__=payload)

    obj = json.loads(result)
    assert obj["_t"] == "BH.oM.Adapter.FileSettings"
```

- **Registered:** the identifier resolves through `bhom_wrapper.get_registered_method` after `import python_toolkit.bhom.wrapped` - this catches a method placed outside `bhom/wrapped/` or missing the decorator.
- **Python face:** called normally, returns Python objects.
- **C# face:** called with `__input_json__` (a JSON string, and a file path via `tmp_path`), returns valid BHoM JSON with the expected `_t`.
- **Through `run_wrapped`:** with `capsys`, stdout is **exactly** one valid JSON document - C# deserialises the whole of stdout, so any extra output is a failure.
- **Inputs from C#:** include at least one argument given as a BHoM JSON string, exactly as the BHoM serialiser produces it, including any `argument_types` upgrade to your subclass.
- **Failure:** invalid input raises a clear exception (the process must exit non-zero, not print a traceback as the result).

### BHoM serialisation

```python
def test_file_settings_round_trips_through_bhom_json():
    obj = FileSettings(file_name="a.epw", directory="C:/data")

    restored = FileSettings.from_json(obj.to_json())

    assert restored == obj  # __eq__ ignores bhom_guid and _bhom_version
```

- **Python -> JSON -> Python**, and **C# JSON -> Python** from a BHoM JSON string produced by the BHoM serialiser - the second catches PascalCase/snake_case drift (acronyms).
- Assert `_t` is the exact C# type name (or `BH.oM.Base.CustomObject` for objects with no C# type).
- `test_bhom_serialiser.py` is the reference; its TODOs (use real BHoM-serialiser output) are worth closing.

### Plots

- `Agg` backend; assert return type (`plt.Axes` / `Figure`) and key properties (title, number of artists, colourbar present) - not pixels.
- Close figures after each test (fixture above).
- Saving: write to `tmp_path`; assert the file exists and is non-empty.

### tkinter UI

- `tk.Tk()`, `withdraw()`, drive widgets programmatically, `destroy()` in teardown.
- Skip when no display is available (catch `tk.TclError` -> `pytest.skip`), so headless CI does not fail.
- Test widget **state and callbacks**, not layout.

### pythonnet / .NET

- Mark `@pytest.mark.dotnet`; skip when `clr` or `%ProgramData%\BHoM\Assemblies` is unavailable.
- Test the JSON contract rather than live .NET objects.

### Files and paths

- `tmp_path` only; never write into the repo or `%ProgramData%` from a test.
- Where an API accepts `str | Path`, test both.

---

## Test Quality Rules

- **Independent:** no ordering dependencies. `pytest-order` is installed but should not be needed; shared setup is a fixture.
- **No shared mutable state:** module-level objects (`TIMESERIES_COLLECTION`) are read-only - copy before mutating.
- **Fast:** unit tests under ~1 s; mark slow ones `@pytest.mark.slow`.
- **Deterministic:** seed randomness (`np.random.default_rng(0)`); pass times explicitly.
- **Meaningful assertions:** "it didn't crash" is not sufficient except for labelled smoke tests. No placeholder docstrings (`"""_"""`).
- **Clear failures:** assertion messages where the cause would otherwise be unclear, as in `test_bhom_serialiser.py`.
- **No notebooks:** notebooks are never committed and never count as tests; turn checks into pytest tests.

---

## Checklist

- [ ] Every new/changed public function has a success-path and a failure-path test
- [ ] Bug fixes include a regression test
- [ ] Floats compared with `pytest.approx`
- [ ] Wrapped methods: registered, Python face, C# face (`__input_json__`), stdout clean, BHoM JSON input
- [ ] BHoM objects: round trip and a BHoM JSON string from the C# serialiser
- [ ] Plots use `Agg` and close figures; UI tests skip without a display
- [ ] No absolute paths, network paths, project data or secrets in tests or assets
- [ ] Test files carry the BHoM copyright header
- [ ] Analytics disabled for the test run
- [ ] `python -m pytest` passes in the Python_Toolkit environment
