---
name: test
description: Produce test-plan.md from user stories, acceptance criteria, scenario sequences, and unit/integration/e2e test matrices, then implement the tests and run them until green. Covers happy paths, edge/corner cases, invalid inputs, and failure modes for this slug.
argument-hint: '[--slug <name>] [focus e.g. "edge cases" "concurrency"]'
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent]
---

# Test — Story-Driven Strategy & Implementation

Turn the requirements and implementation into user stories, acceptance
criteria, scenario sequences, and a concrete test matrix. Then implement the
tests and get them passing. This is the last stop before shipping.

## Arguments

Raw: `$ARGUMENTS`

Parse:
- Optional leading `--slug <name>`. Default slug: `current`.
- Remaining text → extra focus areas (e.g. "error paths", "boundary conditions").

## Workflow

### Step 1: Load Context

1. Resolve `.idea-to-ship/<slug>/`.
2. Require `requirements.md`. If missing, stop and tell the user to run
   `/brainstorm --slug <slug>` first. Read `requirements.md`, plus whichever
   of these exist: `architecture.md`, `implementation-log.md`,
   `code-review.md`, `test-plan.md`.
3. Identify the changed files:
   ```bash
   git diff --name-only HEAD
   git diff --cached --name-only
   ```
   Plus any new files not yet committed. This is the **code under test**.
4. Detect the repo's testing setup:
   - Test framework (pytest / jest / vitest / go test / cargo test / rspec / etc).
   - Conventions: test file location, naming, helpers/fixtures.
   - How tests are run (check `package.json`, `Makefile`, `pyproject.toml`, `justfile`, CI config).
   - Coverage tooling, if any.
   Use Grep/Glob to find existing test files near the changed files and mirror their style.

### Step 1.5: Test Plan Ownership

`test-plan.md` is the canonical verification artifact for this slug. `/test`
owns the full plan, but humans and `/implement --tdd` may have added sections.

On rerun:

1. If `test-plan.md` exists, preserve existing story, acceptance criterion,
   scenario, and test IDs unless the source behavior changed.
2. Update rows by stable ID instead of rewriting the whole file.
3. Preserve human notes, manual exclusions, and prior `## Results` blocks.
4. If the existing file cannot be safely merged because it lacks the expected
   headings or contains unstructured human content, write `test-plan.draft.md`
   or ask before replacing `test-plan.md`.
5. If `/implement --tdd` added a `## Stage TDD Slices` section, fold those
   slices into the full story/scenario/test matrix or explicitly keep them as
   stage-local coverage with a traceability note.

### Step 2: Derive User Stories & Acceptance Criteria

Before listing tests, turn `requirements.md` into behavior that a user or
system actor cares about. Use `architecture.md`, `implementation-log.md`,
`code-review.md`, existing `test-plan.md`, changed-file diff, and `git log`
only as supporting evidence to refine scenarios, identify regression hooks, or
spot drift. They are not substitutes for brainstormed requirements.

If `requirements.md` is too vague to derive stories or acceptance criteria,
stop and send the user back to `/brainstorm --slug <slug>` to refine it. Do not
reverse-engineer product intent from a diff and call that the plan.

For each story, capture:

- **Actor**: user, admin, system job, API client, downstream service, etc.
- **Goal**: the outcome the actor needs.
- **Preconditions**: state required before the story starts.
- **Trigger**: user action, API call, event, cron, retry, migration, etc.
- **Main sequence**: ordered steps from trigger to observable outcome.
- **Expected outcome**: output, side effect, persisted state, emitted event, or
  error signal.
- **Source**: requirement ID, architecture section, implementation-log note,
  code-review finding, or reverse-engineered diff.

Then derive acceptance criteria. Each acceptance criterion must be verifiable:
`<behavior> -> verify: <test/command/assertion>`.

If all available sources are still too vague to derive a story or acceptance
criterion, stop and ask. Do not invent user behavior that no source implies.

### Step 3: Build Scenario Matrix

For every core story sequence, derive scenario rows:

- **Happy path**: the canonical successful sequence.
- **Alternate path**: valid but less common flow (optional only if no
  alternate exists).
- **Corner / boundary cases**: empty, min/max, unicode, null/undefined, zero,
  negative, very large, duplicate, already-exists, not-found, idempotent retry.
- **Invalid / abnormal input**: malformed input, missing fields, invalid enum,
  unauthorized actor, forbidden state transition, wrong content type.
- **Failure modes**: dependency unavailable, timeout, filesystem/DB/API error,
  partial failure, concurrent update, rollback or cleanup behavior.
- **Regression hooks**: adjacent-bug or design-drift notes from
  `implementation-log.md` / `code-review.md`.

Do not create exhaustive combinatorial matrices. Pick cases that prove the
behavior contract and named failure modes. If a story has no meaningful
negative path, say why in `Out Of Scope`.

### Step 4: Derive Test Cases

Go through the scenario matrix and public interfaces from `architecture.md`.
For each behavior, identify:

- **Happy path**: the canonical expected flow.
- **Edge cases**: boundaries, empty inputs, max inputs, unicode, null/undefined, zero, negative, very large.
- **Error paths**: what failure modes are named in `architecture.md § Failure Modes`? Each needs a test that proves the handling works.
- **Integration seams**: the boundaries where this code talks to other systems — DB, HTTP, filesystem, time, randomness. These need either real integration tests or carefully-scoped mocks.
- **Regression hooks**: any adjacent-bug or design-drift notes from `implementation-log.md` / `code-review.md` that map to a test.

**Do not test what you don't own.** Framework behavior, library internals, and trivial getters are noise. Test the behavior your change added.

### Step 5: Decide The Split

Classify each test case into unit / integration / e2e:

- **Unit**: pure, no I/O, fast. Aim for most of the count here.
- **Integration**: hits a real subsystem — DB, HTTP server, file system. Use real things when practical; mock only external third parties.
- **E2E**: full flow from user-visible entry point. Few, high-value.

Respect the repo's existing mix. If the repo has no integration tests at all, don't unilaterally add a new category — stay within the existing layer unless the user asks otherwise.

### Step 6: Write Or Update `test-plan.md`

```markdown
# Test Plan — <slug>

**Date:** <YYYY-MM-DD>
**Target:** <list of changed files>
**Framework:** <detected>
**Run command:** <`npm test` | `pytest` | ...>

## Scope
<One paragraph: what's covered, what's explicitly out.>

## User Stories
| Story ID | Actor | Goal | Preconditions | Trigger | Expected Outcome | Source |
|---|---|---|---|---|---|---|
| US-1 | ... | ... | ... | ... | ... | FR-1 |

## Acceptance Criteria
| AC ID | Story ID | Criterion | Verification Method | Source |
|---|---|---|---|---|
| AC-1 | US-1 | ... | test: ... | FR-1 |

## Scenario Matrix
| Scenario ID | Story ID | Type | Sequence | Inputs / Setup | Expected | Failure Signal | Source |
|---|---|---|---|---|---|---|---|
| S-1 | US-1 | happy | ... | ... | ... | none | AC-1 |
| S-2 | US-1 | invalid-input | ... | ... | ... | ... | AC-1 |

## Test Matrix

### Unit
| # | Scenario | Case | Input | Expected | Source |
|---|---|---|---|---|---|
| U1 | S-1 | ... | ... | ... | AC-1 |

### Integration
| # | Scenario | Case | Setup | Expected | Source |
|---|---|---|---|---|---|
| I1 | S-2 | ... | ... | ... | architecture §... |

### E2E (if applicable)
| # | Scenario | Case | Flow | Expected | Source |
|---|---|---|---|---|---|
| E1 | S-1 | ... | ... | ... | AC-1 |

## Traceability
| Requirement | Story | Acceptance Criteria | Scenarios | Tests |
|---|---|---|---|---|
| FR-1 | US-1 | AC-1 | S-1, S-2 | U1, I1 |

## Out Of Scope
- <what we consciously are NOT testing and why>

## Fixtures & Test Data
<Any shared setup, factories, or data the cases need.>

## Risk Notes
<Anything flaky, slow, or requiring future attention.>

## Stage TDD Slices
<Optional: stage-local slices imported from `/implement --tdd`; each must map to
story/acceptance/scenario/test IDs or be marked provisional.>
```

### Step 7: Implement

Write the tests, case by case. Rules:

- **Match the repo's style** (file location, naming, assertion idioms, fixture patterns).
- **One behavior per test.** A failing test should point to one specific broken thing.
- **Name tests after behavior, not functions.** `returns_empty_list_when_cache_cold` beats `test_get_items`.
- **No shared mutable state between tests.**
- **Don't mock what you could easily use for real.** Mocking internal collaborators hides integration bugs.
- **Don't write tests that only assert implementation details** (e.g., that a specific private helper was called). Test observable behavior.
- **No flaky time/random/network.** Inject or stub at the seam.

### Step 8: Run & Fix

Run the test suite — the full suite, not just the new tests (regressions matter):

```bash
<run command from repo>
```

If tests fail:
- If the new test is wrong → fix the test.
- If the production code is wrong → fix the production code. (This is a real finding; log it.)
- If an **existing** test broke because of this change → that's a regression; either fix the code or, if the test was wrong, update it *and* note in the hand-off why.

Repeat until green. Cap the attempt count at ~5 iterations; if still failing, stop and surface what's wrong to the user.

### Step 9: Coverage Sanity Check

If the repo has coverage tooling, run it for the changed files only (not the whole repo). Report:
- Lines covered on the changed files.
- Any changed line with zero coverage — flag it explicitly; either add a test or document why it's untestable.

Do not chase a coverage percentage — chase meaningful behavior coverage. A 100% line-covered test suite that asserts nothing is worse than 70% that asserts the right things.

### Step 10: Hand-off

1. Append a summary block to `test-plan.md`:

   ```markdown
   ## Results
   **Completed:** <YYYY-MM-DD HH:MM>
   - Tests added: <N>
   - All pass: yes / no (remaining: <list>)
   - Changed-file line coverage: <N%> (if measured)
   - Production fixes triggered by tests: <list, or "none">
   ```

2. Tell the user:
   - Test count, pass/fail status.
   - Any bugs in the production code that the tests exposed (important).
   - Any untestable paths deliberately left uncovered.

3. Suggest: "Review the diff, then commit when ready."

## Anti-Patterns

- **Testing implementation details.** Asserting that a specific private helper was called, or that an internal data structure has a particular shape. Test observable behavior: inputs → outputs, side effects, error signals. If refactoring the internals breaks the test but not the behavior, the test was wrong.
- **Mock everything.** Mocking internal collaborators hides integration bugs. Mock at system boundaries (external APIs, third-party services) — not at the boundary between your own modules. If you're mocking 5 things in one test, the test is too isolated to catch real bugs.
- **One giant test per feature.** A test that checks 8 behaviors will tell you "something broke" but not what. One behavior per test. A failing test should point to one specific broken thing.
- **Chasing coverage numbers.** 100% line coverage with weak assertions is worse than 70% with strong assertions. Coverage tells you what code ran, not what was verified. The right question is: "does each test assert the behavior it claims to test?"
- **Testing framework behavior.** Don't test that React renders a component, that Express routes requests, or that SQLAlchemy saves objects. Test what *your code* does differently from the framework's defaults.
- **Skipping the story layer.** Jumping from requirements straight to test
  names hides missing actors, triggers, and invalid sequences. If you can't
  state the user/system story, the test is probably testing implementation
  trivia.
- **Happy-path-only coverage.** Every core story needs at least one happy path
  and one non-happy-path scenario (edge, invalid input, failure mode, or
  documented reason why none applies).

## Phase Gates

- **⛔ GATE after Step 1.5 (Plan Ownership):** Existing `test-plan.md` content must be preserved, merged by stable ID, drafted around, or approved for replacement before writing.
- **⛔ GATE after Step 2 (Stories):** Every functional requirement must map to at least one user/system story or be explicitly marked untestable/out of scope.
- **⛔ GATE after Step 3 (Scenarios):** Every acceptance criterion must map to at least one scenario. Every core story must have a happy path plus at least one edge, invalid-input, alternate, or failure-mode scenario, unless a documented reason says no such path exists.
- **⛔ GATE after Step 4 (Test Cases):** You must have at least one test case per acceptance criterion. If a criterion has no corresponding test case, either the criterion is untestable (flag it) or you missed something (go back).
- **⛔ GATE after Step 7 (Implement):** All new tests must run and pass before proceeding to Step 8. Do not write 20 tests and then debug them all at once — write a few, run, fix, repeat.

## Notes

- Do **not** commit or push.
- If no `architecture.md` exists, derive interface and regression hints from
  the diff + `git log` of the changed files, but derive scope from
  `requirements.md`. Do not mark a diff-derived plan as complete requirements.
- Flaky tests are bugs. If a test is intermittent, fix the root cause or don't write it.
- If adding tests reveals a production bug, that's a win, not a problem — fix the bug, note it clearly in the results block.
- **Read `../../LANGUAGE.md`** — use "seam" when discussing test boundaries, "vertical slice" when scoping test coverage.
