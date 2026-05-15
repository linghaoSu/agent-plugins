# Antifragile Workflow Contracts

Shared contracts for antifragile audit skills. Skills should cite this file
instead of repeating output, token, and error rules.

## Output, Token, And Error Contract

Antifragile audits are read-only against the target by default. Reports go to
stdout/conversation unless a future skill explicitly documents an artifact path.

Final responses must include these fields, either inline or as a compact
summary:

- `status`: `success`, `needs_user`, `terminal`, or `degraded`.
- `mode`: `audit`.
- `inputs_resolved`: target project, plugin root, or focus area.
- `outputs_written`: `[]` for stdout/conversation-only audits.
- `skipped`: dimensions or paths skipped with reasons.
- `errors[]`: typed as `retryable`, `terminal`, `needs_user`, or `degraded`.
- `next_action`: one command, skill, or decision.
- `truncated`: `true` or `false`.

Default token budget:

- Inspect at most 100 source/config/hook/script/skill files in one pass.
- Cap per-file evidence at 80 surrounding lines.
- Summarize repeated findings by pattern.

If the scan exceeds the budget, set `truncated: true`, name omitted paths or
dimensions, and put the continuation command or narrowed focus in
`next_action`.
