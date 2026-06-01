# Architecture - Shared Audit Checklist Closure

**Slug:** ITS-ROADMAP-011
**Date:** 2026-06-01
**Status:** accepted
**References:** requirements.md

## Summary

Close `ITS-ROADMAP-011` as a focused contract/docs refactor. The existing
`agent-playbook/WORKFLOW-CONTRACTS.md` remains the single owner for shared
audit safety and evaluation fields. Each audit skill cites that section, while
its domain-specific checklist stays local.

## Goals / Non-Goals

Goals:

- Make the shared checklist ownership explicit and fixture-protected.
- Require section-level citations from the audit skills that consume the
  checklist.
- Preserve local checklist headings for tool design, context hygiene,
  vibe-health routing/stop rules, and antifragile infrastructure dimensions.
- Produce the missing slug-local closure artifacts.

Non-goals:

- No new repo-wide contracts file.
- No extraction of domain-specific checklist content.
- No public skill metadata or output contract changes.
- No runtime behavior change.

## Codebase Context

- `agent-playbook/WORKFLOW-CONTRACTS.md` already had a `Shared Safety And
  Evaluation Checklist` section with the common fields.
- `tool-review`, `context-audit`, and `vibe-coding-health-check` already cited
  the workflow contract file, but not the exact shared checklist section.
- `antifragile-agent` already cited its local `antifragile/WORKFLOW-CONTRACTS.md`
  and mentioned agent-playbook audit safety concepts, but did not cite the
  agent-playbook file/section explicitly.
- `tests/agent-playbook-eval-fixtures.py` already uses contract fixture
  invariants and is the right place to protect this documentation contract.

## Cross-Skill Routing

| Signal | Routed skill | Result | Design impact |
|---|---|---|---|
| Documentation/contract refactor for idea-to-ship roadmap item | none | no additional workflow needed | Use local fixtures, release gate, and review-code. |
| Shared audit safety fields overlap antifragile-agent | antifragile remains owner of its audit dimensions | no migration | Cite agent-playbook checklist only for common fields. |

## Alternatives Considered

### Option A - Existing Agent-Playbook Contract Owner

Keep `agent-playbook/WORKFLOW-CONTRACTS.md` as the checklist owner and update
skill citations plus fixtures.

Pros: smallest diff, matches current repo structure, avoids a new global file.

Cons: antifragile-agent has a cross-plugin citation for the shared checklist.

### Option B - New Repo-Wide Shared Checklist

Create a top-level contracts file and point all plugins at it.

Pros: neutral ownership.

Cons: creates a new maintenance surface for one checklist and requires more
cross-plugin churn than the roadmap item needs.

### Option C - Inline Checklist In Every Skill

Leave each skill to state its safety rules directly.

Pros: locally obvious to readers.

Cons: repeats boilerplate and was the maintenance problem this item targets.

## Recommendation

Choose Option A. It closes the roadmap item with the smallest stable contract:
one shared checklist, explicit citations, and fixtures that verify both shared
ownership and local domain criteria.

## Chosen Design

- Add fixture invariants for the shared checklist section and required fields.
- Add fixture invariants that each consuming skill cites the shared checklist
  section by name.
- Add fixture invariants that domain-specific headings remain in each owning
  skill.
- Add a short owner note to `agent-playbook/WORKFLOW-CONTRACTS.md` clarifying
  that the shared checklist owns only common audit/safety fields.
- Update skill prose to cite the shared checklist section explicitly.

## Staged Implementation Plan

1. **Stage 1 - Close shared audit checklist contract**: Add red-first fixture
   checks, update citations and owner note, write closure artifacts, run focused
   and release verification, review the diff, then mark the roadmap item
   complete.

## Open Questions

- None.
