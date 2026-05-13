---
name: tdd
description: Create or update tests before implementation for an idea-to-ship stage, or backfill missing tests for existing code. Writes stage-local TDD evidence to test-plan.md and tdd-log.md; never writes production code.
argument-hint: '[--slug <name>] [--stage <N>] [--backfill] [focus]'
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash]
---

# TDD - Stage Tests Before Production Code

Create the test evidence that lets `/implement` write production code without
guessing. This skill has two modes:

- **stage-tdd** (default when `--stage <N>` is provided): write failing tests
  for the next implementation slice before production code is touched.
- **test-backfill** (`--backfill`): add missing tests for existing behavior.
  Backfill tests may pass immediately; record them as backfill, not TDD.

This skill writes tests and verification artifacts only. It does not edit
production code.

## Arguments

Raw: `$ARGUMENTS`

Parse:
- Optional leading `--slug <name>`. Default slug: `current`.
- Optional `--stage <N>` -> stage-tdd for architecture stage N.
- Optional `--backfill` -> supplement tests for existing code/diff.
- Remaining text -> focus, test layer, or scenario emphasis.

If neither `--stage` nor `--backfill` is supplied, infer stage-tdd only when
there is a clear next stage in `implementation-log.md`; otherwise stop and ask
for `--stage <N>` or `--backfill`.

## Workflow

### Step 1: Load Context

1. Resolve `.idea-to-ship/<slug>/`; create it if this run needs `tdd-log.md`.
2. For stage-tdd, require `requirements.md`. If missing, stop and tell the user
   to run `/brainstorm --slug <slug>` first.
3. For stage-tdd, require `architecture.md` and the selected stage. If missing,
   stop and tell the user to run `/architect --slug <slug>` first.
4. For test-backfill, read `requirements.md` if present. If absent, require a
   concrete user focus, current diff, or explicit file/test target. Treat
   diff/source-derived intent as lower-authority and record that limitation in
   `tdd-log.md`.
5. Read whichever exist: `requirements.md`, `architecture.md`,
   `interface-design.md`, `test-plan.md`, and `implementation-log.md`.
6. Detect the repo's test setup from nearby tests, package scripts, Makefile,
   CI, and existing naming/fixture style.

### Step 1.5: Test Artifact Ownership

`test-plan.md` remains the canonical full verification artifact. `/tdd` may add
or update only `## Stage TDD Slices`, `## Backfill Test Slices`, and `## Results`
entries unless the user explicitly asks for a full `/test` plan.

On rerun:

1. Preserve existing story, acceptance, scenario, and test IDs.
2. Update rows by stable ID instead of rewriting the whole file.
3. Preserve human notes, manual exclusions, prior results, and `/test` matrices.
4. If the existing file cannot be merged safely, write `test-plan.draft.md` or
   ask before replacing `test-plan.md`.

### Step 2: Select Mode And Slice

For **stage-tdd**:

1. Read the selected stage from `architecture.md § Staged Implementation Plan`.
2. Derive the smallest vertical behavior slice from `requirements.md`,
   `architecture.md`, and `interface-design.md` if present.
3. Pick at least one happy-path scenario and one edge/invalid/failure scenario,
   unless the stage has no meaningful negative path and the reason is recorded.
4. If the stage spans multiple stories or broad coverage and no `test-plan.md`
   exists, stop and tell the user to run `/test` first.

For **test-backfill**:

1. Use `requirements.md` if present, existing `test-plan.md`, current diff,
   explicit user focus, and nearby source/tests to identify missing high-value
   coverage.
2. Prefer regression, boundary, invalid-input, failure-mode, accessibility,
   responsive, or E2E gaps over low-value implementation-detail tests.
3. If product intent cannot be inferred from requirements, user focus, or
   existing observable behavior, stop and ask. Do not invent requirements from
   code alone.

### Step 3: Write Or Update Test Plan Evidence

Add or update:

```markdown
## Stage TDD Slices
| Stage | Story | Acceptance | Scenario | Test | Expected Initial Result | Command |
|---|---|---|---|---|---|---|
| Stage N | US-1 | AC-1 | S-1 happy | TDD-1 | fail: behavior not implemented | `<cmd>` |

## Backfill Test Slices
| Source | Gap | Scenario | Test | Expected Result | Command |
|---|---|---|---|---|---|
| diff / requirement | ... | ... | ... | pass or fail-before-fix | `<cmd>` |
```

Only include the section that applies. Keep full matrices for `/test`.

### Step 4: Write Tests

Write minimal tests in the repo's existing style:

- Match test location, naming, fixtures, and assertion idioms.
- Test observable behavior, not private helpers.
- For UI, map relevant `interface-design.md` accessibility, responsive,
  interaction-state, and visual QA expectations to the smallest useful test
  layer: unit, integration, E2E, or explicit manual check.
- Add E2E tests only when the repo already has an E2E setup or the user asked
  for one. Otherwise record the missing E2E tooling in `tdd-log.md` and
  `test-plan.md`.

### Step 5: Run The Gate

For **stage-tdd**:

1. Run the targeted test command.
2. The new test must fail for the expected reason before production code is
   written.
3. If it passes, either rewrite the test so it proves the missing behavior or
   stop and record that the stage appears already implemented. Do not continue
   as TDD.

For **test-backfill**:

1. Run the targeted test command.
2. Passing immediately is acceptable when testing existing behavior.
3. If the test reveals a production bug, stop and report it. Do not fix
   production code in this skill.

### Step 6: Write `tdd-log.md`

Append:

```markdown
## <YYYY-MM-DD HH:MM> - <stage-tdd | test-backfill>
**Stage:** <Stage N or n/a>
**Mode:** <stage-tdd | test-backfill>
**Authority:** <requirements.md | user focus | current diff | source behavior>
**Files touched:** <tests and test-plan only>
**Scenarios:** <happy / edge / invalid / failure / UI contract>
**Command:** `<cmd>`
**Initial Result:** <expected failing result | passed as backfill | bug exposed>
**Implementation Gate:** <ready for /implement | blocked: reason | backfill complete>
```

### Step 7: Hand-off

- Stage-tdd ready: tell `/implement` which failing test command gates the
  production code.
- Backfill complete: report tests added and passing command.
- Blocked: state the exact missing requirement, test tooling, or user decision.

## Phase Gates

- **⛔ GATE after Step 1.5 (Artifact Ownership):** Existing `test-plan.md`
  content must be preserved, updated by stable ID, drafted around, or approved
  for replacement before writing.
- **⛔ GATE after Step 2 (Slice):** Stage-tdd requires a concrete stage story,
  acceptance criterion, scenario, expected failure, and command before writing
  tests. Backfill requires a concrete user focus, current diff, explicit target,
  or existing observable behavior source before writing tests.
- **⛔ GATE after Step 4 (No Production Code):** This skill may not edit
  production code. If tests expose a bug, stop and hand off to `/implement`.
- **⛔ GATE after Step 5 (Red First):** Stage-tdd must produce an expected
  failing test before `/implement` writes production code. Backfill must be
  clearly labeled when tests pass immediately.

## Anti-Patterns

- **Backfill pretending to be TDD.** Existing behavior tests are useful, but
  they are not a red-green implementation gate.
- **Full test-plan creep.** Do not rebuild `/test` matrices from inside `/tdd`.
- **Implementation-detail tests.** A refactor should not break the test if
  observable behavior is unchanged.
- **Silent E2E omission.** If UI behavior needs E2E but the repo has no E2E
  setup, record the missing tooling instead of pretending unit tests cover it.
