# Requirements - ITS-ROADMAP-007

**Date:** 2026-05-09
**Status:** draft
**Source:** `.idea-to-ship/roadmap.md`

## Problem

The secret scanner exists as a plugin and standalone script. The roadmap item
requires deciding whether secret scanning should be enforced through the local
release gate or through installed git hooks.

## Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| FR-1 | Secret scanning must be included in the documented local plugin release path. | `.idea-to-ship/roadmap.md` ITS-ROADMAP-007 |
| FR-2 | The chosen enforcement path must be explicit: command-based release gate or hook installation. | `.idea-to-ship/roadmap.md` ITS-ROADMAP-007 |
| FR-3 | Hook installation must not overwrite or install hooks without explicit user confirmation. | `.idea-to-ship/roadmap.md` no-go; `secret-scanner/README.md` |
| FR-4 | The decision must cite runnable evidence. | `scripts/release-gate.sh`; `RELEASE-GATE.md` |

## Decision

Use the command-based release gate path now. Do not install a repo-wide
pre-commit or pre-push hook as part of this item.

Rationale:

- `scripts/release-gate.sh` already runs `secret-scanner/scripts/scan.py` as a
  blocking `secret-scan` check for `staged`, `working`, and `all` modes.
- `RELEASE-GATE.md` documents `secret-scan` as a blocking check.
- Hook installation is local workflow policy and the secret-scanner plugin
  already has an explicit opt-in `/install-precommit-hook` flow.
- Installing hooks globally would violate the no-go unless the user explicitly
  asks for that workflow change.

## Success Criteria

- `RELEASE-GATE.md` records the command-vs-hook decision.
- `scripts/release-gate.sh --mode staged`, `--mode working`, and `--mode all`
  pass with `secret-scan` present.
- Roadmap status is updated to `Done`.
