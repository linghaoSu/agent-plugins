---
name: review-code
description: Multi-agent, multi-angle, multi-round code review of the current diff, looping fix->review until all angles are clean. Same-context fallback only for explicit unsupported/forbidden/capacity cases.
argument-hint: '[--slug <name>] [extra focus]'
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent]
---

# Review Code — Adversarial Review Loop For Implementation

Run a blunt, adversarial review of the current code changes (staged +
unstaged) with multiple independent reviewer agents and multiple angles.
Iterate fix→review until every required angle returns LGTM or the iteration
budget is spent. Anchored to the requirements, architecture, interface design,
implementation log, and test plan so drift and missing verification are caught.
Same-context review is a fallback only when reviewer sub-agents are explicitly
unsupported by the host/runtime, explicitly forbidden by the user, or the
selected reviewer/model is explicitly unavailable or at capacity; record the
degradation reason.

## Arguments

Raw: `$ARGUMENTS`

Parse:
- Optional leading `--slug <name>`. Default slug: `current`.
- Remaining text → extra focus areas (e.g. "concurrency", "error handling", "SQL injection").

## Multi-Agent Review Routing

Read `../../PRINCIPLES.md` and `../../WORKFLOW-CONTRACTS.md`. Apply the shared
**Multi-Agent Review Routing** contract. Launch independent reviewer agents by
default:

- **Correctness/security angle:** bugs, edge cases, data loss, concurrency,
  auth, injection, serialization, shell, and other risky boundaries.
- **Traceability/testability angle:** requirement/story/acceptance/scenario/test
  trail, TDD evidence, regression coverage, and stage completeness.
- **Maintainability/repo-fit angle:** local conventions, abstraction cost,
  dead code, design drift, and surgical scope.
- **UI/UX angle:** required when `interface-design.md` exists or the diff
  touches UI; checks component, visual token, interaction-state, responsive,
  accessibility, and visual QA expectations.

If reviewer sub-agents are explicitly unsupported by the host/runtime, the user
explicitly forbids reviewer sub-agents, or the selected reviewer/model is
explicitly unavailable or at capacity, write `code-review.md` with `Result:
degraded-same-context-review`, record the exact reason, and run the same
adversarial review prompts in the main context.

## Workflow

### Step 1: Verify Inputs

1. Resolve `.idea-to-ship/<slug>/`. Require `requirements.md`. If missing,
   stop and tell the user to run `/brainstorm --slug <slug>` first. Read
   `requirements.md`, plus `architecture.md`, `interface-design.md`,
   `implementation-log.md`, and `test-plan.md` if present.
2. Check that there's a diff to review:
   ```bash
   git diff --shortstat
   git diff --shortstat --cached
   git status --short
   ```
   If empty, tell the user there's nothing to review and stop.
3. If `test-plan.md` is absent, remember that fact for the review context.

### Step 2: Collect The Diff

```bash
git diff HEAD
git diff --cached
```

Capture both staged and unstaged. This is the review target.

If `test-plan.md` is absent and the diff changes observable behavior, set
`TEST_PLAN_MISSING=true`. This is review context, not an automatic failure: the
reviewer must flag it as a verification gap unless the implementation log or
current request documents why no test plan is applicable.

### Step 3: Review Loop

Track iteration count starting at 1. Max 5 iterations.

#### 3a — Multi-Agent Review

Launch the required reviewer agents in parallel when possible. Each reviewer
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
- Check the diff against the test plan. If a behavior-changing implementation
  lacks traceability from requirement -> story -> acceptance criterion ->
  scenario -> test, flag it as a verification gap. For fixes or user-visible
  behavior, missing tests are a warning; for bug fixes with no reproducible
  regression test, upgrade to critical unless there is a documented reason.
- If `test-plan.md` is not provided and the diff changes observable behavior,
  flag a warning-level verification gap. For bug fixes without a reproducible
  regression test, upgrade to critical unless there is a documented reason.

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

## Extra Focus From User
<extra focus text, or "none">

## Diff To Review
<full git diff HEAD + git diff --cached output>

For each issue, report:
- Severity: critical / warning / nit
- File:line
- What is wrong and why it matters (be concrete)
- Concrete fix

If no material issues exist for your assigned angle, reply with exactly: LGTM
```

#### 3b — Evaluate & Fix

- **LGTM from every required reviewer angle** → break, proceed to Step 4.
- Otherwise:
  1. One-line summary: `Iteration N: <angle> X critical, Y warnings, Z nits (W skipped out-of-scope).`
  2. Filter before fixing:
     - Drop issues that are pure style/format in code the diff did not actually change.
     - Drop nits unless trivially co-located with a larger fix.
     - Keep criticals, warnings, and any design-drift issues.
  3. Fix each kept issue with Edit. Do not touch unrelated code.
  4. If a fix requires a user decision (tradeoff, spec ambiguity), pause and ask. Do not guess.
  5. Loop back to 3a and re-run every required reviewer angle, not just the
     angle that found the issue.

#### 3c — Safety Limit

At iteration 5 without LGTM, stop. Show remaining issues to the user and ask: continue, accept, or abort.

### Step 4: Final Holistic Pass

After LGTM (or user-accepted exit), one comprehensive review of the **full** diff as a whole:

1. Collect `git diff HEAD` + `git diff --cached` again (post-fix state).
2. Self-review with these questions:
   - Does the change match the requirement(s) it was supposed to satisfy?
   - Does every behavior-changing diff hunk trace to a requirement, user story,
     acceptance criterion, scenario, and test? If not, is the gap explicitly
     documented?
   - Is there dead code, half-finished paths, or leftover scaffolding?
   - Are the public interfaces clean and consistent with the rest of the repo?
   - Could a reader diff this and understand *why* from the code alone?
   - Any security-sensitive boundary (auth, input, serialization, shell) handled correctly?
3. Run the four-principle check (from `../../PRINCIPLES.md`):
   - **Think before coding** — any silent assumption visible in the diff
     that should have been surfaced as a question? Flag it.
   - **Simplicity first** — any speculative abstraction, unused config knob,
     error handling for impossible states, or "if 200 lines could be 50"
     smell? Flag and trim.
   - **Surgical changes** — does every changed line trace to a requirement,
     `architecture.md`, or `interface-design.md`? Any drive-by refactors,
     adjacent-code improvements, or formatting fixes in untouched territory?
     Revert anything that can't cite its reason.
   - **Goal-driven execution** — is each functional requirement observably
     satisfied by something runnable (test, command, behavior), not just
     "the code looks right"? If not, flag for `/test`.
   - **Story/test traceability** — for each core user story, is there a
     happy-path scenario and at least one edge/invalid/failure scenario? If
     not, flag the missing scenario or test.
4. Fix anything found. If the fix is big, loop back to 3a for one more
   adversarial pass.

### Step 5: Write `code-review.md`

```markdown
# Code Review — <slug>

**Date:** <YYYY-MM-DD>
**Reviewer:** multi-agent: <angle -> reviewer route>
**Iterations:** <N>
**Result:** <clean | accepted-with-open-issues>
**Mode:** <multi-agent | degraded-same-context-review>
**Degradation reason:** <none | explicit unsupported runtime | user forbade reviewer sub-agents | reviewer/model unavailable or at capacity>
**Diff size:** <files changed>, <+added/-removed>

## Issues Raised & Resolution
| # | Severity | File:line | Issue | Resolution |
|---|---|---|---|---|
| 1 | critical | src/x.go:42 | ... | fixed |

## Out-of-Scope Issues Skipped
<Pre-existing style nits etc., for visibility — not fixed.>

## Design Drift
<Any place the implementation departed from architecture.md or
interface-design.md, and whether it was reconciled (fix implementation / update
design artifact / accept as documented deviation).>

## Test Traceability
<Requirement/story/acceptance/scenario/test gaps. Include missing happy path,
edge/corner case, invalid-input, or failure-mode coverage. Empty if clean.>

## Residual Open Issues
<Empty if clean.>

## Final Verdict
| Angle | Verdict |
|---|---|
| correctness/security | LGTM / ... |
| traceability/testability | LGTM / ... |
| maintainability/repo-fit | LGTM / ... |
| UI/UX | LGTM / not applicable / ... |
```

### Step 6: Hand-off

1. Tell the user where `code-review.md` landed and how many iterations it took.
2. Suggest next step:
   - If tests don't yet exist or are incomplete → `/test`.
   - Otherwise → user-owned: commit / open PR.
3. Do not commit or push.

## Anti-Patterns

- **Style nitpicking on logic PRs.** If the diff fixes a race condition, don't produce 15 nits about naming. Focus severity appropriately — a few nits alongside criticals is fine, but nits should never dominate a review that has real issues.
- **Phantom bugs.** "This *could* be null" without checking if callers actually pass null. If you can't show a concrete call path that triggers the failure, it's speculation, not a finding. State the call path or drop the finding.
- **Reviewing the architecture.** If the chosen design is wrong, that's a design review problem. Code review assumes the design is accepted and checks whether the implementation is correct, safe, and clean. Flag design drift, but don't re-litigate architectural decisions.
- **Generic advice.** "Add error handling" without saying what error, from where, and what the handler should do. Every finding must be actionable and specific enough to implement in one edit.
- **Trusting implementation without traceability.** If a behavior changed and
  there is no story/acceptance/scenario/test trail, the implementation is not
  verifiably done. Flag the missing link instead of saying "looks fine".

## Notes

- Scope rules matter. Reviewing surrounding unchanged code always produces noise and no value.
- **Design drift is a first-class finding** (see `../../LANGUAGE.md`). If the implementation took a shortcut the architecture didn't sanction, either (a) fix the code, (b) update `architecture.md` with a documented reason, or (c) note it in `code-review.md`. Silent drift is forbidden.
- Fall back to same-context review only when reviewer sub-agents are explicitly
  unsupported by the host/runtime, explicitly forbidden by the user, or the
  selected reviewer/model is explicitly unavailable or at capacity. Record
  `degraded-same-context-review` and do not present that result as independent
  multi-agent review.
