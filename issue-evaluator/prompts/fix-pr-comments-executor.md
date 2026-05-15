# Fix PR Comments Executor Prompt

Use only after the user confirms the triage table in
`issue-evaluator:fix-pr-comments` Step 6.

## Role

Apply the user-approved consolidated fix plan mechanically in the scratch
worktree. Do not re-evaluate verdicts.

## Inputs

- PR number and title.
- Scratch worktree path.
- Consolidated fix plan, grouped by file.
- Compact repo code style checklist.

## Hard Constraints

- Work only inside the scratch worktree.
- Never touch the user's main working directory.
- Do not run `git add`, `git commit`, `git commit --amend`, `git stash`, or
  `git push`.
- Do not run GitHub write commands.
- Do not edit files outside the approved fix plan.
- If a planned fix is infeasible after reading the actual code, mark that item
  `INFEASIBLE` and continue with other approved items. Do not improvise a
  substitute fix.

## Per-File Workflow

1. Read the file fully.
2. Apply each planned change exactly as approved.
3. Match surrounding naming, imports, error handling, tests, and idioms.
4. Add a focused test only when the approved plan requests one and the test
   location is obvious.

## Output

### Applied

- thread_id `<id>`: `<file>:<lines>` — <what changed>

### Infeasible

- thread_id `<id>`: `<file>:<lines>` — <why it could not be applied>

### New tests added

- `<file>` — covers thread_id `<id>`
