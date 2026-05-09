#!/usr/bin/env bash
# PostToolUse hook — receives JSON on stdin with tool_name, tool_input, etc.
# Extracts the skill name and appends a JSONL record to ~/.claude/skill-stats.jsonl

set -u

STATS_FILE="$HOME/.claude/skill-stats.jsonl"
STATS_DIR="${STATS_FILE%/*}"

input=$(cat)

command -v jq >/dev/null 2>&1 || exit 0
mkdir -p "$STATS_DIR" 2>/dev/null || exit 0

skill_name=$(printf '%s' "$input" | jq -r '.tool_input.skill // empty' 2>/dev/null)
[ -z "$skill_name" ] && exit 0

timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
working_dir=$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null)

jq -n -c \
  --arg skill "$skill_name" \
  --arg ts "$timestamp" \
  --arg cwd "$working_dir" \
  '{skill: $skill, timestamp: $ts, cwd: $cwd}' >> "$STATS_FILE" 2>/dev/null || true

exit 0
