# Issue Evaluator Plugin

Evaluate GitHub issues against the current repo: diagnose, check fix status, analyze code style, provide reproduction and fix plans, review pull requests, and run runtime-aware adversarial review after fixing.

All skills that write or review code apply the four principles in
[`PRINCIPLES.md`](./PRINCIPLES.md): Think Before Coding · Simplicity First ·
Surgical Changes · Goal-Driven Execution.

Multi-agent validation is runtime-aware. Invoking a review workflow is standing
authorization to launch reviewer and synthesis sub-agents. Review workflows are
multi-agent, multi-angle, and multi-round by default: they keep independent
angles for correctness/security, repo style/scope, and issue/test/plan
traceability, then rerun the required angles after fixes or touchups. In Claude
Code, the skills keep the Opus/Sonnet/Haiku/Codex role split. In non-Claude
runtimes, they use the host's native sub-agent mechanism for the same roles and
report the pipeline by role instead of model name.

Shared runtime routing, code-style-guide, GitHub read-only, and adversarial
review-loop contracts live in [`WORKFLOW-CONTRACTS.md`](./WORKFLOW-CONTRACTS.md).

## Commands

### `/evaluate-issue <issue-url-or-number>`

Evaluates a GitHub issue against the current codebase.

**What it does:**
1. Fetches issue details via `gh` CLI
2. On first run, analyzes the repo's code style and saves to `.issue-evaluator/code-style.md`
3. Launches parallel agents to:
   - Search the codebase for the issue's root cause
   - Check git history for existing fixes
4. Produces a structured report with:
   - Issue confirmation status
   - Root cause analysis
   - Reproduction steps
   - Concrete fix plan

**Usage:**
```bash
/evaluate-issue https://github.com/owner/repo/issues/123
/evaluate-issue 123
/evaluate-issue #123
```

### `/fix-issue [--compete|--tournament] <issue-url-or-number|description>`

Implements a GitHub issue fix from a prior evaluation report, a live GitHub
issue, or a free-form fix description. It creates or reuses an isolated
worktree, writes a verifiable done check before coding, applies the minimal fix,
runs relevant tests, and commits inside the fix worktree.

With `--compete` or `--tournament`, it routes through
`agent-playbook/implementation-tournament` before normal implementation:
multiple independent candidate fixes are produced in isolated worktrees,
verified against the same done check, reviewed independently, and only the
selected patch is applied back to the active fix worktree. If no candidate
wins, the workflow stops instead of writing a fallback fix.

**Usage:**
```bash
/fix-issue https://github.com/owner/repo/issues/123
/fix-issue --compete 123
/fix-issue --tournament "fix intermittent 401 during token refresh"
```

### `/review-pr <pr-url-or-number>`

Reviews a GitHub pull request locally without posting any comments or modifications to the PR.

**What it does:**
1. Fetches PR details, diff, and existing review comments via `gh` CLI (read-only)
2. Loads the repo's code style guide (generates on first run)
3. Launches multi-agent, multi-angle review rounds covering:
   - Bug, logic & security review
   - Code style & quality compliance
   - Existing reviewer feedback deduplication
   - Linked issue/test/plan traceability when applicable
4. Runs adversarial and synthesis rounds before producing a structured review report in the conversation with severity-ranked issues
5. **Never posts comments, reviews, or any modifications to the PR on GitHub**

**Usage:**
```bash
/review-pr https://github.com/owner/repo/pull/123
/review-pr 123
/review-pr #123
```

### `/fix-pr-comments <pr-url-or-number> [--include-resolved]`

Triages review comments on a GitHub pull request, applies fixes for valid ones as **uncommitted local edits** in an isolated worktree, and produces rebuttal text for invalid ones. Fully read-only on GitHub, never creates a commit.

**Pipeline**: analysis → executor → multi-agent adversarial review. In Claude Code this maps to Opus → Sonnet → multiple reviewer roles; in non-Claude runtimes it maps to native sub-agents with the same roles. The split is deliberate — verdicts and fix plans are load-bearing, execution is mechanical, and final review needs independent voices across multiple angles.

**What it does:**
1. Fetches PR metadata, diff, inline comments, review summaries, conversation comments, and thread resolution state via `gh` CLI (read-only)
2. Filters out bots, the PR author's own comments, resolved threads, and noise
3. Loads the repo's code style guide (generates on first run)
4. **Analysis (parallel)**: launches per-comment analyst agents to evaluate each comment as **ACCEPT / ACCEPT_PARTIAL / REJECT / DEFER / ANSWER / NEEDS_HUMAN** with rationale and detailed fix plan
5. **Reconciliation**: a single reconciler agent resolves contradictions and duplicates across the per-comment verdicts
6. Shows the triage table and asks for confirmation before touching any files
7. **Executor**: applies the approved fixes in a **detached worktree** at `../.claude-worktrees/<repo>/pr-<number>-comments` as **unstaged** edits — no `git add`, no `git commit`, no `git push`
8. **Adversarial review**: runs multiple independent review angles over the resulting diff for correctness, scope creep, missed plan items, disputed verdicts, and new bugs. Findings are surfaced for the user — never auto-applied.
9. For rejected items: produces ready-to-paste rebuttal text the user can post manually
10. **Never posts to the PR. Never creates a commit.**

**Usage:**
```bash
/fix-pr-comments https://github.com/owner/repo/pull/123
/fix-pr-comments 123
/fix-pr-comments #123 --include-resolved
```

### `/review-fix [--wait|--background] [focus ...]`

After applying a fix, runs a runtime-aware multi-agent, multi-angle, multi-round adversarial review with the repo's code style guide as context.

**What it does:**
1. Reads the code style guide generated by `/evaluate-issue`
2. Combines style rules with any user-provided focus text
3. Invokes independent reviewer angles, fixes in-scope findings, and repeats until every required angle is clean

**Usage:**
```bash
# After fixing the issue:
/review-fix
/review-fix --wait
/review-fix --background focus on error handling
```

## Generated Files

- `.issue-evaluator/code-style.md` — Auto-generated code style analysis of the repo. Delete to force regeneration on next `/evaluate-issue` run.

## Requirements

- GitHub CLI (`gh`) installed and authenticated
- A runtime with sub-agent support for review workflows. Same-context fallback is allowed only when reviewer sub-agents are explicitly unsupported by the host/runtime, the user explicitly forbids them, or the selected reviewer/model is explicitly unavailable or at capacity; review workflows then report `degraded-same-context-review`.
- Git repository with a GitHub remote

## Typical Workflow

```bash
# 1. Evaluate an issue
/evaluate-issue https://github.com/owner/repo/issues/42

# 2. Review the report, then implement the fix
# (either manually or ask Claude to implement it)

# 3. Run adversarial review on the fix
/review-fix
```
