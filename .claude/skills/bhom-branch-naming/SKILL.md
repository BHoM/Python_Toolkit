---
name: bhom-branch-naming
description: Name git branches for BHoM repositories as <Project>-#<IssueNumber>-<PascalCaseDescription>. Use whenever creating, renaming or reviewing a branch in any BHoM or BHoM toolkit repo - including before committing on develop/main - and when a task has no issue number yet.
version: 0.1.1
author: BHoM
tags: [BHoM, git, branches, workflow]
---

# BHoM Branch Naming Skill

## Role

You create and check git branch names in BHoM repositories so every branch traces back to the issue it addresses.

## Usage Guide

1. Never commit directly to `develop` or `main` - create a branch first.
2. Find the **issue** the work addresses and the **project** that issue belongs to.
3. Build the name with the [format](#format) below.
4. If there is no issue, [stop and ask](#no-issue-yet) - do not invent one or leave it out.
5. Check the name against the [checklist](#checklist) before creating the branch.

---

## Format

```
<Project>-#<IssueNumber>-<PascalCaseDescription>
```

| Part | Rule | Example |
|------|------|---------|
| `<Project>` | Name of the repository (or project) **where the issue lives**, exactly as GitHub spells it | `Python_Toolkit`, `Structure_Engine`, `Grasshopper_UI` |
| `-#` | Literal hyphen then hash | `-#` |
| `<IssueNumber>` | The GitHub issue number in that project | `257` |
| `-<Description>` | Short PascalCase summary, a few words, no spaces | `ReviewOldTests` |

Examples from BHoM remotes:

```
Python_Toolkit-#253-UV_environment_management
Python_Toolkit-#228-CaptureToolkitName
Structure_Engine-#3642-Extend-IsValid-for-ICase      (in the BHoM_Engine repo)
Classification_oM-#1762-AddRICSCategory             (same name in BHoM and BHoM_Engine for a paired change)
Grasshopper_UI-#740-bhom-sample-scripts             (in a toolkit repo, for an issue raised on Grasshopper_UI)
```

### The prefix is the issue's project, not always the repo

- In multi-project repos (BHoM, BHoM_Engine), use the project: `Structure_oM-#...`, `Serialiser_Engine-#...`.
- For an issue in another repo, use that repo's name and issue number, even on a branch in this repo (`Grasshopper_UI-#740-...` on a toolkit).
- **Paired changes** across repos (e.g. oM + Engine, or C# + Python) use the **same branch name in every repo**, so CI and reviewers can pair them.

### Description

- PascalCase, describing the change: `AddSpaceCalcMethods`, `FixSunriseSunset`.
- Hyphens or underscores inside the description appear in existing branches and are tolerated; **for new branches, prefer PascalCase**.
- Keep it short (about 2-5 words).

---

## No Issue Yet

A branch without an issue number breaks the convention (e.g. `Python_Toolkit-bhom-python-claude-skill`). When there is no issue:

1. **Ask the user** for the issue number, or whether to open one.
2. Opening an issue publishes content to GitHub: draft the title and body and **get explicit approval** before creating it.
3. Do not use `#XX`, `#0`, or a guessed number as a placeholder, and do not leave the number out.

---

## Not Allowed

| Wrong | Why | Right |
|-------|-----|-------|
| `Python_Toolkit-bhom-python-claude-skill` | No issue number | `Python_Toolkit-#270-AddBHoMPythonClaudeSkill` |
| `Python_Toolkit_#207-tkinter-ui-patches` | `_` before `#` | `Python_Toolkit-#207-TkinterUIPatches` |
| `Python_Toolkit-#XX-EnsureDirectoriesExist` | Placeholder number | Real issue number |
| `BHoM=#1570-DocumentationUpdates` | `=` instead of `-` | `BHoM-#1570-DocumentationUpdates` |
| `feature/add-thing`, `fix-bug`, `combined-branch` | Not the BHoM format | `<Project>-#<n>-AddThing` |
| Committing on `develop` / `main` | Protected integration branches | Branch first |

Automated branches (`dependabot/...`, `copilot/...`) are created by tools and are exempt.

(`#270` above is illustrative only.)

---

## Renaming a Branch

Local only (not pushed yet):

```bash
git branch -m <old-name> <Project>-#<n>-<Description>
```

If already pushed, rename locally, push the new name, then delete the old remote branch **only with the user's approval** (it may have an open PR or other users):

```bash
git push -u origin <new-name>
git push origin --delete <old-name>
```

An open PR does not follow a renamed branch - it must be reopened from the new branch.

---

## Checklist

- [ ] Not on `develop` / `main`
- [ ] Format `<Project>-#<IssueNumber>-<Description>`
- [ ] `<Project>` is where the issue lives, spelled exactly
- [ ] Real issue number (no placeholder)
- [ ] PascalCase description, a few words
- [ ] Same name in every repo of a paired change

---

## Related Skills

- [bhom-develop](../bhom-develop/SKILL.md) - overall development workflow; branch creation happens at the start of implementation.
- [bhom-python](../bhom-python/SKILL.md) - Python work in Python_Toolkit.

---

## Version History

**See [CHANGELOG.md](./CHANGELOG.md) for full version history.**
