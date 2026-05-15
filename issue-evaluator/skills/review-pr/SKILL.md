---
name: review-pr
description: Multi-agent, multi-angle, multi-round local review of a GitHub PR for bugs, security, issue coverage, and repo-specific style. Read-only on GitHub.
argument-hint: <pr-url-or-number>
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent]
---

# Review Pull Request

Review a GitHub pull request against the current repository's codebase and code style guide. Produce a structured review report **locally in the conversation only**.

## CRITICAL SAFETY RULE

**NEVER post comments, reviews, review comments, reactions, labels, or any other modifications to the PR on GitHub.** This skill is read-only with respect to GitHub and the PR branch. It may create a temporary local review worktree for source reads, and it may remove only that worktree when the review finishes.

This means:
- Do NOT run `gh pr review`
- Do NOT run `gh pr comment`
- Do NOT run `gh api` with POST/PUT/PATCH/DELETE methods against the PR
- Do NOT run any `gh` command that writes to the PR or repository
- Only use `gh` for **read-only** operations (fetching PR details, diff, comments, reviews)
- All review output goes to the conversation — never to GitHub

This rule applies throughout the entire workflow, including any sub-agents launched during the review.

## Review Tone & Principles

**Read `../../REVIEW-RUBRIC.md` for the full review rubric.** All review output — from every agent in every round, and the final synthesis — must follow it. Summary of the key rules:

- **Linus-style**: blunt, direct, technically sharp. Name the concrete failure mode. No hedging. Attack the code, never the author.
- **Repo-grounded**: style findings must cite a rule from the repo's code style guide or an established pattern. No personal preferences, no generic "best practices."
- **Signal over noise**: every finding must be actionable and specific. LGTM if nothing worth saying.
- **Scope discipline**: only review the diff. Pre-existing issues are out of scope.
- **Avoid anti-patterns**: no style nitpicking on logic PRs, no phantom bugs, no repeating human reviewers, no generic advice, no re-litigating architecture.

Every agent prompt below implicitly inherits these principles. Agents that produce review text must write in this voice.

## Arguments

The user provided: `$ARGUMENTS`

This should be a GitHub PR URL (e.g. `https://github.com/owner/repo/pull/123`) or a PR number (e.g. `123` or `#123`).

## Multi-Agent Review Routing

Before launching any review agent, read `../../PRINCIPLES.md` and
`../../WORKFLOW-CONTRACTS.md`. Apply the shared **Multi-Agent Review Routing**
contract and the shared **Output, Token, And Error Contract**. This workflow is
pre-authorized to launch reviewer and synthesis sub-agents. The roles for this
workflow are bug/security review, style review, existing-review context,
independent check, linked-issue compliance, adversarial review, and final
synthesis.

Run these roles as independent sub-agents when supported. Fall back to
same-context review only when reviewer sub-agents are explicitly unsupported by
the host/runtime, the user explicitly forbids them, or the selected
reviewer/model is explicitly unavailable or at capacity. In that degraded mode,
record `degraded-same-context-review`, keep the same roles and rounds
sequentially in the main context, and do not present the result as independent
multi-agent review.

## Workflow

### Step 1: Fetch PR Details

Use `gh` CLI (read-only) to fetch the full PR context:

1. Parse the PR number and optional owner/repo from the argument.
   - If a full URL is provided, extract the owner/repo and PR number.
   - If only a number is provided, use the current repo.

2. Fetch PR metadata and diff in parallel:

   **A — PR metadata:**
   ```bash
   gh pr view <number> [--repo <owner/repo>] --json title,body,author,labels,state,baseRefName,headRefName,files,additions,deletions,commits,reviewDecision,reviews,comments,createdAt,updatedAt
   ```

   **B — PR diff:**
   ```bash
   gh pr diff <number> [--repo <owner/repo>]
   ```

   **C — PR review comments (inline comments on code):**
   ```bash
   gh api "repos/<owner>/<repo>/pulls/<number>/comments" --jq '.[] | {path, line: .original_line, body, user: .user.login, created_at}'
   ```

   Token budget: by default, pass reviewers at most 25 changed files, 400 diff
   lines per file, 100 inline comments, and 50 linked-issue comments. If the PR
   is larger, prioritize changed files with executable code, security-sensitive
   paths, failing diagnostics, and existing human comments. Set `truncated:
   true`, list omitted files/comment pages, and provide a continuation command
   in the final `next_action`.

3. If the PR is already merged or closed, note this in the output but still proceed with the review.

4. **Extract linked issues**: Scan the PR title and body for issue references:
   - Look for closing keywords (case-insensitive): `fix`, `fixes`, `fixed`, `close`, `closes`, `closed`, `resolve`, `resolves`, `resolved` — followed by `#<number>`, `<owner>/<repo>#<number>`, or a full GitHub issue URL
   - Also note plain `#<number>` references without closing keywords (mentioned but not necessarily fixed)
   
   For each referenced issue, fetch its details:
   ```bash
   gh issue view <number> [--repo <owner/repo>] --json title,body,labels,state,comments
   ```
   
   Store as `LINKED_ISSUES` with:
   - Issue number, title, body, state, labels
   - Relationship type: `fixes` (has closing keyword) or `references` (plain mention)
   
   If no issues are referenced, set `LINKED_ISSUES` to empty and skip issue compliance checks in subsequent steps.

### Step 2: Prepare Review Worktree

Check if the current working directory belongs to the PR's target repository. If so, set up an isolated worktree on the PR's head branch so that all review agents have **full code context** (not just the diff).

1. Determine if the current repo matches the PR's repo:
   ```bash
   CURRENT_REPO=$(gh repo view --json owner,name --jq '"\(.owner.login)/\(.name)"' 2>/dev/null)
   ```
   Compare `CURRENT_REPO` with the PR's owner/repo. If they match (or the PR was specified by number only, implying the current repo), proceed with worktree setup. If they don't match (cross-repo review), skip this step — the review will rely on the diff only.

2. Check if a worktree for this branch already exists:
   ```bash
   HEAD_BRANCH="<headRefName from PR metadata>"
   EXISTING_WORKTREE=$(git worktree list --porcelain | grep -B2 "branch refs/heads/$HEAD_BRANCH" | grep "^worktree " | sed 's/^worktree //')
   ```
   - Also check for detached worktrees on the same commit:
     ```bash
     [ -z "$EXISTING_WORKTREE" ] && EXISTING_WORKTREE=$(git worktree list | grep "$HEAD_BRANCH" | awk '{print $1}')
     ```

3. **If an existing worktree is found** (`EXISTING_WORKTREE` is non-empty):
   - Set `REVIEW_WORKTREE="$EXISTING_WORKTREE"`
   - Set `WORKTREE_REUSED=true` (so cleanup step knows NOT to remove it)
   - Log: "Reusing existing worktree at `$EXISTING_WORKTREE` for branch `$HEAD_BRANCH`"

4. **If no existing worktree is found**, create one:
   ```bash
   git fetch origin "$HEAD_BRANCH"
   REPO_ROOT=$(git rev-parse --show-toplevel)
   REPO_NAME=$(basename "$REPO_ROOT")
   REVIEW_WORKTREE="$REPO_ROOT/../.claude-worktrees/$REPO_NAME/pr-review-<pr-number>"
   mkdir -p "$(dirname "$REVIEW_WORKTREE")"
   git worktree add "$REVIEW_WORKTREE" "origin/$HEAD_BRANCH" --detach
   WORKTREE_REUSED=false
   ```

5. Store `REVIEW_WORKTREE` and `WORKTREE_REUSED`. All subsequent review agents that need to **read source files** (not just analyze the diff) must be instructed to read from this path.

6. **Cleanup rule**: After the review is complete (after Step 6), clean up **only if we created the worktree** (`WORKTREE_REUSED=false`):
   ```bash
   if [ "$WORKTREE_REUSED" = "false" ]; then
     git worktree remove "$REVIEW_WORKTREE" 2>/dev/null
   fi
   ```
   Never remove a worktree that existed before the review started — it may be the user's active working directory. If cleanup fails, report the leftover path instead of forcing removal.

**If worktree setup fails** (e.g. branch not found, detached HEAD issues), fall back to reviewing from the diff only and note this in the output.

**Agent instructions**: When launching review agents in Step 4's Three-Round Review, if `REVIEW_WORKTREE` is set:
- Instruct code-reading agents to use `REVIEW_WORKTREE` as their working directory (e.g. "Read files from `<REVIEW_WORKTREE>/path/to/file` to get full context")
- Agents that only analyze the diff text do not need the worktree
- The worktree gives agents the ability to read surrounding code, follow imports, check type definitions, and understand the full context of changes

### Step 3: Code Style Guide

Apply `../../WORKFLOW-CONTRACTS.md` § Code Style Guide Lifecycle:

1. Resolve the guide path.
2. Generate it if absent.
3. Run the Freshness Check if present; stale guides may regenerate in the
   background while review proceeds with the existing guide.
4. Extract a compact checklist of at most 15 rules before launching style
   reviewers.

### Step 4: Three-Round Multi-Agent Review

This review follows a **three-round multi-agent, multi-angle pipeline**. Each
round builds on the previous round's output, producing increasingly validated
findings. If degraded, run the same role prompts sequentially in the main
context and label the report `degraded-same-context-review`.

---

#### Round 1 — Multi-Agent Self Review + Static Analysis

Launch the following agents and tools **all in parallel**:

Use `../../prompts/review-pr-round1.md` to launch these roles:
`ROUND_1_BUG_SECURITY`, `ROUND_1_STYLE_QUALITY`,
`ROUND_1_EXISTING_CONTEXT`, `ROUND_1_INDEPENDENT`, and
`ROUND_1_ISSUE_COMPLIANCE` when `LINKED_ISSUES` is non-empty.

**Tool 1E — IDE Diagnostics:**

Call `mcp__ide__getDiagnostics` to collect compiler/linter diagnostics for all files changed in the PR. These are objective, machine-verified findings (type errors, unused imports, syntax issues, etc.) that serve as ground truth for subsequent rounds. Filter the results to only include diagnostics for files in the PR's changed files list.

**Wait for all Round 1 agents and diagnostics to complete.** Collect:
- `ROUND_1_PRIMARY` — output from Agent 1A + 1B
- `ROUND_1_INDEPENDENT` — output from Agent 1D
- `ROUND_1_DIAGNOSTICS` — output from Tool 1E
- `ROUND_1_CONTEXT` — output from Agent 1C
- `ROUND_1_ISSUE_COMPLIANCE` — output from Agent 1F (empty if no linked issues)
- `ROUND_1_FINDINGS` = all of the above combined

---

#### Round 2 — Multi-Angle Adversarial Review + Evaluation of Round 1

**This round must wait for Round 1 to complete.** Launch adversarial reviewers
for separate angles. In Claude Code, use Codex rescue and/or native review
agents when available. In non-Claude runtimes, use the host's native sub-agent
mechanism and label each output `ROUND_2_ADVERSARIAL_REVIEW:<ANGLE>`.
Required Round 2 angles:

- `CORRECTNESS_SECURITY`: bugs, security, regressions, API/data breakage
- `STYLE_SCOPE`: repo style grounding, maintainability, scope control
- `TRACEABILITY`: linked issue coverage, test evidence, review finding validity

Use `../../prompts/review-pr-round2-adversarial.md` for each angle.

**Wait for all Round 2 angles to complete.** Collect their outputs as
`ROUND_2_FINDINGS`, grouped by angle.

---

#### Round 3 — Final Synthesis Review

Launch a single final synthesis reviewer. In Claude Code, use an **Opus
agent** (`model: "opus"`) as the final arbiter. In non-Claude runtimes, use a
fresh synthesis sub-agent. This review workflow is already authorized for
reviewer sub-agents. Fall back to same-context synthesis only when
synthesis/reviewer sub-agents are explicitly unsupported by the host/runtime,
the user explicitly forbids them, or the selected synthesis reviewer/model is
explicitly unavailable or at capacity; record `degraded-same-context-review`
and do not present it as independent multi-agent synthesis.

Use `../../prompts/review-pr-round3-synthesis.md` with the PR description,
diff, Round 1 outputs, diagnostics, Round 2 outputs, existing human review
comments, and linked issue compliance data.

**Wait for Round 3 to complete.**

### Step 5: Present Final Report

Take the Round 3 agent's output and present it with the PR header using
`../../templates/review-pr-final-report.md`. Omit empty sections.

### Step 6: Suggest Next Steps

After presenting the report:
- If critical issues were found: "This PR has critical issues that should be addressed before merging."
- If only warnings/nits: "This PR looks generally good with some suggestions for improvement."
- If clean: "This PR looks good — no significant issues found."

Remind the user: "This review is local only — no comments have been posted to the PR."

### Step 7: Cleanup Worktree

If a worktree was **created** (not reused) in Step 2, clean it up:
```bash
if [ "$WORKTREE_REUSED" = "false" ]; then
  git worktree remove "$REVIEW_WORKTREE" 2>/dev/null
fi
```

This step **must always run**, even if the review encountered errors. Never remove a reused worktree — it belongs to the user.
If cleanup fails, leave the worktree in place and report it under `errors:
[{type: degraded, ...}]`; do not force-remove review worktrees.

## Phase Gates

- **⛔ GATE after Step 1 (Fetch):** PR diff must be non-empty. If the PR has no code changes (docs-only, CI config), adjust the review scope or skip code review agents entirely.
- **⛔ GATE after Step 3 (Code Style Guide):** The style guide must be loaded before launching Round 1 agents. Style review without a repo-specific guide produces generic findings that violate the "repo-grounded" principle.

## Notes

- **Read-only**: This skill NEVER writes to the PR or repository on GitHub. All output stays in the conversation.
- Always use `gh` CLI for GitHub interactions, not web fetch.
- Focus the review on the actual diff — don't flag issues in unchanged code.
- When the PR description explains a deliberate design choice, respect it rather than flagging it as an issue.
- If the diff is very large (1000+ lines), focus on the most important files and note that a full review may require multiple passes.
- Deduplicate against existing reviewer feedback — don't repeat what humans have already said.
