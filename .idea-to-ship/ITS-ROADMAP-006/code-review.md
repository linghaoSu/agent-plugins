# Code Review - ITS-ROADMAP-006

**Date:** 2026-05-09
**Reviewer:** main-context adversarial review fallback + self-review
**Iterations:** 1
**Result:** clean
**Diff size:** 9 files changed

## Issues Raised & Resolution

| # | Severity | File:line | Issue | Resolution |
|---|---|---|---|---|
| 1 | warning | `tests/idea-to-ship-eval-fixtures.py` | The first `roadmap-first-run-contract` check was too broad: removing one `Candidate Brief` occurrence from the roadmap skill still passed because the helper searched the whole file independently. | Changed the first-run check to require `first run`, `candidate brief`, and `write_target` in a bounded text window. Added a negative smoke that now fails the copied fixture as expected. |
| 2 | warning | `.idea-to-ship/ITS-ROADMAP-006/implementation-log.md` | The original syntax verification used `bash -n a b c`, but Bash only syntax-checks the first script and treats the rest as arguments. | Reran `bash -n` separately for each script and corrected the log. |
| 3 | warning | `.idea-to-ship/ITS-ROADMAP-006/test-plan.md` | The behavior-changing fixture command initially had requirements, architecture, and implementation log, but no story/scenario/test traceability artifact. | Added `test-plan.md` with stories, acceptance criteria, scenario matrix, test matrix, and recorded results. |

## Out-of-Scope Issues Skipped

None.

## Design Drift

None. Stage 1 followed the architecture: manually runnable contract fixtures,
no live model/GitHub execution, no release-gate wiring yet.

## Test Traceability

Clean. `test-plan.md` now covers the happy path, contract-regression negative
path, and invalid setup/input paths. Stage 2 still owns generated artifact
preservation fixtures if those behaviors become executable outside the model
prompt.

## Residual Open Issues

None.

## Final Verdict

LGTM

## Stage 2 Addendum

**Date:** 2026-05-12
**Reviewer:** main-context adversarial review fallback + self-review
**Iterations:** 1
**Result:** clean
**Diff size:** 7 files changed, 265 insertions, 14 deletions before review log update
**Fallback reason:** current runtime policy requires explicit user authorization
for sub-agent delegation; this run used the same review prompt in the main
context.

### Issues Raised & Resolution

| # | Severity | File:line | Issue | Resolution |
|---|---|---|---|---|
| 1 | warning | `idea-to-ship/README.md` | The typical flow ran `/review-code` before `/test`, which conflicts with review-code's test-plan traceability expectations and naturally creates missing-test-plan warnings. | Moved `/test` before final `/review-code`. |
| 2 | warning | `idea-to-ship/README.md`; `idea-to-ship/skills/implement/SKILL.md` | "staged commits" implied git commits even though `/implement` explicitly does not commit or push. | Reworded to stage-by-stage local edits and adjusted implement hand-off guidance. |
| 3 | warning | `tests/idea-to-ship-eval-fixtures.py` | Contract fixtures still did not exercise artifact safety rules. | Added artifact checks for generated markers, lane schema, write target, draft fallback, marker preservation, and test-plan traceability. |

### Out-of-Scope Issues Skipped

None.

### Design Drift

None. Stage 2 stays within the architecture's no-live-agent constraint by
validating artifact safety rules directly in the existing offline Python
fixture helper.

### Test Traceability

Clean. The Stage 2 `test-plan.md` rows map artifact safety behavior to user
stories, acceptance criteria, scenarios, unit-style cases, integration cases,
and fixture command results.

### Residual Open Issues

None.

### Verification

- `python3 -m py_compile tests/idea-to-ship-eval-fixtures.py`: pass.
- `bash tests/idea-to-ship-eval-fixtures.sh`: pass.
- `git diff --check`: pass.
- `scripts/release-gate.sh --mode working`: pass.
- `scripts/release-gate.sh --mode all`: pass.

### Final Verdict

LGTM

## Stage 6 Addendum

**Date:** 2026-05-12
**Reviewer:** main-context adversarial review fallback + user-reported runtime finding
**Iterations:** 1
**Result:** clean
**Fallback reason:** current runtime policy requires explicit user authorization
for sub-agent delegation; additionally, the reported Codex failure mode was a
selected-model capacity error, which now falls back to the main context.

### Issues Raised & Resolution

| # | Severity | File:line | Issue | Resolution |
|---|---|---|---|---|
| 1 | warning | `idea-to-ship/skills/review-code/SKILL.md`; `idea-to-ship/PRINCIPLES.md` | In Codex, "Selected model is at capacity" can make `/review-code` appear broken because the skill did not explicitly classify selected-model/capacity errors as sub-agent unavailability. | Added capacity fallback rules: stop retrying the same selected model, run the same adversarial prompt in the main context, and record the capacity fallback reason. Applied the same rule to `review-design`. |
| 2 | warning | `tests/idea-to-ship-eval-fixtures.py` | The runtime-aware routing fixture did not require capacity fallback wording, so the regression could return. | Added a `capacity fallback` invariant to `review-code-runtime-aware-routing-contract`. |
| 3 | warning | `tests/idea-to-ship-eval-fixtures.py` | Some new invariant groups were too weak because alternative patterns let one concept satisfy a multi-part contract, and a bare `authorized` match could be satisfied inside `unauthorized`. | Split brainstorm/architect preservation checks into separate invariants and replaced the bare authorization pattern with explicit authorization/host-permission requirements. |

### Out-of-Scope Issues Skipped

- Installed Codex plugin cache refresh. The source repo now has the fix, but an
  already-installed cached plugin may need reinstall/refresh before Codex uses
  the new skill text.

### Design Drift

Stage 6 extends runtime-aware routing based on a real Codex capacity failure
mode. The architecture and requirements artifacts now record this extension.

### Test Traceability

Clean. `test-plan.md` now maps capacity fallback behavior to US-9, AC-12,
S-15, and I11.

### Residual Open Issues

None in source. Installed plugin cache may still run older instructions until
refreshed.

### Verification

- `python3 -m py_compile tests/idea-to-ship-eval-fixtures.py`: pass.
- `bash tests/idea-to-ship-eval-fixtures.sh`: pass.
- `bash tests/release-gate-stage1.sh`: pass.
- `scripts/release-gate.sh --mode staged`: pass.
- `scripts/release-gate.sh --mode working`: pass.
- `scripts/release-gate.sh --mode all`: pass.
- `scripts/release-gate.sh --mode all --json`: pass.
- `git diff --check`: pass.

### Final Verdict

LGTM

## Stage 4 Addendum

**Date:** 2026-05-12
**Reviewer:** main-context adversarial review fallback + self-review
**Iterations:** 1
**Result:** clean

### Issues Raised & Resolution

| # | Severity | File:line | Issue | Resolution |
|---|---|---|---|---|
| 1 | warning | `idea-to-ship/PRINCIPLES.md`; review/design/architect/roadmap/brainstorm skills | The prior "sub-agent by default" wording conflicted with runtimes that require explicit user authorization before delegation. | Replaced default delegation with a host/user authorization gate and explicit main-context fallback recording. |
| 2 | warning | `tests/idea-to-ship-eval-fixtures.py` | The runtime-aware routing contract checked fallback wording but did not require authorization gating. | Added a delegation authorization invariant to `review-code-runtime-aware-routing-contract`. |

### Out-of-Scope Issues Skipped

None.

### Design Drift

None. This extends FR-8's runtime-aware routing fixture coverage without
changing the offline fixture command or release-gate advisory shape.

### Test Traceability

Clean. `test-plan.md` now maps delegation authorization behavior to US-7,
AC-9, S-11, and I8.

### Residual Open Issues

None.

### Verification

- `bash tests/idea-to-ship-eval-fixtures.sh`: pass.
- `scripts/release-gate.sh --mode all`: pass.
- `git diff --check`: pass.

### Final Verdict

LGTM

## Stage 3 Addendum

**Date:** 2026-05-12
**Reviewer:** main-context adversarial review fallback + self-review
**Iterations:** 1
**Result:** clean
**Fallback reason:** current runtime policy requires explicit user authorization
for sub-agent delegation; this run used the same review prompt in the main
context.

### Issues Raised & Resolution

| # | Severity | File:line | Issue | Resolution |
|---|---|---|---|---|
| 1 | warning | `scripts/release-gate.sh` | The idea-to-ship fixtures were still manual-only, so full release hardening could miss regressions unless the operator remembered a second command. | Added `idea-to-ship-fixtures` as a non-blocking `--mode all` advisory check. |
| 2 | warning | `tests/release-gate-stage1.sh` | The release-gate fixture suite did not prove advisory checks preserve blocking exit semantics. | Added coverage for staged-mode skip output and all-mode missing-fixture advisory warning with exit `0`. |
| 3 | warning | `RELEASE-GATE.md` | The docs still said advisory checks were not implemented and the fixture command was manual-only. | Documented advisory checks, JSON coverage, staged/working skip behavior, and `--mode all` integration. |

### Out-of-Scope Issues Skipped

None.

### Design Drift

None. Stage 3 chose advisory release-gate integration rather than blocking,
matching the false-confidence guardrail in the architecture.

### Test Traceability

Clean. `test-plan.md` now maps the release-gate advisory behavior to US-6,
AC-7/AC-8, S-9/S-10, and integration cases I6/I7.

### Residual Open Issues

None.

### Verification

- `bash -n scripts/release-gate.sh`: pass.
- `bash -n tests/release-gate-stage1.sh`: pass.
- `bash tests/release-gate-stage1.sh`: pass.
- `bash tests/idea-to-ship-eval-fixtures.sh`: pass.
- `scripts/release-gate.sh --mode staged`: pass, fixture advisory skipped.
- `scripts/release-gate.sh --mode working`: pass, fixture advisory skipped.
- `scripts/release-gate.sh --mode all`: pass, fixture advisory passed.
- `scripts/release-gate.sh --mode all --json`: pass, advisory check included.
- `git diff --check`: pass.

### Final Verdict

LGTM

## Stage 5 Addendum

**Date:** 2026-05-12
**Reviewer:** main-context adversarial review fallback + self-review
**Iterations:** 1
**Result:** clean
**Fallback reason:** current runtime policy requires explicit user authorization
for sub-agent delegation; this run used the same review prompt in the main
context.

### Issues Raised & Resolution

| # | Severity | File:line | Issue | Resolution |
|---|---|---|---|---|
| 1 | warning | `idea-to-ship/skills/brainstorm/SKILL.md`; `idea-to-ship/skills/architect/SKILL.md` | Rerunning early-stage skills could overwrite human-edited `requirements.md` or `architecture.md` because existing artifact handling only said continue or start over. | Added ownership sections requiring stable ID/section preservation, human edit preservation, draft fallback, and explicit approval before replacement. |
| 2 | warning | `tests/idea-to-ship-eval-fixtures.py` | Fixture coverage did not check the new early-stage ownership contracts or artifact draft fallback. | Added brainstorm/architect rerun contract checks plus structured-artifact and malformed-artifact draft fallback checks. |

### Out-of-Scope Issues Skipped

None.

### Design Drift

Stage 5 extends the original fixture scope beyond roadmap/test/review-code into
brainstorm/architect ownership safety. This is recorded in the requirements,
architecture, implementation log, and test plan.

### Test Traceability

Clean. `test-plan.md` now maps ownership safety to US-8, AC-10/AC-11,
S-12/S-14, U3/U4, and I9/I10.

### Residual Open Issues

None.

### Verification

- `python3 -m py_compile tests/idea-to-ship-eval-fixtures.py`: pass.
- `bash tests/idea-to-ship-eval-fixtures.sh`: pass.
- `bash tests/release-gate-stage1.sh`: pass.
- `scripts/release-gate.sh --mode staged`: pass.
- `scripts/release-gate.sh --mode working`: pass.
- `scripts/release-gate.sh --mode all`: pass.
- `scripts/release-gate.sh --mode all --json`: pass.
- `git diff --check`: pass.

### Final Verdict

LGTM
