# Architecture - Executable Skill Eval Fixtures

**Slug:** ITS-ROADMAP-006
**Date:** 2026-05-09
**Status:** draft
**References:** requirements.md

## Summary

Build a dedicated offline contract-fixture command for the critical
`idea-to-ship` skills. The chosen approach is a shell runner plus a small
Python standard-library assertion helper that validates behavioral contracts in
the skill documents and, later, fixture artifact safety rules. It does not try
to run a live model; it catches regressions in the contracts that guide the
model.

## Goals / Non-Goals

Goals:

- Provide one deterministic command for idea-to-ship skill eval fixtures.
- Cover roadmap first-run, rerun preservation, and final-without-approval
  safety contracts.
- Cover test-plan story traceability and non-happy-path requirements.
- Cover review-code missing-test-plan and runtime-aware review contracts.
- Keep the fixtures local, offline, and non-mutating outside temporary state.

Non-goals:

- Live agent evaluation, GitHub access, or network calls.
- Golden-file checking of full generated prose.
- Replacing adversarial review or manual product judgment.

## Codebase Context

- `tests/release-gate-stage1.sh` is the repo's current executable test style:
  shell functions create isolated temporary fixture repos and assert command
  outputs.
- `scripts/release-gate.sh` is the local gate entry point. It already supports
  `--mode staged|working|all` and `--json`.
- `RELEASE-GATE.md` documents that Stage 3 will add dedicated fixture
  assertions around machine-readable output.
- `idea-to-ship/skills/roadmap/SKILL.md` owns roadmap source authority,
  write-target safety, final-lane approval, and acceptance checks.
- `idea-to-ship/skills/test/SKILL.md` owns story-driven test planning and
  requires edge, invalid, abnormal, and failure-mode scenarios.
- `idea-to-ship/skills/review-code/SKILL.md` owns runtime-aware code review,
  missing-test-plan handling, and traceability checks.

The repo has no package-level test framework. Shell plus Python standard
library is the lowest-friction path consistent with the release-gate fixtures.

## Alternatives Considered

### Option A - Static Release-Gate Checks Only

Add the skill contract assertions directly inside `scripts/release-gate.sh`.

**Module changes:** `scripts/release-gate.sh`; maybe `RELEASE-GATE.md`.

**Data flow:** release gate reads `idea-to-ship/skills/*/SKILL.md`, scans for
required contract phrases, and emits pass/fail results.

**Interfaces:** no new command; use `scripts/release-gate.sh --mode <mode>`.

**Pros:** one command for operators; no extra test entry point.

**Cons:** bloats the release gate with skill-specific assertions and makes it
hard to iterate fixture logic without touching the release gate core.

**Risk:** medium - release gate becomes a shallow module with unrelated
responsibilities.

### Option B - Dedicated Offline Eval Fixture Runner

Add `tests/idea-to-ship-eval-fixtures.sh` as the operator command. The shell
runner calls a Python standard-library helper, either inline or in a companion
file, to validate named behavioral contracts in the skill Markdown.

**Module changes:** `tests/idea-to-ship-eval-fixtures.sh`; optional
`tests/idea-to-ship-eval-fixtures.py`; `RELEASE-GATE.md` or roadmap artifacts
for documentation.

**Data flow:**

```text
operator/release gate
  -> tests/idea-to-ship-eval-fixtures.sh
  -> Python assertion helper
  -> read idea-to-ship/skills/{roadmap,test,review-code}/SKILL.md
  -> emit named PASS/FAIL contract results
```

**Interfaces:**

```text
bash tests/idea-to-ship-eval-fixtures.sh
```

Exit codes:

- `0`: all fixture contracts pass.
- `1`: one or more contract regressions.
- `2`: usage/setup problem, such as missing expected skill file.

**Pros:** matches existing shell fixture style, keeps release gate small,
offline and deterministic, and can later be called from the gate.

**Cons:** Stage 1 validates instruction contracts, not actual LLM behavior.
That limitation must be explicit.

**Risk:** low to medium - assertions can become phrase brittle if they check
exact wording instead of grouped invariants.

### Option C - Live Agent Eval Harness

Create temporary repos, invoke the active agent runtime against skill commands,
and compare generated artifacts to expected behavior.

**Module changes:** new eval harness under `tests/` or `evals/`; runtime
adapters for Claude/Codex; fixture repos and expected outputs.

**Data flow:** harness creates temp repo, invokes runtime, runs skill command,
then inspects generated artifacts.

**Interfaces:** runtime-specific command, likely requiring credentials and
installed CLIs.

**Pros:** highest fidelity to actual agent behavior.

**Cons:** non-deterministic, expensive, requires local runtime setup, risks
network/API coupling, and violates the roadmap no-go for live dependencies.

**Risk:** high - likely to be flaky and unsafe as a release gate.

## Recommendation

**We pick Option B.** It fits the repo's existing shell fixture style and gives
us a deterministic eval command without expanding the release gate core. The
accepted tradeoff is that Stage 1 catches contract regressions in the skill
instructions, not full live-agent behavior.

## Chosen Design - Detail

### Module Breakdown

- `tests/idea-to-ship-eval-fixtures.sh` - executable fixture entry point.
  Resolves repo root, requires `python3`, and delegates to the assertion helper.
- `tests/idea-to-ship-eval-fixtures.py` - Python standard-library assertions
  for named skill contracts. If the implementation is small enough, this can be
  embedded in the shell script; a separate file is easier to review.
- `RELEASE-GATE.md` - documents the eval command and whether it is advisory or
  manually run in the current stage.
- `.idea-to-ship/ITS-ROADMAP-006/implementation-log.md` - records fixture
  coverage and limitations.

### Data Flow

```text
developer
  -> bash tests/idea-to-ship-eval-fixtures.sh
  -> python3 tests/idea-to-ship-eval-fixtures.py <repo-root>
  -> read SKILL.md files
  -> run named invariant checks
  -> print concise PASS/FAIL lines
  -> exit 0/1/2
```

### Interfaces

Shell command:

```text
bash tests/idea-to-ship-eval-fixtures.sh
```

Python helper contract:

```text
python3 tests/idea-to-ship-eval-fixtures.py <repo-root>
```

Named checks:

- `brainstorm-rerun-preservation-contract`
- `architect-rerun-preservation-contract`
- `roadmap-first-run-contract`
- `roadmap-rerun-preservation-contract`
- `roadmap-final-without-approval-contract`
- `test-story-traceability-contract`
- `test-negative-scenarios-contract`
- `review-code-missing-test-plan-contract`
- `review-code-runtime-aware-routing-contract`

Each check reports:

```text
PASS <check-id>: <short message>
FAIL <check-id>: <missing invariant>
```

Assertions use grouped invariants rather than exact paragraphs. A check passes
only when every required semantic group is present. For example,
`roadmap-final-without-approval-contract` should require a final-mode concept,
an approval concept, and a block/no-write concept; it should not require one
specific sentence. When a contract depends on the relationship between terms,
the helper should check those terms in a bounded text window instead of
searching the whole file independently.

Stage 1 check definitions:

| Check | Required invariant groups |
|---|---|
| `brainstorm-rerun-preservation-contract` | requirements ownership; stable requirement IDs; human content preservation; draft fallback; replacement approval |
| `architect-rerun-preservation-contract` | architecture ownership; option/stage preservation; human content preservation; draft fallback; replacement approval |
| `roadmap-first-run-contract` | first run/no existing roadmap; Candidate Brief; resolved `WRITE_TARGET` |
| `roadmap-rerun-preservation-contract` | rerun/refresh; human content preservation; generated markers or draft fallback |
| `roadmap-final-without-approval-contract` | `--final`; priority approval; final lanes blocked or not written |
| `test-story-traceability-contract` | user stories; acceptance criteria; scenario matrix; unit/integration/e2e test matrix |
| `test-negative-scenarios-contract` | happy path; edge/corner cases; invalid/abnormal input; failure modes |
| `review-code-missing-test-plan-contract` | `test-plan.md` absent; behavior-changing diff; verification gap warning |
| `review-code-runtime-aware-routing-contract` | runtime-aware routing; non-Claude runtime path; fallback reason recorded |

### Data / Schema Changes

None. Fixtures read Markdown files and do not write repo state.

### Failure Modes & Handling

- Missing `python3`: shell runner exits `2` with a setup message.
- Missing expected skill file: helper exits `2` and names the path.
- Contract removed or weakened: helper exits `1` and names the failed check.
- Wording changed but contract preserved: helper should keep passing by checking
  grouped invariants, not exact paragraphs.
- Temporary directory cleanup failure: no persistent state is required for
  Stage 1; future artifact fixtures should use `trap` cleanup like
  `tests/release-gate-stage1.sh`.

### Rollout / Migration

Stage 1 lands as a manually runnable command and documentation. It can be
called before committing idea-to-ship skill changes. After one stable pass, a
later release-gate stage can call it as an advisory or blocking check.

### Limitations / False Confidence Guardrail

These fixtures prove that the repo's skill contracts still contain the required
safety and traceability instructions. They do not prove that a future model run
will obey those instructions. The command output and implementation log must
label the coverage as contract fixtures to avoid overstating the signal.

### Test Strategy Hooks

- Unit-like checks live in the Python helper as named assertions.
- Integration smoke is `bash tests/idea-to-ship-eval-fixtures.sh`.
- Regression validation is done by temporarily removing one invariant during
  local development and confirming the helper fails; this should be noted in
  the implementation log rather than committed.

## Staged Implementation Plan

1. **Stage 1 - Contract fixture command:** Add the shell runner, Python helper,
   documentation, and implementation log. Cover the named checks and label the
   output as contract-fixture coverage.
2. **Stage 2 - Artifact safety fixtures:** Add temporary artifact fixtures for
   generated-marker preservation and draft fallback behavior if those behaviors
   become executable outside the LLM prompt.
3. **Stage 3 - Release-gate integration:** Decide advisory vs blocking and wire
   the eval command into `scripts/release-gate.sh` or `RELEASE-GATE.md`.
4. **Stage 4 - Delegation authorization hardening:** Require user/host
   authorization before runtime sub-agent delegation, with main-context
   fallback recording.
5. **Stage 5 - Requirements and architecture ownership safety:** Extend
   `/brainstorm` and `/architect` rerun rules plus fixture coverage for
   canonical artifact preservation and draft fallback.
6. **Stage 6 - Capacity fallback hardening:** Treat review sub-agent
   model-selection and capacity errors as sub-agent unavailability, then
   continue in the main context and record the fallback reason.

## Open Questions

- None blocking. Stage 1 should be manually runnable only; release-gate
  invocation belongs to Stage 3 after the check definitions prove stable.
