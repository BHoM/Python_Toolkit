---
name: BHoM Python Framework
description: How to use the python_toolkit BHoM framework - C#-callable methods (bhom_callable + run_wrapped), BHoMObject/IObject and BHoM JSON, bhom_analytics, logging and pythonnet.
version: 0.2.0
parent_skill: bhom-python
author: DRAFT - for QA
tags: [BHoM, Python, framework, serialisation, logging, pythonnet]
---

# BHoM Python Framework

> **Use when:** writing Python that C# calls, that exchanges BHoM objects, that logs or records analytics, or that calls BHoM .NET code.
> **Source of truth:** `Python_Engine/Python/src/python_toolkit/bhom/`. If this file and that code disagree, the code wins - flag the drift.

---

## Quick Navigation

- [Import Cheat Sheet](#import-cheat-sheet)
- [C#-Callable Methods: bhom_callable + run_wrapped](#c-callable-methods-bhom_callable--run_wrapped)
- [BHoM Objects and Serialisation](#bhom-objects-and-serialisation)
- [Logging](#logging)
- [Analytics Decorator](#analytics-decorator)
- [Calling .NET from Python (pythonnet)](#calling-net-from-python-pythonnet)
- [The C# Side](#the-c-side)
- [Known Framework Defects](#known-framework-defects)

---

## Import Cheat Sheet

| Need | Import |
|------|--------|
| Make a method callable from C# | `from python_toolkit.bhom.decorators import bhom_wrapper` |
| Entry point C# runs | `from python_toolkit.bhom.run_wrapped import run_wrapped` |
| BHoM base classes | `from python_toolkit.bhom.bhom_object import BHoMObject, IObject` |
| BHoM JSON | `from python_toolkit.bhom.bhom_object import BHoMJSONEncoder, BHoMJSONDecoder` |
| Console logging | `from python_toolkit.bhom.logging import CONSOLE_LOGGER` |
| Usage analytics | `from python_toolkit.bhom.analytics import bhom_analytics` |
| Project number for analytics | `from python_toolkit.bhom.analytics import set_project_number, get_project_number` |
| Install constants | `from python_toolkit.bhom import BHOM_VERSION, BHOM_LOG_FOLDER, TOOLKIT_NAME` |
| BHoM plot style | `plt.style.use("python_toolkit.bhom")` / `"python_toolkit.bhom_dark"` |
| Desktop UI | `python_toolkit.bhom_tkinter` (windows, widgets, theming) |
| Time-series helpers | `python_toolkit.helpers` |
| Unit conversions | `python_toolkit.units` |

---

## C#-Callable Methods: bhom_callable + run_wrapped

**This is the only route from C# into python_toolkit.** C# never imports modules, runs ad hoc scripts, or parses bespoke CLI arguments - it calls `run_wrapped(identifier, json)`, which dispatches to a method registered with `@bhom_wrapper.bhom_callable(...)`.

### The rules

1. **C# calls Python methods only through `run_wrapped`** (see [The C# Side](#the-c-side) for the call shape).
2. **Every C#-callable method has `@bhom_wrapper.bhom_callable("<identifier>", ...)`.** Without it the method is not registered and `run_wrapped` raises `NotImplementedError`.
3. **Every method with that decorator lives under `python_toolkit/bhom/wrapped/`.** `run_wrapped.py` imports `python_toolkit.bhom.wrapped`, whose `__init__.py` imports every `.py` file in that folder (recursively) - that import is what registers the method. A decorated method anywhere else is never imported by `run_wrapped`, so it is never registered.
4. **Return Python objects, not JSON.** When called from C# (i.e. with `__input_json__`), the decorator encodes the return value with `BHoMJSONEncoder` for you - `BHoMObject`s, `IObject`s, dicts, lists, numpy arrays, pandas Series/Timestamps, `datetime`, `UUID` and `Path` all become BHoM JSON. Do **not** `json.dumps` the result yourself.
5. **The same method stays a normal Python function.** Called from Python without `__input_json__`, the decorator returns the raw result untouched, so Python users and tests call it directly.

### Pattern

`python_toolkit/bhom/wrapped/plot/heatmap_png.py`:

```python
"""C# entry point: render a heatmap of a time series to a PNG file."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: C# runs this in a hidden process

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from python_toolkit.bhom.analytics import bhom_analytics  # noqa: E402
from python_toolkit.bhom.decorators import bhom_wrapper  # noqa: E402
from python_toolkit.plot.heatmap import heatmap  # noqa: E402


@bhom_wrapper.bhom_callable("python_toolkit.plot.heatmap_png")
@bhom_analytics()
def heatmap_png(values: list[float], start: str, output_path: str) -> Path:
    """Render an hourly heatmap of values starting at start and save it as a PNG.

    Args:
        values (list[float]):
            Hourly values.
        start (str):
            ISO 8601 timestamp of the first value.
        output_path (str):
            Where to write the PNG.

    Returns:
        Path:
            The written file (returned to C# as a BH.oM.Adapter.FileSettings).
    """
    series = pd.Series(values, index=pd.date_range(start, periods=len(values), freq="h"))
    fig, ax = plt.subplots()
    heatmap(series, ax=ax)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return Path(output_path)
```

Points to copy:

- **Thin wrapper.** The wrapped method converts C#-friendly inputs (lists, strings, BHoM objects) into Python types, calls the real function in a domain module (`python_toolkit.plot.heatmap`), and returns plain objects. Logic does not live in `bhom/wrapped/`.
- **Decorator order:** `bhom_callable` outermost (it registers what it wraps), `bhom_analytics()` inside it, so analytics records the real function name.
- **Light imports.** Every module in `bhom/wrapped/` is imported on *every* `run_wrapped` call, whichever method is requested. Keep module-level imports cheap and side-effect free; import heavy optional libraries inside the function.
- **Input types C# can produce.** Use JSON-native types (`float`, `str`, `list`, `dict`) or BHoM objects. A `pd.Series` or `datetime` cannot arrive from C# directly.

### Identifiers

- Globally unique across everything registered: **(proposed)** `"python_toolkit.<area>.<function>"`, mirroring the module path.
- Never change a published identifier without a C# deprecation path - it is the API.

### What `run_wrapped` receives (verified)

`run_wrapped(identifier, json)` where `json` is either a JSON string beginning with `{` or a **path to a file** containing it (anything not starting with `{` is treated as a path).

The JSON must be a **plain object whose keys are the method's argument names**. Values can be BHoM-serialised objects:

```json
{ "values": [1.0, 2.0, 3.0], "start": "2026-01-01T00:00", "output_path": "C:/temp/out.png" }
```

```json
{ "geometry": { "_t": "BH.oM.Base.CustomObject", "BHoM_Guid": "f428e614-...", "X": 1 }, "arg2": "hello" }
```

**Do not** pass a BHoM-serialised `CustomObject` or `Dictionary<string, object>` as the *root*. The BHoM serialiser adds `BHoM_Guid` / `_t` / `_bhomVersion` keys at the root, and these arrive as unexpected keyword arguments (`TypeError: ... unexpected keyword argument 'BHoM_Guid'` / `'_t'`). See [Known Framework Defects](#known-framework-defects).

### `argument_types` - getting your subclass back

The decoder turns any JSON object with `_t` and `BHoM_Guid` into a plain `BHoMObject`. To receive your subclass instead, map the argument name to it:

```python
@bhom_wrapper.bhom_callable("python_toolkit.example.move", argument_types={"point": MyPoint})
def move(point: MyPoint, dx: float) -> MyPoint:
    ...
```

Limits: it upgrades **top-level arguments only**, only when the decoded value is exactly `BHoMObject` (not `IObject`), and not items inside lists or nested properties - convert those yourself with `MyPoint._from_bhom_object(obj)`.

### What C# gets back (verified)

- `run_wrapped` `print`s the encoded result: **one line of JSON** on stdout.
- **A `str` return value is not encoded** - it is printed as-is, so C# receives bare text, not JSON. Return a `Path`, dict or object instead of a string when C# deserialises the result.
- **Other stdout output comes first.** `CONSOLE_LOGGER` writes to stdout, and so does any `print`. A real run of the shipped `"test"` method prints:

  ```
  BHoMObject of type BH.oM.Base.CustomObject, name: '', version: '9.3', id: 'f428e614-...'
  hello
  {"Name": "", "BHoM_Guid": "f428e614-...", "_t": "BH.oM.Base.CustomObject", "_bhomVersion": "9.3", "X": 20}
  ```

  The established C# callers deserialise the **whole** of stdout, so anything printed before the result breaks the call. **No `print` in wrapped code**, and keep `CONSOLE_LOGGER` to warnings/errors on wrapped code paths (see the open question in [Known Framework Defects](#known-framework-defects)).
- Exceptions propagate: the process exits non-zero with the traceback on stderr, and `Compute.RunCommandStdout` returns **stderr instead of stdout** on a non-zero exit. The established C# callers treat output containing `Traceback (most recent call last):` as a failure, so raising is the correct way to fail - no need (and no reason) to return `traceback.format_exc()` yourself.

---

## BHoM Objects and Serialisation

### The two base classes

| Class | Mirrors | Use for |
|-------|---------|---------|
| `IObject` | C# `BH.oM.Base.IObject` | BHoM-serialised objects that are **not** `BHoMObject`s (e.g. `BH.oM.Geometry.Point`) |
| `BHoMObject(IObject)` | C# `BH.oM.Base.BHoMObject` | Objects with `Name`, `BHoM_Guid`, `Tags`, `Fragments`, `CustomData` |

Both carry `_t` (the full C# type name) and `_bhom_version` (short version, e.g. `"9.3"`).

### Naming across the boundary

The encoder/decoder convert property names automatically:

| C# (JSON) | Python attribute |
|-----------|------------------|
| `FileName` | `file_name` |
| `BHoM_Guid` | `bhom_guid` |
| `CustomData` | `custom_data` |
| `_bhomVersion` | `_bhom_version` |
| `{"$date": <ticks>}` | `datetime` |

Write Python attributes in the snake_case the converter produces from the C# property name. Acronyms round-trip but give awkward names: `HVACSystem` <-> `h_v_a_c_system` (verified). A hand-written `hvac_system` would serialise as `HvacSystem`, which C# ignores. Test the round trip for any property with consecutive capitals.

### Subclassing (the supported pattern)

```python
from python_toolkit.bhom.bhom_object import BHoMObject


class FileSettings(BHoMObject):
    """Python mirror of BH.oM.Adapter.FileSettings."""

    def __init__(self, file_name: str, directory: str, **kwargs) -> None:
        """
        Args:
            file_name: The name of the file, with extension.
            directory: The folder containing the file.
            **kwargs: BHoMObject properties (name, bhom_guid, tags, ...) passed through from deserialisation.
        """
        kwargs.setdefault("_t", "BH.oM.Adapter.FileSettings")
        super().__init__(**kwargs)
        self.file_name = file_name
        self.directory = directory
```

- `_t` must be the exact C# full type name. **If there is no C# type for the object, use `"BH.oM.Base.CustomObject"`** - never an invented `_t`. C# then reads the extra properties into the `CustomObject`'s `CustomData`.
- Accept `**kwargs` and pass them to `super().__init__`, so `from_json` (via `_from_bhom_object`) can rebuild your subclass.
- Deserialise with `FileSettings.from_json(j)` (single) or `FileSettings.from_json_array(j)` (list). `BHoMObject.from_json` on a JSON array logs a warning and returns only the first item.
- Equality (`==`) compares `_t` and all properties except `bhom_guid` and `_bhom_version`.

### Types the encoder already handles

`uuid.UUID`, `datetime` / `pd.Timestamp` (-> `{"$date": ...}`), `np.ndarray` (-> list), `pd.Series` (-> dict, index as str), `pd.DatetimeIndex` (-> ISO strings), `pathlib.Path` (-> `BH.oM.Adapter.FileSettings`).

For anything else, subclass `BHoMJSONEncoder` and override `serialise_unknown`, calling `super().serialise_unknown(obj)` for types you do not handle; mirror with `deserialise_unknown` on a `BHoMJSONDecoder` subclass. Pass the subclasses to `bhom_callable(encoder_cls=..., decoder_cls=...)`.

### Do not hand-roll BHoM JSON

Building `{"_t": ..., "BHoM_Guid": ..., "Name": ...}` dicts by hand, converting key case yourself, or stripping `_t` keys ad hoc duplicates the encoder/decoder and drifts from them. Extend the classes above instead.

---

## Logging

Two loggers, both configured at import time in `python_toolkit/bhom/logging/`:

| Logger | Name | Handler | Purpose |
|--------|------|---------|---------|
| `CONSOLE_LOGGER` | `"Python_Toolkit[console]"` | `StreamHandler(sys.stdout)`, INFO | User-facing messages |
| `ANALYTICS_LOGGER` | `"Python_Toolkit"` | `RotatingFileHandler` in `%PROGRAMDATA%/BHoM/Logs` (25 MB, 1 backup) | **Analytics only** - written by `bhom_analytics`. Never log to it directly. |

Both set `propagate = False`, so they do not leak into a host's root logger.

### Rules

1. **No `print()`.** Use `CONSOLE_LOGGER`.
2. Pick the level by consequence, mirroring C# `RecordError / RecordWarning / RecordNote`:

   | C# | Python | When |
   |----|--------|------|
   | `RecordError` | `raise` a specific exception | Operation cannot continue |
   | `RecordWarning` | `CONSOLE_LOGGER.warning(...)` | Continues, but the result has caveats |
   | `RecordNote` | `CONSOLE_LOGGER.info(...)` | Informational |
   | - | `CONSOLE_LOGGER.debug(...)` | Developer diagnostics (dropped at the default INFO level) |

3. Inside wrapped methods, remember the console logger shares stdout with the result (see above).
4. Never log secrets, tokens, or project/client names.
5. Never call `logging.basicConfig()` or attach handlers to the root logger - it hijacks the host (Grasshopper, Excel, notebooks).

Code that builds on python_toolkit and needs its own logger makes it a **child** of `CONSOLE_LOGGER` (`logger.parent = CONSOLE_LOGGER; logger.propagate = True`) rather than adding a second handler, so messages are not printed twice.

---

## Analytics Decorator

`@bhom_analytics()` records one usage entry (`BH.oM.Base.UsageLogEntry` shape) per call to `%PROGRAMDATA%/BHoM/Logs/Usage_<package>_<yyyymmdd>.log`, including any exception raised, then re-raises.

- **Apply it to public, user-facing functions and methods** - including wrapped methods. Not to private helpers (`_name`), dunders, properties, classes, or tight inner loops (each call writes a log line).
- **Always call it: `@bhom_analytics()`.** Written as `@bhom_analytics` (no brackets), the decorated function silently returns a wrapper *function* instead of its result - no error (verified).
- Order: `@staticmethod` / `@classmethod` / `@property` outermost; `@bhom_wrapper.bhom_callable` outside `@bhom_analytics()`.
- Set the project number once per session with `set_project_number("<number>")`; never hard-code one.
- Tests and CI run with `DISABLE_BHOM_ANALYTICS=1` (read once at import - set it before importing).
- Type hints matter: the decorator records parameter annotations as `_t` in the log.

---

## Calling .NET from Python (pythonnet)

Direction: **C# never embeds Python** (no `Py.GIL` / `PythonEngine`); it runs Python as a subprocess via `run_wrapped`. pythonnet is used the other way - Python calling BHoM .NET - as in `python_toolkit/bhom/installer_info.py`:

```python
import os
import sys

import clr

sys.path.append(os.path.expandvars("%ProgramData%\\BHoM\\Assemblies"))
clr.AddReference("Serialiser_Engine")

from BH.Engine.Serialiser import Convert  # pylint: disable=import-error,wrong-import-position
```

- Load assemblies from `%ProgramData%\BHoM\Assemblies` only.
- Keep `clr` imports in the module that needs them, guarded for non-Windows (as `python_toolkit.bhom.__init__` does with `os.name == "nt"`), so the package still imports without .NET.
- Cross the boundary with JSON (`Convert.ToJson` / `Convert.FromJson` + `BHoMJSONDecoder`) rather than passing live .NET objects through Python code.
- Non-Windows (Docker) uses `PYTHONNET_RUNTIME=coreclr` - see `Python_Engine/Python/Dockerfile`.

---

## The C# Side

`BH.Engine.Python` (`Python_Engine/`):

| Method | Purpose |
|--------|---------|
| `Compute.BasePythonEnvironment(version, reload, run)` | Install/retrieve base Python (default `v3_10`) with `virtualenv`, `jupyterlab`, `black`, `pylint` and `python_toolkit` |
| `Compute.VirtualEnvironment(version, name, reload)` | Create a venv in `%ProgramData%\BHoM\Extensions\PythonEnvironments\<name>`, add `ipykernel`, `pytest`, `black`, register a Jupyter kernel |
| `Compute.InstallPackageLocal` / `InstallRequirements` / `InstallPackages` | Install local packages and dependencies |
| `Compute.UpdateBHoMPackages(env)` | Reinstall BHoM Python packages into an existing env |
| `Compute.RunCommandStdout(command, ...)` | Run via `cmd.exe`, return stdout - or **stderr** if the exit code is non-zero |
| `Compute.RunPythonString(env, script)` | Write a script to a temp `.py`, run it, return stdout |
| `Query.DirectoryCode()` / `DirectoryEnvironments()` / `VirtualEnvironmentExecutable(name)` | Standard paths - never hard-code them |

`BH.oM.Python.PythonEnvironment` has `Name` and `Executable`.

**Calling a wrapped method - the established shape.** BHoM toolkits that build on python_toolkit each ship a small `run_wrapped.py` **script** in their own `bhom/` folder. It imports `python_toolkit.bhom.wrapped` (and the toolkit's own `wrapped` package) so every method is registered, parses `-command <identifier> -in <json file>`, calls `method(__input_json__=<json file>)` and prints the result. The C# side:

1. Builds a plain JSON object of argument name -> value, BHoM-serialising object values with `BH.Engine.Serialiser.Convert.ToJson`.
2. Writes it to `Path.GetTempFileName()` (avoids `cmd.exe` quoting and the ~8191 character command-line limit).
3. Runs `"<env.Executable>" "<...>/bhom/run_wrapped.py" -command <identifier> -in "<temp file>"` through `Compute.RunCommandStdout`, with the script path built from `Query.DirectoryCode()`, then deletes the temp file.
4. Treats output containing `Traceback (most recent call last):` as failure; otherwise `Convert.FromJson` on the whole output.

python_toolkit's own `run_wrapped(identifier, json)` is the in-process function form of the same thing. From a shell the equivalent is `"<env.Executable>" -c "from python_toolkit.bhom.run_wrapped import run_wrapped; run_wrapped('<identifier>', r'<json file>')"` (verified against the installed `Python_Toolkit/v3_10` env).

> **(proposed)** Give python_toolkit's `run_wrapped.py` the `-command` / `-in` `__main__` entry point, and add a `Compute.RunWrapped(env, identifier, inputs)` to `BH.Engine.Python` that does steps 1-4, so each toolkit stops re-implementing both halves.

Python code ships via the `Python_Engine.csproj` build step: `robocopy` of `Python_Engine/Python` to `%ProgramData%\BHoM\Extensions\PythonCode\Python_Toolkit` (excluding `*.pyc`, `*.ipynb`, dunder and dot folders) plus a `VERSION.txt` that `setup.py` reads. **Rebuild to deploy Python changes**; then `UpdateBHoMPackages` (or recreate the env) to install them.

---

## Known Framework Defects

On `develop` at `d9d1edd`. Until fixed, write code that does not depend on the broken behaviour, and do not copy these patterns:

| Location | Defect | Workaround |
|----------|--------|-----------|
| `_bhom_callable_decorator.py` | Root input that is a BHoM-serialised `CustomObject` or `Dictionary` fails: `BHoM_Guid` / `_t` / `_bhomVersion` become unexpected kwargs (verified) | C# sends a plain JSON object (see [The C# Side](#the-c-side)); fix: drop reserved keys before calling |
| `_bhom_callable_decorator.py` | Bare `except:`; on invalid JSON it logs, then fails with `UnboundLocalError: json_kwargs` (verified) | Validate JSON on the C# side; fix: raise a `ValueError` with the parse error |
| `_bhom_callable_decorator.py` | Input not starting with `{` is assumed to be a path - leading whitespace/BOM or a JSON array gives `FileNotFoundError` | Send compact JSON or a file path; fix: `lstrip()` and check `Path.exists()` |
| `_bhom_callable_decorator.py` | `argument_types={}` mutable default (read-only today, but violates PY-C01) | - |
| `wrapped/_test_wrapped.py` | Ships a `"test"` method that `print`s and mutates its input - and it is registered in every environment that imports `python_toolkit.bhom.wrapped` | Move to `tests/` |
| `logging/console.py` | Console logger writes to **stdout**, the same stream C# deserialises | Keep wrapped paths quiet; **(open question)** move console logging to stderr |
| `analytics.py` wrapper | `Errors.extend(<dict>)` adds the dict's *keys*, not the error event | - (fix: `append`) |
| `bhom_object.py` `IObject.from_dict` | Catches `ctypes.ArgumentError`, but bad kwargs raise `TypeError` | - |
| `helpers/timeseries.py` `validate_timeseries` | `is_annual` check `(n != 365) or (n != 366)` is always true (verified) | Do not use `is_annual=True` |
| `python_toolkit/__init__.py` | On Windows, overwrites `os.environ["HOME"]` with `C:/Users/<user>` at import | Do not rely on `HOME` after import |

Fixed in #263 (`d9d1edd`): shared `bhom_guid` / list defaults in `BHoMObject.__init__`, frozen `datetime.utcnow()` default in `bson_unix_ticks`, non-callable `default_factory` in `UsageLogEntry`.
