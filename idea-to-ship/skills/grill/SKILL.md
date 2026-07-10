---
name: grill
description: Stress-test an existing requirement, plan, or design one decision at a time. Use for “grill me”, unresolved design branches, premise challenges, or optional glossary and ADR updates.
---

# Grill

Resolve a decision tree with the user. This is deeper than batch requirement
discovery: one load-bearing decision per turn, no implementation.

## Arguments

- `--slug <name>`: read `.idea-to-ship/<slug>/` artifacts.
- `--with-docs`: allow glossary and qualifying ADR updates only.
- Remaining text or path: the plan, requirement, or design to challenge.

## Workflow

1. Read the supplied artifact, relevant repo instructions, code, and existing
   domain docs. Discover facts locally; never ask the user for a fact the repo
   can answer.
2. Build a private decision tree covering goal, success, scope, constraints,
   interfaces, failure modes, verification, and unresolved dependencies.
3. Ask exactly one unresolved, highest-dependency decision. Offer 2–4 real
   options, put the recommendation first, and explain its tradeoff.
4. After the answer, update a conversation-local decision ledger. Challenge
   contradictions, vague terms, wrong premises, hidden coupling, weak
   acceptance, irreversible choices, and scope drift.
5. Repeat until every branch is resolved. Summarize the ledger and ask the user
   to confirm shared understanding. Stop; do not invoke another workflow.

Do not answer for the user, batch questions, implement, or write production
code. With `--slug`, artifacts are read-only unless the user separately asks to
synchronize the accepted decisions.

## Domain docs

Without `--with-docs`, do not edit domain docs. With it:

- Preserve human content and update the relevant `CONTEXT.md` when a canonical
  domain term is resolved. Keep implementation details out of the glossary.
- Write an ADR only when the decision is hard to reverse, surprising without
  context, and the result of a real tradeoff. Record alternatives and reasons.
- The flag authorizes only glossary and ADR writes—not code, config, Git, or
  external-system mutation.

## Completion

Finish only after all decision branches are resolved, the ledger names
assumptions and out-of-scope work, and the user confirms the shared model.

Return accepted requirements to `$idea-to-ship:architect` or a design to `$idea-to-ship:review`.
