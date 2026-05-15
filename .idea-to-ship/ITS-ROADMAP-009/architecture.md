# Architecture - Extract Evaluate-Issue Prompts

**Slug:** ITS-ROADMAP-009
**Date:** 2026-05-15
**Status:** draft
**References:** requirements.md

## Summary

Extract the large inline `issue-evaluator:evaluate-issue` Round 2, Round 3,
and final-report prompt/template blocks into the existing
`issue-evaluator/prompts/` and `issue-evaluator/templates/` layout. The chosen
approach is a small vertical slice: add three extracted artifacts, replace the
inline prompt bodies with explicit references from `evaluate-issue/SKILL.md`,
and protect the moved contract through the existing offline
`agent-playbook-eval-fixtures` path that already covers `issue-evaluator/`
changes.

## Goals / Non-Goals

Goals:

- Reduce `issue-evaluator/skills/evaluate-issue/SKILL.md` prompt bulk without
  changing public skill behavior.
- Preserve description mode, ID mode, GitHub read-only behavior, runtime-aware
  multi-agent review routing, degradation handling, diagnosis rounds, review
  angles, and final report fields.
- Reuse the plugin's existing prompt/template conventions instead of inventing
  a new storage layout.
- Add deterministic, offline fixture coverage for the extracted contracts.

Non-goals:

- No public skill rename, argument change, or output-contract change.
- No change to `gh issue view`, code style guide lifecycle, GitHub mutation
  boundaries, or issue fixing workflow.
- No live GitHub, network, or live model evaluation in tests.
- No extraction of unrelated `review-pr`, `fix-pr-comments`, or `fix-issue`
  prompts in this stage.

## Codebase Context

Exploration used one authorized runtime-native explorer sub-agent plus local
source reads. The explorer edited no files.

- `issue-evaluator/skills/evaluate-issue/SKILL.md` is the target skill. It
  currently keeps workflow/routing text inline and also embeds the long Round 2
  adversarial prompt, Round 3 synthesis prompt, and Step 4 final report wrapper.
- `issue-evaluator/skills/review-pr/SKILL.md` is the closest local convention:
  it keeps orchestration/routing instructions in the skill body while
  referencing `../../prompts/review-pr-round1.md`,
  `../../prompts/review-pr-round2-adversarial.md`,
  `../../prompts/review-pr-round3-synthesis.md`, and
  `../../templates/review-pr-final-report.md`.
- `issue-evaluator/skills/fix-pr-comments/SKILL.md` follows the same pattern
  for analyst, reconciler, executor, adversarial reviewer, and final report
  artifacts.
- Existing prompt files under `issue-evaluator/prompts/` are Markdown files
  with explicit sections such as Role, Inputs, Hard Constraints, Tasks, and
  Output. Existing templates under `issue-evaluator/templates/` wrap report
  structure in a fenced Markdown block.
- `tests/agent-playbook-eval-fixtures.py` already holds regex-style contract
  checks for issue-evaluator skills, prompt references, prompt contracts, and
  final report templates.
- `scripts/release-gate.sh` already routes changes under `issue-evaluator/` to
  `bash tests/agent-playbook-eval-fixtures.sh`; `RELEASE-GATE.md` documents
  that fixture route. There is no dedicated issue-evaluator fixture command.
- `scripts/skill-hygiene-check.py` already encourages moving long inline
  prompts/templates out of `SKILL.md`, so this work aligns with existing
  hygiene policy.

## Cross-Skill Routing

| Signal | Routed skill | Result | Design impact |
|---|---|---|---|
| `evaluate-issue` is an agent/evaluator-style workflow, but this stage only moves existing prompt text and preserves current roles. | `harness-engineering:sprint-contract` | Evaluated, not run. No new generator/evaluator contract or harness behavior is being designed. | Keep role names and degradation rules in the skill body; protect moved prompt obligations with fixtures. |
| The skill fetches GitHub issue data, but this stage does not add or change external calls, retries, fallback paths, or observability. | `antifragile:antifragile-system` | Not run. No new external dependency behavior is introduced by prompt extraction. | Explicitly keep `gh issue view` behavior and GitHub read-only boundaries unchanged. |
| Requirements mention read-only GitHub behavior and generated prompt examples, but no credentials or secret-like sample values are introduced. | `secret-scanner:scan-secrets` | Not run during architecture. Implementation-stage routing may run the normal release-gate secret scan. | Do not add credential examples; rely on release gate secret scan after implementation. |

## Alternatives Considered

### Option A - Targeted Extraction With Existing Fixtures

Extract the three load-bearing blocks into:

- `issue-evaluator/prompts/evaluate-issue-round2-adversarial.md`
- `issue-evaluator/prompts/evaluate-issue-round3-synthesis.md`
- `issue-evaluator/templates/evaluate-issue-final-report.md`

Then replace the inline blocks in `evaluate-issue/SKILL.md` with explicit
references and add contract checks to `tests/agent-playbook-eval-fixtures.py`.

**Module changes:** `issue-evaluator/skills/evaluate-issue/SKILL.md`,
`issue-evaluator/prompts/`, `issue-evaluator/templates/`,
`tests/agent-playbook-eval-fixtures.py`.

**Data flow:** A future agent running `evaluate-issue` reads the slim skill body,
then loads the named prompt/template artifact at the exact diagnosis phase that
needs it. Release gate advisory fixtures validate the referenced files when
`issue-evaluator/` changes.

**Interfaces:** Markdown artifact paths and placeholder contracts for issue
number, issue title, issue details, `ROUND_1_PRIMARY`,
`ROUND_1_INDEPENDENT`, `ROUND_1_DIAGNOSTICS`, `ROUND_2_DIAGNOSIS`, review mode,
degradation reason, and Round 3 output insertion point.

**Pros:** Smallest blast radius; matches `review-pr` and `fix-pr-comments`;
reversible; no release-gate plumbing change; fixtures already cover the touched
plugin scope.

**Cons:** The fixture command name remains `agent-playbook-eval-fixtures` even
though it protects issue-evaluator contracts, which is historically accurate
but semantically broad.

**Risk:** Medium-low. The main risk is losing prompt nuance during extraction;
targeted fixture checks and review-design should catch missing required fields.

### Option B - Targeted Extraction With Dedicated Issue-Evaluator Fixtures

Use the same three extracted artifacts and skill references as Option A, but
introduce `tests/issue-evaluator-eval-fixtures.py` and
`tests/issue-evaluator-eval-fixtures.sh`, then update `scripts/release-gate.sh`
and `RELEASE-GATE.md` to run the dedicated command for `issue-evaluator/`
changes.

**Module changes:** Option A files plus new issue-evaluator fixture scripts and
release-gate documentation/plumbing.

**Data flow:** Release gate dispatches issue-evaluator changes to a
plugin-specific fixture command instead of the existing broader fixture.

**Interfaces:** Same prompt/template artifact interfaces as Option A, plus a
new release-gate advisory check id such as `issue-evaluator-fixtures`.

**Pros:** Cleaner ownership boundary for future issue-evaluator checks; easier
to understand from command names.

**Cons:** Larger blast radius; duplicates fixture scaffolding; requires release
gate and docs edits for a single prompt extraction; creates a second fixture
surface before there is enough issue-evaluator-only volume to justify it.

**Risk:** Medium. The extra release-gate wiring is easy to get subtly wrong and
adds maintenance cost unrelated to the prompt extraction itself.

### Option C - Generic Prompt-Extraction Hygiene Rule

Extract the three artifacts, then add a generic rule to
`scripts/skill-hygiene-check.py` that flags missing prompt/template references
or oversized inline prompt blocks, instead of adding evaluate-issue-specific
fixture checks.

**Module changes:** Prompt/template files, `evaluate-issue/SKILL.md`,
`scripts/skill-hygiene-check.py`, and potentially release-gate docs if the
hygiene rule becomes more binding.

**Data flow:** Release gate runs skill hygiene and detects broad classes of
prompt bloat or missing extraction references.

**Interfaces:** Generic hygiene heuristics rather than explicit
evaluate-issue prompt/report invariants.

**Pros:** Helps prevent future bloat beyond this one skill; aligns with
ITS-ROADMAP-010 if that work lands next.

**Cons:** Does not directly prove that `ROOT_CAUSE`, `FIX_PLAN_TESTABILITY`,
`REGRESSION_SCOPE`, final report fields, or degradation fields survived the
move; generic heuristics are weaker than exact contract checks.

**Risk:** Medium-high. It can pass while load-bearing evaluate-issue fields are
missing, so it does not satisfy FR-12 without additional specific checks.

## Recommendation

**We pick Option A.** It fits the existing `issue-evaluator` prompt/template
layout, uses the release-gate fixture path already assigned to
`issue-evaluator/`, and keeps the blast radius to one skill plus three
artifacts and fixture checks. The accepted tradeoff is keeping
issue-evaluator-specific assertions inside a broadly named
`agent-playbook-eval-fixtures` command for now; that is preferable to adding
release-gate plumbing before there is a larger issue-evaluator fixture split to
justify it.

## Chosen Design - Detail

### Module Breakdown

- `issue-evaluator/prompts/evaluate-issue-round2-adversarial.md` - new prompt
  artifact for Round 2 diagnosis adversarial reviewers.
- `issue-evaluator/prompts/evaluate-issue-round3-synthesis.md` - new prompt
  artifact for Round 3 final synthesis.
- `issue-evaluator/templates/evaluate-issue-final-report.md` - new final
  report wrapper template.
- `issue-evaluator/skills/evaluate-issue/SKILL.md` - replace inline prompt and
  template bodies with references to the new artifacts while preserving
  orchestration, phase gates, and routing rules.
- `tests/agent-playbook-eval-fixtures.py` - add contract checks for the new
  skill references, prompt artifacts, and final template artifact.
- `tests/agent-playbook-eval-fixtures.sh` - no expected change; it already
  delegates to the Python helper.
- `scripts/release-gate.sh` - no expected change; it already runs
  `agent-playbook-fixtures` when `issue-evaluator/` changes.
- `RELEASE-GATE.md` - no expected change unless implementation discovers the
  current docs no longer describe fixture scope accurately.

### Data Flow

```text
evaluate-issue/SKILL.md
  Step 3 Round 2 -> read ../../prompts/evaluate-issue-round2-adversarial.md
  Step 3 Round 3 -> read ../../prompts/evaluate-issue-round3-synthesis.md
  Step 4 report  -> read ../../templates/evaluate-issue-final-report.md

implementation diff touching issue-evaluator/
  -> scripts/release-gate.sh --mode staged --strict
  -> bash tests/agent-playbook-eval-fixtures.sh
  -> tests/agent-playbook-eval-fixtures.py checks skill references and artifact invariants
```

The skill body remains the workflow map. The extracted files hold the long
role-specific wording and report skeleton.

Important staging caveat: `tests/agent-playbook-eval-fixtures.py` reads the
working tree, not the staged index. Before accepting a staged gate result, the
implementation must confirm the staged diff includes every intended file and
that those staged files have no unstaged remainder.

### Interfaces

Round 2 prompt artifact:

```text
Path: issue-evaluator/prompts/evaluate-issue-round2-adversarial.md
Inputs: issue details, compact code style checklist, ROUND_1_PRIMARY,
ROUND_1_INDEPENDENT, ROUND_1_DIAGNOSTICS, assigned ANGLE
Required angles: ROOT_CAUSE, FIX_PLAN_TESTABILITY, REGRESSION_SCOPE
Output sections: Section A: Independent Diagnosis; Section B: Evaluation of Round 1
Hard constraints: read-only; no file edits; no GitHub mutation; IDE diagnostics are facts
```

Round 3 prompt artifact:

```text
Path: issue-evaluator/prompts/evaluate-issue-round3-synthesis.md
Inputs: issue details, ROUND_1_PRIMARY, ROUND_1_INDEPENDENT,
ROUND_1_DIAGNOSTICS, ROUND_2_DIAGNOSIS
Output sections: Status, Root Cause, Reproduction, Suggested Fix,
Risks & Edge Cases, Disputed & Resolved, Affected Files
Precedence rules: IDE diagnostics are ground truth; independent agreement
raises confidence; disagreements require reading code to break ties
```

Final report template:

```text
Path: issue-evaluator/templates/evaluate-issue-final-report.md
Fields: Issue Evaluation heading with issue-title placeholder, optional
description-mode line, issue number, review mode, degradation reason, diagnosis
pipeline, Round 3 structured output
```

Do not add the compact `WORKFLOW-CONTRACTS.md` output/token/error block as part
of this roadmap item. The current requirement is prompt/template extraction
without output-contract changes. If a later roadmap item adds the compact
contract to `evaluate-issue`, it must handle code-style guide generation
correctly because Step 2 may write a repo-specific `code-style.md` under the
issue-evaluator data directory.

`evaluate-issue/SKILL.md` should reference files with the same relative style
used by neighboring skills:

```text
Use `../../prompts/evaluate-issue-round2-adversarial.md` for each Round 2 angle.
Use `../../prompts/evaluate-issue-round3-synthesis.md` for Round 3.
Use `../../templates/evaluate-issue-final-report.md` for Step 4.
```

The skill must also say that each referenced artifact is read before use. If a
referenced prompt/template is missing or empty, stop with a terminal error and
do not reconstruct the prompt from memory or from this architecture document.

### Extraction Procedure

Initial extraction must be mechanically faithful:

1. Copy the current Round 2 fenced prompt block from
   `issue-evaluator/skills/evaluate-issue/SKILL.md` under "Use this prompt per
   angle" into `issue-evaluator/prompts/evaluate-issue-round2-adversarial.md`
   verbatim, except for adding a file title.
2. Copy the current Round 3 fenced prompt block under "Final Synthesis" into
   `issue-evaluator/prompts/evaluate-issue-round3-synthesis.md` verbatim,
   except for adding a file title.
3. Copy the current Step 4 fenced `markdown` report wrapper into
   `issue-evaluator/templates/evaluate-issue-final-report.md` verbatim, except
   for adding a file title. Also add the existing Step 0 description-mode
   header line `**Mode**: description-based evaluation (no GitHub issue)` as an
   optional conditional line immediately after the `## Issue Evaluation:
   <issue-title>` heading. Preserve that exact wording and do not otherwise
   normalize the template.
4. Only after those files exist, replace the inline blocks in
   `evaluate-issue/SKILL.md` with references and the missing/empty terminal
   stop rule.

Do not normalize the moved prompts into new Role/Input/Task wording in this
stage. Any wording cleanup is a separate behavior-affecting prompt change and
needs its own requirements or explicit design update.

### Data / Schema Changes

None. This is Markdown workflow and fixture data only. No runtime data model,
database schema, API route, or persisted state changes are needed.

### Failure Modes & Handling

- Extracted file is missing: `tests/agent-playbook-eval-fixtures.py` should
  fail with `Missing required file`.
- Extracted file is missing from an installed plugin at runtime:
  `evaluate-issue/SKILL.md` should stop with a terminal error and should not
  improvise a substitute prompt.
- Skill stops referencing an extracted artifact: add a skill-reference
  contract check so the fixture fails.
- Round 2 prompt loses required angles or read-only constraints: add prompt
  contract checks for all three angles, read-only/no GitHub mutation language,
  IDE diagnostics, and Section A / Section B output.
- Round 3 prompt loses confidence, already-fixed, or report-section fields:
  add prompt contract checks for diagnostics ground truth, confidence rules,
  already-fixed handling, and all structured output headings.
- Final template loses degradation or pipeline metadata: add template contract
  checks for review mode, degradation reason, diagnosis pipeline, issue header,
  optional description-mode line, and Round 3 insertion point.
- Extraction accidentally changes behavior: require design review before
  implementation and run release gate plus strict full gate before considering
  the item done.

### Rollout / Migration

Land as one atomic local diff. There is no migration for users because the
public skill name, arguments, workflow phases, and final output contract remain
unchanged. If the extraction proves wrong, reverting the single diff restores
the previous inline skill body.

### Test Strategy Hooks

The implementation should add these exact fixture checks to
`tests/agent-playbook-eval-fixtures.py`:

| Check ID | Relative path | Required invariant groups |
|---|---|---|
| `evaluate-issue-extracted-reference-contract` | `issue-evaluator/skills/evaluate-issue/SKILL.md` | references `evaluate-issue-round2-adversarial.md`, `evaluate-issue-round3-synthesis.md`, and `evaluate-issue-final-report.md`; requires missing/empty prompt/template terminal stop; forbids reconstructing or improvising missing prompt text |
| `evaluate-issue-round2-prompt-contract` | `issue-evaluator/prompts/evaluate-issue-round2-adversarial.md` | `ROOT_CAUSE`, `FIX_PLAN_TESTABILITY`, `REGRESSION_SCOPE`; read-only/no file edit/no GitHub mutation constraints; Issue Details, Code Style Guide, `ROUND_1_PRIMARY`, `ROUND_1_INDEPENDENT`, `ROUND_1_DIAGNOSTICS`; IDE diagnostics as facts; Section A: Independent Diagnosis; Section B: Evaluation of Round 1; `CONFIRMED`, `DISPUTED`, `INCOMPLETE`; already-fixed commit-sha handling |
| `evaluate-issue-round3-prompt-contract` | `issue-evaluator/prompts/evaluate-issue-round3-synthesis.md` | runtime-aware multi-pass synthesis role; IDE diagnostics as ground truth; 3+ independent sources and 2 independent sources confidence rules; disagreement tie-break by reading code; already-fixed verification; Status, Root Cause, Reproduction, Suggested Fix, Risks & Edge Cases, Disputed & Resolved, Affected Files |
| `evaluate-issue-final-template-contract` | `issue-evaluator/templates/evaluate-issue-final-report.md` | `## Issue Evaluation: <issue-title>`; issue number field; optional description-based evaluation mode line; review mode; degradation reason; diagnosis pipeline text; Round 3 structured output insertion point |

The implementation may also add a `ForbiddenPatternCheck` on
`issue-evaluator/skills/evaluate-issue/SKILL.md` for the old full inline prompt
openers, such as `Adversarial review of issue diagnosis for issue #...`
and `You are the final synthesis agent`, as long as the skill still has brief
phase instructions and artifact references.

Verification commands:

- `python3 -m py_compile tests/agent-playbook-eval-fixtures.py`
- `bash tests/agent-playbook-eval-fixtures.sh`
- `git diff --cached --name-only -- issue-evaluator/skills/evaluate-issue/SKILL.md issue-evaluator/prompts/evaluate-issue-round2-adversarial.md issue-evaluator/prompts/evaluate-issue-round3-synthesis.md issue-evaluator/templates/evaluate-issue-final-report.md tests/agent-playbook-eval-fixtures.py`
- `git diff --name-only -- issue-evaluator/skills/evaluate-issue/SKILL.md issue-evaluator/prompts/evaluate-issue-round2-adversarial.md issue-evaluator/prompts/evaluate-issue-round3-synthesis.md issue-evaluator/templates/evaluate-issue-final-report.md tests/agent-playbook-eval-fixtures.py`
- `scripts/release-gate.sh --mode staged --strict`
- `scripts/release-gate.sh --mode all --strict`

The staged-name check must list all intended implementation files in the index.
The unstaged-name check must be empty for those same paths before treating the
staged strict gate as authoritative. Focused grep checks from requirements may
be used as local smoke tests, but fixture checks are the authoritative
regression guard.

## Staged Implementation Plan

1. **Stage 1 - Extract and Guard Evaluate-Issue Prompts**: One shippable stage
   with red-green verification substeps:
   - **Stage 1A - Red fixture gate**: add the
     `tests/agent-playbook-eval-fixtures.py` checks above before extracting the
     prompt files. The targeted fixture command should fail because the new
     artifacts are still missing.
   - **Stage 1B - Verbatim extraction**: copy the current Round 2, Round 3, and
     Step 4 blocks verbatim into the three new files, then replace the inline
     blocks in `evaluate-issue/SKILL.md` with artifact references and the
     missing/empty terminal stop rule.
   - **Stage 1C - Verification checkpoint**: run `py_compile`, the
     agent-playbook fixtures, staged file-scope checks, the staged strict
     release gate, and the full strict release gate. The stage is complete only
     when all pass and no touched implementation file has unstaged remainder.

## Open Questions

- None blocking. The architecture intentionally resolves the fixture-location
  question in favor of the existing `agent-playbook-eval-fixtures` path.
