---
name: antifragile-agent
description: Read-only audit of agent plugin/hook/skill infrastructure for fragile hooks, missing guards, state pollution, and recovery gaps. Outputs stdout only.
allowed-tools:
  - Bash
  - Read
  - Agent
---

# Antifragile Agent Audit

Audit the Claude Code plugin/hook/skill ecosystem for fragility. Produce a graded report with actionable fixes.

This skill is read-only against the target infrastructure and writes no local
artifact by default; the report goes to stdout/conversation. Apply the shared
safety checklist from `agent-playbook/WORKFLOW-CONTRACTS.md` when comparing
with agent-playbook audits: boundary truth, human gates for destructive
changes, token honesty, typed errors, and realistic scenario fixtures.

## Output, Token, And Error Contract

End with:

```yaml
status: success | needs_user | terminal | degraded
mode: audit
inputs_resolved:
  target: <repo or plugin root>
outputs_written: []
skipped:
  - <path or dimension>: <reason>
errors:
  - type: retryable | terminal | needs_user | degraded
    message: <actionable sentence>
next_action: <one command or decision>
truncated: true | false
```

Token budget: inspect at most 100 hook/script/skill files in one pass, cap
per-file evidence at 80 surrounding lines, and summarize repeated dependency
findings by pattern. If the scan exceeds the budget, set `truncated: true` and
name the omitted paths or dimensions.

## Audit Dimensions

### 1. Hook Robustness

For every hook script (find all `hooks.json` files, then trace to the scripts they reference):

- **Guard clauses**: does the script check for required commands (`command -v jq`, `command -v git`, etc.) before using them? Missing checks → Critical if the command is essential, Warning otherwise.
- **Failure isolation**: does the script use `|| exit 0` or `|| true` to prevent a single failure from blocking the session? A hook that can crash SessionStart → Critical.
- **Input validation**: for PostToolUse/PreToolUse hooks, does the script handle empty stdin or malformed JSON? Use `jq -e` or similar guards.
- **Timeout risk**: does the script make network calls or run commands that could hang indefinitely? Any unbounded `curl`, `git fetch`, or `claude plugin update` without timeout → Warning.
- **set -u / set -e**: `set -u` (fail on unset vars) is good. `set -e` in hooks is risky — a non-zero exit from a benign command kills the hook. Flag `set -e` in hooks as Warning.

### 2. Dependency Chain

- **External tool dependencies**: scan all SKILL.md files and scripts for references to external commands (python3, gh, jq, git, curl, column, etc.). Cross-reference with what's likely available on a fresh macOS/Linux. Flag missing `command -v` guards.
- **Cross-plugin dependencies**: check if any skill assumes artifacts from another plugin exist (e.g., reading `.issue-evaluator/` from a different plugin's skill). Implicit coupling → Warning.
- **Path assumptions**: find hardcoded paths like `$HOME/.claude/...` or absolute paths. Check if the script creates parent directories before writing.

### 3. State Pollution

- **Unbounded growth**: find all files that get appended to (JSONL logs, data caches). Check if there is any rotation, truncation, or size-check mechanism. Unbounded append → Warning.
- **Write conflicts**: if multiple hooks or skills write to the same file, check for locking or atomic-write patterns. Concurrent writes without protection → Warning.
- **Temp file cleanup**: find any `mktemp` or `/tmp/` usage. Check if cleanup happens (via `trap` or explicit `rm`).

### 4. Removal Resilience

- **Plugin independence**: for each plugin, check if removing it would break any other plugin. Look for cross-references in SKILL.md files, hook scripts, and marketplace.json.
- **Graceful absence**: check if skills handle missing optional data gracefully (e.g., `skill-stats` when no JSONL file exists yet).

### 5. Data Corruption Recovery

- **JSON/JSONL files**: any file that is appended to or written incrementally — what happens if the write is interrupted mid-line? Check for atomic-write patterns (write to temp + rename).
- **Git state**: do any hooks modify git state (stage files, create commits)? Interrupted git operations → Critical.

## Output Format

Write the report to stdout in this format:

```
# Antifragile Agent Audit

**Scanned:** <N> plugins, <N> hooks, <N> skills
**Date:** <date>

## Critical (blocks session or loses data)
- [ ] <finding> — <file:line> — <fix>

## Warning (silent failure or degraded function)
- [ ] <finding> — <file:line> — <fix>

## Info (improvement opportunity)
- [ ] <finding> — <file:line> — <fix>

## Passed
- <what looked good>
```

Keep findings actionable — each one should say what to change, not just what's wrong.
