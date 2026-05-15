# Skill-Stats Workflow Contracts

Shared contract for the skill-stats reporting skill.

## Output, Token, And Error Contract

`skill-stats` is read-only and conversation-only. It never edits the usage log,
plugin files, shell config, git state, or external systems.

Final responses must include these fields, either inline or as a compact
summary:

- `status`: `success`, `needs_user`, `terminal`, or `degraded`.
- `mode`: `read-only`.
- `inputs_resolved`: the usage log path.
- `outputs_written`: `[]`.
- `skipped`: missing data or omitted result groups with reasons.
- `errors[]`: typed as `retryable`, `terminal`, `needs_user`, or `degraded`.
- `next_action`: one command or decision.
- `truncated`: `true` or `false`.

Token budget: report top 20 skills by usage, top 20 stale skills, and at most
50 never-called skills. If the installed skill list or log is larger, set
`truncated: true` and explain how to narrow the result.
