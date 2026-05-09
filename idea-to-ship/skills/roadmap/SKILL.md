---
name: roadmap
description: Build or refresh an evidence-backed roadmap for one idea-to-ship slug or the whole project. Produces a candidate brief first, requires explicit goal/horizon/source scope before final Now/Next/Later planning, preserves human edits, and writes .idea-to-ship/roadmap.md or .idea-to-ship/<slug>/roadmap.md.
argument-hint: '[--slug <name> | --portfolio] [--goal <text>] [--horizon <text>] [--include-git] [--include-todos] [--include-github] [--final] [notes]'
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent]
---

# Roadmap — Evidence-Backed Planning

Turn existing project artifacts into a roadmap without laundering weak repo
signals into fake certainty. The output is either:

- `.idea-to-ship/roadmap.md` for the portfolio/project roadmap (default)
- `.idea-to-ship/<slug>/roadmap.md` for a feature-level roadmap (`--slug`)

This skill is a guarded workflow, not a repo-mining report generator.

**Before writing, read `../../PRINCIPLES.md` and `../../LANGUAGE.md`.**
Architecture owns design and staged implementation. Implementation logs own
completion/deviations. Roadmap owns cross-work sequencing, tradeoffs, release
gates, and human decisions.

## Arguments

Raw: `$ARGUMENTS`

Parse:
- `--slug <name>` → feature roadmap for `.idea-to-ship/<slug>/`.
- `--portfolio` → project roadmap at `.idea-to-ship/roadmap.md` (default).
- `--goal <text>` → strategic objective.
- `--horizon <text>` → date, release, or effort horizon (e.g. `next 4 weeks`,
  `v0.4`, `one engineer for 5 days`).
- `--include-git` → include bounded git history/status signals.
- `--include-todos` → include bounded TODO/FIXME signals.
- `--include-github` → include bounded GitHub issue/PR/milestone signals.
- `--final` → after producing a sourced Candidate Brief, write final roadmap
  only if gates are satisfied and candidate priorities are explicitly approved
  by the user or specified in the current request. Without this, stop after the
  brief when user decisions are needed.
- Remaining text → notes, constraints, priorities, or exclusions.

Default sources: idea-to-ship artifacts and local repo manifests/docs. Git,
TODO/FIXME, and GitHub mining are opt-in and quarantined as signals unless
confirmed by higher-authority evidence.

## Critical Safety Rule

If `--include-github` is used, GitHub access is read-only:
- Do NOT run `gh pr review`, `gh pr comment`, `gh issue edit`, `gh pr edit`,
  `gh api` with `POST` / `PUT` / `PATCH` / `DELETE`, or any command that
  writes comments, labels, milestones, assignees, reviews, branches, or repo
  state.
- Only use `gh` to read issue, PR, milestone, review, and CI metadata.
- All roadmap output is local markdown; never post it to GitHub.

## Source Authority

Use this precedence when evidence conflicts:

1. Explicit user goal / instruction in the current request
2. Accepted `requirements.md`
3. Reviewed `architecture.md` / `design-review.md`
4. `implementation-log.md`
5. `test-plan.md`, test results, `code-review.md`
6. Repo docs and manifests
7. GitHub milestones explicitly tied to the goal (only with `--include-github`)
8. Active GitHub PRs explicitly tied to the goal (only with `--include-github`)
9. Labeled/current GitHub issues explicitly tied to the goal (only with
   `--include-github`)
10. Recent git history (only with `--include-git`)
11. TODO/FIXME (only with `--include-todos`)
12. Stale, unlabeled, or generic GitHub issues (only with `--include-github`)

Recent git history confirms freshness, completion, and drift. It does not
override explicit goal-tied planning signals unless those signals are stale or
contradicted by higher-authority artifacts.

Every candidate must cite concrete anchors: `path:line`, artifact heading,
commit SHA, issue/PR URL, or a user-provided statement. Items without anchors
go to `Unverified Signals`, not `Now` or `Next`.

## Confidence Rules

- **High:** explicit user request, accepted requirements, reviewed
  architecture, active implementation artifact, or milestone/issue explicitly
  linked to the goal.
- **Medium:** repo docs, manifests, recent commits, active PRs, current labeled
  issues, or TODOs tied to active files with direct citations.
- **Low:** inferred gaps, generic TODO/FIXME, stale issue, pattern matching,
  or unconfirmed dependency hypothesis.
- **Unknown:** needs a user answer.

`Low`, `Unknown`, and purely inferred items cannot enter `Now` unless the user
explicitly approves them.

## Item Schema

Use stable item IDs so reruns can update instead of rewriting:
`ITS-ROADMAP-001` for portfolio items, or `ITS-<slug>-001` for slug items.

Each candidate item records:

```markdown
| ID | Title | Status | Work Type | Evidence Class | Confidence | Source Anchors | Suggested Action |
|---|---|---|---|---|---|---|---|
```

Controlled values:
- `Status`: `Committed`, `Planned`, `Candidate`, `Blocked`, `Done`,
  `Deferred`, `Needs Revalidation`
- `Work Type`: `Feature`, `Maintenance`, `Spike`, `Bug`, `Docs`, `Release`
- `Evidence Class`: `Explicit`, `Artifact`, `Repo`, `Git`, `TODO`,
  `GitHubMilestone`, `GitHubPR`, `GitHubIssue`, `Inferred`

For every item promoted to `Now`, `Next`, `Later`, a milestone, or a release
gate, use this lane item template verbatim:

```markdown
### <ID> — <Title>
**Status:** <Committed|Planned|Candidate|Blocked|Done|Deferred|Needs Revalidation>
**Work Type:** <Feature|Maintenance|Spike|Bug|Docs|Release>
**Evidence Class:** <Explicit|Artifact|Repo|Git|TODO|GitHubMilestone|GitHubPR|GitHubIssue|Inferred>
**Confidence:** <High|Medium|Low|Unknown>
**Source Anchors:** <path:line | artifact heading | commit SHA | issue/PR URL | user statement>
**Why Now / Why Next / Why Later:** <prioritization rationale>
**Owner:** <owner or Unassigned>
**Decision Owner:** <owner or None>
**Release Gate:** <entry criteria; exit criteria; evidence required; no-go conditions>
**Evidence Required:** <test, review, artifact, command, user decision>
**Dependencies:** <hard dependencies with evidence; otherwise None>
**Risk:** <low|medium|high — concrete failure mode>
```

The lane item template is the source of truth. Do not substitute looser fields
such as `Gate` or `Evidence`.

Each lane item must include:
- `Why Now` / `Why Next`
- `Owner` or `Unassigned`
- `Decision Owner` if a human decision is required
- `Release Gate`
- `Evidence Required`
- `Dependencies`
- `Risk`

## Workflow

### Step 1: Intake Gate

Resolve mode and output path:
- Portfolio mode → `.idea-to-ship/roadmap.md`
- Slug mode → `.idea-to-ship/<slug>/roadmap.md`

Before broad source collection, establish:
- Goal / strategic objective
- Horizon (date-based, release-based, or effort-based)
- Audience / target user or maintainer
- Capacity assumption (if relevant)
- Source scope (local artifacts only, plus any opt-in sources)
- Exclusions / non-goals

If goal or horizon is missing, ask one concise batch of 3-5 questions before
collecting broad sources. Do not write a final roadmap without explicit goal
and horizon.

### Step 1.5: Write Target Safety

Resolve write target before writing any brief or roadmap:

1. Read the existing roadmap file if it exists.
2. If generated markers exist, preserve all human content outside:
   `<!-- idea-to-ship:roadmap generated:start -->` and
   `<!-- idea-to-ship:roadmap generated:end -->`.
3. If the file has no generated markers and contains human content, do not
   overwrite it. Write `roadmap.draft.md` or ask before replacing.
4. Record the full resolved `WRITE_TARGET` path (for example,
   `.idea-to-ship/roadmap.md`, `.idea-to-ship/roadmap.draft.md`,
   `.idea-to-ship/<slug>/roadmap.md`, or
   `.idea-to-ship/<slug>/roadmap.draft.md`) and use it for both Candidate Brief
   and final roadmap output.

### Step 2: Source Plan

List included and excluded sources before reading deeply.

Default source budgets:
- Slug artifacts: all files in `.idea-to-ship/<slug>/` (or all slug dirs in
  portfolio mode)
- Repo docs/manifests: README, plugin manifests, package manifests, and docs
  directly relevant to the goal
- Git (`--include-git`): last 30 commits max
- TODO/FIXME (`--include-todos`): 20 matches max
- GitHub (`--include-github`): 20 total milestones/issues/PRs max; ignore
  stale/closed items unless explicitly requested

Use subagents only for bounded collection tasks when useful:
- artifact scan
- docs/manifests scan
- git/TODO scan
- GitHub scan

Each subagent must return fixed-schema findings with citations and confidence.
Final prioritization stays in the main coordinator.

### Step 3: Collect Evidence

Collect source notes with anchors:

- `.idea-to-ship/*/requirements.md`: functional requirements, success criteria,
  open questions.
- `.idea-to-ship/*/architecture.md`: recommendation, staged implementation,
  hard dependencies.
- `.idea-to-ship/*/design-review.md`: unresolved design risks.
- `.idea-to-ship/*/implementation-log.md`: completed/in-progress stages,
  deviations, adjacent issues.
- `.idea-to-ship/*/test-plan.md` and `code-review.md`: verification gaps and
  unresolved issues.
- Repo manifests/docs: project claims, plugin inventory, release surface.
- Optional sources as requested.

If artifacts disagree (e.g. requirement says one thing, architecture says
another, implementation diverged), add a `Conflicts` entry and stop before
writing `Now / Next / Later` unless the user resolves it.

### Step 4: Candidate Brief

Always produce a Candidate Brief before a final roadmap. This is the
anti-hallucination checkpoint.

Write the brief to `WRITE_TARGET`, preserving human-owned content as decided in
Step 1.5.

Required sections:

```markdown
## Candidate Brief

### Source Plan
<included/excluded sources, source budgets, freshness, repo HEAD>

### Candidate Work
<table using the Item Schema>

### Unverified Signals
<items with weak/no anchors; never promoted automatically>

### Conflicts
<source disagreements that block prioritization>

### Open Decisions
| Decision | Options | Recommended Option | Decision Owner | Needed By | Impact If Delayed |

### Rejected / Not Roadmap-Relevant
<noisy TODOs/issues/docs with reason>
```

After writing the brief, stop unless the user has explicitly approved candidate
priorities or the current request provides unambiguous priority instructions.
Passing `--final` alone is not approval. Ask the user to approve/edit
priorities if approval is missing.

### Step 5: Validation Gates

Before writing final roadmap lanes, enforce:

- Goal and horizon are explicit.
- Existing roadmap overwrite behavior is resolved.
- Candidate priorities were explicitly approved by the user or specified in
  the current request.
- Each lane item has a prioritization rationale using strategic fit, impact,
  urgency, effort, risk reduction, dependency readiness, and verification
  availability where relevant.
- Every lane item has concrete source anchors.
- No `Low` or `Unknown` item enters `Now` without explicit user approval.
- No purely inferred dependency enters `Critical Path`; put it under
  `Dependency Hypotheses`.
- No `Now` item depends on a `Later` item unless explicitly waived or split
  into a spike.
- `Now` has at most 3 items. `Next` has at most 5. Overflow goes to Candidate
  Backlog unchanged.
- Every `Now` item has an owner or is flagged as a blocking open decision.
- Every milestone has release gates.

If any gate fails, write/update the brief and stop. Do not fabricate a final
roadmap.

### Step 6: Write The Roadmap

Preserve human edits:
- Read existing roadmap first.
- If human content exists outside generated blocks, preserve it.
- If the file has no generated markers and contains human edits, write
  `roadmap.draft.md` or ask before replacing.
- Use generated markers for agent-owned content:
  `<!-- idea-to-ship:roadmap generated:start -->` and
  `<!-- idea-to-ship:roadmap generated:end -->`.

Template:

```markdown
---
goal: <explicit goal>
horizon: <date/release/effort horizon>
generated_at: <YYYY-MM-DD HH:MM>
repo_head: <sha>
dirty_worktree: <yes/no>
mode: <portfolio|slug>
source_scope: <local|local+git|local+todos|local+github|...>
---

# Roadmap — <goal or slug>

## Human-Owned Sections

### Strategic Objective
<user-owned objective; preserve edits>

### Manual Overrides
<human priority overrides; preserve edits>

### Out of Scope / Non-Goals
<focus protection>

<!-- idea-to-ship:roadmap generated:start -->

## What Changed Since Last Roadmap
- Added:
- Removed:
- Promoted:
- Demoted:
- Completed:
- Needs Revalidation:

## Inputs
<included/excluded sources with freshness and anchors>

## Now
<max 3 items using the lane item template>

## Next
<max 5 items using the lane item template>

## Later
<valuable but not blocking; use the lane item template>

## Milestones
### Milestone 1 — <name>
**Target:** <date/release/effort offset>
**Scope:** <items>
**Owner:** <owner or Unassigned>
**Dependencies:** <hard dependencies only>
**Release Gate:** <entry/exit criteria, required evidence, no-go conditions>
**Risk Level:** <low|medium|high>

<For milestone work items, use the same lane item template.>

## Dependency Order
<hard dependencies with evidence>

## Dependency Hypotheses
<inferred dependencies needing validation>

## Critical Path
<only validated hard-dependency chain>

## Risks / Spikes
<risks with spike or decision needed>

## Status By Feature
| Slug/ID | Status | Next Action | Blockers | Evidence |

## Candidate Backlog
<items not in Now/Next/Later; grouped by theme>

## Open Decisions
| Decision | Options | Recommended Option | Decision Owner | Needed By | Impact If Delayed |

<!-- idea-to-ship:roadmap generated:end -->
```

### Step 7: Refresh Behavior

On rerun:
- Read previous roadmap and preserve human-owned sections.
- Compare previous items by stable ID.
- Mark items as `new`, `unchanged`, `changed`, `done`, `obsolete`, or
  `needs_revalidation`.
- Record stale triggers:
  - repo HEAD changed
  - artifact source changed
  - milestone date missed
  - dependency changed
  - GitHub sync changed (if used)

### Step 7.5: Roadmap Acceptance Checks

Before hand-off, check the generated brief or roadmap against these scenarios:

- **First run:** no existing roadmap writes the Candidate Brief to the resolved
  `WRITE_TARGET`.
- **Rerun with human content:** human-owned content is preserved, merged by
  generated markers, or a `.draft.md` target is used.
- **`--final` without priority approval:** final Now/Next/Later lanes are not
  written; the brief asks for priority approval instead.
- **`--include-github`:** only read-only GitHub commands were used, and GitHub
  signals keep their evidence class.
- **Conflicting evidence:** conflicts are recorded and final lanes are blocked
  until resolved.
- **Weak signals:** low-confidence, unknown, or inferred items stay out of
  `Now` unless explicitly approved.

If any check fails, fix the artifact or stop with the failed check. Do not
claim a final roadmap is ready.

### Step 8: Hand-off

Tell the user:
- Where the roadmap or brief was written.
- Whether final lanes were written or blocked by gates.
- The top 3 decisions needed.
- The next recommended command, usually `/architect`, `/implement`, `/test`,
  or another `/roadmap --final` after priorities are approved.

## Anti-Patterns

- **Repo mining as strategy.** A TODO is a signal, not a commitment.
- **Fake critical path.** If the dependency is inferred, it is a hypothesis.
- **Overwriting human planning.** Preserve human sections or draft instead.
- **Unbounded source sweeps.** Respect source budgets and opt-in flags.
- **Roadmap as backlog dump.** Cap `Now` and `Next`; group the rest.
- **Passive open decisions.** Every decision needs owner, options, deadline,
  and impact if delayed.

## Phase Gates

- **⛔ GATE after Step 1:** Goal and horizon must be explicit before final
  roadmap lanes are written.
- **⛔ GATE after Step 4:** Candidate Brief must exist with citations before
  final roadmap writing.
- **⛔ GATE after Step 5:** Validation failures stop final roadmap generation.
- **⛔ GATE after Step 7.5:** Acceptance-check failures stop hand-off until the
  artifact is fixed or the failed check is surfaced.
- **⛔ GATE before overwrite:** Existing human edits must be preserved, drafted
  around, or approved for replacement.
