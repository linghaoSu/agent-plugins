# Test Plan - ITS-ROADMAP-006

**Date:** 2026-05-09
**Target:** `tests/idea-to-ship-eval-fixtures.sh`,
`tests/idea-to-ship-eval-fixtures.py`, `RELEASE-GATE.md`
**Framework:** shell fixture tests plus Python standard library
**Run command:** `bash tests/idea-to-ship-eval-fixtures.sh`

## Scope

This plan covers Stage 1 contract fixtures for critical `idea-to-ship` skills.
It verifies the runnable command, contract-regression failure behavior, and
basic usage/setup errors. It does not cover live model behavior or generated
artifact preservation; those are explicit Stage 2/3 concerns.

## User Stories

| Story ID | Actor | Goal | Preconditions | Trigger | Expected Outcome | Source |
|---|---|---|---|---|---|---|
| US-1 | Plugin maintainer | Run a local offline check before changing critical idea-to-ship skills. | Repo has `python3` and the three target skill files. | Execute `bash tests/idea-to-ship-eval-fixtures.sh`. | Seven named contract checks pass and no repo state is mutated. | FR-1, FR-9 |
| US-2 | Skill maintainer | Catch accidental removal of roadmap/test/review-code safety contracts. | A critical contract is missing from a target `SKILL.md`. | Execute the Python helper against that repo root. | Command exits non-zero and names the failed contract. | FR-2..FR-8, FR-10 |
| US-3 | Release operator | Understand setup failures separately from contract failures. | Command is invoked with invalid setup or arguments. | Execute helper with missing/invalid repo root. | Command exits `2` with a usage/setup message. | architecture Failure Modes |

## Acceptance Criteria

| AC ID | Story ID | Criterion | Verification Method | Source |
|---|---|---|---|---|
| AC-1 | US-1 | Current repo passes all seven contract checks. | `T1` current-repo fixture pass. | FR-1 |
| AC-2 | US-2 | Removing the roadmap Candidate Brief contract fails `roadmap-first-run-contract`. | `T2` temporary root negative smoke. | FR-2, FR-10 |
| AC-3 | US-3 | Invalid helper invocation exits `2` and explains usage/setup. | `T3` missing argument and nonexistent root checks. | architecture Failure Modes |

## Scenario Matrix

| Scenario ID | Story ID | Type | Sequence | Inputs / Setup | Expected | Failure Signal | Source |
|---|---|---|---|---|---|---|---|
| S-1 | US-1 | happy | Run shell entry point in repo root. | Current `idea-to-ship` skills. | Exit `0`; seven `PASS` lines. | none | AC-1 |
| S-2 | US-2 | regression | Copy target skills to temp root, remove `Candidate Brief`, run helper. | Modified roadmap skill fixture. | Exit `1`; `FAIL roadmap-first-run-contract`. | failed contract id | AC-2 |
| S-3 | US-3 | invalid-input | Invoke helper without required root argument. | No positional argument. | Exit `2`; usage printed. | usage message | AC-3 |
| S-4 | US-3 | invalid-input | Invoke helper with nonexistent root. | `/tmp/agent-plugins-nonexistent-root-006`. | Exit `2`; setup error printed. | setup message | AC-3 |

## Test Matrix

### Unit

| # | Scenario | Case | Input | Expected | Source |
|---|---|---|---|---|---|
| U1 | S-2 | Bounded invariant catches removed first-run Candidate Brief relation. | Temporary copied skill with `Candidate Brief` removed. | `roadmap-first-run-contract` fails. | AC-2 |

### Integration

| # | Scenario | Case | Setup | Expected | Source |
|---|---|---|---|---|---|
| I1 | S-1 | Current repo contract fixtures pass. | Run shell entry point. | Exit `0`; seven pass lines. | AC-1 |
| I2 | S-3 | Missing helper argument is usage error. | Run Python helper with no args. | Exit `2`; usage text. | AC-3 |
| I3 | S-4 | Nonexistent root is setup error. | Run Python helper with nonexistent root. | Exit `2`; root error text. | AC-3 |

### E2E

None. This stage deliberately avoids live agent/runtime execution.

## Fixtures & Test Data

- Temporary roots are created under `${TMPDIR:-/tmp}` and removed after the
  negative smoke.
- The negative smoke copies the three target `SKILL.md` files and mutates only
  the copied roadmap skill.

## Results

- `bash tests/idea-to-ship-eval-fixtures.sh`: pass, 7 contract checks.
- Negative smoke with removed roadmap Candidate Brief: pass, helper exits `1`
  and reports `FAIL roadmap-first-run-contract`.
- `python3 tests/idea-to-ship-eval-fixtures.py`: pass, exits `2` with usage.
- `python3 tests/idea-to-ship-eval-fixtures.py /tmp/agent-plugins-nonexistent-root-006`: pass, exits `2` with setup error.
