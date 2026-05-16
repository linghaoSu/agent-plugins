# Test Plan - ITS-ROADMAP-015

**Date:** 2026-05-16
**Target:** `scripts/skill-hygiene-check.py`, `scripts/skill-authoring-baseline.txt`, `tests/skill-hygiene-check-fixtures.py`, `tests/skill-hygiene-release-gate-fixtures.sh`, `scripts/release-gate.sh`, `RELEASE-GATE.md`
**Framework:** Python fixture runner + Bash release-gate fixtures
**Run command:** `bash tests/skill-hygiene-check-fixtures.sh`

## Scope

Cover the new authoring-standard hygiene checks, baseline target selection, staged
related-skill inventory behavior, release-gate evidence, and documentation. This
plan does not attempt to prove semantic diagram/prose equivalence beyond the
deterministic Mermaid presence and shape rules in `architecture.md`.

## User Stories

| Story ID | Actor | Goal | Preconditions | Trigger | Expected Outcome | Source |
|---|---|---|---|---|---|---|
| US-1 | Skill author | Get deterministic feedback when a new or changed skill lacks actionable structure. | A changed `SKILL.md` is scanned locally. | Run skill hygiene checker. | Missing usage, workflow tracking, diagram, related-skill, command-safety, and placeholder issues are reported with stable IDs. | FR-1..FR-7 |
| US-2 | Plugin releaser | Keep legacy strict all-mode green without hiding new weak skills. | Baseline file exists. | Run release gate in strict all mode. | Legacy baselined skills are quiet for authoring checks; unbaselined weak skills fail strict advisory promotion. | FR-8, FR-10 |
| US-3 | Maintainer | Trust staged-mode related-skill validation against the index. | Source and target skill changes are staged while the worktree may differ. | Run staged hygiene checker. | Staged-added targets resolve, staged-deleted and worktree-only targets do not. | FR-5 |

## Acceptance Criteria

| AC ID | Story ID | Criterion | Verification Method | Source |
|---|---|---|---|---|
| AC-1 | US-1 | Weak changed skills emit the seven new authoring check IDs. | `bash tests/skill-hygiene-check-fixtures.sh` | FR-1..FR-7 |
| AC-2 | US-1 | Authoring-compliant changed skills do not emit the new IDs. | `bash tests/skill-hygiene-check-fixtures.sh` | FR-1..FR-7 |
| AC-3 | US-2 | Baselined legacy skills skip only authoring checks, not existing hygiene checks. | `bash tests/skill-hygiene-check-fixtures.sh` | FR-8, FR-10 |
| AC-4 | US-2 | Release-gate JSON shows strict all-mode failure for an unbaselined weak committed skill. | `bash tests/skill-hygiene-release-gate-fixtures.sh` | FR-8, FR-10 |
| AC-5 | US-3 | Staged related refs use staged index state, not dirty worktree-only state. | `bash tests/skill-hygiene-check-fixtures.sh` | FR-5 |

## Scenario Matrix

| Scenario ID | Story ID | Type | Sequence | Inputs / Setup | Expected | Failure Signal | Source |
|---|---|---|---|---|---|---|---|
| S-1 | US-1 | invalid-input | Add weak changed skill and run checker. | Missing sections plus unsafe command and placeholder. | Seven new IDs. | Missing or extra IDs. | AC-1 |
| S-2 | US-1 | happy | Add compliant changed skill and run checker. | Usage, workflow tracking, Mermaid, related skill, safe command, explained placeholder. | No findings. | Unexpected authoring ID. | AC-2 |
| S-3 | US-2 | regression | Baseline an existing weak skill, then create an existing all-mode long-description finding. | Baseline includes skill hash. | Existing check still fires. | Existing check hidden by baseline. | AC-3 |
| S-4 | US-2 | failure-mode | Commit weak skill absent from baseline and run strict release-gate fixture. | Candidate repo strict all mode. | `skill-hygiene` advisory promoted to fail with authoring ID evidence. | Pass or missing evidence. | AC-4 |
| S-5 | US-3 | edge | Stage source/target skill changes, dirty or delete worktree files, run staged checker. | Staged-added, staged-deleted, and worktree-only target cases. | Index semantics preserved. | Dirty worktree affects staged result. | AC-5 |

## Test Matrix

### Unit

| # | Scenario | Case | Input | Expected | Source |
|---|---|---|---|---|---|
| U1 | S-1 | `scenario_authoring_standard_findings` | Temporary repo with weak changed skill. | Seven new authoring IDs. | AC-1 |
| U2 | S-2 | `scenario_authoring_standard_non_findings` | Temporary repo with compliant changed skill. | Pass. | AC-2 |
| U3 | S-3 | `scenario_authoring_baseline_target_selection` | Baselined long-description skill. | `long-description` still reports. | AC-3 |
| U4 | S-5 | `scenario_authoring_related_skills_staged_inventory` | Staged-added/deleted/worktree-only refs. | Expected pass/fail per index. | AC-5 |

### Integration

| # | Scenario | Case | Setup | Expected | Source |
|---|---|---|---|---|---|
| I1 | S-4 | release-gate JSON strict evidence | Candidate repo with unbaselined weak committed skill. | `skill-hygiene` fail evidence includes new ID. | AC-4 |

### E2E

| # | Scenario | Case | Flow | Expected | Source |
|---|---|---|---|---|---|
| E1 | S-1..S-5 | full release verification | Run `scripts/release-gate.sh --mode all --strict`. | All blocking and advisory checks pass for this repo. | FR-10 |

## Traceability

| Requirement | Story | Acceptance Criteria | Scenarios | Tests |
|---|---|---|---|---|
| FR-1 | US-1 | AC-1, AC-2 | S-1, S-2 | U1, U2 |
| FR-2 | US-1 | AC-1, AC-2 | S-1, S-2 | U1, U2 |
| FR-3 | US-1 | AC-1, AC-2 | S-1, S-2 | U1, U2 |
| FR-4 | US-1 | AC-1, AC-2 | S-1, S-2 | U1, U2 |
| FR-5 | US-3 | AC-5 | S-5 | U4 |
| FR-6 | US-1 | AC-1, AC-2 | S-1, S-2 | U1, U2 |
| FR-7 | US-1 | AC-1, AC-2 | S-1, S-2 | U1, U2 |
| FR-8 | US-2 | AC-4 | S-4 | I1 |
| FR-9 | US-1, US-2, US-3 | AC-1..AC-5 | S-1..S-5 | U1..U4, I1 |
| FR-10 | US-2 | AC-3, AC-4 | S-3, S-4 | U3, I1, E1 |

## Out Of Scope

- Exact diagram/prose semantic matching is a manual review expectation.
- Full historical cleanup of existing skills is deferred by the baseline.

## Fixtures & Test Data

Temporary git repositories created by `tests/skill-hygiene-check-fixtures.py` and
candidate clones created by `tests/skill-hygiene-release-gate-fixtures.sh`.

## Risk Notes

Baseline behavior is intentionally asymmetric: staged/working can enforce that a
baseline edit does not hide touched weak skills; committed all-mode can only
detect unbaselined weak skills after history has lost the edit context.

## Stage TDD Slices

| Stage | Story | Acceptance | Scenario | Test | Expected Initial Result | Command |
|---|---|---|---|---|---|---|
| Stage 1 | US-1 | AC-1 | S-1 invalid-input | U1 | fail: new authoring checks not implemented | `bash tests/skill-hygiene-check-fixtures.sh` |
| Stage 1 | US-2 | AC-4 | S-4 failure-mode | I1 | fail: release-gate evidence lacks new authoring IDs | `bash tests/skill-hygiene-release-gate-fixtures.sh --self-check` |

## Results

**Date:** 2026-05-16 21:19 CST  
**Status:** pass  
**Commands:**

- `python3 -m py_compile scripts/skill-hygiene-check.py tests/skill-hygiene-check-fixtures.py` - pass after review fixes
- `bash tests/skill-hygiene-check-fixtures.sh` - pass after review fixes
- `bash tests/skill-hygiene-release-gate-fixtures.sh --self-check` - pass after review fixes
- `bash tests/skill-hygiene-release-gate-fixtures.sh` - pass after review fixes
- `bash tests/skill-topology-scan-fixtures.sh` - pass after review fixes
- `python3 scripts/skill-hygiene-check.py --mode working .` - pass after review fixes
- `python3 scripts/skill-topology-scan.py .` - pass after review fixes, 0 broken references
- `python3 secret-scanner/scripts/scan.py --mode working --format json` - pass after review fixes, `[]`
- `scripts/release-gate.sh --mode all --strict` - pass after review fixes
- baseline hash audit - pass, 35 skill hashes match
- `rg -n "skill-creator|skill creator" . --glob '*.md' --glob '*.py' --glob '*.sh'` - no matches

**Coverage notes:** Fixtures now cover weak/compliant authoring structures,
baseline target selection, existing-check preservation under baseline,
self-reference related-skill behavior, staged-added/staged-deleted/worktree-only
related-skill inventory, command safety, placeholder explanation, hidden Mermaid
comments, four-space-indented Mermaid fence content, and strict all-mode
release-gate evidence for an unbaselined weak committed skill.
