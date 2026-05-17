# Design Review - Frontend Visual Testing And Orchestration Intake

**Slug:** ITS-ROADMAP-016-020
**Date:** 2026-05-17
**Status:** passed after fixes

## Scope

Reviewed `.idea-to-ship/ITS-ROADMAP-016-020/requirements.md` and
`.idea-to-ship/ITS-ROADMAP-016-020/architecture.md` for roadmap items
`ITS-ROADMAP-016` through `ITS-ROADMAP-020`.

## Required Angles

| Angle | Result |
|---|---|
| Architecture correctness / traceability | LGTM |
| Implementation and deterministic testability | LGTM |
| Visual-test and orchestration domain fit | LGTM |

## Issues Resolved

- Added explicit `review-code` visual evidence handoff required in this batch.
- Defined content-sensitive `workspace_diff_fingerprint` and
  `untracked_files_manifest` semantics.
- Added matrix carry-forward rules, aggregate verdict enum/table, report-level
  verdict fields, and console/network status vocabulary.
- Made `SKIP-with-reason` non-success for required coverage unless explicitly
  de-scoped.
- Added deterministic scenario fixture requirements for staged, unstaged,
  untracked, stale fingerprint, aggregate verdict, UI-touched/no-report, and
  broad-orchestrator guard cases.
- Replaced phrase-only orchestration guardrails with scoped entry extraction,
  route-token checks, forbidden capability groups, and allowlist semantics.

## Final Review Evidence

Final focused pass returned LGTM for all three angles after the last two fixes:

- Console/network `FAIL` rolls up to aggregate `FAIL`.
- Nested untracked files are enumerated at file level with
  `git ls-files --others --exclude-standard -z`; relevant files are
  content-hashed and unclassified files block aggregate `PASS`.

## Decision

Proceed to TDD and implementation.
