---
name: implement
description: Implement one approved architecture stage as scoped local edits. Requires a test gate for behavior changes, verifies the vertical slice, and updates implementation-log.md; never commits or pushes.
---

# Implement

Implement one architecture stage at a time. Read `../../PRINCIPLES.md` and
`../../WORKFLOW-CONTRACTS.md` before editing.

## Workflow

1. Resolve `--slug` and optional stage. Require approved requirements and
   architecture; require interface design before UI changes. Read current diff,
   implementation log, tests, and repo rules. Stop on unrelated dirty overlap.
2. Select the next incomplete vertical stage. State assumptions, intended
   files, non-goals, observable done condition, and verification command.
3. For behavior changes, invoke `test --mode gate` and require red evidence at
   a public seam before production edits. Documentation/config-only stages may
   record why no red gate applies.
4. If `--compete` was explicitly requested, use
   `agent-playbook:implementation-tournament`; otherwise do not create
   competing implementations.
5. Apply the smallest change satisfying the stage. A `routine` executor is
   allowed only with bounded files and runnable acceptance. Match local style;
   do not refactor adjacent code or add speculative flexibility.
6. Run focused tests first, then required type/lint/build and broader checks
   proportional to risk. Verify original behavior and failure paths.
7. Append stage, changed files, decisions, checks, results, residual risks, and
   next stage to `.idea-to-ship/<slug>/implementation-log.md` using the existing
   template and ownership rules.

Stop on architecture drift, missing test seam, ambiguous product behavior,
failed required checks, or destructive/external action lacking authority.

## Completion

The stage is complete only when its acceptance evidence passes and the log is
current. Recommend `review --target code`; never commit or push.
