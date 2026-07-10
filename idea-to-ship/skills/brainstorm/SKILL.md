---
name: brainstorm
description: Turn a vague product idea into testable requirements through efficient batch questioning. Use as the first idea-to-ship stage; writes the slug requirements artifact.
---

# Brainstorm

Produce requirements another engineer can act on without guessing. This is
batch discovery; use `grill` when decisions require one-at-a-time pressure.

## Workflow

1. Resolve `--slug` and read existing requirements, repo instructions, relevant
   code, domain docs, and `../../WORKFLOW-CONTRACTS.md`. Preserve stable IDs and
   human edits; write a draft if merge safety is unclear.
2. Explore facts before asking. Challenge an already-solved, unsupported, or
   premature premise.
3. Ask only load-bearing unknowns in batches of 3–5: problem/why-now, users,
   scope/non-goals, constraints/integrations, success evidence, and acceptable
   failure. Offer concrete options for “I don’t know.”
4. Continue until problem, users, scope, and success are concrete. If answers
   form dependent design branches, route to `grill` instead of expanding the
   batch interview.
5. Write `.idea-to-ship/<slug>/requirements.md` with problem, actors, in/out of
   scope, stable functional requirement IDs, measurable non-functional
   requirements, verifiable success criteria, open questions, and touch points.

Requirements describe observable behavior, not implementation. Do not inflate
scope, accept handwaves, or invent product decisions. Mark unresolved choices
as open questions and do not call the artifact build-ready.

## Completion

Confirm every success criterion names a check or observable signal, preserve
human content, summarize key decisions, and recommend `architect` only when the
reality gate passes.

Use `$idea-to-ship:grill` for dependent decisions and `$idea-to-ship:architect` next.
