# Requirements - ITS-ROADMAP-002

**Date:** 2026-05-09
**Status:** draft
**Source:** `.idea-to-ship/roadmap.md`

## Problem

The repo added `idea-to-ship` as a planning workflow, but it should not become
ceremony for its own sake. The roadmap item asks whether the repo has actually
dogfooded the workflow enough to treat it as the planning backbone for future
portfolio work.

## Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| FR-1 | At least one subsequent portfolio item must use the idea-to-ship artifact chain. | `.idea-to-ship/roadmap.md` ITS-ROADMAP-002 |
| FR-2 | The artifact chain must include requirements, architecture/design, implementation log, review, and test/verification evidence where useful. | `idea-to-ship/README.md`; `.idea-to-ship/roadmap.md` |
| FR-3 | The closure must avoid process bloat: do not require every docs-only or decision-only change to fake code/test artifacts. | `.idea-to-ship/roadmap.md` no-go |
| FR-4 | Future portfolio planning should use `.idea-to-ship/roadmap.md` as the active roadmap until a refreshed roadmap supersedes it. | `.idea-to-ship/roadmap.md` |

## Success Criteria

- Evidence identifies one completed roadmap item with a complete enough
  idea-to-ship artifact chain.
- The roadmap is updated so `ITS-ROADMAP-002` is no longer deferred.
- No new mandatory ceremony is introduced beyond the existing
  idea-to-ship/roadmap/release-gate artifacts.
