---
name: fix-issue
description: Fix a GitHub issue based on evaluation results - implements the fix following repo code style, then optionally runs adversarial review. Accepts an issue URL/number OR a free-form description of what to fix.
argument-hint: <issue-url-or-number | description>
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent]
---

# Fix GitHub Issue

Implement a fix for a GitHub issue, guided by the evaluation report and the repo's code style guide.

**Before coding, read `../../PRINCIPLES.md` at the plugin root** (Think Before
Coding · Simplicity First · Surgical Changes · Goal-Driven Execution). These
govern every edit in this skill.

## Arguments

The user provided: `$ARGUMENTS`

Optional control flags may precede the issue input:
- `--compete` or `--tournament` -> before normal implementation, run
  `$agent-playbook:implementation-tournament` and adopt only the selected patch.

After removing optional control flags, the remaining input is one of:
- A GitHub issue URL (e.g. `https://github.com/owner/repo/issues/123`)
- An issue number (e.g. `123` or `#123`) — assumes the current repo
- **A free-form natural-language description** of the fix to make (e.g. "把 login page 里的 token 刷新逻辑修好，偶尔 401"). In this mode there is no real GitHub issue.

## Runtime-Aware Agent Routing

Before launching diagnosis or style-analysis agents, read
`../../PRINCIPLES.md` and `../../WORKFLOW-CONTRACTS.md`. Apply the shared
**Multi-Agent Review Routing** contract where this workflow invokes diagnosis
review or `/review-fix`, and the **Code Style Guide Lifecycle** contract.

## Workflow

### Step 0: Classify Input Mode

Decide the mode:

- **ID mode** — URL like `github.com/.../issues/\d+` or a bare/`#`-prefixed integer. Proceed as written; `<issue-number>` is the parsed value.
- **Description mode** — anything else. Apply this sub-flow before Step 1:

  1. **Clarity check.** The description is specific enough only if it identifies (a) what is wrong / what needs to change AND (b) at least one of: a file/area/feature, a trigger, an observed error. If it is one vague phrase ("fix the bug", "修一下登录"), it is NOT specific enough.
  2. **If ambiguous**, use `AskUserQuestion` with up to 3 targeted questions (offer concrete options + free-text "Other"). Ask at most twice; then proceed and flag remaining unknowns in the summary.
  3. **Synthesize pseudo-issue values**:
     ```
     PSEUDO_ISSUE_TITLE  = <one-line summary from description>
     PSEUDO_ISSUE_BODY   = <description + clarifications>
     PSEUDO_ISSUE_NUMBER = "desc"           # substitute anywhere the pipeline uses <issue-number>
     PSEUDO_ISSUE_SLUG   = <3-5 word kebab-case slug from the title, e.g. "login-token-refresh">
     ```
  4. **Branch / worktree naming** (Step 1.5): use `fix/desc-<slug>-<short-ts>` instead of `fix/issue-<number>`, where `<short-ts>` is `date +%Y%m%d%H%M`. Worktree path becomes `fix-desc-<slug>-<short-ts>`. This avoids collisions between unrelated description-mode fixes.
  5. **Step 1C (fetch issue)** and any `gh issue view` call: skip. There is no issue.
  6. **Commit message** (Step 6): use `fix: <concise description>` without a trailing `(#<n>)`.
  7. In the final summary, add: `**Mode**: description-based fix (no GitHub issue)`.

### Step 1: Gather Context

Run the following checks in parallel:

**A — Check for existing evaluation:**
- Look for a prior `/evaluate-issue` report in the current conversation context
- If found, extract: root cause, affected files, and suggested fix plan

**B — Check code style guide:**
- Determine the code style file path using `../../WORKFLOW-CONTRACTS.md`
  § Code Style Guide Lifecycle / Storage Path.
- If it exists, read it and keep key conventions in mind for the fix

**C — Fetch issue details (if no evaluation exists):**
- Use `gh issue view` to fetch the full issue:
  ```bash
  gh issue view <number> [--repo <owner/repo>] --json title,body,labels,comments,state
  ```

### Step 1.5: Set Up Isolated Worktree

Create an isolated worktree so the fix doesn't interfere with the user's current working directory or other in-progress work.

1. Determine the branch name: `fix/issue-<number>` (e.g. `fix/issue-123`)
2. Determine the base branch:
   ```bash
   BASE_BRANCH=$(gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name')
   ```
3. Check if a worktree for this branch already exists:
   ```bash
   EXISTING_WORKTREE=$(git worktree list --porcelain | grep -B2 "branch refs/heads/fix/issue-<number>" | grep "^worktree " | sed 's/^worktree //')
   ```
4. **If an existing worktree is found**: reuse it, set `WORKTREE_REUSED=true`, log: "Reusing existing worktree at `$EXISTING_WORKTREE`"
5. **If no existing worktree is found**, create one:
   ```bash
   REPO_ROOT=$(git rev-parse --show-toplevel)
   REPO_NAME=$(basename "$REPO_ROOT")
   FIX_WORKTREE="$REPO_ROOT/../.claude-worktrees/$REPO_NAME/fix-issue-<number>"
   mkdir -p "$(dirname "$FIX_WORKTREE")"
   git worktree add -b "fix/issue-<number>" "$FIX_WORKTREE" "$BASE_BRANCH"
   ```
   Set `WORKTREE_REUSED=false`.
6. `cd` into the worktree directory. **All subsequent steps (implementation, tests, etc.) run inside this worktree.**

**If worktree setup fails** (e.g. branch already exists without a worktree), try:
```bash
git worktree add "$FIX_WORKTREE" "fix/issue-<number>"
```
If that also fails, fall back to working in the current directory and warn the user.

### Step 2: Evaluate (if not already evaluated)

If no prior evaluation report is found in conversation context, run the full evaluation workflow:

1. Launch parallel agents to diagnose the issue (same as `/evaluate-issue` Step 3):
   - **Agent A — Code Analysis** (Claude: Sonnet; non-Claude: native analysis sub-agent): Search codebase, confirm issue, identify root cause
   - **Agent B — Commit History Check** (Claude: Sonnet; non-Claude: native analysis sub-agent): Check if already fixed
2. If the issue is already fixed, report this and stop.
3. If the issue cannot be confirmed, report this and stop.
4. Synthesize the diagnosis into a concise fix plan.

If a prior evaluation exists, use its root cause and fix plan directly.

### Step 3: Generate Code Style Guide (if missing)

If the code style file does not exist, apply `../../WORKFLOW-CONTRACTS.md`
§ Code Style Guide Lifecycle / Full Regeneration before coding. The generated
guide must include the metadata header and `## Reviewer Preferences` section.

### Step 3.5: Surface Assumptions & Define "Done" Before Coding

Per *Think Before Coding* and *Goal-Driven Execution* in `PRINCIPLES.md`:

1. **List the assumptions** this fix is making beyond what the issue states
   (e.g. "assuming the 401 comes from the refresh path, not the initial
   token fetch"). If any are load-bearing, verify from the code before
   coding, not after.
2. **If the issue is ambiguous** (multiple plausible fixes, unclear repro,
   conflicting reports in comments), stop and ask — even in ID mode. Do not
   guess; a guessed fix wastes a PR.
3. **If the issue premise looks wrong** (e.g. code already handles the
   claimed case, reported behavior isn't reproducible, the "bug" is actual
   intended behavior), **push back**: post the finding and stop. Do not
   proceed to implement a fix for a non-bug.
4. **State the "done" check** in one line, verifiable: a test name that will
   pass, a command that will produce the expected output, or the specific
   reproduction from the issue no longer reproducing. Write this into the
   commit message later so the reviewer can verify without re-deriving.

### Step 3.6: Optional Implementation Tournament

If `--compete`, `--tournament`, or an explicit user request for competing
implementations is present, route to `$agent-playbook:implementation-tournament`
before Step 4.

Pass the tournament skill:
- Caller: `fix-issue`
- Issue title/body/comments or synthesized description-mode pseudo issue
- Diagnosis, root cause, fix plan, assumptions, and one-line done check
- Code style guide path and relevant conventions
- Active fix worktree path and base branch
- Verification commands or reproduction steps
- Artifact path:
  `.agent-playbook/<PSEUDO_ISSUE_SLUG-or-issue-number>/implementation-tournament.md`

The tournament must create isolated candidate worktrees from the same base,
verify every candidate with the same done check, independently review the
patches, and apply only the selected patch back to the active fix worktree. If
it returns `No Winner`, stop and report the rejected candidates instead of
writing a fallback fix in the same turn.

### Step 4: Implement the Fix

Based on the diagnosis, fix plan, and the "done" check from Step 3.5,
implement the fix:

1. Read all affected files fully before making changes
2. Follow the code style conventions from `.issue-evaluator/code-style.md`
3. Make minimal, focused changes — fix the issue without unrelated refactoring
4. If tests exist for the affected code, update them as needed
5. If the fix warrants a new test, add one following the project's testing
   patterns. Prefer **test-first**: write a failing test that captures the
   issue, then make it pass. This turns "fix the bug" into a verifiable goal.

**Guidelines (aligned with `PRINCIPLES.md`):**
- Prefer editing existing files over creating new ones
- Match the naming conventions, import style, and error handling patterns of surrounding code
- Do not add unnecessary comments, type annotations, or docstrings beyond what the codebase convention requires
- Keep the change set as small as possible while fully addressing the issue
- **Surgical changes**: every changed line must trace to the issue. No
  drive-by refactors of adjacent code, no "while I'm here" improvements. If
  you notice unrelated dead code, mention it in Step 7's summary — do not
  delete it.

### Step 5: Verify the Fix

After implementing:

1. Run the project's test suite (or relevant subset) if identifiable:
   ```bash
   # Try common test commands based on the project type
   # e.g. npm test, pytest, cargo test, go test ./...
   ```
2. If tests fail, diagnose and fix the failures
3. If no test suite is found, note this in the output

### Step 6: Commit Changes

Commit all changes inside the worktree with a descriptive message:
```bash
git add -A
git commit -m "fix: <concise description of fix> (#<issue-number>)"
```

### Step 7: Summary

Present a concise summary:

```markdown
## Fix Applied: <issue-title>

### Worktree
- Branch: `fix/issue-<number>`
- Path: `<worktree-path>`

### Changes Made
- `path/to/file1.ext` — <what was changed and why>
- `path/to/file2.ext` — <what was changed and why>

### Tests
- <test run result, or "no test suite found">

### Next Steps
- Run `/review-fix` to get a runtime-aware multi-agent, multi-angle, multi-round adversarial review against the repo's code style
- Review the changes: `cd <worktree-path> && git diff $BASE_BRANCH`
- Push and create PR: `cd <worktree-path> && git push -u origin fix/issue-<number>`
- To clean up later: `git worktree remove <worktree-path>`
```

**Do NOT remove the worktree** — the user may want to review, push, or continue working on it.

## Anti-Patterns

- **Fixing the symptom, not the cause.** Adding a null check where the real bug is that the value should never be null. Trace the root cause. If the evaluation says "add a guard," ask whether the guard hides a deeper issue.
- **Scope creep during fix.** "While I'm here, I'll also clean up this adjacent function." No. Every changed line must trace to the issue. Note unrelated improvements in the summary — do not fix them.
- **Guessing at ambiguous issues.** If the issue has multiple plausible interpretations, don't pick one silently. The "done" check from Step 3.5 exists to force clarity. If you can't state a verifiable "done" condition, you don't understand the issue well enough.
- **Fix without verification.** A fix with no test and no reproduction check is a hope, not a fix. Step 3.5 requires a "done" check — if none exists, the fix is not ready to commit.
- **Tournament by default.** Multiple fixes are expensive. Use
  `$agent-playbook:implementation-tournament` only when the user or flags
  explicitly request competing implementations.

## Phase Gates

- **⛔ GATE after Step 3.5 (Surface Assumptions):** You must have a written "done" check — a test name, command, or specific behavior that proves the fix works. If you can't state one, stop and clarify with the user.
- **⛔ GATE after Step 3.6 (Tournament):** If tournament mode is enabled,
  `$agent-playbook:implementation-tournament` must return an adopted patch,
  merged patch, or `No Winner`. Do not continue with an unreviewed fallback
  after `No Winner`.
- **⛔ GATE after Step 5 (Verify):** Tests must pass. If no test suite exists, you must have verified the fix manually (reproduction no longer reproduces) and noted this explicitly.

## Notes

- Always read files before editing them
- The fix should be complete and correct — not a placeholder or partial implementation
- If the issue is ambiguous or has multiple possible interpretations, pick the most likely one and note the assumption
- If the fix requires changes that seem risky or are beyond the scope of the issue, flag this to the user before proceeding
- Use `gh` CLI for GitHub interactions
- All file edits and test runs must happen inside the worktree, not the user's original working directory
