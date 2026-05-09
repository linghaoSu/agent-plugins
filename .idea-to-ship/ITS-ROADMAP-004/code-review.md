# Code Review - ITS-ROADMAP-004

**Date:** 2026-05-09
**Reviewer:** main-context hook/state review
**Iterations:** 1
**Result:** clean

## Issues Raised & Resolution

| # | Severity | File:line | Issue | Resolution |
|---|---|---|---|---|
| 1 | warning | `auto-updater/scripts/check-update.sh:50`, `auto-updater/scripts/check-update.sh:69` | `claude` commands in a SessionStart hook had no timeout boundary. | Added `run_with_timeout`, configurable `CLAUDE_AUTO_UPDATER_TIMEOUT_SECONDS`, and `CLAUDE_AUTO_UPDATER_DISABLE=1`. |
| 2 | warning | `skill-stats/scripts/track-skill.sh:7`, `skill-stats/scripts/track-skill.sh:25` | JSONL append could fail noisily when `~/.claude` was missing or unwritable. | Added parent directory creation and made append failure non-blocking. |
| 3 | warning | `skill-stats/skills/skill-stats/SKILL.md:28` | `column -N` is not portable across macOS/BSD and Linux environments. | Replaced it with portable `awk` formatting and documented `jq` as required. |

## Deferred

- `skill-stats` JSONL retention/rotation remains deferred. It needs a safe
  locking or atomic compaction strategy; hook-time truncation without that can
  lose records.

## Test Traceability

- FR-1 / FR-2: audit report covers both `hooks.json` files and referenced
  scripts.
- FR-3: state pollution finding recorded for JSONL append.
- FR-4: accepted low-risk fixes implemented.
- FR-5: retention/rotation deferred with rationale.

## Residual Open Issues

None blocking.

## Final Verdict

LGTM
