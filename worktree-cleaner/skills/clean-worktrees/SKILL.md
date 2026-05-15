---
name: clean-worktrees
description: Report stale git worktrees with PR and local-change safety checks. Dry-run by default; requires --apply before any removal.
argument-hint: [--apply] [--all] [--force]
allowed-tools: [Bash, Read]
---

# Clean Git Worktrees

Report stale git worktrees whose corresponding PRs have been merged or closed.
This skill is **report-only by default**. It removes worktrees only when the
user passes `--apply`, reviews the per-worktree safety summary, and confirms
the removal plan.

## Arguments

The user provided: `$ARGUMENTS`

Supported flags:
- `--apply` — Allow removal after the safety summary and user confirmation.
- `--all` — Include worktrees with no associated PR in the candidate report.
  This still requires `--apply` and confirmation before removal.
- `--force` — Permit `git worktree remove --force` only for candidates the
  user has explicitly confirmed after seeing the safety summary.
- `--dry-run` — Explicit report-only mode. This is also the default.
- No arguments — Report candidates only; remove nothing.

## Shared Contract

Apply `../../WORKFLOW-CONTRACTS.md`: final output must include the shared
status/mode/outputs/errors/next_action/truncated fields. Use mode `dry-run`
unless `--apply` passed the confirmation gate.

## Workflow

### Step 1: List All Worktrees

```bash
git worktree list
```

Parse the output to extract each worktree path and branch name. Skip:
- The **main worktree** (the primary working directory).
- Any worktree on a **detached HEAD** — report it separately and do not remove
  unless the user explicitly confirms that exact path in `--apply` mode.

### Step 2: Check PR Status for Each Branch

For each worktree branch, query the PR status:

```bash
gh pr list --head "<branch>" --state all --json state,number --jq '.[0] | "\(.number) \(.state)"'
```

Classify each worktree into one of:
- **MERGED** — PR exists and is merged.
- **CLOSED_NOT_MERGED** — PR exists and is closed without merge.
- **OPEN** — PR exists and is still open. Do NOT remove.
- **NO_PR** — No PR found for this branch.
- **DETACHED** — Detached HEAD, no branch.

### Step 3: Inspect Local Safety For Every Candidate

For every `MERGED`, `CLOSED_NOT_MERGED`, `NO_PR`, or `DETACHED` worktree,
inspect local state before recommending any action:

```bash
git -C "<worktree-path>" status --short
git -C "<worktree-path>" diff --stat HEAD
git -C "<worktree-path>" log --oneline --decorate --max-count=5 @{u}..HEAD
git -C "<worktree-path>" log --oneline --decorate --max-count=5 HEAD..@{u}
```

If the upstream ref is missing, classify the branch as `NO_UPSTREAM` and treat
unpushed-commit status as unknown. Also check whether the branch has a PR, and
whether a closed PR was merged. Never treat `CLOSED_NOT_MERGED`, `NO_PR`,
`DETACHED`, `NO_UPSTREAM`, uncommitted changes, or unpushed commits as safe for
automatic deletion.

Candidate actions:

| Status / local state | Default action |
|---|---|
| `OPEN` | Keep |
| `MERGED` with clean tree and no unpushed commits | Candidate for normal removal |
| `MERGED` with uncommitted changes or unpushed commits | Needs explicit force confirmation |
| `CLOSED_NOT_MERGED` | Needs user decision |
| `NO_PR` | Needs user decision |
| `DETACHED` | Needs user decision |
| `NO_UPSTREAM` or unknown branch state | Needs user decision |

### Step 4: Report Summary

Present a table to the user:

| Worktree | Branch | PR | Status | Local state | Action |
|---|---|---|---|---|---|
| path | branch-name | #123 | MERGED | clean, pushed | Candidate: remove with `git worktree remove` |
| path | branch-name | #124 | CLOSED_NOT_MERGED | clean | Needs explicit confirmation |
| path | branch-name | — | NO_PR | modified files | Needs explicit confirmation |

In dry-run mode, stop here and report `next_action` with the exact `--apply`
command the user can run if they want removal.

### Step 5: Confirm Before Removal

If `--apply` is present, ask the user to confirm the exact list of worktree
paths to remove. The user must have seen, for each path:

- PR status, including `MERGED` vs `CLOSED_NOT_MERGED`.
- Uncommitted change summary.
- Unpushed commit summary or `NO_UPSTREAM`.
- Whether removal would require `--force`.

Do not infer confirmation from `--apply` alone. `--apply` only permits entering
the confirmation gate.

### Step 6: Remove Confirmed Worktrees

For confirmed candidates with a clean local state, prefer normal removal:

```bash
git worktree remove "<worktree-path>"
```

Use `git worktree remove --force "<worktree-path>"` only when all of these are
true:

- The PR status is `MERGED`.
- The user passed `--force`.
- The user saw the per-worktree safety summary.
- The user explicitly confirmed force removal for that exact worktree.

Never remove:
- The main worktree.
- An open-PR worktree.
- A worktree whose status or local state could not be determined.
- A `CLOSED_NOT_MERGED`, `NO_PR`, `DETACHED`, or `NO_UPSTREAM` worktree that
  has uncommitted changes or unpushed commits. Report it for manual handling
  instead.

### Step 7: Final Verification

Run `git worktree list` again and present the final state.

Report:
- How many worktrees were removed.
- How many remain and why.

## Notes

- Default mode is dry-run/report-only.
- Never use `git worktree remove --force` as the default.
- Never remove the main worktree.
- Batch the `gh pr list` calls efficiently — if there are many branches, run them in a single loop rather than spawning parallel agents.
- If `gh` is not available or not authenticated, report the error and abort gracefully.
