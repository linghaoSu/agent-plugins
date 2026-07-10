---
name: test
description: Plan and implement tests in gate, full, or backfill mode. Use --mode gate before behavior-changing implementation, full for story coverage, or backfill for existing behavior.
---

# Test

Test observable behavior through public seams. Read requirements, architecture,
interface design, existing tests, and `../../WORKFLOW-CONTRACTS.md`.

## Arguments

- `--slug <name>`: artifact root; default `current`.
- `--mode gate|full|backfill`: required.
- Optional stage/focus text.

## Shared rules

- Expected values come from requirements, worked examples, or independent
  sources—not the implementation under test.
- Prefer one vertical tracer-bullet slice at a time. Avoid private-method tests,
  internal collaborator assertions, tautologies, and bulk horizontal tests.
- Use the narrowest public seam that reproduces real behavior. Record missing
  tooling rather than pretending a lower-level test covers it.
- Preserve human edits and stable test IDs in `test-plan.md` and `tdd-log.md`.

## Modes

### Gate

Select the smallest stage behavior. Write one test first, run it, and require
failure for the intended missing behavior—not syntax, fixture, or environment
failure. Write the slice and red evidence to `test-plan.md` and `tdd-log.md`.
Never edit production code. A passing new test means backfill or a wrong seam,
not a valid red gate.

### Full

Derive stories and acceptance criteria, build a unit/integration/e2e scenario
matrix including failures and accessibility/visual needs, implement tests,
run/fix them, and write `test-plan.md` plus the existing results summary. Do
not chase percentage coverage without behavior evidence.

### Backfill

Capture current intended behavior from authoritative sources, add regression
tests at stable seams, and label them backfill. Do not claim red-green TDD.

## Completion

Report mode, seams, test IDs, commands and observed results, uncovered behavior,
tooling gaps, and next action. Never claim unrun tests pass.

Gate mode hands off to `$idea-to-ship:implement`; full mode feeds `$idea-to-ship:review`.
