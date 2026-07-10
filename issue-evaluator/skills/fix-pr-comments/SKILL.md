---
name: fix-pr-comments
description: Triage GitHub PR review comments, apply only user-approved actionable fixes as local uncommitted edits, verify them, and run risk-scaled independent review. Never writes to GitHub.
---

# Fix PR Comments

GitHub is read-only. Local edits require explicit approval after triage; no
commit, push, review submission, comment, resolve, label, merge, or PR mutation.

## Workflow

1. Resolve PR and optional `--review-depth`. Fetch metadata, files, reviews,
   inline threads, issue/spec, and current head with `gh`. Normalize comments
   by stable thread/comment ID; include unresolved requested changes and user-
   selected items, excluding bot noise and already-obsolete duplicates.
2. Prepare a clean worktree at the PR head and fingerprint it. Stop if the
   branch moved, worktree is dirty, or checkout safety is unclear.
3. Load repo instructions and internal code-style cache. For each comment, run
   an independent `reasoning` analyst when supported and classify:
   `ACCEPT`, `REJECT_WITH_EVIDENCE`, `ALREADY_ADDRESSED`, `STALE`,
   `NEEDS_USER`, or `OUT_OF_SCOPE`.
4. Require file/line evidence, feared failure mode, issue/spec authority, and a
   minimal fix for every acceptance or rejection. Reconcile conflicting
   comments before presenting the triage table.
5. Show selected fixes, exact files, non-goals, tests, and rejected items. Wait
   for explicit approval; review comments alone do not authorize edits.
6. Give a `routine` executor the approved bounded task packet. Apply only those
   edits, preserve unrelated changes, and leave them uncommitted. The executor
   cannot accept its own output.
7. Run focused checks, then risk-scaled independent review across correctness,
   scope/style, and comment/test traceability. Use `critical` arbitration only
   for material conflict. Permit one approved repair round.
8. Report with `../../templates/fix-pr-comments-final-report.md`. Include each
   source ID, classification, action, files, checks, residual risk, and draft
   human responses for rejected comments. Do not post them.

## Stop conditions

Stop on head/fingerprint drift, ambiguous comment ownership, missing approval,
external/destructive action, failed required checks, or edits outside the
approved packet. Leave a non-clean temporary worktree intact and report it.

Use `$issue-evaluator:review-pr` for a fresh read-only review of the resulting head.
