---
name: review-design
description: Adversarial review of architecture.md via Codex. Linus-style - blunt, skeptical, attacks weak assumptions. Iterates fix->review until clean (max 5 rounds). Writes design-review.md verdict.
argument-hint: '[--slug <name>] [extra focus e.g. "concurrency" "cost"]'
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent]
---

# Review Design — Adversarial Architecture Review

Run a blunt, adversarial review of `architecture.md`. Default reviewer is Codex via the `codex:codex-rescue` agent. Fix→review loop until the reviewer returns LGTM or the iteration budget is exhausted.

This is the designed-in correction step. An architecture that has not been torn apart by a skeptical reviewer is not ready to implement.

## Arguments

Raw: `$ARGUMENTS`

Parse:
- Optional leading `--slug <name>`. Default slug: `current`.
- Remaining text → additional focus areas to emphasize (e.g. "concurrency", "cost", "failure modes").

## Workflow

### Step 1: Verify Inputs

1. Resolve artifact dir `.idea-to-ship/<slug>/`.
2. Require `architecture.md` to exist. If missing, stop and tell the user to run `/architect` first.
3. Read `architecture.md` and `requirements.md`. If the architecture's recommended option contradicts requirements, flag it before even calling Codex.

### Step 2: Review Loop

Track iteration count starting at 1. Max 5 iterations.

#### 2a — Codex Review

Use the **Agent tool with `subagent_type: "codex:codex-rescue"`**. Construct the prompt:

```
Adversarial architecture review (iteration <N>). Be blunt, Linus Torvalds style.
Your job is to find weaknesses — not to validate.

REVIEW PRINCIPLES:
- Attack assumptions that aren't justified by evidence in the document.
- Call out missing failure modes, hand-waved scaling claims, and interfaces
  that will hurt callers.
- If the recommended option is weaker than a rejected alternative for the
  stated requirements, say so.
- Do not invent work. If a concern is out of scope per the requirements,
  say so and move on.
- Do not pile on stylistic nits. Design-level issues only.

## Requirements (for context)
<full content of requirements.md>

## Architecture Under Review
<full content of architecture.md>

## Extra Focus From User
<extra focus text, or "none">

For each issue, report:
- Severity: critical / warning / nit
- Location (section or heading in architecture.md)
- The problem, stated concretely
- What specifically needs to change

If you find no material issues, respond with exactly: LGTM
```

#### 2b — Evaluate & Fix

- If Codex returns **LGTM** → break, proceed to Step 3.
- Otherwise:
  1. Print a 1-line summary: `Iteration N: X critical, Y warnings, Z nits.`
  2. For each **critical** and **warning** issue: update `architecture.md` directly with Edit. Be concrete — change the recommendation, rewrite a section, add a failure mode, revise an interface. Do not just append a footnote.
  3. Skip **nits** unless trivially fixable while you're in the file.
  4. If a critical issue requires the user to decide (e.g. a tradeoff they haven't weighed in on), pause the loop and ask. Do not guess on user-owned decisions.
  5. Go back to 2a.

#### 2c — Safety Limit

If iteration count hits 5 without LGTM, stop. Summarize remaining open issues to the user and ask whether to continue or accept.

### Step 3: Final Holistic Pass

After LGTM (or user-accepted exit), one last pass — this time looking at the document as a whole rather than issue-by-issue:

1. Re-read the updated `architecture.md`.
2. Ask yourself:
   - Does the chosen option still make sense after all the revisions? (Sometimes fixes shift the balance — a rejected alternative may now be better.)
   - Are the staged implementation steps actually independently shippable?
   - Is there anything a new engineer reading this could not act on?
3. If problems remain, do one more targeted edit. Otherwise proceed.

### Step 4: Write `design-review.md`

```markdown
# Design Review — <short title>

**Slug:** <slug>
**Date:** <YYYY-MM-DD>
**Reviewer:** Codex (codex:codex-rescue) + self-review
**Iterations:** <N>
**Result:** <clean | accepted-with-open-issues>

## Issues Raised & Resolution
| # | Severity | Issue | Resolution |
|---|---|---|---|
| 1 | critical | ... | fixed in architecture.md §... |
| 2 | warning  | ... | user decision: <answer> |

## Residual Open Issues
<Anything accepted as open. Empty is fine.>

## Reviewer's Final Verdict
<Paste Codex's final LGTM or accepted summary.>

## Self-Review Notes
<What you noticed in the holistic pass. Empty is fine.>
```

### Step 5: Hand-off

1. Tell the user: the architecture file has been updated in place, review log is in `design-review.md`.
2. Print a 3-bullet summary of the biggest changes made during the loop.
3. Suggest: "Run `/implement` to start building."

## Anti-Patterns

- **Piling on.** Finding 30 issues and reporting all of them. Prioritize ruthlessly — criticals first, then warnings. If there are more than 3 criticals, the architecture needs a rewrite, not 30 patches.
- **Inventing work.** Flagging concerns that are explicitly out of scope per `requirements.md`. If requirements say "no real-time sync needed," don't flag "no real-time sync strategy" as a missing failure mode.
- **Cosmetic rewrites.** Rewriting sections for style or prose quality. This is a technical review, not copyediting. Only change text to fix a technical error or add a missing failure mode.
- **Death by a thousand nits.** If the architecture is fundamentally sound, 20 nits don't make it better — they make the reviewer feel productive while adding no value. A clean architecture with 3 real improvements beats one buried under formatting fixes.

## Notes

- This skill writes to `architecture.md` (updates) and `design-review.md` (new). It does not touch source code.
- If `codex:codex-rescue` is unavailable, fall back to a self-review pass with the same principles, and note in `design-review.md` that Codex was not used.
- **User-owned decisions always pause the loop.** Do not pick a tradeoff the user should pick.
- **Read `../../LANGUAGE.md`** for shared vocabulary — use "design drift", "blast radius", "falsifiable hypothesis" precisely as defined.
