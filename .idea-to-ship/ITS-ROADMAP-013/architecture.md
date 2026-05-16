# Architecture - Skill Frontmatter YAML Validation

**Slug:** ITS-ROADMAP-013
**Date:** 2026-05-16
**Status:** draft
**References:** requirements.md

## Summary

Upgrade the release gate's `skill-frontmatter` blocking check to parse
frontmatter with PyYAML before enforcing required keys. The chosen design keeps
the existing Bash release-gate shape, preserves staged index reads, adds the
roadmap fixture for invalid unquoted bracket `argument-hint`, and documents
that installed-cache synchronization is outside the non-mutating release gate.

## Goals / Non-Goals

Goals:

- Catch real YAML frontmatter parse errors before skills ship.
- Preserve current staged/working/all modes.
- Keep required `name` and `description` validation.
- Add regression coverage for the concrete invalid `argument-hint` case.
- Keep the release gate local, offline, and non-mutating.

Non-goals:

- No installed-cache mutation.
- No network dependency installation.
- No broader semantic schema for every optional frontmatter field.
- No changes to skill-hygiene advisory checks.

## Codebase Context

- `scripts/release-gate.sh` embeds a Python validator in
  `validate_frontmatter_file()`. It currently extracts the frontmatter block and
  checks required keys with regex.
- The script already depends on `python3` and uses `git show :<path>` in staged
  mode, which is the right source for index-based validation.
- `tests/release-gate-stage1.sh` creates fixture repos and already covers valid
  frontmatter, missing required keys, and staged index behavior.
- `RELEASE-GATE.md` documents `skill-frontmatter` as structural validation and
  lists required tools as `git`, `jq`, and `python3`.

## Cross-Skill Routing

| Signal | Routed skill | Result | Design impact |
|---|---|---|---|
| Release-gate change with secret scanner and generated fixture data | secret-scanner guidance | run release gate and secret-scan through existing checks | No separate skill invocation needed; strict release gate includes secret-scan. |

## Alternatives Considered

### Option A - PyYAML Parse In Existing Frontmatter Validator

Import `yaml`, parse the extracted frontmatter with `yaml.safe_load`, require a
mapping, then check `name` and `description` values.

**Module changes:** `scripts/release-gate.sh`, `tests/release-gate-stage1.sh`,
`RELEASE-GATE.md`

**Data flow:** list skill files -> read worktree or index content -> extract
frontmatter -> `yaml.safe_load` -> required-key check -> release-gate result.

**Interfaces:** same `scripts/release-gate.sh --mode staged|working|all`
interface.

**Pros:** Real loader-style YAML parse, smallest implementation, directly
catches the roadmap fixture.

**Cons:** Adds a Python module dependency (`yaml` / PyYAML) to release-gate
execution.

**Risk:** Medium-low; failure is loud if PyYAML is missing.

### Option B - Custom Regex For Known Bad Bracket Argument Hint

Keep the existing structural validator and add a targeted regex that rejects
`argument-hint: [..] [..]` unquoted values.

**Module changes:** same files as Option A.

**Data flow:** regex detects one known syntax class.

**Pros:** No new module dependency.

**Cons:** Does not satisfy "real YAML semantics"; misses other parse errors.

**Risk:** Medium; creates false confidence with a narrow detector.

### Option C - Move Skill Frontmatter Validation Into skill-hygiene

Add YAML parsing to `scripts/skill-hygiene-check.py` as an advisory or strict
hygiene check.

**Module changes:** skill-hygiene checker and fixtures.

**Pros:** Keeps all skill-specific checks in one Python script.

**Cons:** Frontmatter parse failures should be blocking, not advisory. This
would complicate the existing release-gate flow.

**Risk:** Medium; wrong failure category for loader-breaking syntax.

## Recommendation

**We pick Option A.** It is the smallest change that actually parses YAML and
keeps the existing blocking `skill-frontmatter` check in the release gate. The
accepted tradeoff is a PyYAML runtime dependency, documented as a required
Python module and failed loudly if absent.

## Chosen Design - Detail

### Module Breakdown

- `scripts/release-gate.sh` - require the Python `yaml` module and update the
  embedded frontmatter validator to parse YAML.
- `tests/release-gate-stage1.sh` - add a staged fixture for invalid unquoted
  bracket `argument-hint`.
- `RELEASE-GATE.md` - update the check description, dependency note, and
  installed-cache synchronization note.

### Data Flow

```
list_skill_files
  -> validate_frontmatter_file(path)
    -> staged: git show :path
    -> working/all: read file
    -> find --- frontmatter block
    -> yaml.safe_load(block)
    -> require mapping
    -> require non-empty name and description
  -> add PASS/FAIL skill-frontmatter result
```

### Interfaces

No command-line interface changes.

Failure evidence examples:

- `missing opening --- delimiter`
- `missing closing --- delimiter`
- `frontmatter YAML parse error: ...`
- `frontmatter must parse to a mapping`
- `missing required key(s): description`

### Data / Schema Changes

None.

### Failure Modes & Handling

- Missing PyYAML: script exits with a missing dependency message before running
  checks.
- YAML parse error: affected file is reported in `skill-frontmatter` evidence
  and release gate exits `1`.
- Staged index invalid but worktree fixed: staged mode still fails because it
  reads `git show :path`.

### Rollout / Migration

Land in one release-gate hardening commit. Existing valid skills should require
no migration because current quoted `argument-hint` values and list-style
`allowed-tools` parse correctly.

### Test Strategy Hooks

- Stage TDD adds the invalid unquoted bracket fixture and expects
  `tests/release-gate-stage1.sh` to fail before implementation.
- After implementation, run:
  - `bash tests/release-gate-stage1.sh`
  - `scripts/release-gate.sh --mode all --strict`
  - `git diff --check HEAD`

## Staged Implementation Plan

1. **Stage 1 - Parse skill frontmatter with YAML semantics**: Add red-first
   fixture coverage for invalid unquoted bracket `argument-hint`, update the
   release-gate validator to parse YAML, update docs, and verify focused and
   full release-gate commands.

## Open Questions

- None blocking. Optional field type validation is a future hardening item.
