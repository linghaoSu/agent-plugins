# Requirements - ITS-ROADMAP-008

**Slug:** ITS-ROADMAP-008
**Date:** 2026-06-01
**Status:** accepted for closure
**Source:** `.idea-to-ship/roadmap.md`

## Problem

`idea-to-ship:implement` is the central staged execution skill. The roadmap
identified it as carrying repeated routing and implementation-log mechanics that
should be owned by shared contracts/templates instead of duplicated in the skill
body.

Previous cleanup already moved most cross-skill routing authority to
`idea-to-ship/WORKFLOW-CONTRACTS.md` and most log shape to
`idea-to-ship/templates/implementation-log.md`, but no dedicated
`ITS-ROADMAP-008` artifact chain existed and the roadmap still marked the item
as needing a closure decision.

## Users / Actors

- Skill maintainer: can review `implement` behavior without re-reading repeated
  routing and log boilerplate.
- Agent invoking `idea-to-ship:implement`: still gets the same staged workflow,
  TDD gate, UI contract gate, tournament gate, verification gate, and no commit
  behavior.
- Reviewer: can verify the shared contract/template references through
  deterministic fixtures.

## In Scope

- Add this closure artifact set under `.idea-to-ship/ITS-ROADMAP-008/`.
- Keep `idea-to-ship:implement` public behavior unchanged.
- Tighten `implement/SKILL.md` so detailed implementation-log fields are clearly
  delegated to `../../templates/implementation-log.md`.
- Extend `implementation-log.md` template to include pre-stage assumptions,
  success criteria, verification/TDD evidence, deviations, and structured
  cross-skill check fields.
- Add deterministic fixture coverage for the new contract.
- Update `.idea-to-ship/roadmap.md` from `Needs closure decision` to
  `Completed` after verification.

## Out of Scope / Non-Goals

- No public skill rename, argument change, or new command.
- No weakening of TDD, UI-design, drift, tournament, verification, or
  cross-skill routing gates.
- No broad rewrite of `implement/SKILL.md`.
- No new runtime template renderer or code generation.
- No changes to `idea-to-ship:tdd`, `/test`, `/review-code`, or `/architect`
  beyond fixture references required for this closure.

## Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| FR-1 | `implement/SKILL.md` must cite `../../WORKFLOW-CONTRACTS.md` for cross-skill routing instead of duplicating the implementation-stage route table. | roadmap ITS-ROADMAP-008 |
| FR-2 | `implement/SKILL.md` must cite `../../templates/implementation-log.md` for stage status and log fields. | roadmap ITS-ROADMAP-008 |
| FR-3 | `implementation-log.md` template must include pre-stage assumptions, success criteria, files touched, decisions, deviations, adjacent issues, verification, TDD evidence, and cross-skill checks. | roadmap ITS-ROADMAP-008 |
| FR-4 | Cross-skill checks must be recorded with trigger, result, and impact. | `WORKFLOW-CONTRACTS.md` implementation-stage routes |
| FR-5 | Deterministic fixtures must fail if `implement` loses the shared references or the template loses the load-bearing fields. | release-gate fixture expectation |
| FR-6 | The roadmap item must be marked complete only after fixtures and hygiene checks pass, with release-gate status recorded. | roadmap acceptance |

## Non-Functional Requirements

- **Maintainability:** Keep skill text concise without hiding stage-specific
  judgment.
- **Reliability:** Fixture checks should protect the extracted contract from
  silent drift.
- **Compatibility:** No behavior change for existing `idea-to-ship:implement`
  invocations.
- **Dependencies:** Do not introduce new runtime dependencies.

## Success Criteria

- `tests/idea-to-ship-eval-fixtures.sh` passes.
- `python3 scripts/skill-hygiene-check.py --mode working .` passes.
- `git diff --check` passes.
- `scripts/release-gate.sh --mode all --strict` is run if local dependencies are
  available; otherwise the missing dependency is recorded as an environment
  blocker.
- `.idea-to-ship/roadmap.md` marks `ITS-ROADMAP-008` complete and cites the
  closure artifacts.

## Open Questions

- None blocking. The chosen path is a focused closure pass rather than claiming
  earlier commits closed the item without artifacts.

## Touch Points

- `idea-to-ship/skills/implement/SKILL.md`
- `idea-to-ship/templates/implementation-log.md`
- `tests/idea-to-ship-eval-fixtures.py`
- `.idea-to-ship/roadmap.md`
- `.idea-to-ship/ITS-ROADMAP-008/`
