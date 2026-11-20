---
name: BHoM Python Skill Changelog
description: Version history for all files in the bhom-python skill folder
version: 0.3.0
author: BHoM
tags: [BHoM, Python, changelog]
---

# Changelog - BHoM Python Skill

## Change History

### 2026-11-20 (Latest)
**Files modified**:
- SKILL.md (v0.2.4 → v0.3.0)
- SKILL-IMPLEMENTATION.md (v0.2.8 → v0.2.9)
- SKILL-REVIEW.md (v0.2.6 → v0.3.0)
- SKILL-TESTING.md (v0.2.5 → v0.2.6)
- CHANGELOG.md (v0.2.10 → v0.3.0)

**Files added**:
- scripts/check_file_names.py (PY-F03, PY-F07)
- scripts/check_docstrings.py (PY-D05)

**Changes:**
- New rule PY-F07 / S22: no "error" in any file or folder name under `Python_Engine/Python`, because it fails the BHoMBot installer check on dependent toolkits (#266, fixed in #267).
- PY-F03 raised to Major and made precise: the file is named after its one public class or function (`BHoMBaseWindow` -> `bhom_base_window.py`, `ColourScaleError` -> `colour_scale_err.py`); no grab-bag modules.
- New rule PY-D05: `Args:` covers every parameter in signature order, descriptions end with punctuation, `Returns:` when a value is returned.
- New rule PY-B11: no `custom_data` in place of real properties.
- New "BHoM Compliance Mapping" section mapping `CodeComplianceTest_Engine` checks to their Python rules.
- Automated pass runs the new scripts (whole folders, or only a PR's changed files); golden rule 10 added.
- Checked against `develop` at `45d527b`: PY-F07 none, PY-F03 34 existing, PY-D05 9 existing; the commit before #267 is flagged for `errors.py`.

**Rationale:**
Align the skill with BHoM compliance after `errors.py` broke the BHoMBot installer check.

---

### 2026-11-19
**Files modified**:
- SKILL.md (v0.2.3 → v0.2.4)
- SKILL-FRAMEWORK.md (v0.2.2 → v0.2.3)
- SKILL-IMPLEMENTATION.md (v0.2.7 → v0.2.8)
- SKILL-REVIEW.md (v0.2.5 → v0.2.6)
- SKILL-TESTING.md (v0.2.4 → v0.2.5)
- CHANGELOG.md (v0.2.9 → v0.2.10)

**Files removed**:
- QA-NOTES.md

**Changes:**
- Removed the reviewer-only QA notes; remaining open decisions are tracked in issue #264.
- Frontmatter `author` set to `BHoM` in every file.
- Removed "for QA" wording from the skill text.

**Rationale:**
PR #265 review feedback.

---

### 2026-11-18
**Files modified**:
- SKILL-TESTING.md (v0.2.3 → v0.2.4)
- CHANGELOG.md (v0.2.8 → v0.2.9)

**Changes:**
- "Golden JSON string" renamed to "BHoM JSON string" throughout.

**Rationale:**
PR #265 review feedback.

---

### 2026-11-18
**Files modified**:
- SKILL.md (v0.2.2 → v0.2.3)
- SKILL-IMPLEMENTATION.md (v0.2.6 → v0.2.7)
- SKILL-REVIEW.md (v0.2.4 → v0.2.5)
- SKILL-TESTING.md (v0.2.2 → v0.2.3)
- CHANGELOG.md (v0.2.7 → v0.2.8)
- QA-NOTES.md

**Changes:**
- The BHoM copyright header is now required on every `.py` file, source and tests: new review rule PY-F06 with an automated check, style rule S21, checklist items, and the "Copyright for Python Files" section rewritten from an open decision into the rule.

**Rationale:**
PR #265 review feedback (decision D1).

---

### 2026-11-18
**Files modified**:
- SKILL.md (v0.2.1 → v0.2.2)
- SKILL-REVIEW.md (v0.2.3 → v0.2.4)
- SKILL-TESTING.md (v0.2.1 → v0.2.2)
- CHANGELOG.md (v0.2.6 → v0.2.7)

**Changes:**
- "Happy path" renamed to "success path" throughout.

**Rationale:**
PR #265 review feedback.

---

### 2026-11-18
**Files modified**:
- SKILL.md (v0.2.0 → v0.2.1)
- SKILL-FRAMEWORK.md (v0.2.1 → v0.2.2)
- SKILL-IMPLEMENTATION.md (v0.2.5 → v0.2.6)
- SKILL-REVIEW.md (v0.2.2 → v0.2.3)
- CHANGELOG.md (v0.2.5 → v0.2.6)

**Changes:**
- Methods in `bhom/wrapped/` may modify their inputs (they receive copies deserialised from C# JSON): exception added to PY-C04, the input-mutation guidance, golden rule 7 and the wrapped-method guidance.
- `"test"` wrapped-method defect no longer lists input mutation.

**Rationale:**
PR #265 review feedback.

---

### 2026-11-18
**Files modified**:
- SKILL-IMPLEMENTATION.md (v0.2.4 → v0.2.5)
- SKILL-REVIEW.md (v0.2.1 → v0.2.2)
- CHANGELOG.md (v0.2.4 → v0.2.5)

**Changes:**
- S5 reworded: give sensible defaults where a user would not know what to enter; omit them only for inputs the user must supply; document every default in the docstring.
- PY-D02 now requires default values to be documented.

**Rationale:**
PR #265 review feedback.

---

### 2026-11-18
**Files modified**:
- SKILL-IMPLEMENTATION.md (v0.2.3 → v0.2.4)
- SKILL-REVIEW.md (v0.2.0 → v0.2.1)
- SKILL-TESTING.md (v0.2.0 → v0.2.1)
- CHANGELOG.md (v0.2.3 → v0.2.4)

**Changes:**
- Notebooks are never committed (`*.ipynb` is in `.gitignore`): replaced "clear outputs before commit" guidance, added notebooks to PY-S04 committed artefacts, removed "notebook outputs" from privacy rules.

**Rationale:**
PR #265 review feedback.

---

### 2026-11-18
**Files modified**:
- SKILL-IMPLEMENTATION.md (v0.2.2 → v0.2.3)
- CHANGELOG.md (v0.2.2 → v0.2.3)

**Changes:**
- `jupyterlab` stays a runtime dependency (notebooks must work in non-dev environments); only the pytest packages are proposed for the dev group.

**Rationale:**
PR #265 review feedback.

---

### 2026-11-18
**Files modified**:
- SKILL-IMPLEMENTATION.md (v0.2.1 → v0.2.2)
- CHANGELOG.md (v0.2.1 → v0.2.2)

**Changes:**
- `__init__.py` guidance is no longer a hard "constants and re-exports only" rule: keep them light, with nothing heavy or surprising on import.

**Rationale:**
PR #265 review feedback.

---

### 2026-11-18
**Files modified**:
- SKILL-FRAMEWORK.md (v0.2.0 → v0.2.1)
- SKILL-IMPLEMENTATION.md (v0.2.0 → v0.2.1)
- CHANGELOG.md (v0.2.0 → v0.2.1)
- QA-NOTES.md

**Changes:**
- Console-logger-on-stdout defect: points to the UV environment management update (#253) as the fix, instead of an open question about moving logging to stderr.
- Removed references to defects that are already fixed.

**Rationale:**
PR #265 review feedback.

---

### 2026-11-18
**Files modified**:
- SKILL.md (v0.1.0 → v0.2.0)
- SKILL-IMPLEMENTATION.md (v0.1.0 → v0.2.0)
- SKILL-FRAMEWORK.md (v0.1.0 → v0.2.0)
- SKILL-TESTING.md (v0.1.0 → v0.2.0)
- SKILL-REVIEW.md (v0.1.0 → v0.2.0)
- CHANGELOG.md (v0.1.0 → v0.2.0)
- QA-NOTES.md (rewritten)

**Changes:**
- Scoped to Python_Toolkit only: removed all references to other toolkits; toolkit conventions move to their own skills.
- Made `bhom_wrapper.bhom_callable` + `run_wrapped` the only route from C# into Python: decorator required, decorated methods live in `python_toolkit/bhom/wrapped/`, wrappers stay thin.
- Documented that `bhom_callable` encodes return values to BHoM JSON when called from C#, so methods return objects (strings pass through unencoded).
- Documented the input/output contract as verified in the `Python_Toolkit/v3_10` environment, and the established C# call shape (`run_wrapped.py -command <id> -in <json file>`, whole stdout deserialised, `Traceback` text = failure).
- Added review rules PY-W01 to PY-W08 and test patterns for wrapped methods.
- Updated "Known Framework Defects" to `develop` at `d9d1edd` (#263 fixed the mutable/frozen defaults); added newly verified wrapper defects.
- Removed references to colour scales and palettes, which are not on `develop`.
- Objects with no C# type use `_t = "BH.oM.Base.CustomObject"` (review feedback).

**Rationale:**
Review feedback: C# should always call Python through `run_wrapped`; the draft missed the decorator requirement, the `bhom/wrapped/` location rule, and the automatic BHoM JSON output conversion. Content had to be shareable from the Python_Toolkit repo, which is open source.

---

### 2026-11-18
**Files created**:
- SKILL.md, SKILL-IMPLEMENTATION.md, SKILL-FRAMEWORK.md, SKILL-TESTING.md, SKILL-REVIEW.md, CHANGELOG.md (v0.1.0)

**Changes:**
- Initial cross-toolkit draft for QA.

**Rationale:**
No existing BHoM skill covered Python.

---
