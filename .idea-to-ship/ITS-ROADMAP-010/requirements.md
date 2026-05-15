# Requirements - ITS-ROADMAP-010

**Slug:** ITS-ROADMAP-010
**Date:** 2026-05-15
**Status:** draft
**Source:** `.idea-to-ship/roadmap.md`

## Problem

The repo has started extracting long prompt and template blocks out of
`SKILL.md` files to reduce token load and repeated maintenance. The current
`scripts/skill-hygiene-check.py` catches a few broad problems, but it does not
yet protect the cleanup pattern well enough: repeated inline prompts/templates
and moderately bloated skill bodies can creep back in without a targeted
release-gate signal.

This matters because skill files are routing contracts. When they grow by
repeating full prompts, report templates, or cross-skill boilerplate, every
invocation becomes more expensive to load and harder to review. The gate should
warn early without blocking legitimate concise skills or turning normal wording
changes into noisy failures.

## Users / Actors

- Skill maintainer: sees actionable hygiene findings before committing prompt
  or template duplication.
- Plugin releaser: runs the local release gate and gets a clear warning or
  strict-mode failure when a skill regresses into repeated inline bulk.
- Future skill author: follows a predictable expectation for when prompt,
  template, and shared-contract text should move out of `SKILL.md`.
- Reviewer: evaluates smaller skill diffs with evidence that repeated prompt
  text and moderate bloat were checked deterministically.

## In Scope

- Add conservative hygiene checks for repeated inline prompts, repeated inline
  templates, and moderate skill bloat.
- Keep checks local, offline, deterministic, and compatible with
  `scripts/release-gate.sh --mode staged|working|all`.
- Make findings actionable: each finding should name the file, check ID, and
  why extraction or shared-contract reference is recommended.
- Provide fixture or sample coverage that proves the new checks catch intended
  regressions without relying on exact prose snapshots.
- Tune the new rules against existing skills so current acceptable files do not
  create broad false positives.
- Preserve `--strict` behavior: advisory hygiene warnings remain warnings by
  default and become failures only when strict mode is used.

## Out of Scope / Non-Goals

- Rewriting or extracting any specific skill prompt as part of this item.
- Enforcing a hard universal line limit for all skills.
- Deleting or renaming existing skills.
- Introducing network access, GitHub access, or live model evaluation.
- Adding a new linter dependency beyond Python standard library unless a later
  architecture explicitly justifies it.
- Making exact wording or golden-file checks that fail on harmless prose edits.
- Blocking long skills that have a documented reason to remain self-contained.

## Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| FR-1 | The hygiene checker must detect repeated inline prompt-like blocks in changed or all skill files using a conservative, low-noise signal. | `.idea-to-ship/roadmap.md` ITS-ROADMAP-010 |
| FR-2 | The hygiene checker must detect repeated inline template/report-wrapper blocks in changed or all skill files using a conservative, low-noise signal. | `.idea-to-ship/roadmap.md` ITS-ROADMAP-010 |
| FR-3 | The hygiene checker must add a moderate-bloat warning below the existing oversized-skill threshold so maintainers see growth before a skill reaches the current `MAX_SKILL_LINES = 750` limit. | `scripts/skill-hygiene-check.py:19-20`; roadmap ITS-ROADMAP-010 |
| FR-4 | Moderate-bloat findings must recommend extracting prompts/templates or citing shared contracts, but must not require extraction when the skill has a documented reason to remain self-contained. | roadmap ITS-ROADMAP-010 no-go |
| FR-5 | New checks must run through the existing `skill-hygiene` advisory path in `scripts/release-gate.sh` for `staged`, `working`, and `all` modes. | `RELEASE-GATE.md:42-51` |
| FR-6 | In non-strict release-gate mode, new hygiene findings must remain advisory warnings; in `--strict`, those findings must cause release-gate failure through the existing advisory-upgrade behavior. | `RELEASE-GATE.md:15-17`; `RELEASE-GATE.md:42-51` |
| FR-7 | Findings must use stable check IDs so future fixtures and reviews can refer to them without depending on exact prose. | Existing `Finding.check_id` pattern in `scripts/skill-hygiene-check.py` |
| FR-8 | The implementation must include deterministic coverage for at least one repeated-prompt case, one repeated-template case, and one moderate-bloat case. | roadmap ITS-ROADMAP-010 evidence required |
| FR-9 | The checks must avoid broad false positives against current accepted skills when run in `--mode all`, or any intentional existing findings must be documented in the implementation log. | roadmap ITS-ROADMAP-010 risk |
| FR-10 | The checks must not scan generated or ignored scratch artifacts outside the existing skill-file scope unless architecture explicitly expands scope. | Existing `iter_all_skill_files` / `changed_skill_files` scope |

## Non-Functional Requirements

- **Performance:** `python3 scripts/skill-hygiene-check.py --mode all .` should
  remain fast enough for local release-gate use; target under 5 seconds on the
  current repo.
- **Scale:** Must handle the current repo's plugin/skill count and modest
  growth without quadratic cross-file text comparison.
- **Reliability / failure mode:** If a rule is uncertain, it should warn with a
  precise reason rather than silently rewriting files or attempting extraction.
- **Security / compliance:** The check must be read-only and offline. It must
  not read secrets outside repo files selected by the existing skill scope.
- **Platform / constraints:** Python standard library only; compatible with
  existing zsh/bash release-gate commands.

## Success Criteria

- Repeated prompt detection works -> verify: a fixture or temporary sample skill
  containing repeated long prompt-like blocks produces a stable finding ID.
- Repeated template detection works -> verify: a fixture or temporary sample
  skill containing repeated final-report/template wrapper text produces a
  stable finding ID.
- Moderate-bloat detection works -> verify: a fixture or temporary sample skill
  over the selected moderate threshold but below `MAX_SKILL_LINES` produces a
  stable finding ID.
- Existing release-gate integration remains intact -> verify:
  `scripts/release-gate.sh --mode working --strict` passes or fails only for
  intentional current-diff findings.
- Full-repo strict check is usable -> verify:
  `scripts/release-gate.sh --mode all --strict` passes after implementation or
  documents any intentional existing advisory findings before hand-off.
- No brittle prose snapshots -> verify: tests assert check IDs / invariant
  tokens / structural behavior, not exact full warning sentences.

## Open Questions

- What moderate-bloat threshold should architecture choose? Initial candidates:
  advisory over 300 lines, strict-over-warning at 400 lines, or keep only the
  existing 750-line oversized threshold.
- Should repeated prompt/template detection be purely intra-file, or should it
  also detect near-duplicate blocks across multiple skills?
- Should allowlist comments be supported for intentionally self-contained long
  skills, and if so what exact syntax should avoid becoming an escape hatch?
- Should this item include a lightweight token/character budget report, or
  should measurement stay line-count based for now?

## Touch Points

- `scripts/skill-hygiene-check.py`
- `scripts/release-gate.sh`
- `RELEASE-GATE.md`
- `tests/agent-playbook-eval-fixtures.py`
- `tests/agent-playbook-eval-fixtures.sh`
- `tests/idea-to-ship-eval-fixtures.py`
- `tests/idea-to-ship-eval-fixtures.sh`
