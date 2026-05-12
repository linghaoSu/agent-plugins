---
name: review-fix
description: Iteratively review and fix code changes using runtime-aware adversarial review until all issues are resolved, then run a final holistic review
argument-hint: '[focus ...]'
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent]
---

# Review & Fix Loop

Iteratively review the current changes with a runtime-aware adversarial reviewer, fix any issues found, and repeat until clean — then run a final holistic review.

## Arguments

Raw arguments: `$ARGUMENTS`

These are optional additional focus areas for the review (e.g. "concurrency", "error handling").

## Runtime-Aware Agent Routing

Before launching an adversarial review agent, read `../../PRINCIPLES.md` and
`../../WORKFLOW-CONTRACTS.md`. Apply the shared **Runtime-Aware Agent Routing**
and **Adversarial Review Loop** contracts.

## Workflow

### Step 1: Verify Prerequisites

1. Determine the code style guide path with `../../WORKFLOW-CONTRACTS.md`
   § Code Style Guide Lifecycle / Storage Path.
2. Check that this file exists. If not, tell the user to run `/evaluate-issue` first to generate the code style analysis.
3. Check that there are uncommitted changes or recent commits representing the fix:
   ```bash
   git diff --shortstat
   git diff --shortstat --cached
   git status --short
   ```
   If there are no changes, warn the user that there is nothing to review.

### Step 2: Read Code Style Guide

Read `<data-dir>/<owner>/<repo>/code-style.md` and extract the key conventions. Summarize the most important rules into a compact checklist (max 15 items) to use as review context. Keep this checklist for use in all review iterations.

### Step 3: Review-Fix Loop

Repeat the following cycle. Track the iteration count starting at 1.

#### 3a: Adversarial Review

Use the runtime-aware adversarial reviewer to inspect the diff. In Claude Code this is the **Agent tool with `subagent_type: "codex:codex-rescue"`**; in non-Claude runtimes use the host's native sub-agent mechanism. Construct the prompt:

1. Get the current diff (staged + unstaged against the last commit before the fix):
   ```bash
   git diff HEAD
   git diff --cached
   ```
2. Build the adversarial reviewer prompt:
   ```
   Adversarial code review (iteration <N>). Review the following diff for bugs, security issues, and design problems.

   IMPORTANT SCOPE RULE: Only report issues within the lines changed in the diff. Do NOT flag lint, style, or formatting issues in unchanged/surrounding code. Even within the diff, only flag style issues if they introduce NEW inconsistencies with the repo's conventions — do not flag pre-existing style patterns that the diff merely touches.

   ## Code Style Rules for This Repo
   <compact style checklist from Step 2>

   ## Additional Focus
   <user's additional focus text if provided>

   ## Diff to Review
   <the diff output>

   For each issue found, report:
   - Severity (critical / warning / nit)
   - File and line
   - What's wrong and how to fix it
   - Which style rule it violates (if applicable)

   If you find NO issues, respond with exactly: LGTM
   ```

#### 3b: Evaluate Results

- If the adversarial review returns **LGTM** (no issues found) → exit the loop, proceed to Step 4.
- If the adversarial review reports issues:
  1. Present a brief summary to the user: "Iteration N: found X issues (Y critical, Z warnings, W nits). Fixing..."
  2. **Filter issues before fixing**: Only fix issues that are within the scope of the current change. Skip any issues that are purely lint/style/formatting problems in code that was not changed by the fix. Note skipped issues in the summary as "out of scope".
  3. Fix the remaining in-scope issues directly in the code. For each fix:
     - Apply the change using Edit tool
     - Ensure the fix aligns with the code style checklist
     - Do NOT touch unrelated code, even if it has obvious style issues nearby
  4. After all fixes are applied, go back to **Step 3a** for the next iteration.

#### 3c: Safety Limit

If the loop reaches **5 iterations** without a clean review, stop and present the remaining issues to the user. Ask whether to continue fixing or stop here.

### Step 4: Final Holistic Review

After the loop exits clean, run one final comprehensive review. This review looks at the **entire change as a whole** rather than incremental diffs:

1. Get the full diff of all changes:
   ```bash
   git diff HEAD
   git diff --cached
   ```
2. Use the runtime-aware adversarial reviewer with prompt:
   ```
   Final holistic code review. The changes below have passed incremental review. Now review them as a complete unit, focusing on:

   1. **Consistency**: Do all the changes work together coherently?
   2. **Completeness**: Are there any missing edge cases, error paths, or tests?
   3. **Architecture**: Do the changes fit well within the existing codebase structure?
   4. **Code style compliance**: Check against the repo's style rules below.
   5. **Unintended side effects**: Could these changes break anything not directly modified?
   6. **Four-principle check** (from the plugin's PRINCIPLES.md):
      - *Think before coding* — any silent assumption embedded in the diff
        that should have been surfaced?
      - *Simplicity first* — any speculative abstraction, unused knob, or
        error handling for impossible states? If 50 lines would do, flag any
        bloat beyond that.
      - *Surgical changes* — every changed line must trace to the issue or
        a specific review finding. Flag drive-by refactors or formatting
        churn in untouched territory.
      - *Goal-driven execution* — is the fix actually verifiable by running
        something (test, repro command, observable behavior)? If only by
        inspection, flag as weak.

   ## Code Style Rules for This Repo
   <compact style checklist>

   ## Additional Focus
   <user's additional focus text if provided>

   ## Full Diff
   <the diff output>

   For each issue found, report:
   - Severity (critical / warning / nit)
   - File and line
   - What's wrong and how to fix it

   If you find NO issues, respond with exactly: LGTM
   ```

3. If the final review finds issues, fix them and run the final review **one more time** to confirm. If it still has issues after the second final review, present the remaining issues to the user.

### Step 5: Report

Present a summary to the user:

```markdown
## Review & Fix Complete

- **Iterations**: <N> incremental reviews
- **Issues found and fixed**: <total count>
- **Final holistic review**: Clean / <N remaining issues>

### Changes Made During Review
<list of files modified during the review-fix loop, with one-line descriptions of what was changed>
```

## Notes

- Always re-read the diff fresh before each review iteration — don't reuse stale diffs.
- When fixing issues, make minimal targeted changes. Don't refactor surrounding code.
- **Scope discipline**: Only fix issues in code that is part of the current change. Lint/style/formatting issues in unrelated code are out of scope — do not touch them. This keeps diffs clean and avoids unintended regressions.
- If an adversarial-review issue is a false positive or out of scope, skip it and note it in the summary.
- If the user hasn't run `/evaluate-issue` yet but has a code style doc, the review still works.
