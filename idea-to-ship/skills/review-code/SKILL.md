---
name: review-code
description: Risk-scaled code review of the current diff with auto-selected or forced review depth. Supports --review-depth quick|standard|deep; when findings require edits, generates a Plannotator modification plan before applying approved critical/high fixes and re-reviewing.
argument-hint: '[--slug <name>] [--review-depth quick|standard|deep] [extra focus]'
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent]
---

# Review Code — Adversarial Review Loop For Implementation

Run a risk-scaled review of staged and unstaged code changes. Select
`review_intensity` automatically unless `--review-depth quick|standard|deep`
forces it. Findings that require code, test, architecture, or design artifact
edits become a Plannotator modification plan before edits; after approval or
`bypassed-current-conversation`, apply only approved critical/high bug or
design-drift fixes and re-review until no critical/high bugs remain. Anchor the
review to requirements, architecture, interface design, implementation log, and
test plan so drift and missing verification are caught.

## Arguments

Parse:
- Optional `--slug <name>`. Default slug: `current`.
- Optional `--review-depth quick|standard|deep`. If present, force that
  intensity and record it in `code-review.md`.
- Remaining text → extra focus areas (e.g. "concurrency", "error handling", "SQL injection").

## Multi-Agent Review Routing

Read `../../PRINCIPLES.md` and `../../WORKFLOW-CONTRACTS.md`. Apply the shared
**Review Intensity Selection** and **Multi-Agent Review Routing** contracts.
Launch independent reviewer agents for selected `standard` and `deep`; for
selected `quick`, run the same-context checklist from the shared contract and
do not label it degraded.

- **Correctness/security angle:** bugs, data loss, concurrency, auth, injection, serialization, shell.
- **Traceability/testability angle:** requirement/story/acceptance/scenario/test trail, TDD evidence, regression coverage.
- **Maintainability/repo-fit angle:** local conventions, abstraction cost, dead code, design drift, surgical scope.
- **UI/UX angle:** required when `interface-design.md` exists or the diff touches UI; checks component, visual token, interaction-state, responsive, accessibility, and visual QA expectations.

If reviewer sub-agents are explicitly unsupported by the host/runtime, the user
explicitly forbids reviewer sub-agents, or the selected reviewer/model is
explicitly unavailable or at capacity, write `code-review.md` with `Result:
degraded-same-context-review`, record the exact reason, and run the same
adversarial review prompts in the main context.

## Plannotator Modification Plan Gate

Apply `../../WORKFLOW-CONTRACTS.md` Review Finding Severity And Fix Policy,
Review Loop Shape, and Human Approval Routing. Write
`.idea-to-ship/<slug>/code-review-modification-plan.md` before edits with
finding id/severity/path/source angle, must-fix status, planned edits,
verification/re-review, user-owned decisions, deferred Known Issues, and
skipped findings. If current-conversation approval bypass is active, record
`bypassed-current-conversation`; bypass skips approval, not planning. Treat
Plannotator approval or bypass as authorization that the planned solution is
the correct solution to apply. If Plannotator is unavailable and no bypass is
active, record that in `code-review.md` and stop without editing.

## Workflow

Track status after input verification, each reviewer iteration, plan
generation/application, final holistic review, and `code-review.md` handoff.

```mermaid
flowchart TD
  A[Review Diff] --> B{Plan Approved?}
  B --> C[Fix Critical/High And Re-Review]
```

### Step 1: Verify Inputs

1. Resolve `.idea-to-ship/<slug>/`. Require `requirements.md`; if missing,
   stop and tell the user to run `/brainstorm --slug <slug>` first. Read
   `requirements.md` and any present `architecture.md`, `interface-design.md`,
   `implementation-log.md`, `test-plan.md`, `visual-test-report.md`,
   `visual-test-matrix.md`, `visual-artifact-rca.md`, and `visual-test-selectors.md`.
2. Check for a diff:
   ```bash
   git diff --shortstat
   git diff --shortstat --cached
   git status --short
   ```
   If empty, tell the user there's nothing to review and stop.
3. If `test-plan.md` is absent, retain that review context. If a UI-touching
   diff lacks `visual-test-report.md` or `visual-test-matrix.md`, set
   `VISUAL_TEST_REPORT_MISSING` or `VISUAL_TEST_MATRIX_MISSING`.
4. Build bounded reviewer context with artifact paths/anchors. Cap requirements,
   architecture, implementation log, and test plan at 200 lines or 16 KiB each;
   cap combined visual evidence at 24 KiB. Set `context_truncated: true` and
   list omissions when truncating.

### Step 2: Collect The Diff

```bash
git status --porcelain=v1 -z --untracked-files=no
git diff --binary --full-index --no-ext-diff --no-color
git diff --cached --binary --full-index --no-ext-diff --no-color
git ls-files --others --exclude-standard -z
```

Capture unstaged and staged diffs separately. This is the review target.

For binary tracked changes, include path and SHA-256 summaries in the review
payload instead of raw binary patches. Use full binary diffs only as hash input
for `workspace_diff_fingerprint`, not as reviewer context.

When visual-test artifacts exist or the diff touches UI, compute the current
`workspace_diff_fingerprint` with the same contract as `$idea-to-ship:visual-test`:
tracked porcelain status, full binary staged and unstaged diffs, and a sorted
`untracked_files_manifest` from `git ls-files --others --exclude-standard -z`,
excluding the current slug's visual evidence artifacts
(`visual-test-selectors.md`, `visual-test-matrix.md`, `visual-artifact-rca.md`,
and `visual-test-report.md`) from the fingerprint hash input.
Every untracked file must be classified as a content-hashed relevant input or
excluded with rationale. If the fingerprint cannot be computed, treat that as a
visual evidence gap rather than "fresh." If it differs from
`visual-test-report.md`, flag stale fingerprint evidence.

Include bounded untracked file evidence in the review payload when those files
are relevant to the diff or fingerprint: text file contents with path and
truncation note, and binary files as path plus SHA-256 only. Sensitive
auth/session/cookie/token/log/env-like untracked files must never be included as
raw text; represent them as path + SHA-256 + redacted summary only. Run
secret-scan or equivalent redaction before including any untracked text content.
Do not let an untracked file affect freshness without giving reviewers either
safe text content, a redacted sensitive summary, or its binary hash.

Keep untracked text bounded: cap each text file excerpt at 200 lines or 8 KiB
and cap total untracked text at 32 KiB. Include path, SHA-256, classification,
and `truncated: true|false` for every relevant untracked entry. If the text diff
is too large for one reviewer prompt, split review assignments by path group and
include a complete changed-path manifest plus omitted-hunk notes.

If `test-plan.md` is absent and the diff changes observable behavior, set
`TEST_PLAN_MISSING=true`. This is review context, not an automatic failure: the
reviewer must flag it as a verification gap unless the implementation log or
current request documents why no test plan is applicable.

If the diff touches UI, set `UI_DIFF=true`. If `UI_DIFF=true` and
`visual-test-report.md` is absent, set `VISUAL_TEST_REPORT_MISSING=true`. If
`UI_DIFF=true` and `visual-test-matrix.md` is absent, set
`VISUAL_TEST_MATRIX_MISSING=true`. Either flag is missing visual evidence and
reviewers must report it. If visual-test artifacts exist, compare the current
`workspace_diff_fingerprint` to the report; stale fingerprint evidence must be
flagged. Reviewers must also flag missing matrix evidence, unresolved visual
failures, missing baseline approval, weak artifact anchors, and unjustified
console/network failures.

### Step 3: Select Review Intensity

Apply `../../WORKFLOW-CONTRACTS.md` Review Intensity Selection using the current
diff, artifacts, and user arguments:

- Auto-select `quick`, `standard`, or `deep` by risk.
- Honor `--review-depth quick|standard|deep` as a forced override.
- Record `Review intensity: <tier> (<auto|forced>: <reason>)` in
  `code-review.md`.
- Escalate if a lower tier discovers security, data-loss, external-IO,
  persistence, public-contract, UI visual-evidence, or broad-scope risk.

### Step 4: Review Loop

Track iteration count starting at 1. `deep` maxes at 5 iterations; `quick` and
`standard` use the caps in `../../WORKFLOW-CONTRACTS.md`.

#### 4a — Multi-Agent Review

For `quick`, run one same-context checklist over correctness/security,
traceability/testability, and maintainability/repo-fit. If it finds issues that
require edits, generate a Plannotator modification plan before editing.

For `standard`, launch the required reviewer agents in parallel when possible
for one multi-angle round. If findings require edits, generate a Plannotator
modification plan. After approval, apply only planned critical/high fixes and
re-review affected angles unless the change affects architecture, public
contracts, security, data flow, UI evidence, or broad scope.

For `deep`, launch the required reviewer agents in parallel when possible. Each reviewer
gets the shared prompt plus its assigned angle. If fewer than the required
reviewer agents can run because reviewer sub-agents are explicitly unsupported
by the host/runtime, explicitly forbidden by the user, or the selected
reviewer/model is explicitly unavailable or at capacity, continue as
`degraded-same-context-review` using the same prompts in the main context and
record the reason.

```
Adversarial code review (iteration <N>, angle: <angle>). Be blunt, skeptical,
no hedging. Find real bugs, security holes, bad abstractions, and wrong code
within your assigned angle.

SCOPE RULES (important):
- Only report issues within the lines changed in this diff.
- Do NOT flag lint/style/format issues in unchanged surrounding code.
- Within the diff, only flag style if the change introduces NEW inconsistency
  with what's already in this repo. Do not flag pre-existing patterns the diff
  happens to touch.
- Check the diff against the architecture. If the implementation deviates from
  the design in a way the implementation-log does not justify, flag it as a
  "design drift" issue.
- If `interface-design.md` is provided and the diff touches UI, check component
  choices, visual tokens, interaction states, responsive behavior,
  accessibility, and visual QA expectations against it. Undocumented
  divergence is design drift.
- If the diff touches UI and either `VISUAL_TEST_REPORT_MISSING` or
  `VISUAL_TEST_MATRIX_MISSING` is true, flag missing visual evidence. If visual
  artifacts are provided, check `aggregate_verdict`, `blocking_reasons`,
  `visual-test-matrix.md`, `visual-artifact-rca.md`, and
  `visual-test-selectors.md`. Flag stale fingerprint evidence, missing matrix
  evidence, unresolved `FAIL`, `FLAKY`, `MISS`, or `NEEDS-RUN` cells,
  non-de-scoped `SKIP-with-reason`, missing baseline approval, weak artifact
  anchors, unclassified untracked files, and unjustified console/network
  failures.
- Check the diff against the test plan. If a behavior-changing implementation
  lacks traceability from requirement -> story -> acceptance criterion ->
  scenario -> test, flag it as a verification gap. For fixes or user-visible
  behavior, missing tests are medium; for bug fixes with no reproducible
  regression test, upgrade to high unless there is a documented reason.
- If `test-plan.md` is not provided and the diff changes observable behavior,
  flag a medium verification gap. For bug fixes without a reproducible
  regression test, upgrade to high unless there is a documented reason.
- Use exactly these severity labels: `critical`, `high`, `medium`, `low`,
  `nit`. Only concrete bugs, verification blockers, security issues, data
  loss, primary-flow regressions, or technical design defects can be
  `critical` or `high`. Style, preference, speculative cleanup, and generalized
  advice must be `low`/`nit` or dropped.
- Mark a `critical`/`high` finding as must-fix only when it is a true bug,
  verification blocker, or design defect. If a `high`/`medium` issue is an
  extreme edge case or its fix has disproportionate scope/regression risk,
  explicitly say whether it is eligible for Known Issue deferral and why.

## Requirements (required context)
<requirements.md>

## Architecture (context, may be empty)
<architecture.md or "not provided">

## Interface Design (context, may be empty)
<interface-design.md or "not provided">

## Implementation Log (context, may be empty)
<implementation-log.md or "not provided">

## Test Plan (context, may be empty)
<test-plan.md or "not provided">

## Visual Test Evidence (context, may be empty)
Report: <path plus bounded summary/anchors, or "not provided">
Matrix: <path plus status counts and affected cell summaries, or "not provided">
Artifact RCA: <path plus bounded summaries/anchors, or "not provided">
Selectors: <path plus selector/state summary, or "not provided">
UI-touching diff: <true|false>
Missing visual evidence: <true|false>
Current workspace_diff_fingerprint: <fingerprint or VISUAL_EVIDENCE_GAP when not computed>
context_truncated: <true|false; include omitted paths/sections when true>

## Extra Focus From User
<extra focus text, or "none">

## Diff To Review
<full text diff when within budget, otherwise complete changed-path manifest plus focused hunks>
<bounded relevant untracked file contents with SHA-256/classification/truncation, or binary path + SHA-256>

For each issue, report severity, file:line, concrete problem/impact, and
concrete fix. Also state `must_fix: yes|no` and, when relevant,
`known_issue_deferral: eligible|not eligible` with the ROI rationale.

If no material issues exist for your assigned angle, reply with exactly: LGTM
```

#### 4b — Evaluate & Plan

- **LGTM from every required reviewer angle** and no remaining
  `critical`/`high` bugs or design defects → break, proceed to Step 5.
- Otherwise:
  1. One-line summary: `Iteration N: <angle> C critical, H high, M medium, L low, N nits (S skipped out-of-scope).`
  2. Filter before planning:
     - Drop issues that are pure style/format in code the diff did not actually change.
     - Drop `low`/`nit` issues unless they are part of the same necessary change.
     - Keep true `critical`/`high` bugs, verification blockers, and
       design-drift defects as must-fix findings.
     - Record eligible low-ROI `high`/`medium` findings as Known Issues only
       when they do not affect the primary path and the rationale includes
       severity, ROI, primary-path impact, and future trigger.
  3. Generate `.idea-to-ship/<slug>/code-review-modification-plan.md` using
     the Plannotator Modification Plan Gate. Do not touch unrelated code and
     do not edit the reviewed files here.
  4. If a fix requires a user decision (tradeoff, spec ambiguity), put the
     decision and options in the plan. Do not guess.
  5. Stop before edits unless Plannotator approval or
     `bypassed-current-conversation` approval is recorded.

#### 4c — Approval Boundary

If the plan is approved in the same conversation, including by
`bypassed-current-conversation`, treat implementation of that plan as the
approved modification pass. Apply only the approved `critical`/`high` bug,
verification-blocker, and design-defect fixes. Do not apply medium/low/nit
cleanup unless required by an approved critical/high fix.

After edits, run the appropriate review again. For `deep`, re-run every required reviewer angle
after the approved changes land. If fresh review finds new `critical`/`high`
bugs or design defects, append them to the modification plan and require
Plannotator approval unless the current-conversation bypass is active. With
bypass, record that the bypass covers the new plan entries and continue. Repeat until `Remaining critical/high bugs: none` can be recorded.

### Step 5: Final Holistic Pass

After LGTM, or after an approved plan has been applied and re-reviewed, run the
holistic pass required by the selected intensity:

1. Re-read `git diff HEAD`, `git diff --cached`, and the plan when present.
2. Check requirements, architecture, public interfaces, security boundaries,
   dead code, test traceability, and `../../PRINCIPLES.md`.
3. If new `critical`/`high` problems appear, add them to the Plannotator
   modification plan and return to the Approval Boundary. Record eligible
   low-ROI `high`/`medium` problems as Known Issues. Do not finish until
   remaining critical/high bugs are `none`.

### Step 6: Write `code-review.md`

```markdown
# Code Review — <slug>

**Date:** <YYYY-MM-DD>
**Reviewer:** multi-agent: <angle -> reviewer route>
**Iterations:** <N>
**Result:** <clean | accepted-with-open-issues>
**Review intensity:** <quick|standard|deep> (<auto|forced>: <reason>)
**Mode:** <selected-quick-same-context | multi-agent | degraded-same-context-review>
**Degradation reason:** <none | explicit unsupported runtime | user forbade reviewer sub-agents | reviewer/model unavailable or at capacity>
**Diff size:** <files changed>, <+added/-removed>
**Plannotator modification plan:** <path | not needed | unavailable>
**Plan approval:** <approved | denied | pending | bypassed-current-conversation | not needed | unavailable>
**Critical/high bugs fixed:** <count and finding ids | none>
**Remaining critical/high bugs:** <none | list with blocker status>

## Issues Raised & Resolution
| # | Severity | File:line | Issue | Planned action / status |
|---|---|---|---|---|
| 1 | critical | src/x.go:42 | ... | planned in code-review-modification-plan.md §... |

## Known Issues Deferred
| # | Severity | File:line | Issue | ROI rationale | Primary-path impact | Future trigger |
|---|---|---|---|---|---|---|
| 1 | medium | src/x.go:88 | ... | fix would broaden scope beyond current release | no primary path impact | fix when feature X is expanded |

## Out-of-Scope Issues Skipped
<Pre-existing style nits etc., for visibility — not planned.>

## Design Drift
<Any place the implementation departed from architecture.md or
interface-design.md, and whether it is planned for implementation fix,
artifact update, accepted documented deviation, or clean.>

## Test Traceability
<Requirement/story/acceptance/scenario/test gaps. Include missing happy path,
edge/corner case, invalid-input, or failure-mode coverage. Empty if clean.>

## Residual Open Issues
<Non-critical/high residuals only, or empty if clean.>

## Final Verdict
| Angle | Verdict |
|---|---|
| correctness/security | LGTM / ... |
| traceability/testability | LGTM / ... |
| maintainability/repo-fit | LGTM / ... |
| UI/UX | LGTM / not applicable / ... |
```

### Step 7: Hand-off

1. Tell the user where `code-review.md` landed and where the plan landed, if
   any.
2. Suggest next step: approve a pending plan, fix a blocking approval denial,
   run `/test` if tests are incomplete, or commit/open PR once remaining
   critical/high bugs are none.
3. Do not commit or push.

## Related Skills

- `$idea-to-ship:visual-test`, `$idea-to-ship:test`, and `$idea-to-ship:implement` produce the evidence this review consumes.

## Anti-Patterns

- **Style nitpicking on logic PRs.** If the diff fixes a race condition, don't produce 15 nits about naming. Focus severity appropriately — a few nits alongside critical/high bugs is fine, but nits should never dominate a review that has real issues.
- **Phantom bugs.** "This *could* be null" without checking if callers actually pass null. If you can't show a concrete call path that triggers the failure, it's speculation, not a finding. State the call path or drop the finding.
- **Reviewing the architecture.** If the chosen design is wrong, that's a design review problem. Code review assumes the design is accepted and checks whether the implementation is correct, safe, and clean. Flag design drift, but don't re-litigate architectural decisions.
- **Generic advice.** "Add error handling" without saying what error, from where, and what the handler should do. Every finding must be actionable and specific enough to implement in one edit.
- **Trusting implementation without traceability.** If a behavior changed and
  there is no story/acceptance/scenario/test trail, the implementation is not
  verifiably done. Flag the missing link instead of saying "looks fine".
