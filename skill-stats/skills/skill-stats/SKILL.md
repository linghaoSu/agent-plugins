---
name: skill-stats
description: Conversation-only read of local skill usage JSONL. Use when the user asks for skill call counts, recency, unused skills, or truncation status; never edits logs, hooks, or plugin files.
allowed-tools:
  - Bash
  - Read
---

# Skill Usage Statistics

Read the local usage log at `~/.claude/skill-stats.jsonl` and present a summary.
This skill is read-only and conversation-only: it never edits the log, plugin
files, or shell config.

Apply the shared output, token, and error contract from
`../../WORKFLOW-CONTRACTS.md`. Final output uses mode `read-only` and
`outputs_written: []`.

## Steps

1. Check if `~/.claude/skill-stats.jsonl` exists. If not, tell the user no data has been collected yet.

2. If `jq` is unavailable, tell the user it is required for local analysis.
   Otherwise, run the following analysis via `jq` on the JSONL file:

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
