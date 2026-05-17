# Architecture - Frontend Visual Testing And Orchestration Intake

**Slug:** ITS-ROADMAP-016-020
**Date:** 2026-05-17
**Status:** implemented
**References:** requirements.md

## Summary

Add `$idea-to-ship:visual-test` as a gate-driven, artifact-first visual QA
workflow and keep the repo orchestration idea as a bounded spike artifact. The
chosen design adds one new idea-to-ship skill, four reusable templates, updates
`review-code` to consume visual-test evidence, README/catalog entries, and
static fixture coverage. It deliberately avoids runtime Playwright tooling and
avoids a broad repo orchestrator.

## Goals / Non-Goals

Goals:

- Provide a concrete workflow for visual verification after frontend changes.
- Make selector/state recipes, visual matrix status, screenshot report output,
  and large-artifact RCA reusable through templates.
- Keep visual baselines explicit and reviewable.
- Preserve existing idea-to-ship ownership: `ui-design` defines UI contracts,
  `test` owns story matrices, `review-code` reviews diffs, and `visual-test`
  collects visual evidence.
- Make visual-test evidence fresh enough for review: every matrix cell must
  state when and against what commit/range it was verified, or why a prior pass
  can carry forward.
- Evaluate orchestration/bootstrap as a spike, not a shipped broad skill.

Non-goals:

- No Playwright installation, package scripts, browser execution, or generated
  screenshot baselines in this repo.
- No new `frontend` plugin.
- No new all-purpose repo orchestrator, self-replication, auto-commit, push,
  GitHub write, deployment mutation, or plugin installation behavior.

## Codebase Context

- `idea-to-ship/skills/*/SKILL.md` contains the existing stage skills. New
  workflow skills live under `idea-to-ship/skills/<slug>/SKILL.md` with optional
  `agents/openai.yaml` metadata.
- `idea-to-ship/templates/` already stores reusable report and artifact
  templates. This is the right home for visual report, selector/state, matrix,
  and artifact-RCA structures.
- `idea-to-ship/skills/review-code/SKILL.md` already owns UI/UX review when
  `interface-design.md` exists or the diff touches UI; it must read
  visual-test artifacts so this evidence is not orphaned.
- `tests/idea-to-ship-eval-fixtures.py` owns static contract checks for
  idea-to-ship skills and templates.
- `tests/agent-playbook-eval-fixtures.py` owns static contract checks for
  agent-playbook boundaries and can guard against broad repo-orchestrator drift.
- `scripts/skill-hygiene-check.py` now checks new/changed skills for actionable
  usage, task tracking, workflow diagrams, related skills, command safety, and
  metadata.
- `scripts/skill-topology-scan.py` checks broken related-skill refs and README
  catalog gaps, so README entries and valid `Related Skills` are required.

## Cross-Skill Routing

| Signal | Routed skill | Result | Design impact |
|---|---|---|---|
| Visual-test workflow produces generated examples, command snippets, reports, and artifact paths. | `secret-scanner:scan-secrets` during implementation | Run working-tree scan after edits. | Avoid hardcoded credentials and ensure templates do not normalize secret dumping. |
| Roadmap item 020 concerns repo orchestration, bootstrap, phased plans, and self-replication risk. | `agent-playbook` boundary review via code review and fixture guards | Do not run a mutating orchestration workflow. | Deliver a spike artifact and static boundary fixture instead of a new orchestrator skill. |

## Alternatives Considered

### Option A - Add `idea-to-ship:visual-test` Plus Templates And 020 Spike

Add one new idea-to-ship skill, four templates, README entries, fixture
coverage, and `.idea-to-ship/ITS-ROADMAP-020/orchestration-spike.md`.

**Module changes:** `idea-to-ship/skills/visual-test/*`,
`idea-to-ship/skills/review-code/SKILL.md`,
`idea-to-ship/templates/visual-test-*.md`,
`idea-to-ship/templates/visual-artifact-rca.md`, `README.md`,
`idea-to-ship/README.md`, `tests/*-eval-fixtures.py`, and idea-to-ship
artifacts.

**Data flow:** user invokes `$idea-to-ship:visual-test` -> skill reads
`requirements.md`, `interface-design.md`, optional `test-plan.md`, and project
tooling -> creates/updates selector recipe, matrix, report, and artifact-RCA
files under `.idea-to-ship/<slug>/` -> user or review-code consumes report.

**Interfaces:** no new executable command beyond the skill invocation; templates
define Markdown contracts.

**Pros:** Small blast radius; aligns with existing artifact-first flow; directly
addresses 016-019 through skill/template/review-code contracts; keeps 020 safe.

**Cons:** Does not run screenshots by itself; depends on project Playwright or
browser tooling when used in real frontend repos. It must be strict about matrix
freshness and baseline approval or the report can become plausible but stale.

**Risk:** Low-medium; main risks are vague workflow gates, stale carry-forward
evidence, and unreviewed baseline changes. The design closes those with
required gate names, fields, and fixtures.

### Option B - Create A New `frontend` Plugin

Create a standalone frontend plugin with `visual-test`, selector recipes,
Playwright RCA, and matrix loops.

**Module changes:** new plugin folder, marketplace metadata, README section,
fixtures, and templates.

**Data flow:** frontend plugin owns visual QA independently from idea-to-ship.

**Interfaces:** new `$frontend:visual-test` skill.

**Pros:** More reusable outside idea-to-ship.

**Cons:** More packaging work; weaker integration with `interface-design.md`;
larger release and review surface.

**Risk:** Medium; premature plugin boundary could duplicate existing UI gates.

### Option C - Add A Broad Repo Orchestrator

Implement a repo-bootstrap/orchestration skill inspired by Kagenti, including
phased enhancement plans and potentially test/CI/security phases.

**Module changes:** likely `agent-playbook/skills/orchestrate/*`, templates,
state tracking, and many fixture checks.

**Data flow:** orchestrator scans target repo -> plans phases -> modifies repo.

**Interfaces:** new `$agent-playbook:orchestrate` or similar.

**Pros:** Could eventually cover repo enablement workflows.

**Cons:** Directly conflicts with existing skill ownership and is not required
to complete visual-test work. High risk of becoming a broad autopilot.

**Risk:** High; reject for this roadmap batch.

## Recommendation

**We pick Option A.** It completes 016-019 with one focused visual-test workflow
and completes 020 as a spike decision with boundary fixtures. This is the
smallest reversible design that fits the current repo and the roadmap's
explicit warning not to copy Kagenti self-replication wholesale.

## Chosen Design - Detail

### Module Breakdown

- `idea-to-ship/skills/visual-test/SKILL.md` - new visual QA workflow.
- `idea-to-ship/skills/visual-test/agents/openai.yaml` - runtime metadata.
- `idea-to-ship/skills/review-code/SKILL.md` - load visual-test artifacts when
  present or when UI is touched; reviewer prompt must check matrix status,
  unresolved visual failures, baseline approval, artifact anchors, and missing
  visual evidence.
- `idea-to-ship/templates/visual-test-report.md` - handoff report template.
- `idea-to-ship/templates/visual-test-selectors.md` - selector/state recipe.
- `idea-to-ship/templates/visual-test-matrix.md` - matrix status template.
- `idea-to-ship/templates/visual-artifact-rca.md` - bounded large-artifact RCA
  template.
- `README.md` and `idea-to-ship/README.md` - discoverability and workflow docs.
- `tests/idea-to-ship-eval-fixtures.py` - contract checks for the skill,
  metadata, templates, visual-test hard gates, review-code visual artifact
  consumption, hygiene/topology prerequisites, and README coverage.
- `tests/agent-playbook-eval-fixtures.py` - static guard that the 020 spike
  stays artifact-only and rejects broad orchestrator capabilities.
- `.idea-to-ship/ITS-ROADMAP-020/orchestration-spike.md` - spike verdict.

### Data Flow

```
requirements.md + interface-design.md + optional test-plan.md + current diff
  -> visual-test skill resolves app/tooling and output directory
  -> selector/state recipe records route selectors, auth/session, states
  -> matrix derives required cells from Visual QA Plan and UI test-plan rows
  -> matrix records freshness fields for each cell
  -> test runner or manual user captures screenshots/traces in project tooling
  -> artifact RCA summarizes large Playwright/CI artifacts by file/line anchors
  -> visual-test report links selectors, matrix, screenshots, baselines, RCA
  -> review-code consumes report for UI/UX and test-traceability verdicts
```

### Interfaces

Skill invocation:

```text
$idea-to-ship:visual-test --slug <name> [--baseline compare|create-requested|update-requested] [app root or URL notes]
```

Canonical output paths for a target slug:

```text
.idea-to-ship/<slug>/visual-test-selectors.md
.idea-to-ship/<slug>/visual-test-matrix.md
.idea-to-ship/<slug>/visual-artifact-rca.md
.idea-to-ship/<slug>/visual-test-report.md
```

Matrix statuses:

- `PASS`: required assertions and screenshot comparison passed.
- `FAIL`: assertion, screenshot diff, console/network, or state setup failed.
- `FLAKY`: same code/config alternates between pass and fail.
- `MISS`: required cell has no evidence; never counts as success.
- `SKIP-with-reason`: intentionally skipped with owner-visible reason.
- `NEEDS-RUN`: evidence might exist but cannot safely carry forward because
  relevance to the current diff is uncertain.

Matrix cell required fields:

- `cell_id`
- `source_ids` from `interface-design.md` Visual QA Plan and/or `test-plan.md`
  UI scenario rows
- `required` (`yes` / `no`)
- `route_or_screen`
- `state`
- `viewport`
- `theme`
- `browser_or_project`
- `assertion_command`
- `screenshot_path`
- `baseline_path`
- `artifact_rca_link`
- `status`
- `verified_at`
- `source_commit`
- `comparison_range`
- `git_status_snapshot`
- `workspace_diff_fingerprint`
- `changed_paths_reviewed`
- `relevant_paths_or_config`
- `carry_forward_allowed`
- `carry_forward_rationale`
- `console_status`
- `network_status`
- `ignored_console_network_justification`
- `console_network_rca_link`
- `owner_or_approver`

Carry-forward rule:

- A prior `PASS` may carry forward only when the report records the previous
  report path, prior `cell_id`, previous `source_commit`, current
  `comparison_range`, `git_status_snapshot`, `workspace_diff_fingerprint`,
  changed paths reviewed, and a concrete rationale that none of the changed
  files, route/state definitions, UI components, CSS/assets, test data, browser
  config, Playwright config, or baseline files can affect the cell.
- The workflow computes `workspace_diff_fingerprint` from content, not stats:
  SHA-256 over normalized tracked-file status from
  `git status --porcelain=v1 -z --untracked-files=no`,
  `git diff --binary --full-index --no-ext-diff --no-color`, and
  `git diff --cached --binary --full-index --no-ext-diff --no-color`, plus an
  `untracked_files_manifest` from `git ls-files --others --exclude-standard -z`.
  The manifest is sorted by path after NUL-safe decoding and classifies every
  untracked file, including files inside nested untracked directories, as either
  a content-hashed relevant input or an excluded path with rationale. Relevant
  untracked files and visual-affecting config/baseline files named in
  `relevant_paths_or_config` must include path names and SHA-256 file-content
  hashes. Unclassified untracked files block aggregate `PASS` and `review-code`
  handoff. `review-code` must compare the current fingerprint to the report and
  invalidate visual evidence when it differs.
- If relevance cannot be proven, the cell becomes `NEEDS-RUN` or `MISS`, never
  carried as `PASS`.
- `FLAKY`, `FAIL`, `MISS`, and `SKIP-with-reason` cannot be converted to `PASS`
  without fresh evidence.

Baseline modes:

- `compare` is default. If an approved baseline is missing, required cells become
  `MISS` or the workflow returns `needs_user`.
- `create-requested` writes an approval request record; it does not bless the
  current UI unless approval is already documented.
- `update-requested` writes a request with before/after artifacts and rationale;
  it never updates baselines silently.
- Approval record fields: approver/source, date, baseline path, diff summary,
  before artifact, after artifact, linked matrix cells, and rationale. The
  visual-test agent cannot self-approve.

Console/network status values:

- `PASS`: collected and no blocking errors were observed.
- `FAIL`: collected and blocking console or network errors remain unresolved.
- `NOT_COLLECTED`: the signal was not collected; this blocks aggregate `PASS`
  and yields `NEEDS_USER`.
- `IGNORED-with-justification`: collected failures are accepted as non-blocking
  only when `ignored_console_network_justification`,
  `console_network_rca_link`, and an owner/source are present. Missing
  justification, missing RCA, or unknown status blocks aggregate `PASS`.

Artifact RCA required fields:

- artifact path or URL
- source command or CI job
- test id/title
- project/browser
- retry index
- trace step/action or screenshot/video filename when applicable
- timestamp
- inspected anchor range, line range, or byte range
- snippet cap used
- redaction notes
- linked matrix cell IDs
- failure classification
- suspected cause
- next action/status

Raw logs, full HTML reports, traces, videos, screenshots, cookies, auth state,
or secret-bearing snippets must not be pasted into the report.

`visual-test-report.md` required report-level fields:

- `aggregate_verdict`
- `blocking_reasons`
- `matrix_status_counts`
- `required_cell_status_counts`
- `workspace_diff_fingerprint`
- `git_status_snapshot`
- `untracked_files_manifest`
- `baseline_approval_summary`
- `console_status`
- `network_status`
- `console_network_summary`
- `artifact_rca_summary`
- `next_action`

Report-level `console_status` and `network_status` summarize the worst matrix
cell value: any cell `FAIL` makes the report-level field `FAIL`; any
`NOT_COLLECTED` keeps the report from aggregate `PASS`; any
`IGNORED-with-justification` keeps the report from aggregate `PASS` unless the
required justification and RCA fields are complete.

Report-level `aggregate_verdict` allowed values:

| Condition | Verdict |
|---|---|
| Every required cell is `PASS`, each pass is fresh or a valid carried-forward `PASS` under the carry-forward rule, the current `workspace_diff_fingerprint` matches, baselines are approved, artifact RCA has no unresolved blockers, and report-level console/network status is `PASS` or complete `IGNORED-with-justification` | `PASS` |
| Any required cell is `FAIL` or `FLAKY`, report-level `console_status` or `network_status` is `FAIL`, or artifact RCA identifies an unresolved product/test failure | `FAIL` |
| Any required cell is `MISS`, `NEEDS-RUN`, or `SKIP-with-reason` without an explicit de-scope approval/source, or the fingerprint is stale, baseline approval is missing, unclassified untracked files exist, console/network status is `NOT_COLLECTED`, or console/network ignored status lacks justification/RCA/owner | `NEEDS_USER` |

`SKIP-with-reason` is non-success for required coverage. A skipped source can
coexist with aggregate `PASS` only after it is explicitly de-scoped from required
coverage with approver/source and rationale; otherwise it yields `NEEDS_USER`.

Visual-test ordered gates:

1. **Gate 1 - Input Contract:** resolve slug, `requirements.md`,
   `interface-design.md` when available, optional `test-plan.md`, app root/URL,
   and baseline mode. Missing design contract downgrades compliance claims.
2. **Gate 2 - Tooling Discovery:** detect Playwright/Storybook/browser tooling
   or record manual evidence mode; do not invent commands.
3. **Gate 3 - Selector/State Readiness:** write/update selector/state recipe
   with stable role/test-id selectors, auth/session notes, route preconditions,
   loading completion, and known flaky states.
4. **Gate 4 - Matrix Derivation:** derive required matrix cells from
   `interface-design.md` Visual QA Plan and `test-plan.md` UI rows; every
   required source maps to a required cell or an explicit de-scope decision with
   approver/source and rationale. `SKIP-with-reason` alone is not success for
   required coverage.
5. **Gate 5 - Assert Before Capture:** every screenshot cell names the assertion
   that proves the route/state is ready before capture.
6. **Gate 6 - Capture And Compare:** record screenshot and baseline paths,
   console/network status, ignored-console/network justification when any issue
   is intentionally accepted, RCA links for unresolved noise, baseline approval
   mode, `git_status_snapshot`, and `workspace_diff_fingerprint`.
7. **Gate 7 - Artifact RCA:** summarize large Playwright/CI artifacts by
   bounded anchors and redaction notes.
8. **Gate 8 - Matrix Closure:** no required cell remains blank; unresolved
   `FAIL`, `FLAKY`, `MISS`, or `NEEDS-RUN` is visible in the final verdict.
   Aggregate verdict may be `PASS` only when every required cell is `PASS`, and
   each pass is fresh or validly carried forward under the carry-forward rule,
   baseline approvals are recorded, current workspace fingerprint matches the
   report, and no console/network or artifact RCA failure is unresolved. Any
   unresolved required cell, non-de-scoped `SKIP-with-reason`, missing approval,
   stale fingerprint, or unjustified console/network failure produces `FAIL` or
   `NEEDS_USER` according to the aggregate verdict table.
9. **Gate 9 - Report Handoff:** write `visual-test-report.md` with
   `aggregate_verdict`, `blocking_reasons`, matrix status counts,
   report-level console/network summary, `workspace_diff_fingerprint`, matrix
   link, approval records, artifact RCA links, residual risk, and next action.

### Data / Schema Changes

No runtime data schema. New Markdown template contracts only.

### Failure Modes & Handling

- Missing `interface-design.md`: visual-test may still run for an explicit user
  visual-check request, but report must mark design-contract source as missing
  and cannot claim interface compliance.
- No Playwright or browser tooling: report `needs_user` or document manual
  evidence; do not invent screenshots.
- Screenshot captured before loaded state: mark the matrix cell `FAIL`.
- Console/network failures: mark `FAIL` unless explicitly classified as known
  non-blocking noise in the report.
- Baseline create/update requested without approval: write approval request,
  stop or mark `needs_user`, and never bless the baseline automatically.
- Compare requested with no approved baseline: required cells become `MISS` or
  `needs_user`.
- Large CI/Playwright report: save or reference files and summarize bounded
  anchors only, with redaction notes.
- Missing matrix cell: `MISS`, not `PASS`.
- Flaky cell: `FLAKY` and requires RCA; do not hide with retries.
- Orchestrator pressure: route to existing bounded skills; do not create
  `agent-playbook/skills/orchestrate/SKILL.md` or a `$agent-playbook:orchestrate`
  entry in this batch.

### Rollout / Migration

Land as additive docs/skill/template/fixture changes, with one required
integration point in this batch: `review-code` must read visual-test artifacts
when present or when UI is touched and must surface unresolved visual evidence.
Other existing workflows remain unchanged. New visual-test use is otherwise
opt-in until a future roadmap item wires it more deeply into UI implementation
stages.

### Test Strategy Hooks

- Static fixture checks assert the skill mentions required inputs, artifacts,
  ordered gates, baseline policy, selector/state recipe, matrix freshness
  fields, console/network justification fields, artifact RCA fields, aggregate
  verdict rules, hygiene prerequisites, and related skills.
- Static fixture checks assert `review-code` reads visual-test artifacts and
  flags unresolved visual evidence, stale `workspace_diff_fingerprint`, missing
  matrix evidence, missing baseline approval, weak artifact anchors, and
  unjustified console/network failures in its UI/UX or traceability review
  context.
- Template fixture checks assert required headings, required fields, and status
  vocabularies.
- Deterministic scenario fixture checks exercise the helper contracts rather
  than only keyword presence:
  - staged content change changes `workspace_diff_fingerprint`;
  - unstaged content change changes `workspace_diff_fingerprint`;
  - relevant untracked file content changes `workspace_diff_fingerprint`;
  - nested untracked files from `git ls-files --others --exclude-standard -z`
    are enumerated at file level;
  - unclassified untracked file blocks aggregate `PASS`;
  - irrelevant excluded file is ignored only when an exclusion rationale is
    recorded;
  - UI-touching diff without `visual-test-report.md` or matrix evidence is
    surfaced by `review-code` as missing visual evidence;
  - `review-code` invalidates a stale fingerprint;
  - aggregate verdict truth-table cases cover required `FAIL`, `FLAKY`, `MISS`,
    `NEEDS-RUN`, non-de-scoped `SKIP-with-reason`, stale fingerprint,
    unapproved baseline, console/network `FAIL`, `NOT_COLLECTED`, incomplete
    `IGNORED-with-justification`, and valid carried-forward `PASS`.
- Agent-playbook fixture checks assert the 020 spike stays artifact-only, has
  an adopt/reject/adapt verdict, includes overlap/allowed/forbidden/future-gate
  sections, and rejects commit, push, GitHub mutation, plugin installation,
  skill-tree copy, deployment mutation, and self-replication.
- Broad-orchestrator fixture algorithm is deterministic:
  - Scan roots/globs:
    `*/skills/*/SKILL.md`, `*/skills/*/agents/openai.yaml`, `*/README.md`,
    `*/.claude-plugin/plugin.json`, and root `README.md`.
  - Extract entries deterministically before pairing route/trigger text with
    forbidden capabilities: skill id and body from each skill path/frontmatter;
    default prompt or command token from each `openai.yaml`; skill ids and
    descriptions from plugin JSON; and README catalog blocks from headings or
    bullet/list items that contain a skill link, command token, or skill path.
    Forbidden capability pairing happens inside one extracted entry, not across
    an entire README file.
  - Allowlist existing bounded skill IDs for route-token absence checks only:
    `agent-playbook:commit-changes`,
    `agent-playbook:bootstrap-project-memory`,
    `agent-playbook:context-audit`,
    `agent-playbook:vibe-coding-health-check`,
    `agent-playbook:vibe-coding-fix`,
    `agent-playbook:implementation-tournament`, and
    `agent-playbook:tool-review`. These allowlisted skills still participate in
    the forbidden capability scan below if their text adds broad orchestrator
    trigger language.
  - Normalize route tokens by lowercasing, treating `_` as `-`, and mapping
    `repository-*` aliases to `repo-*`. Fail on any non-allowlisted skill path
    or catalog entry whose normalized route token is one of: `orchestrate`,
    `orchestrator`, `repo-orchestrator`, `repo-bootstrap`, `repo-autopilot`,
    `autopilot`, `bootstrap-agent`, `agent-orchestrator`,
    `bootstrap-orchestrator`, `repo-enable`, `repo-enabler`, `repo-driver`,
    `project-bootstrap`, `project-autopilot`, `workspace-agent`, or
    `workspace-orchestrator`.
  - Treat route-token variants such as `repo-runner`, `repo-orchestrate`,
    `repository-runner`, `repository-driver`, `repository-orchestrator`,
    `repository-autopilot`, `repository-enable`, and `repository-enabler` as
    broad route aliases for the broader mutation check below.
  - For any scanned entry, including allowlisted skills, whose text contains
    `orchestrat`, `autopilot`, `whole repo`, `whole-repo`,
    `entire repository`, `entire-repository`, `repo bootstrap`, `repo-bootstrap`,
    `repository bootstrap`, `repo runner`, `repo driver`, `repo-enable`,
    `repository-enable`, `repo enabler`, `repository enabler`,
    `bootstrap agent`, `agent orchestrator`, `repo enable`,
    `bootstrap this repository`, `workspace agent`,
    `project autopilot`, or `run the repo`, fail if it also contains a forbidden
    capability regex group: git mutation
    `git\s+(commit|push|tag|merge|checkout\s+-b)`, natural-language commit,
    push, tag, merge, branch, worktree, file, code, or diff mutation, GitHub mutation
    `gh\s+(pr|issue|api).*(create|comment|merge|review|edit|POST|PATCH|PUT|DELETE)`,
    natural-language PR, issue, GitHub, GitHub Actions, CI, workflow, or
    deployment mutation including `add`, `set up`, `setup`, `manage`,
    `author`, `generate`, `scaffold`, and `maintain` variants,
    plugin/cache installation `(plugin|skill).*(install|copy|sync)|cache mutation`,
    skill-tree copy `(cp|rsync).*(skills|plugins)|copy.*skill tree`,
    deployment/CI mutation `(deploy|kubectl apply|terraform apply|gh workflow run)`,
    or self-replication `(self[- ]?replicat|replicate.*skill|install.*itself)`.
  - Treat bounded `whole-repo audit/scan/scanning` references as safe only when
    the local clause/window does not claim a forbidden capability. Markdown
    emphasis and inline-code markers in negated safety boundaries, such as
    `Do not **commit** or **push**` or ``Do not `git push` ``, are normalized
    before evaluating negation.
  - Add fixture scenarios proving a synthetic broad candidate with a banned route
    and `git push` fails, proving an allowlisted skill with newly added broad
    orchestration language plus `git push` also fails, proving a synonym route
    such as `repo-enabler` or `repo-enable` plus plugin install fails, proving
    README first-column route-only entries are scanned, proving embedded fake
    diff headers in visual evidence exclusions stay in fingerprint input, and
    proving unchanged allowlisted bounded skills pass.
- Existing release gate validates metadata, frontmatter, hygiene, topology, and
  README coverage.

## Staged Implementation Plan

1. **Stage 1 - Visual-test and orchestration contract fixtures:** Add failing
   fixture checks for the new visual-test skill, metadata, templates, ordered
   gates, freshness fields, baseline approval, artifact RCA, `review-code`
   consumption, README entries, hygiene prerequisites, and orchestration spike
   boundaries.
2. **Stage 2 - Skill, templates, review-code handoff, and spike:** Add
   `idea-to-ship:visual-test`, metadata, the four templates, README catalog
   entries, review-code visual artifact handling, and the 020 spike artifact.
3. **Stage 3 - Verification hardening:** Run fixture suites, hygiene, topology,
   secret scan, and strict release gate; fix drift or missing coverage.

## Open Questions

- Future placement of a generic frontend plugin remains open.
- Future implementation of an `agent-playbook` repo-bootstrap skill remains
  open and should require a separate requirements/design/review cycle.
