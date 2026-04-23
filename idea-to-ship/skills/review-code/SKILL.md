---
name: review-code
description: Adversarial code review of the current diff via Codex, looping fix->review until clean. Linus-style bluntness. Uses architecture.md as context. Writes code-review.md.
argument-hint: '[--slug <name>] [extra focus]'
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent]
---

# Review Code — Adversarial Review Loop For Implementation

Run a blunt, adversarial review of the current code changes (staged + unstaged). Uses `codex:codex-rescue`. Iterates fix→review until the reviewer returns LGTM or the iteration budget is spent. Anchored to the architecture and requirements for this slug so drift is caught.

## Arguments

Raw: `$ARGUMENTS`

Parse:
- Optional leading `--slug <name>`. Default slug: `current`.
- Remaining text → extra focus areas (e.g. "concurrency", "error handling", "SQL injection").

## Workflow

### Step 1: Verify Inputs

1. Resolve `.idea-to-ship/<slug>/`. Read `architecture.md` and `requirements.md` if present (both optional — if absent, proceed but note in the final log).
2. Check that there's a diff to review:
   ```bash
   git diff --shortstat
   git diff --shortstat --cached
   git status --short
   ```
   If empty, tell the user there's nothing to review and stop.

### Step 2: Collect The Diff

```bash
git diff HEAD
git diff --cached
```

Capture both staged and unstaged. This is the review target.

### Step 3: Review Loop

Track iteration count starting at 1. Max 5 iterations.

#### 3a — Codex Review

Use **Agent tool with `subagent_type: "codex:codex-rescue"`**. Prompt:

```
Adversarial code review (iteration <N>). Linus Torvalds style — blunt, skeptical,
no hedging. Find real bugs, security holes, bad abstractions, wrong-feeling code.

SCOPE RULES (important):
- Only report issues within the lines changed in this diff.
- Do NOT flag lint/style/format issues in unchanged surrounding code.
- Within the diff, only flag style if the change introduces NEW inconsistency
  with what's already in this repo. Do not flag pre-existing patterns the diff
  happens to touch.
- Check the diff against the architecture. If the implementation deviates from
  the design in a way the implementation-log does not justify, flag it as a
  "design drift" issue.

## Requirements (context, may be empty)
<requirements.md or "not provided">

## Architecture (context, may be empty)
<architecture.md or "not provided">

## Extra Focus From User
<extra focus text, or "none">

## Diff To Review
<full git diff HEAD + git diff --cached output>

For each issue, report:
- Severity: critical / warning / nit
- File:line
- What is wrong and why it matters (be concrete)
- Concrete fix

If no material issues, reply with exactly: LGTM
```

#### 3b — Evaluate & Fix

- **LGTM** → break, proceed to Step 4.
- Otherwise:
  1. One-line summary: `Iteration N: X critical, Y warnings, Z nits (W skipped out-of-scope).`
  2. Filter before fixing:
     - Drop issues that are pure style/format in code the diff did not actually change.
     - Drop nits unless trivially co-located with a larger fix.
     - Keep criticals, warnings, and any design-drift issues.
  3. Fix each kept issue with Edit. Do not touch unrelated code.
  4. If a fix requires a user decision (tradeoff, spec ambiguity), pause and ask. Do not guess.
  5. Loop back to 3a.

#### 3c — Safety Limit

At iteration 5 without LGTM, stop. Show remaining issues to the user and ask: continue, accept, or abort.

### Step 4: Final Holistic Pass

After LGTM (or user-accepted exit), one comprehensive review of the **full** diff as a whole:

1. Collect `git diff HEAD` + `git diff --cached` again (post-fix state).
2. Self-review with these questions:
   - Does the change match the requirement(s) it was supposed to satisfy?
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
   - **Surgical changes** — does every changed line trace to a requirement
     or to `architecture.md`? Any drive-by refactors, adjacent-code
     improvements, or formatting fixes in untouched territory? Revert
     anything that can't cite its reason.
   - **Goal-driven execution** — is each functional requirement observably
     satisfied by something runnable (test, command, behavior), not just
     "the code looks right"? If not, flag for `/test`.
4. Fix anything found. If the fix is big, loop back to 3a for one more Codex pass.

### Step 5: Write `code-review.md`

```markdown
# Code Review — <slug>

**Date:** <YYYY-MM-DD>
**Reviewer:** Codex (codex:codex-rescue) + self-review
**Iterations:** <N>
**Result:** <clean | accepted-with-open-issues>
**Diff size:** <files changed>, <+added/-removed>

## Issues Raised & Resolution
| # | Severity | File:line | Issue | Resolution |
|---|---|---|---|---|
| 1 | critical | src/x.go:42 | ... | fixed |

## Out-of-Scope Issues Skipped
<Pre-existing style nits etc., for visibility — not fixed.>

## Design Drift
<Any place the implementation departed from architecture.md, and whether it was
reconciled (fix implementation / update architecture / accept as documented deviation).>

## Residual Open Issues
<Empty if clean.>

## Final Verdict
<Paste the final LGTM line, or the accepted summary.>
```

### Step 6: Hand-off

1. Tell the user where `code-review.md` landed and how many iterations it took.
2. Suggest next step:
   - If tests don't yet exist or are incomplete → `/test`.
   - Otherwise → user-owned: commit / open PR.
3. Do not commit or push.

## Notes

- Scope rules matter. Reviewing surrounding unchanged code always produces noise and no value.
- **Design drift is a first-class finding.** If the implementation took a shortcut the architecture didn't sanction, either (a) fix the code, (b) update `architecture.md` with a documented reason, or (c) note it in `code-review.md`. Silent drift is forbidden.
- If `codex:codex-rescue` is unavailable, do a self-review pass with the same prompt and note the fallback in the final log.
