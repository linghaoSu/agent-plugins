---
name: clean-worktrees
description: List all git worktrees, check PR status for each branch, and remove worktrees whose PRs are merged or closed. Optionally inspect and remove no-PR worktrees.
argument-hint: [--all | --dry-run]
allowed-tools: [Bash, Read]
---

# Clean Git Worktrees

Remove stale git worktrees whose corresponding PRs have been merged or closed.

## Arguments

The user provided: `$ARGUMENTS`

Supported flags:
- `--all` — Also remove worktrees with no associated PR (after showing their contents).
- `--dry-run` — Only report what would be removed, do not actually delete anything.
- No arguments — Remove merged/closed PR worktrees, report no-PR worktrees for user decision.

## Workflow

### Step 1: List All Worktrees

```bash
git worktree list
```

Parse the output to extract each worktree path and branch name. Skip:
- The **main worktree** (the primary working directory).
- Any worktree on a **detached HEAD** — report it separately but do not auto-remove.

### Step 2: Check PR Status for Each Branch

For each worktree branch, query the PR status:

```bash
gh pr list --head "<branch>" --state all --json state,number --jq '.[0] | "\(.number) \(.state)"'
```

Classify each worktree into one of:
- **MERGED** — PR exists and is merged.
- **CLOSED** — PR exists and is closed (not merged).
- **OPEN** — PR exists and is still open. Do NOT remove.
- **NO_PR** — No PR found for this branch.
- **DETACHED** — Detached HEAD, no branch.

### Step 3: Report Summary

Present a table to the user:

| Worktree | Branch | PR | Status | Action |
|---|---|---|---|---|
| path | branch-name | #123 | MERGED | Will remove |
| path | branch-name | — | NO_PR | Needs review |

### Step 4: Inspect NO_PR Worktrees

For each NO_PR worktree, show:

```bash
git -C "<worktree-path>" diff --stat HEAD
git -C "<worktree-path>" log main..HEAD --oneline | head -5
```

Report whether the worktree has:
- **No changes, no commits** — empty, safe to remove.
- **Uncommitted changes** — describe what files are modified.
- **Unpushed commits** — list the commit messages.

### Step 5: Remove Worktrees

**For MERGED and CLOSED worktrees:**
Remove immediately with `--force` (to handle uncommitted changes in stale worktrees):

```bash
git worktree remove --force "<worktree-path>"
```

**For NO_PR worktrees:**
- If `--all` flag is set: remove them all with `--force`.
- Otherwise: present the inspection results from Step 4 and ask the user whether to remove each one (or all at once).

**For OPEN worktrees:**
Never remove. Report them as "kept (PR still open)".

**For DETACHED worktrees:**
Report and ask the user whether to remove.

If `--dry-run` is set, skip all removals and only report what would happen.

### Step 6: Final Verification

Run `git worktree list` again and present the final state.

Report:
- How many worktrees were removed.
- How many remain and why.

## Notes

- Always use `git worktree remove --force` for stale worktrees — they may have leftover uncommitted changes from abandoned work.
- Never remove the main worktree.
- Batch the `gh pr list` calls efficiently — if there are many branches, run them in a single loop rather than spawning parallel agents.
- If `gh` is not available or not authenticated, report the error and abort gracefully.
