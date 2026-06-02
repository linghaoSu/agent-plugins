# Skill-Stats Workflow Contracts

Shared contract for the skill-stats reporting skill.

## Modes

### usage-stats

Default `skill-stats` usage-stats mode is read-only and conversation-only. It
never edits the usage log, plugin files, shell config, git state, or external
systems.

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

### skill-cleaner-report

`skill-stats --cleaner` runs the local `skill_cleaner_wrapper.py report`
adapter around a user-configured external skill-cleaner analyzer. It is
report-only by default: the wrapper performs no target, config, or skill-root mutation.
It may write one wrapper-owned temp evidence bundle so later plan
stages can use canonical action ids without reconstructing paths from redacted
display text.

Final responses must include:

- `status`: `success`, `needs_user`, `terminal`, or `degraded`.
- `mode`: `skill-cleaner-report`.
- `inputs_resolved`: analyzer display path, scan roots, log sources, skipped
  logs, and any explicit roots.
- `outputs_written`: the evidence bundle path when one is written, otherwise
  `[]` for setup failures.
- `skipped`: omitted roots, logs, or report sections with reasons.
- `errors[]`: typed as `retryable`, `terminal`, `needs_user`, or `degraded`.
- `next_action`: analyzer setup guidance or the next report-only review step.
- `truncated`: `true` or `false`.

The report may show opaque `action_id` values, but this mode does not apply
cleanup actions. Delete, edit, disable, commit, and push behavior are outside
this mode. If bounded log sources are recorded but the external analyzer cannot
accept those exact sources, the report must return `degraded` and suppress
cleanup action ids rather than presenting unscoped log-derived authority.

### skill-cleaner-plan

`skill-stats --cleaner --apply` must run `preflight-plan` first. Plan mode
consumes the wrapper-owned evidence bundle and selected `action_id` values,
then writes a wrapper-owned temp plan bundle. It returns `mode:
skill-cleaner-plan`, the redacted display plan, and the `plan_id` that must be
approved through `/plan` in the current session.

Final responses must include:

- `status`: `success`, `needs_user`, `terminal`, or `degraded`.
- `mode`: `skill-cleaner-plan`.
- `inputs_resolved`: evidence bundle path, selected action ids, explicit roots,
  and explicit config files.
- `outputs_written`: the plan bundle path when one is written.
- `errors[]`: typed as `retryable`, `terminal`, `needs_user`, or `degraded`.
- `next_action`: ask for current-session `/plan` approval for the exact
  `plan_id`.
- `truncated`: `true` or `false`.

### skill-cleaner-apply

Apply mode is mutating and only runs after exact current-session `/plan`
approval. The wrapper must receive the plan bundle plus
`--approved-plan-sha`. Missing or mismatched `--approved-plan-sha` returns
`needs_user` and mutates nothing.

Final responses must include:

- `status`: `success`, `needs_user`, `terminal`, or `degraded`.
- `mode`: `skill-cleaner-apply`.
- `inputs_resolved`: plan bundle path, approved plan hash, explicit roots, and
  explicit config files.
- `outputs_written`: only target paths actually deleted, edited, or
  config-updated, plus consumed bundle cleanup when successful.
- `errors[]`: typed as `retryable`, `terminal`, `needs_user`, or `degraded`.
- `next_action`: review touched paths before using the owning commit workflow.
- `truncated`: `true` or `false`.

Apply mode must never run `git add`, `git commit`, `git stash`, `git push`, or
GitHub writes.
