---
name: architect
description: Design implementation architecture from approved requirements, with alternatives, tradeoffs, staged delivery, and test seams. Writes the slug architecture artifact without production code.
---

# Architect

Design for the existing codebase, not an imagined one.

## Workflow

1. Resolve `--slug`; require build-ready `requirements.md`. Read existing
   architecture/interface artifacts, repo rules, domain vocabulary, ADRs, and
   `../../WORKFLOW-CONTRACTS.md`. Preserve human edits and stable stage names.
2. Explore relevant modules, callers, data flow, conventions, tests, reusable
   utilities, integration boundaries, and migration constraints. Use a
   `reasoning` explorer only when authorized; otherwise run the pass locally.
3. Route specialized concerns only when present: system resilience, agent
   harnessing, UI contract, secrets, or commercialization. Do not run unrelated
   audits by habit.
4. Produce 2–3 materially different alternatives including the simplest viable
   option. Compare requirement coverage, complexity, operability, migration,
   failure behavior, testability, and reversibility.
5. Recommend one option and explain the accepted tradeoff. Detail modules,
   interfaces, data/schema changes, flow, failures, rollout/rollback, public
   seams, and vertical implementation stages.
6. Write `.idea-to-ship/<slug>/architecture.md`; keep requirement traceability
   and open user-owned decisions explicit. Obtain approval before replacing a
   canonical architecture.

No production implementation belongs here. If requirements are wrong or soft,
return to `brainstorm` or `grill` rather than forcing architecture around them.

## Completion

Every stage must deliver observable behavior, name its verification, and be
independently implementable. Recommend `review --target design` after approval.

Use `$idea-to-ship:review --target design` for independent design validation.
