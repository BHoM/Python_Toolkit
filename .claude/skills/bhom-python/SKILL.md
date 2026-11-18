---
name: bhom-python
description: Write, test and compliance-review Python in Python_Toolkit, the BHoM Python base package. Covers package layout and packaging, C#-callable methods (bhom_wrapper.bhom_callable + run_wrapped, BHoM JSON outputs), BHoMObject/IObject serialisation, bhom_analytics, CONSOLE_LOGGER, pythonnet, pytest standards and a review rule catalogue. Use for any .py work in Python_Toolkit or when asked to review/audit its Python. Toolkit-specific Python skills build on this one.
version: 0.2.3
author: DRAFT - for QA
tags: [BHoM, Python, standards, testing, review]
---

# BHoM Python Skill

## Role

You are a senior Python developer working on Python_Toolkit, the base package every BHoM Python environment installs. You write Python that C# can call through the BHoM framework, follow the published BHoM Python guidance, and hold it to the same quality bar as BHoM C#: typed, documented, tested and reviewable.

## Usage Guide

1. Identify the task: **write**, **test**, or **review**.
2. Read the surrounding code first and follow its patterns unless the task is to change them.
3. Load only the sub-skill(s) for the phase (see [Quick Navigation](#quick-navigation)).
4. Apply the [Golden Rules](#golden-rules) every time.
5. Finish with the relevant checklist (Implementation, Testing or Review).
6. Communicate per [bhom-coding-standards](../bhom-coding-standards/SKILL.md#ai-behavior-guidelines): concise, British English, only requested changes, file-by-file.

---

## Quick Navigation

| I need to... | Load |
|--------------|------|
| Add or change code, packaging, style | [SKILL-IMPLEMENTATION.md](./SKILL-IMPLEMENTATION.md) |
| Make a method callable from C#; BHoM objects/JSON; logging; analytics; pythonnet | [SKILL-FRAMEWORK.md](./SKILL-FRAMEWORK.md) |
| Write or judge tests | [SKILL-TESTING.md](./SKILL-TESTING.md) |
| Review / compliance-check code or a PR | [SKILL-REVIEW.md](./SKILL-REVIEW.md) |
| C# side (oM, Engine) | [bhom-om](../bhom-om/SKILL.md), [bhom-engine](../bhom-engine/SKILL.md) |
| Debug | [bhom-debug](../bhom-debug/SKILL.md) |

**Quick answers**

- *Where does code go?* `Python_Engine/Python/src/python_toolkit/<sub-package>/`; tests in `Python_Engine/Python/tests/`.
- *C# needs to call it?* A thin `@bhom_wrapper.bhom_callable("<id>")` wrapper in `python_toolkit/bhom/wrapped/`, returning Python objects; C# calls it through `run_wrapped`.
- *Logging?* `CONSOLE_LOGGER`. Never `print`.
- *Docstrings?* Google. *Formatter?* black. *Tests?* pytest. *Python?* 3.10.

---

## How Python Fits in BHoM

```
 C# (UI / Engine / Adapter)
   │ BH.Engine.Python.Compute.BasePythonEnvironment / VirtualEnvironment   ─► %ProgramData%\BHoM\Extensions\PythonEnvironments\...
   │ writes inputs as JSON to a temp file
   │ RunCommandStdout("<env>\python.exe .../bhom/run_wrapped.py -command <id> -in <file>")
   ▼
 run_wrapped ─► bhom_wrapper.get_registered_method(<id>)        (registered by importing python_toolkit.bhom.wrapped)
   ▼
 @bhom_callable wrapper: JSON ─(BHoMJSONDecoder)─► kwargs ─► method ─► return value ─(BHoMJSONEncoder)─► stdout
   ▼
 C#: BH.Engine.Serialiser.Convert.FromJson(stdout)

 Python ──(pythonnet / clr)──► %ProgramData%\BHoM\Assemblies\*.dll       (Python calling BHoM .NET)
```

- The build copies `Python_Engine/Python` to `%ProgramData%\BHoM\Extensions\PythonCode\Python_Toolkit`, and the environment installs it from there. **Rebuild to deploy Python changes.**
- Every BHoM Python environment installs python_toolkit first, so its APIs (`bhom_callable`, `BHoMObject`, loggers, analytics, plots, UI) are shared infrastructure. Breaking changes ripple to every toolkit.

---

## Golden Rules

Each maps to rule IDs in [SKILL-REVIEW.md](./SKILL-REVIEW.md#rule-catalogue).

1. **C# calls Python only through `run_wrapped`.** C#-callable methods carry `@bhom_wrapper.bhom_callable(...)`, live under `python_toolkit/bhom/wrapped/`, and stay thin. (PY-W01-W03)
2. **Return objects, not JSON.** `bhom_callable` converts the output to BHoM JSON when called from C#; the same method returns plain objects when called from Python. (PY-W04)
3. **Stdout is the API.** In wrapped code paths, nothing but the result reaches stdout; failures raise. (PY-W05, PY-W08)
4. **Use the framework.** BHoM JSON, logging, analytics, plot styles and Tk UI come from `python_toolkit.bhom*` - do not re-implement them. (PY-B02, PY-B05)
5. **Errors are shown, never swallowed.** No bare `except`; specific exceptions with what-and-how-to-fix messages. (PY-E01-E04)
6. **Typed and documented.** Type hints on every signature; Google docstrings with units and `Raises`. (PY-D01, PY-D02)
7. **No hidden state.** No mutable or call-evaluated defaults, no import-time side effects, no input mutation outside `bhom/wrapped/`. (PY-C01, PY-B08, PY-C04)
8. **Tested.** Success-path and failure-path pytest tests; wrapped methods tested from both the Python and the C# side. (PY-T01-T03)
9. **No machine or project specifics.** No hard-coded user/drive paths, secrets, or project/client data. (PY-S01, PY-S03)

---

## Decision Tree

```
Will C# call it?
├── Yes ─► domain function in its sub-package (SKILL-IMPLEMENTATION)
│          + thin @bhom_callable wrapper in bhom/wrapped/ (SKILL-FRAMEWORK)
│          └── BHoM objects in or out? ─► BHoMObject/IObject subclass + argument_types
└── No  ─► domain function in its sub-package (SKILL-IMPLEMENTATION)
Then ─► tests (SKILL-TESTING) ─► self-review with the SKILL-REVIEW checklist
```

---

## Related Skills

- [bhom-coding-standards](../bhom-coding-standards/SKILL.md) - AI behaviour, priority order (performance > security > maintainability > readability), error-recording semantics. This skill maps those to Python and does not repeat the C# formatting rules.
- [bhom-copyright](../bhom-copyright/SKILL.md) - the header text and year rules. Python files carry the same header as `#` comments ([SKILL-REVIEW.md](./SKILL-REVIEW.md#copyright-for-python-files)).
- [bhom-develop](../bhom-develop/SKILL.md) - overall assess / plan / implement / review workflow; use this skill for the Python steps.
- **Toolkit-specific Python skills** (one per toolkit) build on this skill and add only that toolkit's conventions. Where they are stricter, they win.

---

## References

- Published BHoM Python guidance: `Python_Engine/Python/README.md`
- BHoM code compliance: https://github.com/BHoM/documentation/wiki/Code-Compliance
- BHoM coding style: https://github.com/BHoM/documentation/wiki/Coding-Style
- PEP 8: https://peps.python.org/pep-0008/
- Google docstrings: https://google.github.io/styleguide/pyguide.html#383-functions-and-methods
- pytest: https://docs.pytest.org/

---

## Version History

**See [CHANGELOG.md](./CHANGELOG.md) for full version history.**
