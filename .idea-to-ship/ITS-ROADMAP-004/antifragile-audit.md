# Antifragile Agent Audit

**Scanned:** 10 plugins, 2 hooks, 27 skills
**Date:** 2026-05-09

## Critical (blocks session or loses data)

None.

## Warning (silent failure or degraded function)

- [x] `auto-updater` ran `claude plugin list` and `claude plugin update`
  without a timeout boundary — `auto-updater/scripts/check-update.sh:19`,
  `auto-updater/scripts/check-update.sh:38` — fixed by routing both commands
  through a configurable timeout wrapper and adding
  `CLAUDE_AUTO_UPDATER_DISABLE=1` as an emergency opt-out.
- [x] `skill-stats` could emit shell redirection errors when
  `~/.claude/` did not exist or could not be written —
  `skill-stats/scripts/track-skill.sh:7`, `skill-stats/scripts/track-skill.sh:23`
  — fixed by creating the parent directory best-effort and suppressing
  append errors so the hook remains non-blocking.
- [ ] `skill-stats` appends to `~/.claude/skill-stats.jsonl` without a
  retention policy — `skill-stats/scripts/track-skill.sh:25` — deferred.
  Adding rotation safely needs a locking/atomic-write decision; a naive
  truncate-on-hook path risks losing records under concurrent hook writes.
- [x] `skill-stats` analysis docs used `column -N`, which is not portable
  across macOS/BSD `column` implementations —
  `skill-stats/skills/skill-stats/SKILL.md:27` — fixed by using portable
  `awk` formatting and documenting the `jq` requirement.

## Info (improvement opportunity)

- [ ] `auto-updater` intentionally mutates Claude plugin installation state
  during `SessionStart`. This is the plugin's purpose, but it remains a
  higher-blast-radius behavior than passive reporting. The new timeout and
  disable flag reduce operational risk; a future product decision could make
  updates advisory-only.
- [ ] `skill-stats` has no corruption recovery for partial JSONL lines. The
  display skill currently relies on `jq` over the whole file; a future update
  could ignore malformed lines or compact the file.

## Passed

- Hook scripts use `set -u`, not `set -e`.
- Both hook scripts guard optional command dependencies before using them.
- PostToolUse input parsing handles empty or malformed JSON by exiting cleanly.
- No hook script stages files, commits, pushes, or mutates git state.
- `auto-updater` already fails closed when marketplace metadata or source git
  directories are missing.
- `skill-stats` gracefully reports no data when the JSONL file does not exist.
