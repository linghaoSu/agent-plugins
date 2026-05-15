# Requirements - ITS-ROADMAP-009

**Slug:** ITS-ROADMAP-009
**Date:** 2026-05-15
**Status:** draft
**Source:** `.idea-to-ship/roadmap.md`

## Problem

`issue-evaluator: evaluate-issue` carries long inline prompt and report
template blocks for its adversarial diagnosis review, final synthesis, and
final user-facing issue report. This makes the skill body expensive to load,
harder to review, and harder to keep consistent with the prompt/template
layout already used by neighboring issue-evaluator workflows.

The repo already has `issue-evaluator/prompts/` and
`issue-evaluator/templates/` for extracted review and PR-comment artifacts.
`evaluate-issue` should use the same pattern while preserving its current
diagnosis pipeline, read-only GitHub behavior, runtime-aware review routing,
and output contract.

## Users / Actors

- Skill maintainer: reviews and edits `evaluate-issue` workflow behavior with
  less inline prompt noise.
- Agent invoking `issue-evaluator:evaluate-issue`: loads a smaller skill body
  and follows exact references to the prompt/template artifacts when needed.
- Reviewer of future changes: diffs prompt wording and report fields in
  purpose-specific files instead of inside a long workflow document.

## In Scope

- Extract the Round 2 adversarial diagnosis prompt from
  `issue-evaluator/skills/evaluate-issue/SKILL.md` into
  `issue-evaluator/prompts/`.
- Extract the Round 3 final synthesis prompt from `evaluate-issue` into
  `issue-evaluator/prompts/`.
- Extract the Step 4 final issue report wrapper/template into
  `issue-evaluator/templates/`.
- Update `evaluate-issue/SKILL.md` to reference the extracted artifacts at the
  exact workflow points where they are needed.
- Preserve all current required roles, diagnosis rounds, review angles,
  degradation behavior, final report fields, and read-only constraints.
- Add or update deterministic fixture coverage if an existing issue-evaluator
  or release-gate fixture path can protect the extracted contract.

## Out of Scope / Non-Goals

- Changing the public skill name, arguments, input modes, or output contract.
- Changing GitHub fetch behavior or replacing `gh issue view`.
- Changing the code style guide lifecycle beyond references needed for this
  extraction.
- Rewriting `evaluate-issue` as an executable program.
- Implementing an actual issue fix workflow; this item is requirements for
  evaluation prompt/template extraction only.
- Adding network-dependent, live GitHub, or live model evaluations as tests.
- Extracting unrelated `fix-issue`, `review-pr`, or `fix-pr-comments` prompts.

## Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| FR-1 | `evaluate-issue/SKILL.md` must no longer inline the full Round 2 adversarial review prompt; it must reference an extracted prompt file under `issue-evaluator/prompts/`. | `.idea-to-ship/roadmap.md` ITS-ROADMAP-009; `evaluate-issue/SKILL.md:128-187` |
| FR-2 | The extracted Round 2 prompt must preserve the three required angles: `ROOT_CAUSE`, `FIX_PLAN_TESTABILITY`, and `REGRESSION_SCOPE`. | `evaluate-issue/SKILL.md:136-141` |
| FR-3 | The extracted Round 2 prompt must preserve read-only constraints, issue details, code style guide, Round 1 primary output, independent output, IDE diagnostics, and the Section A / Section B output structure. | `evaluate-issue/SKILL.md:143-187` |
| FR-4 | `evaluate-issue/SKILL.md` must no longer inline the full Round 3 final synthesis prompt; it must reference an extracted prompt file under `issue-evaluator/prompts/`. | `.idea-to-ship/roadmap.md` ITS-ROADMAP-009; `evaluate-issue/SKILL.md:194-263` |
| FR-5 | The extracted Round 3 prompt must preserve synthesis precedence rules: IDE diagnostics as ground truth, independent-source agreement confidence rules, tie-breaking by reading code, already-fixed verification, and specific implementable fix plans. | `evaluate-issue/SKILL.md:199-218` |
| FR-6 | The extracted Round 3 prompt must preserve the structured report fields: Status, Root Cause, Reproduction, Suggested Fix, Risks & Edge Cases, Disputed & Resolved, and Affected Files. | `evaluate-issue/SKILL.md:235-262` |
| FR-7 | `evaluate-issue/SKILL.md` must no longer inline the Step 4 final report wrapper; it must reference an extracted template file under `issue-evaluator/templates/`. | `.idea-to-ship/roadmap.md` ITS-ROADMAP-009; `evaluate-issue/SKILL.md:267-280` |
| FR-8 | The final report template must preserve issue title, issue number, review mode, degradation reason, diagnosis pipeline description, and the Round 3 structured output insertion point. | `evaluate-issue/SKILL.md:271-280` |
| FR-9 | The skill body must remain self-contained enough for routing: it should say which prompt/template file to read and when, but should not duplicate the long prompt text. | `issue-evaluator/prompts/`; `issue-evaluator/templates/` |
| FR-10 | The change must preserve description mode and ID mode behavior. | `evaluate-issue/SKILL.md:21-66` |
| FR-11 | The change must preserve runtime-aware multi-agent review routing and `degraded-same-context-review` rules. | `evaluate-issue/SKILL.md:14-34`; `issue-evaluator/WORKFLOW-CONTRACTS.md:6-84` |
| FR-12 | Deterministic verification must fail if a future edit removes the required Round 2 angles, Round 3 report fields, read-only constraints, or final report wrapper fields from the extracted artifacts. | Roadmap release gate and fixture expectation |

## Non-Functional Requirements

- **Performance:** Reduce repeated prompt text in the loaded skill body; no
  runtime performance requirement beyond smaller instruction payload.
- **Scale:** Applies to one skill now, with file naming and layout consistent
  enough to support future prompt extraction in this plugin.
- **Reliability / failure mode:** If a referenced prompt/template file is
  missing or incomplete, deterministic checks should fail before release.
- **Security / compliance:** Preserve read-only behavior. The workflow must
  not mutate GitHub, git state, repository files, credentials, deployment
  state, or external systems during evaluation.
- **Platform / constraints:** Use Markdown prompt/template files and existing
  shell/Python-standard-library fixture style. Do not introduce new runtime
  dependencies.

## Success Criteria

- `evaluate-issue` prompt extraction is complete -> verify:
  `rg -n "Use this prompt per angle|You are the final synthesis agent|## Issue Evaluation:" issue-evaluator/skills/evaluate-issue/SKILL.md`
  shows references or brief routing text, not full inline prompt/template
  blocks.
- Required extracted artifacts exist -> verify:
  `test -f issue-evaluator/prompts/evaluate-issue-round2-adversarial.md &&
  test -f issue-evaluator/prompts/evaluate-issue-round3-synthesis.md &&
  test -f issue-evaluator/templates/evaluate-issue-final-report.md`.
- Round 2 contract is preserved -> verify deterministic fixture or grep checks
  find `ROOT_CAUSE`, `FIX_PLAN_TESTABILITY`, `REGRESSION_SCOPE`,
  read-only constraints, IDE diagnostics, and Section A / Section B structure
  in the extracted Round 2 prompt.
- Round 3 contract is preserved -> verify deterministic fixture or grep checks
  find IDE diagnostics as ground truth, confidence rules, already-fixed
  handling, and all required structured report headings in the extracted Round
  3 prompt.
- Final report wrapper is preserved -> verify deterministic fixture or grep
  checks find issue title, issue number, review mode, degradation reason,
  diagnosis pipeline, and Round 3 insertion point in the extracted template.
- Existing release checks pass -> verify:
  `scripts/release-gate.sh --mode staged` passes after the implementation is
  staged.
- Full strict confidence check passes if fixtures are touched -> verify:
  `scripts/release-gate.sh --mode all --strict` passes before considering the
  roadmap item done.

## Open Questions

- Should the new deterministic fixture live in the existing
  `tests/agent-playbook-eval-fixtures.*` path, or should this stage introduce a
  dedicated issue-evaluator fixture command? Architecture should pick the
  smallest maintainable option.
- Should `issue-evaluator:review-pr` and `issue-evaluator:fix-pr-comments`
  prompt extraction conventions be documented as naming guidance, or is local
  file naming enough for this item?

## Touch Points

- `issue-evaluator/skills/evaluate-issue/SKILL.md`
- `issue-evaluator/prompts/`
- `issue-evaluator/templates/`
- `issue-evaluator/WORKFLOW-CONTRACTS.md`
- `tests/agent-playbook-eval-fixtures.sh`
- `tests/agent-playbook-eval-fixtures.py`
- `scripts/release-gate.sh`
- `RELEASE-GATE.md`
