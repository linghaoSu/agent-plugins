# Test Plan - ITS-ROADMAP-008

**Slug:** ITS-ROADMAP-008
**Date:** 2026-06-01
**Status:** stage-local

## Stage TDD Slices

| Stage | Slice | Expected Red Signal | Expected Green Signal |
|---|---|---|---|
| Stage 1 | Protect `implement` shared-template contract in `tests/idea-to-ship-eval-fixtures.py`. | Initial red run failed on missing `template owns log details` and `success criteria`; post-review fixture hardening split the former into `template owns stage status` and `template owns cross-skill check fields` so either missing token fails independently. | The same command passes after `implement/SKILL.md`, `templates/implementation-log.md`, and the split fixture invariants are updated. |

## Acceptance Criteria

| ID | Criterion | Verification Method |
|---|---|---|
| AC-1 | `implement` keeps shared routing and template references. | `tests/idea-to-ship-eval-fixtures.sh` |
| AC-2 | Implementation-log template records assumptions, success criteria, verification/TDD evidence, deviations, and cross-skill trigger/result/impact. | `tests/idea-to-ship-eval-fixtures.sh` |
| AC-3 | Skill hygiene stays clean. | `python3 scripts/skill-hygiene-check.py --mode working .` |
| AC-4 | Diff has no whitespace errors. | `git diff --check` |
| AC-5 | Release gate status is known. | `scripts/release-gate.sh --mode all --strict` or recorded dependency blocker |

## Traceability

| Requirement | Tests |
|---|---|
| FR-1, FR-2 | `implement-template-reference-contract` |
| FR-3, FR-4 | `implementation-log-template-contract` |
| FR-5 | Red-first fixture run in `tdd-log.md` |
| FR-6 | Final roadmap update and verification notes |
