---
name: implementation-tournament
description: Run an optional best-of-N implementation tournament with isolated candidate patches, shared verification, independent review, and explicit adopt, merge, or reject decisions. Use only when the user or caller explicitly asks for competing implementations.
argument-hint: '[--slug name] [--candidates 2-4] [--artifact path] [--caller implement|fix-issue|manual] [goal]'
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent]
---

# Implementation Tournament

Run multiple independent candidate implementations, verify them against the
same contract, review them from separate angles, and adopt only the best patch.
This is a high-cost mode. Do not run it by default.

Use this skill only when the user explicitly asks for multiple independent
implementations, "best of N", competing agents, tournament mode, or when a
caller skill passes an explicit `--compete` / `--tournament` option.

## Arguments

Raw: `$ARGUMENTS`

Parse:
- `--slug <name>` -> artifact slug. Default: `current`.
- `--candidates <N>` -> number of candidate implementations. Default: 3, max 4.
- `--artifact <path>` -> caller-owned tournament artifact path. If omitted,
  write `.agent-playbook/<slug>/implementation-tournament.md`.
- `--caller <implement|fix-issue|manual>` -> workflow that invoked this skill.
- Remaining text -> implementation goal, constraints, stage, issue, or notes.

## When To Use

Good fits:
- Multiple plausible implementation strategies exist and the wrong choice is
  expensive.
- The stage or issue touches shared architecture, core domain logic, data
  safety, UI architecture, or public API behavior.
- The user explicitly wants independent implementations before choosing.
- Prior attempts failed or converged on overly large patches.

Poor fits:
- Trivial one-file fixes.
- Formatting, copy, docs-only, dependency bumps, or mechanical migrations.
- No objective verification command can be defined.
- The repo cannot tolerate temporary worktrees or parallel branches.
- The user wants speed more than decision quality.

## Selection Values

Rank candidates by these values, in order:

1. Correctness against the fixed contract and objective checks.
2. Requirement or issue traceability.
3. Small blast radius and low diff surface.
4. Fit with existing code style and architecture.
5. Readability and testability.
6. Rollback simplicity.
7. Extensibility only when the contract or architecture explicitly needs it.

Do not reward abstract "flexibility" without evidence. Small code is good only
when it stays readable and complete; clever dense code does not win.

## Workflow

### Step 1: Tournament Brief

Read `../../PRINCIPLES.md`. Then collect the caller contract:

- Goal and non-goals.
- Required artifacts: requirements, architecture, interface design, issue body,
  code style guide, TDD log, or evaluation report.
- Exact verification commands and expected signals.
- Files or modules likely in scope.
- Constraints: public API compatibility, performance, accessibility, security,
  migration, rollout, or supportability.

If the goal or verification is unclear, stop and ask. Do not run a tournament
where candidates can only be judged by taste.

Write or update the tournament artifact before launching candidates.

### Step 2: Candidate Isolation

Create isolated candidate worktrees from the same base commit. Never run
multiple candidates in the same working tree.

Recommended shape:

```text
../.agent-tournaments/<repo>/<slug>/
├── candidate-a/
├── candidate-b/
└── candidate-c/
```

Each candidate must start from the same base and receive the same brief. If
worktrees cannot be created safely, either run candidates sequentially from a
clean resettable copy or stop and report that true independence is unavailable.
Do not fake independence by asking agents to edit the same files in place.

### Step 3: Independent Candidate Implementation

Use runtime-native worker agents when the host supports subagents and the
current user/host policy authorizes delegation. Otherwise run sequential fresh
passes and record `degraded-sequential-candidates`.

Each candidate owns only its worktree. Tell each worker:

- You are not alone in the codebase.
- Do not revert or inspect other candidate patches.
- Follow the shared contract and verification commands.
- Keep the patch surgical.
- Prefer existing local patterns over new abstractions.
- Return changed files, diffstat, verification results, assumptions, and known
  tradeoffs.

Require every candidate to produce:

```markdown
| Candidate | Branch / Worktree | Summary | Files Changed | Verification | Assumptions | Known Tradeoffs |
|---|---|---|---|---|---|---|
```

### Step 4: Objective Verification

Run the same checks for every candidate:

- Contract-specific test or reproduction command.
- Build, typecheck, lint, or relevant suite when available.
- UI visual/accessibility checks when `interface-design.md` applies.
- Security, secret, resilience, or harness checks when signaled.

A failing candidate cannot win unless every candidate fails and the synthesis
explicitly chooses `No Winner`. Do not let an attractive design override a
failing test.

### Step 5: Independent Review

Review every candidate with distinct angles. Use separate reviewer agents when
authorized; otherwise run same-context review passes and record the degraded
mode.

Required angles:
- **Correctness / contract fit:** satisfies the requirement, stage, or issue.
- **Minimality / blast radius:** fewest meaningful changes without hiding
  complexity.
- **Maintainability / readability:** easy to understand, local style, simple
  seams for tests.
- **Risk / rollback:** failure modes, migration risk, public API risk, recovery.

Conditional angles:
- **UI / accessibility:** when the patch touches UI.
- **Performance / scale:** when hot paths or data volume are involved.
- **Security / data safety:** when auth, secrets, permissions, persistence, or
  irreversible side effects are involved.

Reviewer schema:

```markdown
| Candidate | Verdict | Strengths | Material Risks | Required Fixes | Score 1-5 |
|---|---|---|---|---|---|
```

Reviewer verdicts:
- `Adopt`
- `Adopt With Fixes`
- `Merge Idea Only`
- `Reject`

### Step 6: Synthesis

Choose one of:

- `Adopt Candidate X`: one patch clearly wins.
- `Adopt Candidate X With Fixes`: one patch wins after bounded fixes.
- `Merge Ideas Into Candidate X`: one patch is the base and specific ideas
  from others are incorporated.
- `No Winner`: all candidates fail the contract, are too risky, or cost too
  much for the benefit.

If combining ideas, name the exact hunks or design choices being taken. Do not
create a fourth unreviewed implementation by freely mixing everything.

### Step 7: Apply Selected Patch

Apply only the selected final patch to the caller's active worktree. Use a
binary-safe patch or careful manual integration, then rerun the verification
commands in the active worktree.

If no candidate wins, do not apply any candidate patch. Record why and hand
control back to the caller to revise requirements, architecture, TDD scope, or
the issue diagnosis.

Do not commit or push. Do not remove candidate worktrees unless the user asks.
Record cleanup commands in the artifact.

### Step 8: Write Artifact

Template:

```markdown
# Implementation Tournament - <goal>

**Slug:** <slug>
**Caller:** <implement|fix-issue|manual>
**Date:** <YYYY-MM-DD>
**Base Commit:** <sha>
**Status:** <running|adopted|merged|no-winner|blocked>

## Tournament Brief
<goal, contract, non-goals, verification commands, constraints>

## Candidates
| Candidate | Branch / Worktree | Summary | Files Changed | Verification | Assumptions | Known Tradeoffs |
|---|---|---|---|---|---|---|

## Verification Matrix
| Candidate | Command | Result | Evidence |
|---|---|---|---|

## Reviewer Findings
| Candidate | Reviewer Angle | Verdict | Strengths | Material Risks | Required Fixes | Score |
|---|---|---|---|---|---|---|

## Synthesis Decision
**Decision:** <Adopt Candidate X|Adopt Candidate X With Fixes|Merge Ideas Into Candidate X|No Winner>
**Reason:** <why this wins or why none win>
**Rejected Candidates:** <candidate -> reason>
**Merged Ideas:** <none or exact ideas/hunks>

## Applied Patch
<files applied to caller worktree, or "none">

## Cleanup
<candidate worktree paths and safe cleanup commands>
```

### Step 9: Hand-Off

Tell the caller:
- Which candidate won, or why there was no winner.
- Which verification commands passed in the active worktree.
- Which candidates were rejected and why.
- Whether any follow-up fixes remain before normal caller verification.

## Anti-Patterns

- **Same-tree competition.** Multiple candidates editing the same worktree is
  not a tournament; it is uncontrolled merge conflict.
- **LLM beauty contest.** Do not choose by prose quality. Objective checks and
  material code risks dominate.
- **Extensibility theater.** Do not choose the most abstract solution unless the
  contract requires extension seams now.
- **Line-count worship.** The fewest lines do not win if the code is dense,
  fragile, or hides failure cases.
- **Unreviewed hybrid.** Combining ideas from candidates creates a new patch;
  rerun verification and review the final patch.

## Phase Gates

- **Gate before candidates:** fixed contract, non-goals, candidate count, base
  commit, and verification commands are recorded.
- **Gate before selection:** every candidate has objective verification and at
  least the required reviewer angles.
- **Gate before applying:** synthesis names a single adopted base candidate or
  `No Winner`.
- **Gate after applying:** active worktree verification passes before handing
  control back to the caller.
