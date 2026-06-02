---
name: skill-stats
description: Conversation-only usage report plus optional skill-cleaner report and apply-confirm scoped cleanup.
allowed-tools:
  - Bash
  - Read
---

# Skill Usage Statistics

Apply the shared output, token, and error contract from
`../../WORKFLOW-CONTRACTS.md`.

## Arguments

- No flag: run legacy usage-statistics mode.
- `--cleaner`: run skill-cleaner report mode through the local wrapper.
- `--analyzer <path>`: external `skill-cleaner.ts`, skill directory, or
  checkout root. Overrides `SKILL_STATS_CLEANER_ANALYZER`.
- `--root <path>`: explicit extra skill root for report scanning. May repeat.
- `--config <json-path>`: explicit JSON config file eligible for config-disable
  planning. May repeat.
- `--apply`: enter apply-confirm mode. This first renders and validates a plan;
  it does not imply mutation by itself.
- `--months <n>`, `--max-log-mb <n>`, `--context-tokens <n>`,
  `--budget-percent <n>`, `--deep-logs`, `--no-logs`: forwarded to the report
  wrapper when present.

Do not infer cleanup from `--cleaner` alone. Cleaner mode is report-only by
default; mutation requires `--apply`, a generated `preflight-plan`, exact
current-session `/plan` approval, and wrapper validation with
`--approved-plan-sha`.

## Usage-Statistics Mode

Read the local usage log at `~/.claude/skill-stats.jsonl` and present a summary.
This usage-statistics branch is read-only and conversation-only: it never edits
the log, plugin files, or shell config. Final output uses mode `read-only` and
`outputs_written: []`.

### Steps

1. Check if `~/.claude/skill-stats.jsonl` exists. If not, tell the user no data has been collected yet.

2. If `jq` is unavailable, tell the user it is required for local analysis.
   Otherwise, run the following analysis via `jq` on the JSONL file:
   the uppercase table labels in this command are output headers, not
   placeholders to replace.

```bash
echo "=== Skill Usage Stats ==="
echo ""
echo "--- Call counts (descending) ---"
jq -r '.skill' ~/.claude/skill-stats.jsonl | sort | uniq -c | sort -rn

echo ""
echo "--- Last used per skill ---"
jq -s 'group_by(.skill) | map({skill: .[0].skill, last_used: (map(.timestamp) | sort | last), count: length}) | sort_by(-.count) | .[] | "\(.skill)\t\(.count)\t\(.last_used)"' ~/.claude/skill-stats.jsonl \
  | awk -F '\t' 'BEGIN { printf "%-32s %8s %s\n", "SKILL", "COUNT", "LAST_USED" } { printf "%-32s %8s %s\n", $1, $2, $3 }'

echo ""
echo "--- Daily trend (last 14 days) ---"
jq -r '.timestamp[:10]' ~/.claude/skill-stats.jsonl | sort | uniq -c | sort -k2
```

3. Compare tracked skills against the list of all installed skills (from the system-reminder in the conversation). Identify skills that have **never been called** — these are candidates for removal or re-evaluation.

4. Present results as a concise table. Highlight:
   - Top 5 most-used skills
   - Skills never called (if any installed skills are absent from the log)
   - Any skills not called in the last 30 days

## Skill-Cleaner Report Mode

When `--cleaner` is present, call the local wrapper in report mode:

In the command examples below, replace placeholders such as `<path>`, `<n>`,
`<id>`, `<json-path>`, and `<hex>` with the concrete analyzer, root, config,
action, or hash values from the current run.

```bash
python3 skill-stats/scripts/skill_cleaner_wrapper.py report \
  --analyzer <path> \
  [--root <path> ...] [--months <n>] [--max-log-mb <n>] \
  [--context-tokens <n>] [--budget-percent <n>] [--deep-logs] [--no-logs] \
  [--config <json-path> ...]
```

If `--analyzer` is absent, rely on `SKILL_STATS_CLEANER_ANALYZER`. If neither
is available, return the wrapper's `needs_user` setup guidance.

Report mode may write a wrapper-owned temp `evidence_bundle`; include its
`evidence_bundle` metadata and `outputs_written` path in the final contract.
It performs no target, config, or skill-root mutation. It must not delete,
edit, disable, commit, push, or install hooks.

Show bounded known sections, skipped roots/logs, typed errors, truncation
state, and opaque `action_id` values from the wrapper. Treat unused candidates
as heuristic; do not label them safe to delete.

If recent log sources are discovered but cannot be forwarded through an
explicit external-analyzer flag, the wrapper returns `degraded` and suppresses
cleanup action ids. Rerun with `--no-logs` only when the user intentionally
wants cleanup candidates without usage-log evidence.

## Skill-Cleaner Apply-Confirm Mode

When both `--cleaner` and `--apply` are present:

1. Run report mode or use the just-rendered report evidence.
2. Select only machine-readable `action_id` values from
   `display_findings[].action_candidates[]`; do not scrape human section text.
3. Call `preflight-plan` with the evidence bundle, selected action ids, and the
   same explicit `--root` and `--config` inputs. Replace placeholders in the
   command with the concrete evidence path, action ids, roots, and configs:

```bash
python3 skill-stats/scripts/skill_cleaner_wrapper.py preflight-plan \
  --evidence-bundle <path> \
  --action-id <id> ... \
  [--root <path> ...] [--config <json-path> ...]
```

4. Render the redacted display plan and exact `plan_id`, then stop with
   `status: needs_user` unless the user approves that exact plan through
   `/plan` in the current session.
5. After approval, call apply with the plan bundle and approved hash. Replace
   placeholders in the command with the concrete plan bundle, hash, roots, and
   configs:

```bash
python3 skill-stats/scripts/skill_cleaner_wrapper.py apply \
  --plan-bundle <path> \
  --approved-plan-sha sha256:<hex> \
  [--root <path> ...] [--config <json-path> ...]
```

The wrapper validates roots, configs, plan hash, source action ids, and current
preconditions before touching files. It may delete, edit, or config-disable
only named targets from the approved plan. It must never run `git add`,
`git commit`, `git stash`, `git push`, or GitHub writes.

## Related Skills

- No other local related skills own skill usage statistics.
- Use `$agent-playbook:context-audit` for broader agent context hygiene.
