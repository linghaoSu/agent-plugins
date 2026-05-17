# Orchestration Spike - ITS-ROADMAP-020

**Date:** 2026-05-17
**Decision:** adapt narrow intake patterns; reject a broad repo orchestrator
**Boundary:** artifact-only / read-only spike

## Decision

Reject a new broad repo orchestrator for this batch. The useful parts of the
referenced orchestration/bootstrap pattern are intake discipline, explicit
handoffs, matrix thinking, and recovery notes. Those are adapted into existing
bounded skills and artifacts instead of adding a new autopilot route.

## Existing Skill Overlap

| Capability | Existing Owner | Decision |
|---|---|---|
| Repo agent-memory bootstrap | `$agent-playbook:bootstrap-project-memory` | Keep existing owner. |
| Context and workflow hygiene audit | `$agent-playbook:context-audit` | Keep existing owner. |
| Diff health check after AI-assisted work | `$agent-playbook:vibe-coding-health-check` | Keep existing owner. |
| Explicit best-of-N implementation tournament | `$agent-playbook:implementation-tournament` | Use only when explicitly requested. |
| Product idea to implementation flow | `$idea-to-ship:*` stages | Keep product implementation inside idea-to-ship. |

## Adopt / Reject / Adapt Verdict

| Choice | Verdict | Rationale |
|---|---|---|
| Adopt wholesale repo orchestrator | Reject | It overlaps existing skills and would blur ownership. |
| Reject all orchestration ideas | Reject | Intake checklists, handoff artifacts, and recovery notes are useful. |
| Adapt narrow artifact-only bootstrap guidance | Adopt | Fits existing agent-playbook boundaries without new mutation authority. |

## Allowed Actions

- Write or update local planning artifacts under `.idea-to-ship/` or
  `.agent-playbook/`.
- Route users to existing bounded skills by name.
- Produce a read-only checklist for repository intake, context inventory, and
  handoff risks.
- Recommend explicit next skills; do not execute mutating routes without user
  authorization.

## Forbidden Actions

- no git commit
- no git push
- no GitHub mutation
- no plugin install
- no plugin/cache installation
- no skill-tree copy
- no skill tree copy
- no deployment mutation
- no self-replication
- no automatic PR comments, merges, releases, CI edits, credential retrieval,
  or target repo mutation.

## Future Decision Gate

A future repo-bootstrap skill can be reconsidered only if it has:

1. A non-overlapping owner boundary distinct from `idea-to-ship` and existing
   `agent-playbook` skills.
2. A read-only default mode.
3. Explicit user authorization for every git, GitHub, plugin/cache, CI, or
   deployment mutation.
4. Fixture coverage proving broad orchestrator routes cannot silently commit,
   push, mutate GitHub, install plugins, copy skill trees, deploy, or replicate
   themselves.
5. A concrete artifact contract with success, `needs_user`, terminal, and
   degraded outcomes.

## Evidence

The accepted path for this roadmap batch is:

- Add `$idea-to-ship:visual-test` for visual QA evidence.
- Add fixture coverage for broad-orchestrator drift.
- Keep repo-bootstrap/orchestration as a bounded, artifact-only spike until a
  future design proves a smaller non-overlapping skill is necessary.
