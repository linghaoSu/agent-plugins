# Code Review - ITS-ROADMAP-009

**Date:** 2026-05-15
**Reviewer:** multi-agent: correctness/security -> runtime-native reviewer; traceability/testability -> runtime-native reviewer; maintainability/repo-fit -> runtime-native reviewer; UI/UX -> not applicable
**Iterations:** 4
**Result:** clean
**Mode:** multi-agent
**Degradation reason:** none
**Diff size:** 11 implementation files, +933/-124 before this review artifact

## Issues Raised & Resolution

| # | Severity | File:line | Issue | Resolution |
|---|---|---|---|---|
| 1 | critical | `tests/agent-playbook-eval-fixtures.py:171` | New fixture checks grouped multiple mandatory tokens in one `InvariantGroup`, but groups are OR matches. This let fixtures pass after losing required angles, inputs, verdicts, or report fields. | Split mandatory tokens into separate groups across the evaluate-issue skill, Round 2 prompt, Round 3 prompt, and final template contracts. |
| 2 | warning | `tests/agent-playbook-eval-fixtures.py:578` | Forbidden inline-prompt coverage protected Round 2 and Round 3 only, so the final report wrapper could be reintroduced inline while fixtures stayed green. | Added `evaluate-issue-forbidden-inline-final-report-template`. |
| 3 | warning | `issue-evaluator/skills/evaluate-issue/SKILL.md:42` | `Prompt & Template Artifacts` was inserted as a top-level heading under `Workflow`, which would make later workflow steps nest under the wrong section. | Changed it to a workflow subsection. |
| 4 | warning | `.idea-to-ship/ITS-ROADMAP-009/implementation-log.md:52` | The implementation log claimed staged scope was clean while review fixes were still unstaged. | Staged the review fixes, verified no implementation path had unstaged remainder, and reran strict gates. |
| 5 | warning | `tests/agent-playbook-eval-fixtures.py:197` | The no-GitHub-mutation invariant matched only `post anything to GitHub`, allowing an opposite sentence to satisfy the check. | Tightened the invariant to the full no-mutation sentence. |
| 6 | warning | `tests/agent-playbook-eval-fixtures.py:178` | Artifact reference checks could pass from the inventory alone even if Round 2, Round 3, or Step 4 workflow wiring was removed. Round 3 input placeholders were also under-protected. | Added workflow-section-scoped artifact checks plus Round 2 assigned-angle and Round 3 input placeholder checks. |

## Out-of-Scope Issues Skipped

None.

## Design Drift

None. The implementation still follows Option A from `architecture.md`: three extracted artifacts, slim skill references, and deterministic offline fixture coverage through `tests/agent-playbook-eval-fixtures.py`.

## Test Traceability

Clean. The TDD slice covers missing extracted artifacts and missing skill references, then fixtures were expanded during review to protect mandatory prompt fields, workflow-site references, read-only constraints, and forbidden inline regressions.

Verification run after fixes:

- `python3 -m py_compile tests/agent-playbook-eval-fixtures.py`
- `bash tests/agent-playbook-eval-fixtures.sh`
- `git diff --cached --check`
- `scripts/release-gate.sh --mode staged --strict`
- `scripts/release-gate.sh --mode all --strict`

## Residual Open Issues

None.

## Final Verdict

| Angle | Verdict |
|---|---|
| correctness/security | LGTM |
| traceability/testability | LGTM |
| maintainability/repo-fit | LGTM |
| UI/UX | not applicable |
