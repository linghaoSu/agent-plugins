---
name: review-pr
description: Review a GitHub pull request locally - analyze diff, check code style compliance, find bugs and issues, report results without posting any comments to the PR
argument-hint: <pr-url-or-number>
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent]
---

# Review Pull Request

Review a GitHub pull request against the current repository's codebase and code style guide. Produce a structured review report **locally in the conversation only**.

## CRITICAL SAFETY RULE

**NEVER post comments, reviews, review comments, reactions, labels, or any other modifications to the PR on GitHub.** This means:
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
     git worktree remove "$REVIEW_WORKTREE" --force 2>/dev/null
   fi
   ```
   Never remove a worktree that existed before the review started — it may be the user's active working directory.

**If worktree setup fails** (e.g. branch not found, detached HEAD issues), fall back to reviewing from the diff only and note this in the output.

**Agent instructions**: When launching review agents in Step 4's Three-Round Review, if `REVIEW_WORKTREE` is set:
- Instruct code-reading agents to use `REVIEW_WORKTREE` as their working directory (e.g. "Read files from `<REVIEW_WORKTREE>/path/to/file` to get full context")
- Agents that only analyze the diff text do not need the worktree
- The worktree gives agents the ability to read surrounding code, follow imports, check type definitions, and understand the full context of changes

### Step 3: Code Style Guide

Determine the code style file path for this repo:

1. Get the repo's owner and name:
   ```bash
   gh repo view --json owner,name --jq '"\(.owner.login)/\(.name)"'
   ```
   If `gh` fails, fall back to the current directory name.
2. Resolve this plugin's source data directory:
   ```bash
   MARKETPLACE_PATH=$(cat ~/.claude/settings.local.json | jq -r '.extraKnownMarketplaces["claude-skills"].source.path // empty')
   [ -z "$MARKETPLACE_PATH" ] && MARKETPLACE_PATH=$(cat ~/.claude/settings.json | jq -r '.extraKnownMarketplaces["claude-skills"].source.path // empty')
   echo "$MARKETPLACE_PATH/issue-evaluator/data"
   ```
3. The code style file path is: `<data-dir>/<owner>/<repo>/code-style.md`

Check if this file exists:

- If it **does not exist**, generate it using **two Sonnet agents in parallel**:

  **Agent 1 — Static Code Analysis:**
  1. Read the project's config files (e.g. `.editorconfig`, `eslint*`, `prettier*`, `tsconfig*`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Makefile`, `package.json`, etc.)
  2. Sample 5-8 representative source files from the main directories
  3. Analyze and document:
     - Language(s) and framework(s) used
     - Naming conventions (variables, functions, classes, files)
     - Import/module organization patterns
     - Error handling patterns
     - Testing patterns and framework
     - Code organization and directory structure conventions
     - Comment style and documentation conventions
     - Type system usage (if applicable)
     - Common idioms and patterns specific to this codebase

  **Agent 2 — Reviewer Preference Mining:**
  Extract code style preferences from PR review comments on the last 100 commits:
  1. Get the last 100 merge commit PR numbers:
     ```bash
     git log --oneline -100 | grep -oP '#\K[0-9]+' | head -30
     ```
  2. For each PR (batch with `gh api` to stay within rate limits), fetch review comments:
     ```bash
     gh api "repos/{owner}/{repo}/pulls/<number>/comments" --jq '.[].body' 2>/dev/null
     gh api "repos/{owner}/{repo}/pulls/<number>/reviews" --jq '.[] | select(.body != "") | .body' 2>/dev/null
     ```
  3. Focus on comments expressing **style preferences or code conventions** (e.g. nit, rename, "use X instead of Y", import ordering, error handling preferences)
  4. Ignore comments about logic, bugs, or feature design
  5. Aggregate into a ranked list of **Reviewer Preferences**

  Synthesize both outputs into a single document with a `## Reviewer Preferences` section and write to `<data-dir>/<owner>/<repo>/code-style.md` with a metadata header:
  ```markdown
  <!-- generated: YYYY-MM-DD | commits-analyzed: <latest-commit-sha> -->
  ```

- If it **already exists**, run a lightweight staleness check (same as `/evaluate-issue`):
  1. Extract the `commits-analyzed` sha from the metadata header
  2. Count commits since: `git rev-list --count <sha>..HEAD 2>/dev/null`
  3. Also calculate days since generation from the `generated: YYYY-MM-DD` date in the metadata
  4. If 400+ commits **or** 30+ days old → launch background update agent; proceed with existing guide
  4. Otherwise → use the existing guide as-is

Read the code style guide and extract a compact checklist (max 15 items) of the most important rules.

### Step 4: Three-Round Sequential Review

This review follows a **three-round sequential pipeline**. Each round builds on the previous round's output, producing increasingly validated findings.

---

#### Round 1 — Multi-Model Self Review + Static Analysis

Launch the following agents and tools **all in parallel**:

**Agent 1A — Bug, Logic & Security Review (Sonnet, `model: "sonnet"`):**

Review the PR diff for:
1. **Bugs**: Logic errors, off-by-one errors, nil/null pointer dereferences, race conditions, resource leaks
2. **Security**: Injection vulnerabilities, auth/authz issues, sensitive data exposure, insecure defaults
3. **Error handling**: Missing error checks, swallowed errors, incorrect error propagation
4. **Edge cases**: Unhandled boundary conditions, empty inputs, concurrent access
5. **Breaking changes**: API contract changes, behavioral changes that could affect callers

Provide the agent with the full PR diff, description, and changed files list. Instruct: "Follow the Review Tone & Principles in the parent skill — Linus-style: blunt, direct, name the concrete failure mode. Attack the code, not the author. For each issue, report: severity (critical/warning/nit), file and line, what's wrong (specific failure mode), and how to fix it. If no issues found, respond with LGTM."

**Agent 1B — Code Style & Quality Review (Sonnet, `model: "sonnet"`):**

Review the PR diff for compliance with the repo's code style:
1. **Naming conventions**: Variables, functions, types, files match repo conventions
2. **Import organization**: Grouping and ordering follows repo patterns
3. **Error handling patterns**: Matches the repo's established patterns
4. **Testing**: New/changed code has appropriate test coverage; tests follow repo patterns
5. **Code organization**: Changes are in the right place structurally
6. **Documentation**: Comments and docs match repo style
7. **Common idioms**: Code uses the repo's preferred patterns and idioms

Provide the agent with the full PR diff and the compact code style checklist from Step 3. Instruct: "Follow the Review Tone & Principles in the parent skill. CRITICAL: style findings must be grounded in THIS repo's conventions (the checklist below or patterns in surrounding code) — not your personal preferences or generic best practices. If you can't cite a repo rule or established pattern, drop the finding. Only flag issues within the changed lines. Do NOT flag pre-existing style patterns. For each issue, report: severity (critical/warning/nit), file and line, which specific repo rule or established pattern it violates (cite it), and how to fix it. Be blunt. If no issues found, respond with LGTM."

**Agent 1C — Existing Review Context (Sonnet, `model: "sonnet"`):**

Analyze existing PR reviews and comments to avoid duplicating feedback:
1. Read through all existing review comments and inline comments fetched in Step 1
2. Summarize what has already been flagged by human reviewers
3. Note any open discussion threads or unresolved conversations
4. Identify areas that have NOT been reviewed yet

Provide the agent with the PR metadata (reviews, comments, review comments) and the list of changed files.

**Agent 1D — Haiku Independent Review (`model: "haiku"`):**

Launch a **Haiku agent** as an independent third perspective. Haiku's different model characteristics often catch different classes of issues. Provide it with the full PR diff, description, and code style checklist. Instruct:

"You are an independent code reviewer in the spirit of Linus Torvalds: blunt, direct, technically sharp. Call bad code bad and name the concrete failure mode. Attack the code, not the author. Style findings must cite a rule from the code style checklist provided — do NOT impose personal preferences or generic best practices; this repo's conventions win. Review this PR diff for bugs, security issues, logic errors, and code style violations. For each issue, report: severity (critical/warning/nit), file and line, what's wrong, and how to fix it. If no issues found, respond with LGTM. Be concise."

**Agent 1F — Linked Issue Compliance (Sonnet, `model: "sonnet"`):**

**Skip this agent if `LINKED_ISSUES` is empty.**

Review whether the PR diff adequately addresses the requirements of each linked issue. Provide the agent with the full PR diff, PR description, and the full text of each linked issue (title, body, comments). Instruct:

"For each linked issue, evaluate:
1. **Requirement coverage**: Does the diff address all requirements/acceptance criteria described in the issue? List each requirement and whether it's addressed, partially addressed, or missing.
2. **Fix correctness**: For issues marked as `fixes`, does the code change actually fix the reported problem? Could the described bug/feature request still reproduce after this change?
3. **Scope alignment**: Does the PR stay within scope of the issue, or does it include unrelated changes? Does it miss parts of the issue scope?
4. **Edge cases from issue discussion**: Do the issue comments mention edge cases, constraints, or requirements that the PR doesn't handle?

For each linked issue, report:
- Issue reference (e.g. #123)
- Relationship: fixes / references
- Verdict: **FULLY ADDRESSED** / **PARTIALLY ADDRESSED** / **NOT ADDRESSED**
- Details: what's covered, what's missing or incomplete
- Severity of gaps (critical/warning/nit)

If all linked issues are fully addressed, respond with: 'All linked issues are fully addressed by this PR.'"

**Tool 1E — IDE Diagnostics:**

Call `mcp__ide__getDiagnostics` to collect compiler/linter diagnostics for all files changed in the PR. These are objective, machine-verified findings (type errors, unused imports, syntax issues, etc.) that serve as ground truth for subsequent rounds. Filter the results to only include diagnostics for files in the PR's changed files list.

**Wait for all Round 1 agents and diagnostics to complete.** Collect:
- `ROUND_1_SONNET` — output from Agent 1A + 1B
- `ROUND_1_HAIKU` — output from Agent 1D
- `ROUND_1_DIAGNOSTICS` — output from Tool 1E
- `ROUND_1_CONTEXT` — output from Agent 1C
- `ROUND_1_ISSUE_COMPLIANCE` — output from Agent 1F (empty if no linked issues)
- `ROUND_1_FINDINGS` = all of the above combined

---

#### Round 2 — Codex Adversarial Review + Evaluation of Round 1

**This round must wait for Round 1 to complete.** Launch a single Codex agent with `subagent_type: "codex:codex-rescue"`:

```
Adversarial code review of PR #<number>: "<pr-title>".

TONE: Linus-style — blunt, direct, technically sharp. Call bad code bad and name the concrete failure mode (race, leak, UB, broken invariant, API misuse, O(n²), etc.). No hedging, no corporate softening. Attack the code, never the author.

STYLE GROUNDING: Style findings must cite a rule from the repo's code style checklist below, or an established pattern in the surrounding code. Personal preferences and generic "best practices" from other projects are OUT — this repo's conventions are the law. If a Round 1 style finding isn't grounded in this repo, DISPUTE it.

You are the second reviewer in a multi-round review pipeline. Your jobs:
1. Independently review the PR diff for bugs, security issues, design problems, and code style violations.
2. Evaluate the first-round review findings below — challenge any findings you believe are false positives, confirm findings you agree with, and flag anything the first round missed.
3. If this PR links to issues, evaluate whether the issue compliance assessment from Round 1 is accurate — verify the PR actually addresses the linked issue requirements.

IMPORTANT: This is a READ-ONLY review. Do NOT run any commands that modify the PR, post comments, or write to GitHub.

## PR Description
<pr body>

## Code Style Rules for This Repo
<compact style checklist from Step 3>

## PR Diff
<the full diff>

## Round 1 Findings — Sonnet
<ROUND_1_SONNET — full output from Agent 1A + 1B>

## Round 1 Findings — Haiku (independent)
<ROUND_1_HAIKU — full output from Agent 1D>

## IDE Diagnostics (compiler/linter — ground truth)
<ROUND_1_DIAGNOSTICS — machine-verified findings, treat these as facts>

## Linked Issue Compliance (if applicable)
<ROUND_1_ISSUE_COMPLIANCE — assessment of whether this PR addresses its linked issues; empty if no linked issues>

SCOPE RULE: Only report issues within the lines changed in the diff. Do NOT flag lint, style, or formatting issues in unchanged/surrounding code. Even within the diff, only flag style issues if they introduce NEW inconsistencies with the repo's conventions.

Your output should have THREE sections (Section C only if linked issues exist):

### Section A: Independent Findings
For each NEW issue you found (not already in Round 1), report:
- Severity (critical / warning / nit)
- File and line
- What's wrong and how to fix it
- Which style rule it violates (if applicable)

If you found NO new issues, say: "No additional issues found."

### Section B: Evaluation of Round 1
For each Round 1 finding (from BOTH Sonnet and Haiku), give a verdict:
- **CONFIRMED** — you agree this is a real issue. Briefly state why.
- **DISPUTED** — you believe this is a false positive or overstated. Explain why.
- **UPGRADED/DOWNGRADED** — you agree the issue exists but disagree on severity. State the correct severity and why.

Note: IDE Diagnostics are machine-verified facts — do not dispute them. You may add context or suggest fixes for them.

### Section C: Issue Compliance Evaluation (only if linked issues exist)
For each linked issue in the Round 1 issue compliance assessment:
- **CONFIRMED** — you agree with the compliance verdict. Briefly state why.
- **DISPUTED** — you disagree (e.g. Round 1 said FULLY ADDRESSED but you see gaps, or vice versa). Explain.
- Note any issue requirements that both Round 1 and you believe are missing from the PR.

If Round 1 was LGTM across all sources and you agree, say: "Confirmed: LGTM"
```

**Wait for Round 2 to complete.** Collect its output as `ROUND_2_FINDINGS`.

---

#### Round 3 — Opus Final Synthesis Review

Launch a single **Opus agent** (`model: "opus"`) that acts as the final arbiter. Opus is the most capable model and is used here to make the highest-quality final judgment:

```
You are the final reviewer in a multi-model code review pipeline for PR #<number>: "<pr-title>".

TONE: Write the final report in Linus Torvalds' voice — blunt, direct, technically sharp. Name concrete failure modes, not vague concerns. No hedging, no praise padding, no corporate softening. Attack the code, never the author. If something is wrong, say it plainly.

STYLE GROUNDING: Every style/quality finding in the final report must be traceable to a rule in the repo's code style guide or an established pattern in the repo's surrounding code. Drop any Round 1/2 finding that amounts to personal preference or generic best-practice with no repo-grounded citation — list it under "Disputed & Dropped" with a one-line reason.

Four sources provided input: Sonnet (Round 1), Haiku (Round 1), IDE Diagnostics (Round 1), and Codex (Round 2). Your job is to produce the definitive review by synthesizing all sources. You must:

1. For each finding, count how many independent sources flagged it and make a final judgment:
   - IDE Diagnostics findings are **ground truth** — always include them as `[verified]`
   - If 3+ AI models agree → `[high]` confidence
   - If 2 AI models agree → `[high]` confidence
   - If 1 AI model found it and others didn't comment → `[medium]`, verify by reading the code yourself
   - If 1 AI model found it and another disputed it → re-examine the code to break the tie
   - If a finding is a clear false positive → DROP it and note why

2. Assign final severity (critical/warning/nit) and a confidence tag:
   - `[verified]` — confirmed by IDE Diagnostics (compiler/linter)
   - `[high]` — multiple AI models agree, or you verified independently
   - `[medium]` — single AI model found it, you believe it's valid
   - `[low]` — uncertain, included for completeness

3. Deduplicate against issues already flagged by human reviewers (from the existing review context below).

4. **Four-principle check** (from the plugin's PRINCIPLES.md). Add a finding
   under the appropriate severity if the diff violates any of:
   - *Think before coding* — silent assumptions in the diff (a branch
     chosen without justification, an interpretation picked without a
     comment explaining why). Flag as `warning` unless clearly load-bearing.
   - *Simplicity first* — speculative abstractions, unused config knobs,
     error handling for impossible states, or obvious "if 200 lines could
     be 50" bloat. Flag as `warning`; upgrade to `critical` if it masks a
     real bug.
   - *Surgical changes* — changed lines that don't trace to the PR's stated
     purpose (drive-by refactors, adjacent-code "improvements", formatting
     churn in untouched files). Flag as `warning`.
   - *Goal-driven execution* — a fix/feature with no observable
     verification (no test, no command, no behavior change a reviewer can
     run). For `fix:` PRs, this is `critical` — the fix can't be verified.
     For others, `warning`.

## PR Description
<pr body>

## PR Diff
<the full diff>

## Round 1 Findings — Sonnet
<ROUND_1_SONNET>

## Round 1 Findings — Haiku
<ROUND_1_HAIKU>

## IDE Diagnostics (ground truth)
<ROUND_1_DIAGNOSTICS>

## Round 2 Findings (Codex) + Round 1 Evaluation
<ROUND_2_FINDINGS>

## Existing Human Review Comments
<ROUND_1_CONTEXT>

## Linked Issue Compliance (if applicable)
Round 1 assessment: <ROUND_1_ISSUE_COMPLIANCE>
Round 2 evaluation: <relevant Section C from ROUND_2_FINDINGS>

Produce a structured review in this exact format:

### Critical Issues
- **[critical]** `file:line` — <description> `[high]`|`[medium]`|`[low]`

### Warnings
- **[warning]** `file:line` — <description> `[high]`|`[medium]`|`[low]`

### Nits
- **[nit]** `file:line` — <description>

### Disputed & Dropped
<findings from either round that you determined to be false positives, with brief explanation>

### Already Flagged by Reviewers
<issues human reviewers have already raised — not duplicated above>

### Linked Issue Compliance
For each linked issue (if any), give the final verdict:
- **#<number>** (<fixes|references>) — **FULLY ADDRESSED** / **PARTIALLY ADDRESSED** / **NOT ADDRESSED**
  - What's covered and what's missing
  - If PARTIALLY/NOT ADDRESSED with `fixes` relationship, this is a critical finding — the PR claims to fix the issue but doesn't fully do so

### Positive Notes
<things done well in this PR>

### Verdict
<LGTM / Approve with nits / Request changes — with brief justification>
Note: If the PR claims to fix an issue (via fix/close/resolve keywords) but the linked issue is NOT FULLY ADDRESSED, this should weigh heavily toward "Request changes".

Omit empty sections.
```

**Wait for Round 3 to complete.**

### Step 5: Present Final Report

Take the Round 3 agent's output and present it with the PR header prepended:

```markdown
## PR Review: <pr-title>

**PR**: #<number> by @<author>
**Base**: <base-branch> <- <head-branch>
**Files changed**: <count> (+<additions> -<deletions>)
**Status**: <open/merged/closed> | Review decision: <approved/changes_requested/review_required/none>
**Linked issues**: <#N (fixes), #M (references), ... or "None">
**Review pipeline**: Round 1 (Sonnet + Haiku + IDE Diagnostics + Issue Compliance) → Round 2 (Codex + evaluation) → Round 3 (Opus synthesis)

### Summary
<2-3 sentence summary of what this PR does>

<Round 3 structured output follows: Critical Issues, Warnings, Nits, Disputed & Dropped, Already Flagged, Linked Issue Compliance, Positive Notes, Verdict>
```

Omit empty sections.

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
  git worktree remove "$REVIEW_WORKTREE" --force 2>/dev/null
fi
```

This step **must always run**, even if the review encountered errors. Never remove a reused worktree — it belongs to the user.

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
