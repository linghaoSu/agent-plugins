---
name: evaluate-issue
description: Evaluate a GitHub issue against the current repo - diagnose, check fix status, analyze code style, provide reproduction and fix plan. Accepts an issue URL/number OR a free-form natural-language description of the issue.
argument-hint: <issue-url-or-number | description>
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent]
---

# Evaluate GitHub Issue

Evaluate a GitHub issue against the current repository codebase.

## Arguments

The user provided: `$ARGUMENTS`

This is one of:
- A GitHub issue URL (e.g. `https://github.com/owner/repo/issues/123`)
- An issue number (e.g. `123` or `#123`) — assumes the current repo
- **A free-form natural-language description** of the issue to evaluate (e.g. "点击登录按钮后有时会 401，token 刷新没生效"). In this mode there is no real GitHub issue; the description itself is the input.

## Runtime-Aware Agent Routing

Before launching any review or diagnosis agent, read `../../PRINCIPLES.md` and
`../../WORKFLOW-CONTRACTS.md`. Apply the shared **Runtime-Aware Agent Routing**
contract. The roles for this workflow are `ROUND_1_CODE_ANALYSIS`,
`ROUND_1_HISTORY_CHECK`, `ROUND_1_INDEPENDENT_CHECK`,
`ROUND_2_ADVERSARIAL_REVIEW`, and `ROUND_3_SYNTHESIS`.

## Workflow

Execute the following steps in order. Use parallel agents where indicated.

### Step 0: Classify Input Mode

Decide which mode `$ARGUMENTS` falls into:

- **ID mode** — matches a URL regex (`github\.com/.+/issues/\d+`) or is a bare/`#`-prefixed integer. Proceed to Step 1 as written.
- **Description mode** — anything else (or `$ARGUMENTS` is empty). Skip Step 1's fetch and run this sub-flow instead:

  1. **Clarity check.** Read the description and ask: is it specific enough to diagnose? It is specific enough if it identifies (a) the observed wrong behavior AND (b) at least one of: trigger / affected area / error signal. It is NOT specific enough if it is one vague phrase (e.g. "登录有问题", "fix the bug", "something is off with the API").
  2. **If ambiguous**, use `AskUserQuestion` to gather up to 3 missing facts in a single call. Prefer questions with concrete options when possible (e.g. "Which area?", "When does it happen?"). Always include a free-text "Other" path for specifics. Do NOT invent facts; if the user's answers are still vague, ask once more, then proceed with what you have and clearly flag the remaining unknowns in the final report.
  3. **Synthesize a pseudo-issue** from the description (+ any clarifications):
     ```
     PSEUDO_ISSUE_TITLE = <one-line summary of the problem, derived from the description>
     PSEUDO_ISSUE_BODY  = <description + clarifications, lightly cleaned up>
     PSEUDO_ISSUE_NUMBER = "desc"   # used wherever the pipeline expects an issue number
     ```
     Use these values anywhere the downstream steps reference `<issue-title>`, `<issue-body>`, `<issue-number>`, or issue comments. There are no real comments in this mode — treat the comment field as empty.
  4. Skip Step 1 entirely. All other steps (code style analysis, three-round diagnosis, report) run unchanged against the pseudo-issue.
  5. In the final report (Step 4), add a header line: `**Mode**: description-based evaluation (no GitHub issue)` so the user sees this wasn't a real issue fetch.

### Step 1: Fetch Issue Details

Use `gh issue view` to fetch the full issue details including title, body, labels, and comments.

- If a full URL is provided, extract the owner/repo and issue number, then run:
  ```bash
  gh issue view <number> --repo <owner/repo> --json title,body,labels,comments,state,createdAt,updatedAt
  ```
- If only a number is provided, assume the current repo:
  ```bash
  gh issue view <number> --json title,body,labels,comments,state,createdAt,updatedAt
  ```

### Step 2: Code Style Analysis (First Run Only)

Apply `../../WORKFLOW-CONTRACTS.md` § Code Style Guide Lifecycle:

1. Resolve `<data-dir>/<owner>/<repo>/code-style.md`.
2. If the guide is missing, run Full Regeneration before diagnosis.
3. If the guide exists, run the Freshness Check. If stale, launch regeneration
   in the background when possible and continue with the existing guide.

### Step 3: Three-Round Diagnosis & Fix Plan

This diagnosis follows a **three-round sequential pipeline**. Each round builds on the previous round's output to produce an increasingly validated analysis and fix plan.

---

#### Round 1 — Multi-Model Diagnosis + Static Analysis

Launch the following agents and tools **all in parallel**:

**Agent 1A — Code Analysis (`ROUND_1_CODE_ANALYSIS`; Claude: Sonnet, non-Claude: native analysis sub-agent):**
- Based on the issue description, search the codebase for the relevant code paths
- Determine whether the reported issue can be confirmed from the code
- Identify the root cause if the issue exists
- Propose a concrete fix plan with specific files, lines, and changes
- Report: confirmed/unconfirmed, affected files and lines, root cause analysis, proposed fix

**Agent 1B — Commit History Check (`ROUND_1_HISTORY_CHECK`; Claude: Sonnet, non-Claude: native analysis sub-agent):**
- Search git log for commits that may have already fixed this issue:
  ```bash
  git log --all --oneline --grep="<issue-number>"
  git log --all --oneline --grep="<key-terms-from-issue>"
  ```
- Check if any recent commits touch the affected code paths
- If a potential fix commit is found, verify whether it actually addresses the issue
- Report: fixed/not-fixed, relevant commits if any

**Agent 1C — Independent Diagnosis (`ROUND_1_INDEPENDENT_CHECK`; Claude: Haiku, non-Claude: native independent sub-agent):**

Launch an independent third perspective. In Claude Code use a Haiku agent; in non-Claude runtimes use a separate sub-agent with no access to the first two agents' conclusions. Provide it with the issue details and instruct it to search the codebase independently:

"You are an independent code analyst. Based on this issue, search the codebase for relevant code paths, identify the root cause, and propose a fix plan. Report: confirmed/unconfirmed, affected files and lines, root cause analysis, proposed fix. Be concise."

**Tool 1D — IDE Diagnostics:**

Call `mcp__ide__getDiagnostics` to collect compiler/linter diagnostics for the current project. These are objective, machine-verified findings that may be related to the reported issue (type errors, unused imports, syntax issues, etc.). If the issue mentions specific files, filter diagnostics to those files.

**Wait for all Round 1 agents and diagnostics to complete.** Collect:
- `ROUND_1_PRIMARY` — output from Agent 1A + 1B
- `ROUND_1_INDEPENDENT` — output from Agent 1C
- `ROUND_1_DIAGNOSTICS` — output from Tool 1D
- `ROUND_1_DIAGNOSIS` = all of the above combined

---

#### Round 2 — Adversarial Review of Diagnosis

**This round must wait for Round 1 to complete.** Launch a single adversarial reviewer. In Claude Code, use the Codex agent with `subagent_type: "codex:codex-rescue"` if available. In non-Claude runtimes, use the host's native sub-agent mechanism and assign it the `ROUND_2_ADVERSARIAL_REVIEW` role:

```
Adversarial review of issue diagnosis for issue #<number>: "<issue-title>".

You are the second reviewer in a multi-round diagnosis pipeline. You have TWO jobs:
1. Independently analyze the issue and the relevant code to form your own diagnosis and fix plan.
2. Evaluate the first-round diagnosis below — challenge any conclusions you believe are wrong, confirm conclusions you agree with, and flag anything the first round missed.

IMPORTANT: This is a READ-ONLY analysis. Do NOT modify any files or post anything to GitHub.

## Issue Details
<issue title, body, labels, comments>

## Code Style Guide (if available)
<compact style checklist>

## Round 1 Diagnosis — Primary Analysis
<ROUND_1_PRIMARY — full output from Agent 1A + 1B>

## Round 1 Diagnosis — Independent Check
<ROUND_1_INDEPENDENT — full output from Agent 1C>

## IDE Diagnostics (compiler/linter — ground truth)
<ROUND_1_DIAGNOSTICS — machine-verified findings, treat these as facts>

Your output should have TWO sections:

### Section A: Independent Diagnosis
- Your own root cause analysis (agree or disagree with Round 1)
- Your own proposed fix plan with specific files and changes
- Any edge cases or risks the fix plan should account for

### Section B: Evaluation of Round 1
For each Round 1 conclusion, give a verdict:
- **CONFIRMED** — you agree. Briefly state why.
- **DISPUTED** — you disagree. Explain the correct diagnosis/fix.
- **INCOMPLETE** — Round 1 is partially right but missed important aspects. State what's missing.

Note: IDE Diagnostics are machine-verified facts — do not dispute them. They may provide additional clues about the root cause.

If Round 1 said "already fixed" and you agree, say: "Confirmed: already fixed in <sha>"
```

**Wait for Round 2 to complete.** Collect its output as `ROUND_2_DIAGNOSIS`.

---

#### Round 3 — Final Synthesis

Launch a single final synthesis reviewer. In Claude Code, use an **Opus agent** (`model: "opus"`) as the final arbiter. In non-Claude runtimes, use a fresh synthesis sub-agent if available; otherwise perform a separate final synthesis pass in the main context and state that fallback in the report:

```
You are the final reviewer in a runtime-aware multi-pass issue diagnosis pipeline for issue #<number>: "<issue-title>".

Four sources provided input: primary analysis (Round 1), independent check (Round 1), IDE Diagnostics (Round 1), and adversarial review (Round 2). Your job is to produce the definitive diagnosis and fix plan by synthesizing all sources. You must:

1. For the root cause analysis:
   - IDE Diagnostics findings are **ground truth** — if they point to the root cause, that takes precedence
   - If 3+ independent review sources agree on root cause → HIGH CONFIDENCE
   - If 2 independent review sources agree → HIGH CONFIDENCE
   - If they disagree → re-examine the code yourself (read the relevant files) to break the tie
   - State your final root cause with confidence level

2. For the fix plan:
   - If multiple models propose the same fix → HIGH CONFIDENCE, adopt it
   - If they propose different fixes → evaluate all proposals, pick the best (or combine), and explain why
   - If any model found risks or edge cases that others missed → incorporate them
   - The final fix plan must be specific enough to implement directly

3. For already-fixed status:
   - If multiple sources agree it's fixed → confirm
   - If they disagree → verify by reading the code at the relevant commit

## Issue Details
<issue title, body, labels, comments>

## Round 1 Diagnosis — Primary Analysis
<ROUND_1_PRIMARY>

## Round 1 Diagnosis — Independent Check
<ROUND_1_INDEPENDENT>

## IDE Diagnostics (ground truth)
<ROUND_1_DIAGNOSTICS>

## Round 2 Diagnosis (Adversarial Review) + Round 1 Evaluation
<ROUND_2_DIAGNOSIS>

Produce a structured report in this exact format:

### Status
- **Issue exists in code**: Yes/No/Partially `[high]`|`[medium]`|`[low]` confidence
- **Already fixed**: Yes/No/Partially (commit: <sha> if applicable)

### Root Cause
<Final root cause with file:line references>
**Confidence**: `[high]`|`[medium]`|`[low]` — <brief justification: both rounds agreed / verified independently / etc.>

### Reproduction
<Step-by-step instructions to reproduce the issue locally>

### Suggested Fix
<Final concrete fix plan with specific files and changes>
**Confidence**: `[high]`|`[medium]`|`[low]` — <brief justification>

### Risks & Edge Cases
<Any risks, edge cases, or caveats identified across both rounds>

### Disputed & Resolved
<Any disagreements between rounds and how they were resolved>

### Affected Files
- `path/to/file1.ext:L42` — <what needs to change>
- `path/to/file2.ext:L88` — <what needs to change>

Omit empty sections.
```

**Wait for Round 3 to complete.**

### Step 4: Present Final Report

Take the Round 3 agent's output and present it with the issue header prepended:

```markdown
## Issue Evaluation: <issue-title>

**Issue**: #<number>
**Diagnosis pipeline**: Round 1 (primary analysis + independent check + IDE Diagnostics) → Round 2 (adversarial review + evaluation) → Round 3 (final synthesis)

<Round 3 structured output follows>
```

### Step 5: Prompt for Next Steps

After presenting the report, tell the user:
- If the issue is confirmed and not fixed: "I can implement the fix now, or you can review the plan first. After the fix is applied, run `/review-fix` to get an adversarial review against the repo's code style."
- If the issue is already fixed: "This issue appears to be fixed in commit <sha>. No further action needed."
- If the issue cannot be confirmed: "I could not confirm this issue in the current codebase. The issue may be environment-specific, already fixed, or require additional context."

## Anti-Patterns

- **Confirmation bias.** Deciding the root cause before reading the code, then finding "evidence" that supports it. Let the code lead. If Round 1 and Round 2 disagree, that's a signal — don't just pick the first answer.
- **Surface-level diagnosis.** "The error is on line 42" without explaining *why* it fails. A diagnosis must include the causal chain: what triggers the code path, what state is wrong, and why.
- **Unfalsifiable hypotheses.** "It might be a race condition" without stating a concrete check. Use the falsifiable hypothesis pattern: "If X is the cause, then doing Y will produce Z." If you can't state the prediction, dig deeper.

## Phase Gates

- **⛔ GATE after Step 1 (Fetch) / Step 0 (Description mode):** You must have a clear problem statement. In description mode, if the description is too vague after two rounds of clarification, stop and tell the user — do not proceed with a vague diagnosis.
- **⛔ GATE after Round 1:** At least two agents must have produced findings before proceeding to Round 2. If all agents returned empty results, something is wrong with the issue or the search scope — surface this rather than sending empty context to the adversarial reviewer.

## Notes

- Always use `gh` CLI for GitHub interactions, not web fetch
- Keep the code style analysis focused and concise — it's a reference doc, not a novel
- When searching for root cause, prioritize understanding over breadth
- Provide actionable reproduction steps that the user can run immediately
- The fix plan should be specific enough to implement directly
- **Scope discipline**: When implementing a fix, only modify code that is directly related to the issue. Do NOT fix lint warnings, style issues, or formatting problems in surrounding or unrelated code — even if they are obvious. The goal is a minimal, focused fix. Unrelated cleanups create noise in diffs and risk introducing regressions.
