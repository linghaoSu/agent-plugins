---
name: fix-pr-comments
description: Triage GitHub PR review comments, apply accepted fixes as local unstaged edits, then run multi-agent adversarial review. Read-only on GitHub.
argument-hint: <pr-url-or-number> [--include-resolved]
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent]
---

# Triage & Address PR Review Comments (Read-Only)

After a GitHub pull request has accumulated review comments, walk through every reviewer comment, **evaluate whether it's a reasonable change request**, and:

- For comments that **are** worth addressing → apply the fix as **uncommitted local edits** in an isolated worktree, so the user can inspect and decide what to do next.
- For comments that **are not** worth addressing → produce a justified rebuttal the user can paste back manually.

This skill is **strictly read-only with respect to GitHub** and **never creates a commit**. The user is the one who decides whether to commit, push, or post anything.

## CRITICAL SAFETY RULES

**1. Never write to GitHub.** This means:
- Do NOT run `gh pr review`, `gh pr comment`, `gh pr edit`, `gh pr merge`, `gh pr close`, `gh pr ready`, `gh pr resolve`, etc.
- Do NOT run `gh api` with `POST` / `PUT` / `PATCH` / `DELETE` against the PR or its discussions
- Do NOT post replies, resolve threads, add reactions, change labels, request reviewers, or modify state in any way
- Only use `gh` for **read-only** operations (fetching PR details, diff, comments, reviews, files)
- All rebuttal text goes to the conversation — never to GitHub

**2. Never create a commit.** This means:
- Do NOT run `git commit`, `git commit --amend`, `git stash`, `git push`, or anything that records history
- Do NOT run `git add` either — the changes should remain visible as unstaged edits so the user can review with `git diff`
- File edits go into an **isolated worktree** (so the user's working copy is not disturbed) and stay as **uncommitted, unstaged** modifications
- The user is the only one who decides whether to stage, commit, or discard

These two rules apply throughout the entire workflow, including any sub-agents launched by this skill.

## When to use

- A PR you authored has accumulated review comments and you want them triaged and pre-implemented in one read-only pass before deciding what to commit.
- You want a second opinion on whether a reviewer's pushback is actually correct before changing the code.
- Multiple reviewers left overlapping or conflicting feedback and you need it consolidated and answered.

## Arguments

The user provided: `$ARGUMENTS`

This should be one of:
- A full GitHub PR URL (e.g. `https://github.com/owner/repo/pull/123`)
- A PR number (e.g. `123` or `#123`) — assumes the current repo

Optional flag:
- `--include-resolved` — also evaluate comments on already-resolved threads (default: skip them)

## Multi-Agent Review Routing

Before launching analysis, executor, or adversarial review agents, read
`../../PRINCIPLES.md` and `../../WORKFLOW-CONTRACTS.md`. Apply the shared
**Multi-Agent Review Routing** contract for all review phases. The roles for
this workflow are `ANALYST`, `RECONCILER`, `EXECUTOR`, and multiple
`ADVERSARIAL_REVIEWER:<ANGLE>` roles. Keep the human confirmation gate before
edits and keep adversarial review read-only.

The adversarial review phase is pre-authorized for reviewer sub-agents. Fall
back to same-context review only when reviewer sub-agents are explicitly
unsupported by the host/runtime, the user explicitly forbids them, or the
selected reviewer/model is explicitly unavailable or at capacity. In degraded
mode, record `degraded-same-context-review`, run the same angle prompts
sequentially in the main context, and do not present the result as independent
multi-agent review.

## Workflow

### Step 1: Parse Arguments & Fetch PR Context

1. Parse the PR number and optional `owner/repo` from `$ARGUMENTS`.
   - If a full URL is provided, extract the owner/repo and PR number.
   - If only a number is provided, use the current repo.
   - Note whether `--include-resolved` was passed.

2. Fetch PR metadata, diff, and all comment streams in parallel using `gh` (read-only):

   **A — PR metadata:**
   ```bash
   gh pr view <number> [--repo <owner/repo>] --json number,title,body,author,state,baseRefName,headRefName,headRepositoryOwner,headRepository,files,additions,deletions,reviewDecision,reviews,comments,createdAt,updatedAt,url,isCrossRepository
   ```
   Capture: `title`, `body`, `author.login`, `state`, `baseRefName`, `headRefName`, `url`, `isCrossRepository`, `reviewDecision`.

   **B — PR diff:**
   ```bash
   gh pr diff <number> [--repo <owner/repo>]
   ```
   Used for evaluating whether each inline comment is anchored to code that actually exists / behaves as the reviewer claims.

   **C — Inline review comments (anchored to code lines):**
   ```bash
   gh api "repos/<owner>/<repo>/pulls/<number>/comments?per_page=100" --paginate \
     --jq '[.[] | {id, in_reply_to_id, pull_request_review_id, path, line, original_line, side, start_line, body, user: .user.login, created_at, updated_at, html_url, position, original_position, commit_id, original_commit_id}]'
   ```
   These are the per-line review comments (the most actionable kind).

   **D — Review summaries (top-level review bodies):**
   ```bash
   gh api "repos/<owner>/<repo>/pulls/<number>/reviews?per_page=100" --paginate \
     --jq '[.[] | {id, user: .user.login, state, body, submitted_at, html_url}]'
   ```
   Capture the body of each review (general review notes that aren't anchored to a line).

   **E — Issue-level conversation comments (the PR conversation tab):**
   ```bash
   gh api "repos/<owner>/<repo>/issues/<number>/comments?per_page=100" --paginate \
     --jq '[.[] | {id, user: .user.login, body, created_at, updated_at, html_url}]'
   ```
   These are the general PR comments (not tied to code lines).

   **F — Review threads with `isResolved` (GraphQL — needed because the REST API does not expose thread resolution):**
   ```bash
   gh api graphql -F owner=<owner> -F repo=<repo> -F number=<number> -f query='
     query($owner: String!, $repo: String!, $number: Int!) {
       repository(owner: $owner, name: $repo) {
         pullRequest(number: $number) {
           reviewThreads(first: 100) {
             nodes {
               id
               isResolved
               isOutdated
               path
               line
               comments(first: 50) {
                 nodes {
                   databaseId
                   author { login }
                   body
                   createdAt
                   url
                 }
               }
             }
           }
         }
       }
     }'
   ```
   Use this to know which inline comments belong to a **resolved** thread so they can be filtered (unless `--include-resolved` is set).

3. If the PR is closed or merged, note it in the report but proceed — the user may still want to triage stale feedback.

### Step 2: Set Up Read-Only Worktree

The fix needs somewhere to live. We use an **isolated, detached worktree** on the PR's head commit so that:
- The user's current working directory and branches are untouched.
- The edits are visible as uncommitted changes in a clearly-named scratch directory.
- There is no local branch to accidentally push.

1. Confirm we're in the right repo (skip worktree setup if cross-repo and just diff-review):
   ```bash
   CURRENT_REPO=$(gh repo view --json owner,name --jq '"\(.owner.login)/\(.name)"' 2>/dev/null)
   ```
   Compare with the PR's `owner/repo`. If they don't match (cross-repo PR from a fork), skip the worktree and operate in **diagnosis-only mode** — explain the rebuttals and produce a fix plan as text, but do not edit any files.

2. Determine the head ref. For same-repo PRs:
   ```bash
   HEAD_BRANCH="<headRefName from PR metadata>"
   git fetch origin "$HEAD_BRANCH"
   HEAD_REF="origin/$HEAD_BRANCH"
   ```
   For PRs from a fork in the same workflow (rare path — usually skipped above), use `gh pr checkout --detach` into the worktree instead.

3. Check for an existing worktree on this branch (so we don't fight with a previous run or the user's own checkout):
   ```bash
   EXISTING_WORKTREE=$(git worktree list --porcelain | grep -B2 "branch refs/heads/$HEAD_BRANCH" | grep "^worktree " | sed 's/^worktree //')
   [ -z "$EXISTING_WORKTREE" ] && EXISTING_WORKTREE=$(git worktree list | grep "$HEAD_BRANCH" | awk '{print $1}')
   ```

4. **If found**: STOP and ask the user. A pre-existing worktree on the PR branch is almost certainly the user's in-progress work — silently editing it would clobber their changes. Tell the user:
   > "A worktree for `<HEAD_BRANCH>` already exists at `<path>`. Should I (a) operate inside it (will leave uncommitted edits in your in-progress work), or (b) create a separate scratch worktree at a different path?"
   
   Default to (b) unless the user explicitly chooses (a). Set `WORKTREE_REUSED=true` only if the user picks (a).

5. **If not found**: create a fresh **detached** worktree (so there's no branch to accidentally push):
   ```bash
   REPO_ROOT=$(git rev-parse --show-toplevel)
   REPO_NAME=$(basename "$REPO_ROOT")
   FIX_WORKTREE="$REPO_ROOT/../.claude-worktrees/$REPO_NAME/pr-<number>-comments"
   mkdir -p "$(dirname "$FIX_WORKTREE")"
   git worktree add --detach "$FIX_WORKTREE" "$HEAD_REF"
   WORKTREE_REUSED=false
   ```
   Detached HEAD is intentional — there is no branch and there will be no commit, so there is nothing for `git push` to send anywhere.

6. `cd` into the worktree. **All subsequent file reads and edits run inside it.**

7. **Cleanup rule**: Do **NOT** automatically remove the worktree at the end, even if we created it. The whole point is for the user to review the uncommitted edits. Tell them how to remove it manually in the final report.

### Step 3: Build the Comment Set

From the raw comment streams (Step 1 C/D/E/F), build a clean **comment-to-evaluate set**:

1. **Drop the PR author's own comments** — they're not review feedback. Keep them as **CONTEXT** for evaluating reviewer comments (e.g. "the author already explained X here").

2. **Drop bot comments** by default — Dependabot, CodeRabbit, sonar-bot, etc. (`user.type == "Bot"` or username ends in `[bot]`). The user can re-run with `--include-bots` if they want them. (If the user passes that flag, treat bot comments as a separate, lower-priority category.)

3. **Drop already-resolved threads** (from the GraphQL data in Step 1F) unless `--include-resolved` was passed.

4. **Drop pure noise** — single emoji, "+1", "LGTM" with no actionable content, "approved" with no body. Keep "approved with nits" only if there are nits to extract from the body.

5. **Group threaded replies** — for inline comments, walk `in_reply_to_id` chains and group them into one thread per top-level comment. Treat the **whole thread** as one comment-to-evaluate, with the **latest reviewer position** as the operative ask. If the PR author replied last, the operative ask is still the most recent reviewer note above their reply.

6. **Classify each remaining comment** into one of:
   - **BUG** — reviewer claims the code is broken / incorrect
   - **STYLE** — naming, formatting, idiom, convention
   - **DESIGN** — architecture, abstraction, API shape, separation of concerns
   - **PERF** — performance / memory / complexity concern
   - **SECURITY** — security or correctness-under-adversarial-input concern
   - **TEST** — missing test coverage, weak assertions, brittle test
   - **DOC** — comment / docstring / changelog request
   - **NIT** — minor preference, no real impact
   - **QUESTION** — reviewer is asking for clarification, not requesting a change

7. For each comment, record: `thread_id` (top-level inline comment id, or review id, or issue-comment id), `latest_note_id`, `author`, `category`, `location` (`file:line` if anchored, else "general"), `html_url`, full thread body, and `is_question` flag (questions get a different verdict path — they need answers, not fixes).

If after filtering the set is **empty**, stop and report:
> "No actionable review comments found on PR #<number>. Either no human review has happened yet, or all discussions are already resolved."

### Step 4: Load Code Style Guide

The triage decisions need to be grounded in this repo's actual conventions, otherwise REJECT/ACCEPT verdicts will drift.

Apply `../../WORKFLOW-CONTRACTS.md` § Code Style Guide Lifecycle:

1. Resolve the guide path.
2. Generate it if absent.
3. Run the Freshness Check if present; stale guides may regenerate in the
   background while triage proceeds with the existing guide.
4. Extract a compact checklist of at most 15 rules. Reviewer Preference Mining
   is especially important here because it indicates which current comments are
   project convention versus personal preference.

### Step 5: Triage — Evaluate Each Comment (runtime-aware analysis)

This is the central step. Each comment gets an **independent verdict** before any code is touched. In Claude Code, analysis is done by Opus because verdicts have to be load-bearing — every ACCEPT becomes a code edit, every REJECT becomes a message back to a reviewer, and the cost of getting either wrong is high. In non-Claude runtimes, use separate analysis sub-agents with the same load-bearing role.

#### Phase 1 — Per-Comment Evaluation (parallel analysts)

For each comment in the set, launch an **analyst agent** in parallel, capped at ~4 concurrent. In Claude Code this is an Opus agent (`model: "opus"`); in non-Claude runtimes use the host's native sub-agent mechanism and label the role `ANALYST`. Each agent gets:

```
You are evaluating a single code review comment on GitHub PR #<number>: "<pr-title>".

Your job: decide whether this comment is a VALID change request that should be implemented, and if so, design the fix. You are doing **analysis only** — a separate executor will apply the fix later, so your fix plan must be detailed enough for an executor to follow without re-deriving anything.

CRITICAL: This is read-only with respect to GitHub. Do NOT run any gh commands that write to the PR (no gh pr review, gh pr comment, gh api POST/PATCH/DELETE, etc.). Do NOT run git commit. You may read files in the worktree at <FIX_WORKTREE>, but DO NOT edit files yourself — analysis only.

## Context
- PR description: <pr body>
- Code style checklist: <compact checklist from Step 4>
- PR author: @<pr-author>
- Worktree (read source from here): <FIX_WORKTREE>

## The comment
- Thread id: <thread_id>
- Reviewer: @<author>
- Category (initial): <category>
- Location: <file:line or "general">
- Thread URL: <html_url>
- Full thread:
<thread body — original comment + any back-and-forth replies, oldest first>

## Relevant code
<for inline comments: the diff hunk around the anchored line, plus 30 lines of surrounding context read from <FIX_WORKTREE>/<file>>
<for general comments: the relevant section of the PR description, and any files the comment mentions>

## Evaluation rubric
For this comment, decide one of:

1. **ACCEPT** — the comment is correct and the change should be made. Provide:
   - A concrete fix plan: file, lines, exact change (use diff-style or "replace X with Y" — be specific enough that the implementer doesn't have to guess)
   - Rationale: why the reviewer is right
   - Whether a test should be added

2. **ACCEPT_PARTIAL** — the comment identifies a real problem but the suggested fix is wrong / suboptimal. Provide:
   - The actual problem (acknowledging the reviewer's insight)
   - A better fix
   - A short note for the reviewer explaining the alternative approach (the user will deliver this manually)

3. **REJECT** — the comment is incorrect, based on a misunderstanding, or asks for something that conflicts with project conventions / requirements / existing design. Provide:
   - A factual rebuttal: what the reviewer got wrong
   - Evidence: cite the specific code (file:line), doc, or convention that supports your position
   - A polite, technical reply the user can paste back to the reviewer (3-5 sentences max, professional tone, no defensiveness)

4. **DEFER** — the comment is valid but out of scope for this PR (e.g. asks for a refactor of unrelated code, requests a feature beyond the PR's stated purpose). Provide:
   - Why it's out of scope
   - A suggestion for a follow-up issue / PR
   - A polite reply the user can post

5. **ANSWER** — the comment is a QUESTION, not a change request. Provide:
   - A direct answer based on the actual code
   - A reply text the user can post

6. **NEEDS_HUMAN** — the comment requires a judgment call, business context, or stakeholder input you don't have. Provide:
   - What's unclear and why
   - The specific question the user needs to answer

## Ground rules
- Be honest. Don't ACCEPT a bad comment to be polite, and don't REJECT a good one because it's annoying to fix.
- Read the actual code in the worktree before deciding. Don't trust the diff snippet alone.
- If the reviewer cites a specific behavior, verify it in the code. If they're factually wrong, that's a strong REJECT signal.
- For NIT-level comments, lean ACCEPT if the fix is trivial and matches the style guide; lean REJECT or DEFER if it would touch many files or conflict with existing conventions.
- If two comments contradict each other, note it — the meta-evaluation in Phase 2 will resolve it.
- DO NOT edit files. DO NOT run git commit. DO NOT run any gh write commands. Just analyze and report.

## Output format
A single block with:
  thread_id: <id>
  verdict: ACCEPT | ACCEPT_PARTIAL | REJECT | DEFER | ANSWER | NEEDS_HUMAN
  confidence: high | medium | low
  rationale: <2-4 sentences>
  fix_plan: <only if ACCEPT or ACCEPT_PARTIAL — file paths, line numbers, exact change>
  reply_text: <only if REJECT, DEFER, ANSWER, or ACCEPT_PARTIAL — the message the user can post>
  question_for_user: <only if NEEDS_HUMAN — the specific decision the user needs to make>
```

Wait for all per-comment agents to finish. Collect into `PHASE_1_VERDICTS`.

#### Phase 2 — Cross-Comment Reconciliation (single reconciler)

Many PRs have overlapping or contradictory comments. Launch a single reconciler agent. In Claude Code this is an Opus agent (`model: "opus"`); in non-Claude runtimes use a fresh sub-agent with role `RECONCILER`. Same reasoning as Phase 1: this is final analysis, and a wrong reconciliation gets baked into the executor's instructions.

```
You are reconciling multiple per-comment verdicts on GitHub PR #<number>.

You receive a list of independent verdicts from Phase 1. Your job:

1. **Detect contradictions** — two comments asking for opposite changes on the same code. Pick the one that's more consistent with the PR's stated purpose, the code style guide, and the higher-authority reviewer (e.g. a maintainer over a drive-by). Mark the other as REJECT with a note about the conflict.

2. **Detect duplicates** — multiple comments saying the same thing. Merge them into one ACCEPT, citing all source thread ids.

3. **Detect chains** — comment B builds on comment A. If A is REJECTED, re-evaluate B without A's premise.

4. **Sanity-check the REJECTs** — for each REJECT verdict, ask: "Is the rebuttal actually correct, or am I being defensive?" Re-read the code in the worktree if uncertain. Better to flip to ACCEPT than to die on a bad hill.

5. **Sanity-check the ACCEPTs** — for each ACCEPT verdict, ask: "Does the fix plan actually address the comment, or am I over-fitting?" Make sure the fix is minimal and scoped.

6. **Order the ACCEPTs by file** so the implementation step can batch by file and avoid re-reading.

## Phase 1 Verdicts
<PHASE_1_VERDICTS>

## Code Style Checklist
<compact checklist>

## PR Context
- Title: <title>
- Description: <body, truncated to ~50 lines if long>
- Files changed: <list>

## Output

### Final triage table
| thread_id | reviewer | category | location | final verdict | confidence | notes |

### Consolidated fix plan
For ACCEPT and ACCEPT_PARTIAL only, deduplicated and ordered by file:
- file: <path>
  - thread_id: <id> — <one-line description of change>
  - thread_id: <id> — <one-line description of change>

### Rebuttal text bundle
For REJECT, DEFER, ANSWER: the reply text from Phase 1, organized by thread_id, ready to copy-paste.

### Items needing user judgment
For NEEDS_HUMAN: the open questions.
```

Wait for this agent. Store as `TRIAGE_REPORT` and `CONSOLIDATED_FIX_PLAN`.

### Step 6: Confirm With User Before Touching Code

Before any file is edited, present the triage table and get confirmation. The user is the final arbiter.

```markdown
## Review Comment Triage for PR #<number>: "<title>"

Found <N> actionable comments after filtering. Worktree: `<FIX_WORKTREE>`

| # | Reviewer | Location | Category | Verdict | Confidence |
|---|---|---|---|---|---|
| 1 | @alice | `src/foo.go:42` | BUG | **ACCEPT** | high |
| 2 | @bob | `src/bar.go:18` | STYLE | **REJECT** | medium |
| 3 | @carol | `src/baz.ts:101` | DESIGN | **DEFER** | high |
| ... | ... | ... | ... | ... | ... |

**Summary**: <X> to accept, <Y> to reject (with rebuttal), <Z> to defer, <W> answers, <V> need your input.

**Reminder**: I will only **edit files in the worktree**. I will NOT commit, push, or post anything to GitHub.

How would you like to proceed?
1. Apply all ACCEPT items as-is (default)
2. Show me the full rebuttal text for the REJECTs first
3. Show me the full fix plan for the ACCEPTs first
4. Let me override specific verdicts before proceeding
5. Skip the implementation entirely — just give me the report
```

Wait for the user's response. **Do not skip this step.** The whole point of this skill is human-in-the-loop validation; silently proceeding undermines that.

If the user picks option 5, jump straight to Step 10 (Final Report) without editing any files. Skip the executor (Step 7) and adversarial review (Step 8) — there's nothing to execute or review.

### Step 7: Apply the Accepted Fixes (runtime-aware executor, uncommitted)

**Execution is delegated to a separate executor.** In Claude Code this is Sonnet: Opus did the analysis, and Sonnet is faster and cheaper for the mechanical work of reading files, matching surrounding style, and applying the planned edits. In non-Claude runtimes, use a worker/executor sub-agent with the same constraints. The fix plan from Phase 2 is detailed enough that no fresh judgment is required — the executor just executes it.

Launch a single executor agent with the consolidated fix plan as input. In Claude Code this is a **Sonnet agent** (`model: "sonnet"`); in non-Claude runtimes use the host's native worker/executor sub-agent. Group all accepted items into one agent run so it can see cross-file relationships and avoid redundant file re-reads.

```
You are the executor for a pre-approved PR review fix plan on PR #<number>: "<pr-title>".

A separate analyst already produced the verdicts and fix plans below. The user has reviewed and approved them. Your job is mechanical: read the affected files, apply each change exactly as planned, match surrounding code style, and stop. You are not re-evaluating verdicts — analysis is complete and the user signed off.

CRITICAL CONSTRAINTS:
- Work ONLY inside the worktree at <FIX_WORKTREE>. Never touch the user's main working directory.
- Do NOT run `git add`, `git commit`, `git commit --amend`, `git stash`, `git push`, or anything that records history. Edits must stay as **unstaged** modifications visible to `git diff`.
- Do NOT run any `gh` command that writes to GitHub (`gh pr review`, `gh pr comment`, `gh api POST/PATCH/DELETE`, etc.). Read-only `gh` is fine if you actually need it (you probably don't).
- Do NOT touch files that are not in the fix plan. Do NOT expand scope, refactor neighboring code, or add unrelated improvements.
- If a fix turns out to be infeasible after reading the actual code (e.g. the function moved, the variable doesn't exist, the planned change would break a callsite the analyst missed), STOP that specific fix and report it as `INFEASIBLE` with details. Do not silently substitute a different fix. Continue with the other fixes.

## Worktree
<FIX_WORKTREE>

## Consolidated fix plan (from Phase 2 reconciliation, user-approved)
<CONSOLIDATED_FIX_PLAN — file-grouped, with thread_id, file:line, exact change description>

## Code style checklist (for matching surrounding style)
<compact checklist from Step 4>

## Per-file workflow
For each file in the plan:
1. Read the file fully.
2. Apply each planned change for that file.
3. Match naming, imports, error handling, and idioms of the surrounding code.
4. If the analyst flagged "add a test" for any change AND the project has an obvious test location for the affected file, add one focused test alongside the change. One test per accepted comment is the rule of thumb.

## Output format
After all edits, report:

### Applied
- thread_id <id>: <file>:<lines> — <one-line description of what you actually wrote>
- ...

### Infeasible (couldn't apply)
- thread_id <id>: <file>:<lines> — <why it didn't work; what the analyst missed>

### New tests added
- <file> — covers thread_id <id>
- ...

Remember: NO commits, NO staging, NO pushes, NO GitHub writes. Just edits + report.
```

Wait for the executor to finish. Collect the result as `EXECUTOR_REPORT`. Move any `INFEASIBLE` items into the final report's "Needs Your Input" section so the user knows why those comments weren't addressed.

### Step 8: Multi-Angle Adversarial Review of the Applied Fixes

After the executor has applied the edits, run an **adversarial review** over the resulting diff. This is the safety net: the reviewer is an independent pass after analysis and execution, and its job is to catch cases where the executor mis-applied a plan, the plan itself was subtly wrong, or a fix introduced a new bug.

Launch multiple adversarial reviewers. In Claude Code, use Codex rescue and/or
native review agents when available. In non-Claude runtimes, use fresh
sub-agents with roles `ADVERSARIAL_REVIEWER:<ANGLE>`.

Required angles:

- `PLAN_TRACE_SCOPE`: every diff hunk traces to an approved thread/fix plan;
  no scope creep
- `CORRECTNESS_REGRESSION_SECURITY`: correctness, regressions, security, API
  or data breakage
- `COMPLETENESS_TESTS`: missed plan items, test coverage, verification gaps,
  disputed upstream verdicts

Use this prompt per angle:

```
Adversarial review of the uncommitted edits applied for PR #<number>: "<pr-title>" review-comment fixes.

You are the third reviewer in a multi-pass pipeline:
- The analysis phase produced the verdicts and fix plans for each reviewer comment.
- The executor applied the approved fix plans as uncommitted edits in a worktree.
- You are reviewing the resulting diff from the assigned angle: <ANGLE>.

CRITICAL: This review is READ-ONLY.
- Do NOT run `git commit`, `git add`, `git stash`, `git push`, or anything that records history.
- Do NOT run any `gh` command that writes to GitHub.
- You may read files, run the diff, run tests, and read the original PR — but no writes anywhere.

## Worktree
<FIX_WORKTREE>

## How to see what was changed
```bash
cd <FIX_WORKTREE>
git diff
```

## Original PR context
- Title: <pr title>
- Description: <pr body>
- Base ← head: <baseRefName> ← <headRefName>

## What the analysis phase approved (consolidated fix plan)
<CONSOLIDATED_FIX_PLAN>

## What the executor reported applying
<EXECUTOR_REPORT>

## Your job
For each change in the worktree diff, evaluate the checks in your assigned
angle. Use the list below for shared context, but focus your findings on
<ANGLE>:

1. **Does the change actually address the cited reviewer comment?** Cross-reference each diff hunk against its `thread_id` in the fix plan. If a hunk doesn't trace back to a thread, that's scope creep — flag it.

2. **Is the change correct?** Read the surrounding code and the call sites. Common failure modes to look for:
   - Off-by-one errors introduced while "fixing" boundary conditions
   - Nil/null/undefined checks added in the wrong place
   - Error handling that swallows errors instead of propagating them
   - Type changes that break callers
   - Imports added but not used (or used but not added)
   - Tests that don't actually test the claimed behavior

3. **Did the executor miss anything from the plan?** Cross-check the EXECUTOR_REPORT against the CONSOLIDATED_FIX_PLAN. If the plan said "fix X in foo.go and bar.go" but the executor only touched foo.go, flag it.

4. **Was the upstream verdict actually right?** You're allowed to dispute an upstream verdict if reading the code now makes you think the analyst got it wrong. Be specific: cite the file and line.

5. **Did the fixes introduce any NEW bugs?** Independent of the original comments — does the diff have any new logic errors, race conditions, resource leaks, or security issues?

## Output format

### Section A — Verified
For each fix that is correct and properly scoped: one-line confirmation with thread_id and file:line.

### Section B — Issues found
For each problem, report:
- Severity: critical / warning / nit
- thread_id (if traceable) or "scope creep" / "new bug"
- file:line
- What's wrong
- Suggested correction (do NOT apply it — just describe)

### Section C — Missed from the plan
Items in the CONSOLIDATED_FIX_PLAN that the EXECUTOR_REPORT doesn't account for.

### Section D — Disputed verdicts
Cases where, after reading the actual code, you believe the original verdict was wrong. Be specific.

### Section E — Verdict
- **CLEAN** — all fixes look correct, scoped, and complete. Safe for the user to commit as-is.
- **NEEDS_TOUCHUP** — minor issues; list what the user should fix before committing.
- **NEEDS_REWORK** — significant problems; recommend the user roll back specific files and re-run.

### Section F — Angle
<ANGLE>
```

Wait for every adversarial review angle. Collect as `ADVERSARIAL_REVIEW`,
grouped by angle, and synthesize the strictest verdict. **Do not auto-apply any
suggested corrections** — surface them in the final report and let the user
decide. The whole skill is human-in-the-loop; the adversarial review is one
more safety round, not a closer.

### Step 9: Verify Locally (Optional, Read-Only)

If the user is interested in verification before deciding what to commit, offer to run tests/linters in the worktree. Do not run them automatically — they may be slow or have side effects. Ask:

> "Want me to run the project's tests / typecheck / lint on the changed files in the worktree? (y/n)"

If yes, try in order based on what the project uses: `npm test`, `pnpm test`, `yarn test`, `pytest`, `go test ./...`, `cargo test`, `make test`, `tsc --noEmit`, `mypy`, `golangci-lint run`, `eslint`. Honor `package.json` / `Makefile` scripts when present. Report the result. Do NOT fix test failures automatically — surface them so the user can decide.

### Step 10: Final Report

```markdown
## PR Review Comments Triaged: #<number> "<pr-title>"

**PR**: #<number> by @<author> → <baseRefName> ← <headRefName>
**State**: <open/merged/closed> | Review decision: <approved/changes_requested/review_required/none>
**Worktree**: `<FIX_WORKTREE>` (detached HEAD on `<short-sha>`)
**Pipeline**: analysis → executor → multi-agent adversarial review
**Review mode**: <multi-agent | degraded-same-context-review>
**Degradation reason**: <none | explicit unsupported runtime | user forbade reviewer sub-agents | reviewer/model unavailable or at capacity>
**Comments triaged**: <total> total → <actionable> actionable → <accepted> accepted, <rejected> rejected, <deferred> deferred, <answered> answered, <human> need-input
**Adversarial review verdict**: <CLEAN / NEEDS_TOUCHUP / NEEDS_REWORK>

> **No commits were made. No changes were posted to GitHub.** All edits are uncommitted modifications in the worktree above. All rebuttal text is below — you decide whether to post any of it.

### Accepted & Implemented (uncommitted edits in worktree)
| # | Thread | Reviewer | Category | File | Change |
|---|---|---|---|---|---|
| 1 | [link](<html_url>) | @alice | BUG | `src/foo.go:42` | <one-line> |
| ... | ... | ... | ... | ... | ... |

To inspect: `cd <FIX_WORKTREE> && git diff`

### Rejected — Rebuttals to Post Manually
For each REJECT verdict, here is the suggested reply you can paste into the discussion. **This skill never posts to GitHub itself.**

#### Thread [<id>](<html_url>) — @bob, `src/bar.go:18`
> <original comment, blockquoted>

**Reply**:
> <3-5 sentence technical rebuttal with evidence — file:line citations included>

(repeat for each REJECT)

### Deferred — Follow-Up Suggestions
- Thread [<id>](<html_url>) by @carol — <one-line about why deferred and what follow-up issue to file>
  - Reply (optional):
    > <polite reply text>

### Answered — Replies to Questions
- Thread [<id>](<html_url>) by @dan — question about <topic>
  - Reply:
    > <direct answer based on the code>

### Needs Your Input
- Thread [<id>](<html_url>) by @eve — <the specific question that needs human judgment>

### Files Modified (in worktree only)
- `path/to/file1.ext` — <what and why, citing thread id>
- `path/to/file2.ext` — <what and why, citing thread id>

### Adversarial Review
**Verdict**: <CLEAN / NEEDS_TOUCHUP / NEEDS_REWORK>
**Angles**: plan_trace_scope, correctness_regression_security, completeness_tests

**Issues found by adversarial review** (none of these were auto-applied — review and decide):
- **[critical|warning|nit]** `file:line` (thread <id> | scope creep | new bug) — <what's wrong> → <suggested correction>
- ...

**Missed from the plan** (executor didn't apply):
- thread <id>: <file> — <what was missing>

**Disputed verdicts** (adversarial review disagrees with the analysis phase):
- thread <id>: <adversarial review reasoning>

(Omit any subsection that's empty.)

### Verification
<test/lint result if Step 9 was run, or "verification skipped — run yourself in the worktree if needed">

### Next Steps
- Inspect the edits: `cd <FIX_WORKTREE> && git diff`
- If you like them, stage and commit yourself: `cd <FIX_WORKTREE> && git checkout -B <some-branch> && git add ... && git commit ...`
- For each REJECT, paste the rebuttal into the discussion on GitHub manually
- Resolve threads on GitHub manually after the reviewer agrees
- When you're done with the worktree: `git worktree remove <FIX_WORKTREE>` (or `--force` if there are still uncommitted edits you want to discard)
```

## Notes

- **Three-phase pipeline**: analysis produces verdicts and fix plans, execution applies approved fixes, and multi-angle adversarial review checks the result. In Claude Code these roles map to Opus, Sonnet, and reviewer agents respectively; in non-Claude runtimes they map to native sub-agents with the same responsibilities. The split is deliberate — analysis is load-bearing, execution is mechanical, and adversarial review needs independent voices across multiple angles.
- **Read-only on GitHub, no commits locally.** Both rules are central to this skill — they're what make it safe to run on a PR you're not yet ready to update. Every sub-agent must obey both.
- **The user is the arbiter** — Step 6 is mandatory. Never silently auto-implement without showing the triage table. Adversarial review findings in Step 8 are surfaced for the user, never auto-applied.
- **Be honest in evaluation** — don't ACCEPT a bad comment to be polite, don't REJECT a good one to avoid work. Rigorous, justifiable triage is the entire point.
- **One comment, one citation** — every change in the fix plan must trace back to a specific thread id. If you can't cite a thread, you've expanded scope.
- **Verify reviewer claims against the actual code** — if a reviewer says "this leaks memory" and the code clearly doesn't, that's REJECT material. Don't take the reviewer's word for it; read the code in the worktree.
- **Detached HEAD is intentional** — there's no branch to push. The user explicitly creates a branch later if they want to publish the fix.
- **Worktree is left in place** at the end — the user reviews and cleans up themselves.
- All file reads and edits happen **inside the worktree**, never in the user's original working directory.
