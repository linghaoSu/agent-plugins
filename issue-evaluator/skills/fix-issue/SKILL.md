---
name: fix-issue
description: Implement a confirmed GitHub issue or concrete bug fix in an isolated worktree with a red-capable regression gate, scoped edits, verification, and a local commit.
---

# Fix Issue

Fix one confirmed problem. Read `../../PRINCIPLES.md` and
`../../WORKFLOW-CONTRACTS.md`; preserve unrelated changes and contribution
etiquette.

## Workflow

1. Resolve issue URL/number or concrete description. Reuse a fresh evaluation
   from conversation/artifact; otherwise run the `evaluate-issue` workflow.
   Stop when unconfirmed, already fixed, duplicated, actively claimed, or too
   vague for a fix-ready plan.
2. Inspect status and create an isolated worktree from the correct base. If
   isolation fails or the branch/worktree already contains ambiguous changes,
   stop rather than editing the caller’s tree.
3. Load repo instructions and internal code-style lifecycle. State assumptions,
   exact allowed files, non-goals, causal root, and runnable done condition.
4. Require a tight red-capable reproduction for the exact symptom. Minimize it,
   then turn it into a regression test at the real public seam. If no correct
   seam exists, document the architectural gap and do not substitute a shallow
   test that cannot catch the bug.
5. If competing implementations were explicitly requested, route to
   `agent-playbook:implementation-tournament`; otherwise apply the smallest
   direct fix. A `routine` executor may implement only the bounded approved
   plan and cannot accept its own result.
6. Run the regression red, implement, run it green, then re-run the original
   unminimized reproduction. Run relevant type/lint/build and broader checks
   proportional to risk. Remove tagged instrumentation and throwaway harnesses.
7. Inspect the full diff for scope and secrets. Commit only fix/test files with
   a concise message stating the verified cause. Do not push or create a PR.

## Stop conditions

Stop on base drift, wrong-branch risk, missing reproduction, uncertain product
behavior, destructive/external action, failed required checks, or edits outside
the approved scope.

## Output

Report worktree/branch, commit SHA, causal chain, files changed, red/green and
original-repro evidence, other checks, skipped checks, residual risk, and the
next review command.

Use `$issue-evaluator:review-fix` for independent post-fix review.
