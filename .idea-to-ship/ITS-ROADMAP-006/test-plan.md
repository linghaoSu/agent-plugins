# Test Plan - ITS-ROADMAP-006

**Date:** 2026-05-09
**Target:** `tests/idea-to-ship-eval-fixtures.sh`,
`tests/idea-to-ship-eval-fixtures.py`, `RELEASE-GATE.md`,
`idea-to-ship/README.md`, `idea-to-ship/skills/implement/SKILL.md`,
`idea-to-ship/skills/brainstorm/SKILL.md`,
`idea-to-ship/skills/architect/SKILL.md`
**Framework:** shell fixture tests plus Python standard library
**Run command:** `bash tests/idea-to-ship-eval-fixtures.sh`

## Scope

This plan covers contract and artifact fixtures for critical `idea-to-ship`
skills. It verifies the runnable command, contract-regression failure behavior,
basic usage/setup errors, roadmap artifact safety rules, and test-plan
traceability sections. It also covers rerun ownership safety for
`requirements.md` and `architecture.md`. It does not cover live model behavior
or release-gate integration; those remain explicit non-goals for this stage.

## User Stories

| Story ID | Actor | Goal | Preconditions | Trigger | Expected Outcome | Source |
|---|---|---|---|---|---|---|
| US-1 | Plugin maintainer | Run a local offline check before changing critical idea-to-ship skills. | Repo has `python3` and the target idea-to-ship skill/docs files. | Execute `bash tests/idea-to-ship-eval-fixtures.sh`. | Named contract checks pass and no repo state is mutated. | FR-1, FR-9 |
| US-2 | Skill maintainer | Catch accidental removal of roadmap/test/review-code safety contracts. | A critical contract is missing from a target `SKILL.md`. | Execute the Python helper against that repo root. | Command exits non-zero and names the failed contract. | FR-2..FR-8, FR-10 |
| US-3 | Release operator | Understand setup failures separately from contract failures. | Command is invoked with invalid setup or arguments. | Execute helper with missing/invalid repo root. | Command exits `2` with a usage/setup message. | architecture Failure Modes |
| US-4 | Plugin maintainer | Detect unsafe roadmap artifact shapes before relying on rerun preservation. | Roadmap artifacts may have generated markers, human-only content, or malformed marker state. | Execute the fixture helper. | Valid generated artifacts stay writable; human-only content resolves to `roadmap.draft.md`; malformed artifacts fail or draft safely. | Stage 2 |
| US-5 | Plugin maintainer | Confirm test-plan artifacts still expose story/scenario/test traceability. | A slug test-plan exists. | Execute the fixture helper. | Required traceability headings are present. | Stage 2 |
| US-6 | Release operator | See idea-to-ship fixture health during full-repo release hardening without blocking release-gate exit on advisory-only failures. | Release gate runs in `--mode all`. | Execute `scripts/release-gate.sh --mode all`. | `idea-to-ship-fixtures` appears under Advisory and does not alter blocking exit semantics. | Stage 3 |
| US-7 | Skill author | Avoid spawning sub-agents in runtimes that require explicit delegation authorization. | A skill defines explorer/reviewer/collection roles. | Read the runtime-aware routing contract. | It says delegation happens only when host/user policy authorizes it and otherwise records a main-context fallback. | Stage 4 |
| US-8 | Skill author | Avoid overwriting existing requirements or architecture artifacts during reruns. | `requirements.md` or `architecture.md` may contain human edits or unstructured content. | Run `/brainstorm` or `/architect` again, or execute the fixture helper. | Stable IDs/sections are preserved when safe; unsafe merges write a draft or require approval. | FR-11 |
| US-9 | Codex user | Continue `/review-code` when a selected review model is at capacity. | A review sub-agent request fails with a model-selection or capacity error. | Run `/review-code` in Codex. | The skill falls back to main-context adversarial review and records the capacity fallback reason. | FR-12 |

## Acceptance Criteria

| AC ID | Story ID | Criterion | Verification Method | Source |
|---|---|---|---|---|
| AC-1 | US-1 | Current repo passes all contract checks. | `T1` current-repo fixture pass. | FR-1 |
| AC-2 | US-2 | Removing the roadmap Candidate Brief contract fails `roadmap-first-run-contract`. | `T2` temporary root negative smoke. | FR-2, FR-10 |
| AC-3 | US-3 | Invalid helper invocation exits `2` and explains usage/setup. | `T3` missing argument and nonexistent root checks. | architecture Failure Modes |
| AC-4 | US-4 | Roadmap artifacts with valid generated markers resolve to the original file, while human-only roadmap content resolves to `roadmap.draft.md`. | `T4` artifact fixture pass. | Stage 2 |
| AC-5 | US-4 | Existing roadmap lane items use the full lane item schema. | `T5` artifact fixture pass. | Stage 2 |
| AC-6 | US-5 | The current test plan keeps user story, acceptance, scenario, test matrix, and result sections. | `T6` artifact fixture pass. | Stage 2 |
| AC-7 | US-6 | `--mode all` runs the idea-to-ship fixture command as an advisory pass in this repo. | `T7` release-gate all pass. | Stage 3 |
| AC-8 | US-6 | A repo without the idea-to-ship fixture command reports an advisory warning but exits `0` when blocking checks pass. | `T8` release-gate fixture repo pass. | Stage 3 |
| AC-9 | US-7 | The runtime-aware review fixture requires delegation authorization wording in `review-code`. | `T9` contract fixture pass. | Stage 4 |
| AC-10 | US-8 | `brainstorm` and `architect` define ownership rules for preserving stable IDs/sections, human edits, draft fallback, and explicit replacement approval. | `T10` contract fixture pass. | FR-11 |
| AC-11 | US-8 | Structured current requirements/architecture artifacts stay writable, while malformed human-only artifacts resolve to `.draft.md` files. | `T11` artifact fixture pass. | FR-11 |
| AC-12 | US-9 | Runtime-aware review contracts explicitly treat selected-model capacity errors as fallback-required and prohibit retrying the same selected model. | `T12` contract fixture pass. | FR-12 |

## Scenario Matrix

| Scenario ID | Story ID | Type | Sequence | Inputs / Setup | Expected | Failure Signal | Source |
|---|---|---|---|---|---|---|---|
| S-1 | US-1 | happy | Run shell entry point in repo root. | Current `idea-to-ship` skills/docs. | Exit `0`; all contract checks pass. | none | AC-1 |
| S-2 | US-2 | regression | Copy target skills to temp root, remove `Candidate Brief`, run helper. | Modified roadmap skill fixture. | Exit `1`; `FAIL roadmap-first-run-contract`. | failed contract id | AC-2 |
| S-3 | US-3 | invalid-input | Invoke helper without required root argument. | No positional argument. | Exit `2`; usage printed. | usage message | AC-3 |
| S-4 | US-3 | invalid-input | Invoke helper with nonexistent root. | `/tmp/agent-plugins-nonexistent-root-006`. | Exit `2`; setup error printed. | setup message | AC-3 |
| S-5 | US-4 | happy | Inspect current `.idea-to-ship/roadmap.md`. | Generated marker pair and lane items. | Markers are valid; lane items have required fields; write target remains roadmap.md. | artifact failure line | AC-4, AC-5 |
| S-6 | US-4 | preservation | Create temporary generated roadmap fixture. | Human note plus generated marker pair. | Write target remains the original generated file. | artifact failure line | AC-4 |
| S-7 | US-4 | overwrite-safety | Create temporary human-only roadmap fixture. | Non-empty roadmap without generated markers. | Write target resolves to `roadmap.draft.md`. | artifact failure line | AC-4 |
| S-8 | US-5 | happy | Inspect this slug's `test-plan.md`. | Current test-plan artifact. | Required traceability headings are present. | artifact failure line | AC-6 |
| S-9 | US-6 | happy | Run full release gate in this repo. | `tests/idea-to-ship-eval-fixtures.sh` exists and passes. | Advisory reports `PASS idea-to-ship-fixtures`; exit `0`. | release-gate output | AC-7 |
| S-10 | US-6 | alternate | Run full release gate in fixture repo without idea-to-ship fixtures. | Blocking checks pass; fixture command absent. | Advisory reports `WARN idea-to-ship-fixtures`; exit `0`. | release-gate fixture output | AC-8 |
| S-11 | US-7 | regression | Remove authorization wording from runtime-aware routing contract. | Modified review-code skill fixture. | Runtime-aware routing contract fails. | fixture failure line | AC-9 |
| S-12 | US-8 | regression | Remove brainstorm/architect ownership wording. | Modified skill fixture. | Rerun preservation contract fails. | fixture failure line | AC-10 |
| S-13 | US-8 | overwrite-safety | Create temporary human-only requirements and architecture fixtures. | Non-empty artifacts without expected headings. | Write targets resolve to `requirements.draft.md` and `architecture.draft.md`. | artifact failure line | AC-11 |
| S-14 | US-8 | happy | Inspect this slug's requirements and architecture artifacts. | Current structured artifacts. | Core headings exist and write targets remain canonical files. | artifact failure line | AC-11 |
| S-15 | US-9 | fallback | Review sub-agent request reports "Selected model is at capacity". | Runtime-aware review skill text. | Skill says to stop sub-agent attempts, continue main-context review, and record capacity fallback. | fixture failure line | AC-12 |

## Test Matrix

### Unit

| # | Scenario | Case | Input | Expected | Source |
|---|---|---|---|---|---|
| U1 | S-2 | Bounded invariant catches removed first-run Candidate Brief relation. | Temporary copied skill with `Candidate Brief` removed. | `roadmap-first-run-contract` fails. | AC-2 |
| U2 | S-7 | Human-only roadmap content is not overwritten. | Temporary roadmap without generated markers. | Write target is `roadmap.draft.md`. | AC-4 |
| U3 | S-13 | Human-only requirements content is not overwritten. | Temporary requirements artifact without core headings. | Write target is `requirements.draft.md`. | AC-11 |
| U4 | S-13 | Human-only architecture content is not overwritten. | Temporary architecture artifact without core headings. | Write target is `architecture.draft.md`. | AC-11 |

### Integration

| # | Scenario | Case | Setup | Expected | Source |
|---|---|---|---|---|---|
| I1 | S-1 | Current repo contract fixtures pass. | Run shell entry point. | Exit `0`; all contract checks pass. | AC-1 |
| I2 | S-3 | Missing helper argument is usage error. | Run Python helper with no args. | Exit `2`; usage text. | AC-3 |
| I3 | S-4 | Nonexistent root is setup error. | Run Python helper with nonexistent root. | Exit `2`; root error text. | AC-3 |
| I4 | S-5 | Current roadmap artifact is structurally safe. | Run shell entry point. | Generated markers, lane schema, and write target checks pass. | AC-4, AC-5 |
| I5 | S-8 | Current test-plan artifact exposes traceability sections. | Run shell entry point. | Test-plan traceability artifact check passes. | AC-6 |
| I6 | S-9 | Current repo release gate includes advisory fixture pass. | Run `scripts/release-gate.sh --mode all`. | Exit `0`; Advisory contains `PASS idea-to-ship-fixtures`. | AC-7 |
| I7 | S-10 | Missing idea-to-ship fixture is non-blocking outside this plugin repo. | Run `bash tests/release-gate-stage1.sh`. | Fixture test passes advisory warning scenario. | AC-8 |
| I8 | S-11 | Runtime-aware routing contract includes delegation authorization wording. | Run `bash tests/idea-to-ship-eval-fixtures.sh`. | `review-code-runtime-aware-routing-contract` passes. | AC-9 |
| I9 | S-12 | Brainstorm and architect rerun contracts include ownership safety wording. | Run `bash tests/idea-to-ship-eval-fixtures.sh`. | `brainstorm-rerun-preservation-contract` and `architect-rerun-preservation-contract` pass. | AC-10 |
| I10 | S-14 | Current requirements and architecture artifacts are structurally safe to update. | Run `bash tests/idea-to-ship-eval-fixtures.sh`. | `requirements-structured-artifact` and `architecture-structured-artifact` pass. | AC-11 |
| I11 | S-15 | Runtime-aware review contract includes capacity fallback wording. | Run `bash tests/idea-to-ship-eval-fixtures.sh`. | `review-code-runtime-aware-routing-contract` passes with capacity fallback invariant. | AC-12 |

### E2E

None. This stage deliberately avoids live agent/runtime execution.

## Fixtures & Test Data

- Temporary roots are created under `${TMPDIR:-/tmp}` and removed after the
  negative smoke.
- The negative smoke copies the three target `SKILL.md` files and mutates only
  the copied roadmap skill.

## Results

- `bash tests/idea-to-ship-eval-fixtures.sh`: pass, 13 contract checks.
- Negative smoke with removed roadmap Candidate Brief: pass, helper exits `1`
  and reports `FAIL roadmap-first-run-contract`.
- `python3 tests/idea-to-ship-eval-fixtures.py`: pass, exits `2` with usage.
- `python3 tests/idea-to-ship-eval-fixtures.py /tmp/agent-plugins-nonexistent-root-006`: pass, exits `2` with setup error.

## Results

**Completed:** 2026-05-12

- `python3 -m py_compile tests/idea-to-ship-eval-fixtures.py`: pass.
- `bash tests/idea-to-ship-eval-fixtures.sh`: pass, 13 contract checks and 6
  artifact checks.
- Artifact fixtures covered generated marker structure, lane item schema,
  write-target preservation, human-only draft fallback, generated-marker
  preservation, and test-plan traceability sections.

## Results

**Completed:** 2026-05-12

- `bash tests/release-gate-stage1.sh`: pass, including all-mode non-blocking
  advisory warning coverage.
- `scripts/release-gate.sh --mode all`: pass, with `PASS idea-to-ship-fixtures`
  under Advisory.
- `scripts/release-gate.sh --mode all --json`: pass, with
  `idea-to-ship-fixtures` reported as `category: advisory`.

## Results

**Completed:** 2026-05-12

- `bash tests/idea-to-ship-eval-fixtures.sh`: pass, including delegation
  authorization in `review-code-runtime-aware-routing-contract`.
- `scripts/release-gate.sh --mode all`: pass, advisory fixture check included.

## Results

**Completed:** 2026-05-12

- `python3 -m py_compile tests/idea-to-ship-eval-fixtures.py`: pass.
- `bash tests/idea-to-ship-eval-fixtures.sh`: pass, including
  `brainstorm-rerun-preservation-contract`,
  `architect-rerun-preservation-contract`, `requirements-structured-artifact`,
  `architecture-structured-artifact`, and draft fallback checks for both
  artifacts.
- `bash tests/release-gate-stage1.sh`: pass.
- `scripts/release-gate.sh --mode staged`: pass, fixture advisory skipped.
- `scripts/release-gate.sh --mode working`: pass, fixture advisory skipped.
- `scripts/release-gate.sh --mode all`: pass, advisory fixture check included.
- `scripts/release-gate.sh --mode all --json`: pass, advisory check included.
- `git diff --check`: pass.

## Results

**Completed:** 2026-05-12

- `python3 -m py_compile tests/idea-to-ship-eval-fixtures.py`: pass.
- `bash tests/idea-to-ship-eval-fixtures.sh`: pass, including selected-model
  capacity fallback coverage in
  `review-code-runtime-aware-routing-contract`.
- `bash tests/release-gate-stage1.sh`: pass.
- `scripts/release-gate.sh --mode staged`: pass, fixture advisory skipped.
- `scripts/release-gate.sh --mode working`: pass, fixture advisory skipped.
- `scripts/release-gate.sh --mode all`: pass, advisory fixture check included.
- `scripts/release-gate.sh --mode all --json`: pass, advisory check included.
- `git diff --check`: pass.
