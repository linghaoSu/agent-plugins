# Worktree-Cleaner Workflow Contracts

Shared contract for safe git worktree cleanup.

## Output, Token, And Error Contract

`clean-worktrees` is report-only by default. Removal requires `--apply`, a
per-worktree safety summary, and explicit user confirmation.

Final responses must include these fields, either inline or as a compact
summary:

- `status`: `success`, `needs_user`, `terminal`, or `degraded`.
- `mode`: `dry-run` or `apply`.
- `inputs_resolved`: repo path and parsed flags.
- `outputs_written`: `[]`.
- `skipped`: worktrees kept or omitted with reasons.
- `errors[]`: typed as `retryable`, `terminal`, `needs_user`, or `degraded`.
- `next_action`: one command or decision.
- `truncated`: `true` or `false`.

Token budget: inspect at most 100 worktrees. For each candidate, show at most
20 changed-file stat lines and 5 commit subjects. If the budget is exceeded,
set `truncated: true`, summarize what was omitted, and provide a narrower
follow-up command or manual inspection target in `next_action`.
