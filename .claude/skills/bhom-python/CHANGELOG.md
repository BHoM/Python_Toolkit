---
name: BHoM Python Skill Changelog
description: Version history for all files in the bhom-python skill folder
version: 0.2.0
author: DRAFT - for QA
tags: [BHoM, Python, changelog]
---

# Changelog - BHoM Python Skill

## Change History

### 2026-11-18 (Latest)
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
