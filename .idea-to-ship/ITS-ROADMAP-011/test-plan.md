# Test Plan - ITS-ROADMAP-011

**Slug:** ITS-ROADMAP-011
**Date:** 2026-06-01
**Status:** stage-local

## Stage TDD Slices

| Stage | Slice | Expected Red Signal | Expected Green Signal |
|---|---|---|---|
| Stage 1 | Protect shared audit checklist ownership in `tests/agent-playbook-eval-fixtures.py`. | `bash tests/agent-playbook-eval-fixtures.sh` fails because `tool-review`, `context-audit`, `vibe-coding-health-check`, and `antifragile-agent` do not cite the shared checklist section explicitly. | The same command passes after the shared contract owner note and skill citations are updated. |

## Acceptance Criteria

| ID | Criterion | Verification Method |
|---|---|---|
| AC-1 | Shared checklist section exists with boundary, human gate, token, error, evaluation, and report ownership fields. | `bash tests/agent-playbook-eval-fixtures.sh` |
| AC-2 | Audit skills cite the shared checklist section explicitly. | `bash tests/agent-playbook-eval-fixtures.sh` |
| AC-3 | Domain-specific checklist headings stay in their owning skills. | `bash tests/agent-playbook-eval-fixtures.sh` |
| AC-4 | Skill hygiene remains clean for changed skills. | `python3 scripts/skill-hygiene-check.py --mode working .` |
| AC-5 | Diff has no whitespace errors. | `git diff --check` |
| AC-6 | Full release gate status is known. | `scripts/release-gate.sh --mode all --strict` |
| AC-7 | Independent review is recorded before roadmap closure. | `.idea-to-ship/ITS-ROADMAP-011/code-review.md` |

## Traceability

| Requirement | Tests |
|---|---|
| FR-1, FR-2 | `agent-playbook-shared-safety-evaluation-checklist-contract` |
| FR-3 | `tool-review-shared-checklist-reference-contract`, `context-audit-shared-checklist-reference-contract`, `vibe-health-shared-checklist-reference-contract` |
| FR-4 | `antifragile-agent-shared-checklist-reference-contract` |
| FR-5, FR-6 | Local heading invariants in the same shared-checklist reference contracts |
| FR-7 | Final verification notes, code-review artifact, and roadmap update |
