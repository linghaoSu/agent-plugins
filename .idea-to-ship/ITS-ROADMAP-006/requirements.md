# Requirements - ITS-ROADMAP-006

**Date:** 2026-05-09
**Status:** draft
**Source:** `.idea-to-ship/roadmap.md`

## Problem

The idea-to-ship skills now carry critical planning, testing, and review
contracts, but most of those contracts are verified by manual Markdown review.
That is too weak for a plugin repo that is starting to use release gates. We
need repeatable, offline fixtures that catch accidental regressions in the
critical skill workflows without requiring a live GitHub connection, live LLM
execution, or mutation of a user's real repository.

## Scope

In scope:

- Add executable fixture coverage for critical `idea-to-ship` skill contracts.
- Cover `/roadmap`, `/test`, and `/review-code` critical paths named in the
  portfolio roadmap.
- Keep fixtures local, deterministic, and safe to run from the release gate.
- Document limitations so these fixtures are not mistaken for full agent evals.

Out of scope:

- Live Claude/Codex/GitHub driven evaluations.
- CI wiring beyond a local command hook point.
- Rewriting the skills to be executable programs.
- Golden-file assertions over long generated prose.

## Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| FR-1 | Provide one repo-owned command that runs the idea-to-ship eval fixtures and returns non-zero on contract regression. | `.idea-to-ship/roadmap.md` ITS-ROADMAP-006 |
| FR-2 | The `/roadmap` fixture coverage must check the first-run contract: no existing roadmap writes a candidate brief to the resolved target before final lanes. | `idea-to-ship/skills/roadmap/SKILL.md` acceptance checks |
| FR-3 | The `/roadmap` fixture coverage must check the rerun-safety contract: existing human content is preserved, merged by generated markers, drafted around, or requires approval before overwrite. | `idea-to-ship/skills/roadmap/SKILL.md` write target safety |
| FR-4 | The `/roadmap` fixture coverage must check the `--final` without priority approval contract: final lanes are blocked and approval is requested. | `idea-to-ship/skills/roadmap/SKILL.md` acceptance checks |
| FR-5 | The `/test` fixture coverage must check the story-first planning contract: user stories, acceptance criteria, scenario matrix, and unit/integration/e2e matrix are required before tests. | `idea-to-ship/skills/test/SKILL.md` |
| FR-6 | The `/test` fixture coverage must check the non-happy-path contract: edge/corner, invalid or abnormal input, and failure modes are explicitly required. | `idea-to-ship/skills/test/SKILL.md` |
| FR-7 | The `/review-code` fixture coverage must check the missing-test-plan contract: behavior-changing diffs without `test-plan.md` are flagged as a verification gap. | `idea-to-ship/skills/review-code/SKILL.md` |
| FR-8 | The `/review-code` fixture coverage must check the runtime-aware routing and fallback documentation contract without hard-coding Claude-only execution in non-Claude runtimes. | `idea-to-ship/skills/review-code/SKILL.md`; ITS-ROADMAP-003 |
| FR-9 | Fixtures must avoid live GitHub, network, plugin installation, and mutation outside temporary files. | `.idea-to-ship/roadmap.md` no-go |
| FR-10 | Assertions must prefer behavioral invariants over exact prose snapshots to keep evals stable as wording improves. | `.idea-to-ship/roadmap.md` risk |
| FR-11 | The `/brainstorm` and `/architect` fixture coverage must check rerun-safety contracts: stable IDs/sections are preserved, human edits are not overwritten, and unsafe merges draft or require approval. | Stage 5 hardening |
| FR-12 | Review skills must treat model-selection/capacity failures as sub-agent unavailability and fall back to main-context review instead of failing or retrying the same selected model. | User report: Codex shows "Selected model is at capacity" |

## Success Criteria

- `bash tests/idea-to-ship-eval-fixtures.sh` passes on the current repo.
- The command fails with a clear message if a critical contract is removed from
  `roadmap`, `test`, or `review-code`.
- The output labels these as contract fixtures, not proof of live model
  behavior.
- The fixture command is referenced from the release-gate path as either an
  advisory or documented next-stage check.
- Limitations are documented in the implementation artifact.
- Rerun preservation for `requirements.md` and `architecture.md` is covered by
  both skill-contract checks and artifact draft-fallback checks.
- Runtime-aware review fixtures require explicit capacity fallback wording so
  Codex capacity errors do not break `/review-code`.

## Constraints

- Use only shell and Python standard library unless the repo later adopts a
  broader test framework.
- Keep all temporary state under `mktemp` directories.
- Do not require `claude`, `codex`, `gh`, network access, or API tokens.
- Do not assert exact generated Markdown output from a model.

## Open Questions

- None blocking. Stage 1 should land as a manually runnable command first and
  be considered for release-gate integration after one stable iteration.
