---
name: test
description: Produce test-plan.md (unit/integration/e2e split, edge cases from requirements), then implement the tests and run them until green. Covers the implementation for this slug.
argument-hint: '[--slug <name>] [focus e.g. "edge cases" "concurrency"]'
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent]
---

# Test — Strategy & Implementation

Turn the requirements and the implementation into a concrete test plan, then implement the tests and get them passing. This is the last stop before shipping.

## Arguments

Raw: `$ARGUMENTS`

Parse:
- Optional leading `--slug <name>`. Default slug: `current`.
- Remaining text → extra focus areas (e.g. "error paths", "boundary conditions").

## Workflow

### Step 1: Load Context

1. Resolve `.idea-to-ship/<slug>/`.
2. Read whichever of these exist: `requirements.md`, `architecture.md`, `implementation-log.md`, `code-review.md`.
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

### Step 2: Derive Test Cases

Go through the functional requirements and the public interfaces from `architecture.md` and build a list. For each behavior, identify:

- **Happy path**: the canonical expected flow.
- **Edge cases**: boundaries, empty inputs, max inputs, unicode, null/undefined, zero, negative, very large.
- **Error paths**: what failure modes are named in `architecture.md § Failure Modes`? Each needs a test that proves the handling works.
- **Integration seams**: the boundaries where this code talks to other systems — DB, HTTP, filesystem, time, randomness. These need either real integration tests or carefully-scoped mocks.
- **Regression hooks**: any adjacent-bug or design-drift notes from `implementation-log.md` / `code-review.md` that map to a test.

**Do not test what you don't own.** Framework behavior, library internals, and trivial getters are noise. Test the behavior your change added.

### Step 3: Decide The Split

Classify each test case into unit / integration / e2e:

- **Unit**: pure, no I/O, fast. Aim for most of the count here.
- **Integration**: hits a real subsystem — DB, HTTP server, file system. Use real things when practical; mock only external third parties.
- **E2E**: full flow from user-visible entry point. Few, high-value.

Respect the repo's existing mix. If the repo has no integration tests at all, don't unilaterally add a new category — stay within the existing layer unless the user asks otherwise.

### Step 4: Write `test-plan.md`

```markdown
# Test Plan — <slug>

**Date:** <YYYY-MM-DD>
**Target:** <list of changed files>
**Framework:** <detected>
**Run command:** <`npm test` | `pytest` | ...>

## Scope
<One paragraph: what's covered, what's explicitly out.>

## Test Matrix

### Unit
| # | Case | Input | Expected | Source (FR/section) |
|---|---|---|---|---|
| U1 | ... | ... | ... | FR-1 |

### Integration
| # | Case | Setup | Expected | Source |
|---|---|---|---|---|
| I1 | ... | ... | ... | architecture §... |

### E2E (if applicable)
| # | Case | Flow | Expected |
|---|---|---|---|
| E1 | ... | ... | ... |

## Out Of Scope
- <what we consciously are NOT testing and why>

## Fixtures & Test Data
<Any shared setup, factories, or data the cases need.>

## Risk Notes
<Anything flaky, slow, or requiring future attention.>
```

### Step 5: Implement

Write the tests, case by case. Rules:

- **Match the repo's style** (file location, naming, assertion idioms, fixture patterns).
- **One behavior per test.** A failing test should point to one specific broken thing.
- **Name tests after behavior, not functions.** `returns_empty_list_when_cache_cold` beats `test_get_items`.
- **No shared mutable state between tests.**
- **Don't mock what you could easily use for real.** Mocking internal collaborators hides integration bugs.
- **Don't write tests that only assert implementation details** (e.g., that a specific private helper was called). Test observable behavior.
- **No flaky time/random/network.** Inject or stub at the seam.

### Step 6: Run & Fix

Run the test suite — the full suite, not just the new tests (regressions matter):

```bash
<run command from repo>
```

If tests fail:
- If the new test is wrong → fix the test.
- If the production code is wrong → fix the production code. (This is a real finding; log it.)
- If an **existing** test broke because of this change → that's a regression; either fix the code or, if the test was wrong, update it *and* note in the hand-off why.

Repeat until green. Cap the attempt count at ~5 iterations; if still failing, stop and surface what's wrong to the user.

### Step 7: Coverage Sanity Check

If the repo has coverage tooling, run it for the changed files only (not the whole repo). Report:
- Lines covered on the changed files.
- Any changed line with zero coverage — flag it explicitly; either add a test or document why it's untestable.

Do not chase a coverage percentage — chase meaningful behavior coverage. A 100% line-covered test suite that asserts nothing is worse than 70% that asserts the right things.

### Step 8: Hand-off

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

## Notes

- Do **not** commit or push.
- If no `architecture.md` exists, derive scope from the diff + `git log` of the changed files. Note in `test-plan.md` that the plan was reverse-engineered.
- Flaky tests are bugs. If a test is intermittent, fix the root cause or don't write it.
- If adding tests reveals a production bug, that's a win, not a problem — fix the bug, note it clearly in the results block.
