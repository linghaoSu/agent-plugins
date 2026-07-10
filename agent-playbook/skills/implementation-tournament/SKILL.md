---
name: implementation-tournament
description: Compare explicitly requested competing implementations in isolated worktrees with shared verification and independent review, then adopt, merge, or reject them.
---

# Implementation Tournament

Run only when the user explicitly requests competing implementations or best
of N. Write `.agent-playbook/<slug>/implementation-tournament.md`.

## Workflow

1. Define one brief: invariant goal, allowed files, non-goals, objective tests,
   candidate count, cost/time cap, and adoption policy.
2. Snapshot the base commit and dirty state. Create isolated worktrees/branches;
   never let candidates share uncommitted files or conclusions.
3. Give each executor the same bounded task packet. Each returns changed files,
   assumptions, checks, and known limits. Do not commit or push.
4. Run identical objective verification for every candidate. Reject failures
   before subjective review.
5. Give surviving patches to independent reviewers using the capability
   contract. Score correctness, simplicity, scope, maintainability, and test
   evidence; reviewers do not see peer verdicts.
6. The arbiter chooses `adopt`, `merge`, or `reject-all` from evidence. Merge
   only complementary, non-conflicting changes and re-run the full checks.
7. Apply the selected patch to the original worktree only after confirming the
   base fingerprint is unchanged. Preserve unrelated user changes.
8. Record candidates, verification matrix, findings, decision, applied patch,
   cleanup, and residual risk.

Stop on base drift, unavailable isolation, unverifiable success, or candidate
side effects outside scope. Clean tournament worktrees only when safe and
authorized.
