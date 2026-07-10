---
name: review-fix
description: Risk-scaled review of current local changes against issue intent, repo style, correctness, security, and tests. May apply only approved severe fixes, then re-review.
---

# Review Fix

Review the complete current diff. Read `../../PRINCIPLES.md` and shared
contracts for intensity, capability routing, modification approval, and output.

## Workflow

1. Resolve `--review-depth quick|standard|deep` and focus. Require a non-empty
   diff; include staged, unstaged, and untracked files. Fingerprint it and load
   issue/plan, repo rules, code-style cache, and relevant tests.
2. Review independent axes: correctness/security/regressions, style/scope, and
   issue/test traceability. Keep Standards and Spec findings separate. Each
   finding needs severity, file/line, evidence, consequence, and minimal repair.
3. Quick uses a same-context checklist. Standard/deep use independent reviewer
   roles where supported; record `degraded` otherwise. `critical` arbitration
   is reserved for conflicts or high-impact uncertainty.
4. Deduplicate by root cause. If critical/high edits are needed, generate the
   documented modification plan and obtain approval. Apply only approved
   severe repairs, run objective checks, and re-run affected axes. Allow one
   repair round.
5. Stop on diff drift, missing intent, failed required checks, or unresolved
   severe findings. Do not commit, push, post review comments, or clean the
   worktree.

## Output

Report intensity/mode, fingerprint, findings/resolution, checks, deferred and
out-of-scope issues, degradation, and verdict. Clean requires every required
axis to return `LGTM` on the current diff.

Use `$agent-playbook:commit-changes` only after the review is clean.
