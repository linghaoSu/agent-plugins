---
name: clean-worktrees
description: Report stale Git worktrees with PR, merge, branch, dirty-state, and untracked-file safety checks. Dry-run by default; removal requires --apply and confirmation.
---

# Clean Worktrees

Apply the local `../../WORKFLOW-CONTRACTS.md`. Never infer removal authority
from a request to inspect or clean generally.

## Workflow

1. Resolve repo and list worktrees with porcelain output. Protect the main/current
   worktree, locked/prunable entries, and any path outside the expected root.
2. For every candidate, inspect branch/HEAD, status including untracked files,
   ahead/behind commits, local-only commits, stash relevance, and linked PR
   state. Batch read-only `gh` queries where practical.
3. Classify `safe`, `needs_user`, or `keep`. Safe requires no local changes or
   untracked files, no unpushed/local-only commits, and a merged/closed PR or
   other explicit user-approved disposition.
4. Print a dry-run table with path, branch, PR, dirty state, unique commits,
   classification, and reason. Without `--apply`, stop here.
5. With `--apply`, ask confirmation for the exact safe paths. Revalidate every
   path immediately before removal and skip anything that changed.
6. Remove only confirmed paths with normal `git worktree remove`; never force,
   delete directories manually, remove branches, prune globally, or clean
   files. Verify remaining worktrees afterward.

Report removed, skipped, changed-since-plan, and failed paths. A removal error
is not permission to retry destructively.

Use `$agent-playbook:commit-changes` before cleanup when work still needs preservation.
