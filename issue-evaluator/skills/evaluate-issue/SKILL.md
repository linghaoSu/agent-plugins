---
name: evaluate-issue
description: Diagnose a GitHub issue or concrete bug description against the current repo. Confirms status and root cause, builds a red-capable feedback loop, and returns a fix-ready plan without editing code.
---

# Evaluate Issue

Read `../../PRINCIPLES.md` and `../../WORKFLOW-CONTRACTS.md`. Accept an issue
URL/number or free-form description. Write no production changes.

## Workflow

1. Fetch issue metadata/comments with `gh`, or synthesize a pseudo-issue from a
   description. Require observed wrong behavior plus trigger, error signal, or
   affected area; otherwise return `needs_user`.
2. Load repo instructions and the code-style cache. If the cache is missing or
   stale, run its internal lifecycle from the shared contract; there is no
   separate user-facing update skill.
3. Build a tight feedback loop before committing to a theory. Name one command
   already run that can fail on the exact symptom, is deterministic (or has a
   measured high reproduction rate), fast enough to iterate, and unattended.
   Try focused test, request/CLI script, browser flow, trace replay, minimal
   harness, fuzz/property loop, bisection, or differential comparison.
4. If no red-capable loop is possible, list attempts and required evidence or
   access. Do not produce a certain root cause or fix-ready verdict.
5. Reproduce and minimize until every remaining input/step is load-bearing.
   Generate 3–5 ranked, falsifiable hypotheses; each must predict an observable
   result. Probe one variable at a time with tagged temporary instrumentation.
6. Use independent `reasoning` roles for code-path analysis, history/already-
   fixed check, and adversarial validation when risk warrants it. Use
   `critical` arbitration only for conflicting or high-impact conclusions.
7. Synthesize confirmed status, causal chain, affected files, minimal repair,
   regression seam, checks, risks, and contribution etiquette using
   `../../templates/evaluate-issue-final-report.md`.

## Completion

Return confirmed, already-fixed, unconfirmed, or needs-evidence. A fix-ready
plan requires a reproduced causal chain and runnable acceptance. Remove or
explicitly hand off all temporary instrumentation.

Use `$issue-evaluator:fix-issue` only after a fix-ready verdict.
