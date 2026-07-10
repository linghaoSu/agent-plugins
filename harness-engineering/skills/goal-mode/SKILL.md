---
name: goal-mode
description: Run long-horizon work as a persistent verified loop with objective, state, one next action, checkpoints, and compact handoff. Writes the slug-specific goal directory.
---

# Goal Mode

Use for work too large to trust to chat history. This skill executes the goal;
`harness --mode resilience` designs reset/consolidation around longer systems.

## Arguments

- `--slug <name>`; default `current`.
- `--resume`, `--status`, or `--complete`.
- Remaining text: objective/update.

## Workflow

1. Use `scripts/goal_state.py` to initialize, validate, status, record, and
   complete `.harness-engineering/<slug>/goal/`. Keep `objective.md`,
   `state.json`, append-only `iteration-log.md`, and generated `handoff.md`.
2. Define one objective, objective success criteria, non-goals, constraints,
   and approvals. Make conservative assumptions only when they do not change
   product intent; record them.
3. Before each cycle, read objective, state, and only the recent log tail.
   Choose exactly one material, locally recoverable step and announce it.
4. Execute and verify using machine checks first, structural checks second,
   independent subjective review only where necessary, and user confirmation
   for user-owned decisions.
5. Immediately record step, observed result, verification, blockers/risks, and
   exactly one next action. The script regenerates the compact handoff.
6. Continue while the next step is clear and authorized. Stop for destructive
   or external actions, credentials, production changes, or product decisions.
7. Complete only when every success criterion has cited evidence.

## Handoff

Reference existing requirements, plans, ADRs, commits, diffs, and reports; do
not duplicate them. Redact secrets and personal data. Include status, latest
verification, blockers, next action, and suggested next skill. Keep handoff
small enough for a fresh context and never reload the full historical log.

Use `$harness-engineering:harness --mode resilience` for reset/consolidation design.
