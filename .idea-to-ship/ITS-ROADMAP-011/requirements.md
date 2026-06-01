# Requirements - ITS-ROADMAP-011

**Slug:** ITS-ROADMAP-011
**Date:** 2026-06-01
**Status:** accepted for closure
**Source:** `.idea-to-ship/roadmap.md` and completion plan

## Problem

The roadmap identified repeated audit and safety checklist language across
`agent-playbook` audit skills and `antifragile-agent`. The repo already has
`agent-playbook/WORKFLOW-CONTRACTS.md` with a shared checklist, but the owning
skills did not all cite that section explicitly and fixture coverage did not
protect the contract from drifting back into duplicated boilerplate.

## Users / Actors

- Skill maintainer: updates common audit safety rules in one file.
- Audit skill user: still sees the domain-specific checklist in the skill they
  are invoking.
- Reviewer: can verify shared checklist ownership and local domain checklist
  preservation through deterministic fixtures.

## In Scope

- Keep `agent-playbook/WORKFLOW-CONTRACTS.md` as the shared checklist owner.
- Make `tool-review`, `context-audit`, `vibe-coding-health-check`, and
  `antifragile-agent` cite the shared checklist section explicitly.
- Preserve domain-specific checklist headings in the owning skills.
- Add deterministic fixture coverage for the shared checklist fields,
  section-level citations, and local checklist headings.
- Add this closure artifact set under `.idea-to-ship/ITS-ROADMAP-011/`.
- Update `.idea-to-ship/roadmap.md` only after review and verification.

## Out of Scope / Non-Goals

- No new public skill, command, argument, or artifact path.
- No generic audit checklist that replaces tool-review, context-audit,
  vibe-health, or antifragile domain judgment.
- No movement of antifragile hook/state/recovery audit dimensions into
  `agent-playbook`.
- No behavior-changing code path or runtime dependency.
- No commit, push, package install, or generated `.agent-playbook/` report.

## Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| FR-1 | `agent-playbook/WORKFLOW-CONTRACTS.md` must own the shared safety/evaluation checklist. | roadmap ITS-ROADMAP-011 |
| FR-2 | The shared checklist must contain boundary, human gate, token, error, evaluation, and report ownership fields. | completion plan |
| FR-3 | `tool-review`, `context-audit`, and `vibe-coding-health-check` must cite `../../WORKFLOW-CONTRACTS.md` and the `Shared Safety And Evaluation Checklist` section. | completion plan |
| FR-4 | `antifragile-agent` must keep its local antifragile output/token/error contract and cite `agent-playbook/WORKFLOW-CONTRACTS.md` for the shared checklist. | completion plan |
| FR-5 | Domain-specific checklist headings must remain local in each owning skill. | completion plan |
| FR-6 | Fixtures must fail if shared checklist ownership, section citations, or local domain headings are removed. | release-gate fixture expectation |
| FR-7 | The roadmap item must be marked complete only after focused fixtures, hygiene, strict release gate, and code review complete or record a concrete blocker. | roadmap acceptance |

## Non-Functional Requirements

- **Maintainability:** Keep common safety wording centralized without hiding
  skill-specific audit criteria.
- **Reliability:** Add fixture coverage that protects load-bearing references
  without overfitting to line wrapping.
- **Compatibility:** Preserve public skill names, metadata, allowed tools, and
  output paths.
- **Scope control:** Limit changes to docs/contracts, fixture checks, and
  roadmap closure artifacts.

## Success Criteria

- `bash tests/agent-playbook-eval-fixtures.sh` passes.
- `python3 scripts/skill-hygiene-check.py --mode working .` passes.
- `scripts/release-gate.sh --mode all --strict` passes.
- `git diff --check` passes.
- `idea-to-ship:review-code --slug ITS-ROADMAP-011` completes and
  `.idea-to-ship/ITS-ROADMAP-011/code-review.md` records a clean result or
  any accepted fixes.

## Open Questions

- None blocking. The selected shared location is the existing
  `agent-playbook/WORKFLOW-CONTRACTS.md`.

## Touch Points

- `agent-playbook/WORKFLOW-CONTRACTS.md`
- `agent-playbook/skills/tool-review/SKILL.md`
- `agent-playbook/skills/context-audit/SKILL.md`
- `agent-playbook/skills/vibe-coding-health-check/SKILL.md`
- `antifragile/skills/antifragile-agent/SKILL.md`
- `tests/agent-playbook-eval-fixtures.py`
- `.idea-to-ship/roadmap.md`
- `.idea-to-ship/ITS-ROADMAP-011/`
