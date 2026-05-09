---
name: implement
description: Implement the design in architecture.md in staged commits, optionally in --tdd mode that writes failing story/acceptance tests before production code. Stops between stages for user review. Logs decisions and deviations to implementation-log.md. Does not commit or push.
argument-hint: '[--slug <name>] [--tdd] [stage-number | all]'
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent]
---

# Implement — Staged Build From Architecture

Read `architecture.md` and build it. One stage at a time by default, so you can review and course-correct before the next stage. Every stage leaves the system in a working state. With `--tdd`, write the stage's failing story/acceptance tests before production code, then implement until they pass.

This skill writes code. It does **not** commit, push, or run adversarial review — those are separate (`git` is yours; use `/review-code` when a stage is complete).

**Before coding, read `../../PRINCIPLES.md` and `../../LANGUAGE.md` at the
plugin root.** PRINCIPLES governs every line written here. LANGUAGE defines
shared terms (vertical slice, staged implementation, design drift, seam,
blast radius) — use them precisely.

## Arguments

Raw: `$ARGUMENTS`

Parse:
- Optional leading `--slug <name>`. Default slug: `current`.
- Optional `--tdd` flag → test-first mode for behavior-changing stages.
- Remaining: stage selector:
  - `<N>` → implement stage N only (e.g. `2`)
  - `all` → run every remaining stage sequentially, pausing between for user confirmation
  - empty → implement the next incomplete stage (default)

## Workflow

### Step 1: Load Context

1. Resolve `.idea-to-ship/<slug>/`.
2. Require `architecture.md`. If missing → stop, tell user to run `/architect`.
3. Read `requirements.md` (if present), `architecture.md`, and `test-plan.md` (if present) fully.
4. Read or create `implementation-log.md`:

   ```markdown
   # Implementation Log — <slug>

   **Architecture:** architecture.md
   **Started:** <YYYY-MM-DD>

   ## Stage Status
   - [ ] Stage 1 — <name>
   - [ ] Stage 2 — <name>
   ...
   ```
   Mirror the stages from `architecture.md` § Staged Implementation Plan.

### Step 2: Pick The Stage

- If argument is `<N>` → jump to that stage.
- If argument is `all` → start from first unchecked stage.
- Otherwise → first unchecked stage.

If all stages are already complete, tell the user and stop.

### Step 3: Pre-Stage Sanity Check

Before writing any code:

1. Re-read the stage's subsection in `architecture.md`.
2. Check the current codebase with Grep/Glob/Read to confirm the assumed pre-stage state (are the files mentioned where the doc claims, with roughly the shape it assumed?).
3. If the codebase has drifted from what the architecture assumed, **stop and surface the mismatch** rather than guessing. Ask the user whether to update the architecture doc first or proceed with a documented deviation.

### Step 3.5: Surface Assumptions, Then Push Back If Needed

Before writing a single line (per *Think Before Coding* in `PRINCIPLES.md`):

1. Write down the assumptions this stage is making that aren't already
   spelled out in `architecture.md`. Things like: "will use existing `X`
   helper", "will place the file at `Y`", "will rely on library `Z` version
   ≥ N".
2. If any assumption has multiple plausible interpretations, **list them and
   pick one explicitly** in the log instead of picking silently.
3. If the stage itself looks wrong now that you're in the code — e.g. the
   proposed interface doesn't compose with an existing one, or the stage is
   redundant with something already present — **stop and push back**. Do not
   implement a design you can see is broken.
4. If a simpler approach than the architecture's would work and you're
   confident, raise it and wait for confirmation. Do not silently substitute.

### Step 3.6: TDD Setup (only with `--tdd`)

If `--tdd` is set and the stage changes observable behavior:

1. Identify the user/system story slice for this stage from `requirements.md`,
   `architecture.md`, and `test-plan.md` if present.
2. Derive or update the stage's acceptance criteria and scenarios:
   - happy path
   - at least one edge/corner case or invalid-input path
   - named failure modes from the architecture
3. Write the minimal tests first, matching the repo's existing test style.
   Prefer tests already listed in `test-plan.md`.
   - If `test-plan.md` exists, update only the rows or `## Stage TDD Slices`
     entries for this stage. Preserve existing story, acceptance, scenario, and
     test IDs unless the source behavior changed.
   - If no `test-plan.md` exists and the stage spans multiple stories or has
     broad coverage implications, stop and tell the user to run `/test` first.
   - If no `test-plan.md` exists and the stage is a small single-story slice,
     create a minimal `test-plan.md` with a clearly labeled
     `## Stage TDD Slices` section. Mark it stage-local, not full coverage.
   - If the existing plan cannot be safely merged, write `test-plan.draft.md`
     or ask before replacing `test-plan.md`.
4. Run the new/targeted tests and confirm they fail for the expected reason.
   A test that passes before implementation is not proving the new behavior;
   rewrite it or explain why this stage is not suitable for TDD.
5. Record the failing test command and expected failure in
   `implementation-log.md`.

If the stage is docs-only, metadata-only, or otherwise has no meaningful
runtime behavior, do not fake TDD. Document why `--tdd` was skipped for this
stage and continue with normal implementation.

### Step 4: Implement The Stage

Build it. Keep in mind:

- **Follow the repo's existing conventions**, not external templates. Match naming, layering, error handling, logging style used nearby.
- **Minimum viable change.** Do not add helpers, abstractions, or future-proofing that the architecture did not call for. A stage is about doing the described thing — nothing more.
- **No speculative error handling.** Validate at system boundaries only. Don't wrap internal calls in defensive try/except that swallows real bugs.
- **No scope creep.** If you spot an adjacent bug or cleanup opportunity, note it in the log; do not fix it in this stage.
- **Keep it working.** At the end of the stage the build, type-checker, and existing tests must pass. Run them. If something fails, fix it before declaring the stage done.
- **TDD mode:** if `--tdd` is active, do not write production code before the
  stage's failing tests exist and fail for the expected reason, unless the
  stage is explicitly documented as not TDD-suitable.

For each file touched:
- Prefer Edit over rewrite.
- If adding a new file, put it where the architecture said.

### Step 5: Verify

Run whatever the repo uses to verify code is working:

- Build / compile
- Type check / lint (if fast)
- Existing test suite (if fast; otherwise run only tests near the changed files)

Report the results concisely. If anything is broken, fix it before moving on.

Outside `--tdd`, do **not** write new tests in this skill — that's `/test`.
But do not break existing tests either. In `--tdd` mode, run the failing tests
again after implementation and require them to pass before the stage is done.

### Step 6: Update The Log

Append a section to `implementation-log.md`:

```markdown
## Stage <N> — <name>
**Completed:** <YYYY-MM-DD HH:MM>

### Files touched
- `path/to/file.ext` — <what changed, 1 line>

### Decisions made during implementation
- <decision>: <reasoning>

### Deviations from architecture.md
- <none | or: "did X instead of Y because Z">

### Adjacent issues noticed (NOT fixed here)
- <bullet or "none">

### Verification
- build: ok / fail (fixed: <what>)
- lint:  ok / skipped / ...
- tests: N passed, M skipped, 0 failed
- tdd: skipped / failing test written then passed (`<command>`)
```

Tick the stage's checkbox in the Stage Status list at the top.

### Step 7: Hand-off

1. Print a concise summary: stage name, files touched count, deviations (if any), verification status.
2. Next-step suggestion:
   - If more stages remain and mode is `all` → ask "Continue to stage N+1?" and loop on confirmation.
   - Otherwise suggest: "Review the diff, then `/review-code` to run adversarial review, or `/test` to write tests."
3. Do **not** commit.

## Anti-Patterns

- **Big-bang implementation.** Implementing all stages at once, or treating "all" mode as permission to skip the pause between stages. Each stage must leave the system working. If you find yourself thinking "I'll fix the breakage in stage 3" while in stage 2, you're doing it wrong — stage 2 must work on its own.
- **Silent deviation.** The architecture says X, you do Y because it's "obviously better." This is design drift (see `../../LANGUAGE.md`). Either push back and update the architecture first, or document the deviation in the log. Never just do it.
- **Speculative scaffolding.** Adding config knobs, feature flags, abstraction layers, or "flexibility" that no stage calls for. This stage is about doing the described thing — nothing more.
- **Horizontal slicing.** Writing all the models first, then all the handlers, then all the tests. Each stage should be a vertical slice — end-to-end through all layers, delivering one observable behavior. If you're implementing "the database layer" as a stage, the architecture is sliced wrong — push back.
- **Fake TDD.** Writing tests after implementation and calling it TDD, or
  writing tests that pass before the behavior exists. In `--tdd` mode, the
  expected failing test is the gate.

## Phase Gates

- **⛔ GATE after Step 3 (Sanity Check):** If the codebase has drifted from what `architecture.md` assumed, STOP. Do not improvise around the mismatch. Surface it, get a decision (update architecture or proceed with documented deviation), then continue.
- **⛔ GATE after Step 3.5 (Surface Assumptions):** Assumptions must be written down before any code is written. If an assumption has multiple plausible interpretations, you must pick one explicitly and log the pick. "I'll figure it out as I go" is not an option.
- **⛔ GATE after Step 3.6 (`--tdd` only):** Behavior-changing stages must have failing tests for the stage story/acceptance criteria before production code is written. If TDD is skipped, the log must explain why the stage has no meaningful runtime behavior.
- **⛔ GATE before touching `test-plan.md` (`--tdd` only):** Existing test-plan content must be preserved, updated by stable ID, drafted around, or explicitly approved for replacement. Stage-local TDD slices must not pretend to be a full `/test` plan.
- **⛔ GATE after Step 5 (Verify):** Build, lint, and existing tests must pass. If anything fails, fix it before declaring the stage done. Do not move to Step 6 with a broken build — a "mostly done" stage is worse than an unstarted one.

## Notes

- Never skip Step 3 (sanity check). Drift between doc and reality is the #1 cause of bad stage-1 implementations.
- If a stage turns out to be too big mid-implementation, stop, split it in the architecture doc, update Stage Status, and finish only the first half. Honesty about scope beats a half-working stage.
- If the architecture says something demonstrably wrong once you're in the code (e.g. proposed interface doesn't compose with an existing one), stop and fix the architecture doc first. Implementations should not silently diverge from design.
