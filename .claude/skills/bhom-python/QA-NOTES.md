# QA Notes - bhom-python 0.2.0 (delete before publishing)

## 1. Decisions needed

| # | Question | Draft position | Where |
|---|----------|----------------|-------|
| D1 | Copyright header on `.py` files? | **Decided (PR #265 review): required** on every `.py` file, source and tests (PY-F06, S21) | SKILL-REVIEW "Copyright for Python Files" |
| D2 | Test location: `Python_Engine/Python/tests/` (practice) vs `.ci/unit_tests/python/` (README) | Practice; update the README | SKILL-TESTING "Where Tests Live" |
| D3 | Wrapped identifier convention | `python_toolkit.<area>.<function>` | SKILL-FRAMEWORK "Identifiers" |
| D4 | Give python_toolkit's `run_wrapped.py` a `-command`/`-in` CLI and add `BH.Engine.Python.Compute.RunWrapped` | Proposed | SKILL-FRAMEWORK "The C# Side" |
| D5 | Logging output mixed into wrapped results on stdout | To be resolved by the UV update (#253): the C# run method returns stdout and stderr separately | SKILL-FRAMEWORK "Known Framework Defects" |
| D6 | Lint/format config (black + pylint, 120 columns) and a Python CI job in `BHoM/CI_Toolkit` | Proposed | SKILL-REVIEW "Proposed Tool Configuration" |
| D7 | `requires-python = ">=3.10"`; dev tools out of runtime dependencies | Proposed | SKILL-IMPLEMENTATION "Packaging" |
| D8 | British English for new identifiers (third-party names exempt) | Yes | SKILL-IMPLEMENTATION S8 |

## 2. Verified against `develop` (`d9d1edd`) in the installed `Python_Toolkit/v3_10` environment

- Decorated method called from Python returns objects; with `__input_json__` it returns BHoM JSON (nested `BHoMObject` encoded).
- `argument_types` upgrades a top-level `BHoMObject` argument to the subclass.
- A `str` return is passed through unencoded.
- Plain JSON object input works; a BHoM-serialised `CustomObject` or `Dictionary` as the root fails with `TypeError` (`BHoM_Guid` / `_t` kwargs).
- Invalid JSON gives `UnboundLocalError` after an error log.
- `run_wrapped('test', <file path>)` via `python -c` works; the shipped `"test"` method's `print`s appear on stdout before the result.
- `CONSOLE_LOGGER` output shares stdout with the result in a real subprocess.

## 3. Defects to raise as issues

See SKILL-FRAMEWORK "Known Framework Defects" - ten items, five of them in the wrapper code (input root, invalid JSON, path detection, mutable default, `"test"` method).

## 4. Placement

The folder sits in `Python_Toolkit/.claude/skills/bhom-python/`, where Claude Code picks it up as a project skill. Links to sibling skills (`../bhom-coding-standards/SKILL.md` and so on) resolve only once it sits next to them in the shared skills plugin.

## 5. Suggested QA method

1. Read SKILL.md, then each sub-skill against the decisions above.
2. Ask Claude to add a small helper plus a C#-callable wrapper and tests, and check that it follows PY-W01 to PY-W08.
3. Ask Claude to review `bhom/decorators/_bhom_callable_decorator.py` and `bhom/wrapped/_test_wrapped.py`, and compare its findings with the rule catalogue.
