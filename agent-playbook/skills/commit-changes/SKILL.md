---
name: commit-changes
description: Verify intended local changes, create a scoped commit, and optionally open a GitHub draft PR. Use only when the user explicitly asks to commit or publish completed work.
---

# Commit Changes

Commit only the user-approved scope. A request to commit does not authorize a
push or PR; a request for a PR authorizes the required push after final review.

## Workflow

1. Read repo instructions, contribution rules, commit conventions, PR template,
   current branch, status, staged/unstaged/untracked files, and full relevant
   diff. Preserve unrelated user changes.
2. State the intended file set and exclusions. If scope is ambiguous or mixes
   goals, stop for a decision. Never stage secrets, generated noise, local env,
   or unrelated formatting.
3. Run repo-required checks plus relevant focused tests. Apply
   `../../WORKFLOW-CONTRACTS.md` contribution gate for any external PR.
4. Draft a concise imperative commit message from the diff. Do not add tool,
   model, assistant, or synthetic co-author attribution.
5. Stage explicit paths, inspect the staged diff, and commit. Verify the commit
   contains exactly the approved files and the remaining worktree still holds
   all excluded changes.
6. If the user requested a draft PR, re-check duplicates and target policy,
   push the current branch, then create a draft using every required template
   heading with concrete summary, checks, issue linkage, and limitations.

## Stop conditions

Stop for failed required checks, unresolved secrets, detached/default branch,
unexpected staged content, duplicate PR, missing publication authorization, or
target policy conflict. Never use destructive cleanup to make the state look
clean.

## Output

Report commit SHA/message, included and excluded files, checks and failures,
remaining worktree state, and PR URL/status when created. Never claim skipped
checks passed.

Use `$secret-scanner:scan-secrets` before committing sensitive changes and
`$worktree-cleaner:clean-worktrees` for later worktree removal.
