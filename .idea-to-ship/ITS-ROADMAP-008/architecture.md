# Architecture - Implement Contract Closure

**Slug:** ITS-ROADMAP-008
**Date:** 2026-06-01
**Status:** accepted
**References:** requirements.md

## Summary

Close `ITS-ROADMAP-008` with a small contract refactor. Keep
`idea-to-ship:implement` as the workflow map, keep shared routing in
`WORKFLOW-CONTRACTS.md`, and make `templates/implementation-log.md` the source
for implementation-log field shape. Add fixture coverage and roadmap closure
evidence.

## Goals / Non-Goals

Goals:

- Preserve all public `implement` gates and behavior.
- Make the implementation-log template explicit enough that the skill does not
  need to repeat log-field mechanics.
- Add deterministic fixture checks for the shared-reference and template-field
  contract.
- Produce the missing `ITS-ROADMAP-008` artifact chain.

Non-goals:

- No new executable template renderer.
- No routing table move; the implementation-stage route table already lives in
  `WORKFLOW-CONTRACTS.md`.
- No broad skill rewrite or line-count-driven deletion.
- No changes to public skill metadata.

## Codebase Context

- `idea-to-ship/skills/implement/SKILL.md` already references
  `../../WORKFLOW-CONTRACTS.md` and `../../templates/implementation-log.md`.
- `idea-to-ship/templates/implementation-log.md` had stage status, decisions,
  deviations, verification, and cross-skill checks, but did not explicitly carry
  pre-stage assumptions or success criteria.
- `tests/idea-to-ship-eval-fixtures.py` already has contract checks for
  `implement` template references and the implementation-log template.
- `scripts/skill-hygiene-check.py` already warns about long routing sections
  without `WORKFLOW-CONTRACTS.md` and repeated inline output contracts.

## Cross-Skill Routing

| Signal | Routed skill | Result | Design impact |
|---|---|---|---|
| Documentation/contract refactor for idea-to-ship skill infrastructure | none | no separate architecture-stage route needed | Use local fixtures and release-gate checks. |

## Alternatives Considered

### Option A - Focused Closure Pass

Add the missing artifacts, tighten the existing `implement` references, extend
the existing log template, and strengthen existing fixtures.

Pros: smallest diff, preserves current behavior, matches roadmap evidence
required.

Cons: does not aggressively shorten every possible line in `implement`.

### Option B - Close From Earlier Commits Only

Record that previous work already satisfied the item and mark the roadmap done.

Pros: no code changes.

Cons: leaves no slug-local evidence and misses the template gaps found during
exploration.

### Option C - Extract More Implement Text Into New Templates

Create additional templates for assumptions, verification, and handoff.

Pros: more line-count reduction.

Cons: over-extracts behavior-specific guidance and makes `implement` harder to
follow.

## Recommendation

Choose Option A. It is the minimum change that creates closure evidence and
protects the shared-template contract without weakening the implementation
workflow.

## Chosen Design

- `implement/SKILL.md`: keep the staged workflow inline, but explicitly state
  that the implementation-log template owns stage status, assumptions,
  decisions, deviations, verification, TDD evidence, and cross-skill check
  fields.
- `templates/implementation-log.md`: add `### Pre-Stage Assumptions` and
  `### Success Criteria`; convert cross-skill checks to a table with `Trigger`,
  `Result`, and `Impact`.
- `tests/idea-to-ship-eval-fixtures.py`: add invariant groups that fail if the
  skill/template loses those fields.
- `.idea-to-ship/roadmap.md`: mark the item complete only after verification.

## Staged Implementation Plan

1. **Stage 1 - Close implement shared-contract cleanup**: Add red fixture
   expectations, update the skill/template contract, create closure artifacts,
   run focused checks, and update the roadmap status.

## Open Questions

- None.
