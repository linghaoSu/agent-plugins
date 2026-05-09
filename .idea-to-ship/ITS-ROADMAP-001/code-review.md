# Code Review - ITS-ROADMAP-001

**Date:** 2026-05-09
**Reviewer:** runtime-native adversarial sub-agent + self-review
**Iterations:** 3
**Result:** clean
**Diff size:** review target before this file: 11 files, +1646/-5

## Issues Raised & Resolution

| # | Severity | File:line | Issue | Resolution |
|---|---|---|---|---|
| 1 | warning | `.idea-to-ship/ITS-ROADMAP-001/test-plan.md` / `tests/release-gate-stage1.sh` | Stage 1 covered exit `0` and exit `1`, but did not cover the architecture's usage/missing-checker exit `2` behavior. That left an observable public contract unverified. | Added `AC-7`, scenarios `S-7`/`S-8`, tests `T7`/`T8`, plus fixture cases for invalid `--mode` and missing `secret-scanner/scripts/scan.py`. |
| 2 | warning | `scripts/release-gate.sh` | `check_manifest_json` and `check_skill_frontmatter` reset the script's global `EXIT` trap from inside functions. That made cleanup behavior harder to reason about and could clobber future cleanup additions. | Removed the function-local trap overrides; the function temp files are removed explicitly and the global trap owns the result file. |
| 3 | critical | `scripts/release-gate.sh` | `--mode staged` validated manifest JSON and skill frontmatter from the worktree instead of the staged index. A bad staged manifest/skill could pass if the worktree was fixed after `git add` but not re-staged. | Added staged-mode index file listing and index content reads via `git ls-files`, `git cat-file -e :path`, and `git show :path`; added regression tests `T9` and `T10`. |

## Out-of-Scope Issues Skipped

None.

## Design Drift

Minimal `--json` output landed in Stage 1 even though the staged plan lists
machine-readable fixture assertions in Stage 3. This is accepted as a
documented deviation in `implementation-log.md`: the public interface already
advertised `--json`, and Stage 3 still owns dedicated JSON fixture assertions
and advisory-check JSON coverage.

## Test Traceability

Clean after the review fixes:

- FR-1 manifest validation -> `AC-1`, `AC-2` -> `T1`, `T2`
- FR-2 skill frontmatter validation -> `AC-1`, `AC-3` -> `T1`, `T3`
- FR-3 diff whitespace validation -> `AC-1`, `AC-4`, `AC-5` -> `T1`, `T4`, `T5`
- FR-4 secret scan gate -> `AC-1`, `AC-6` -> `T1`, `T6`
- usage/missing-checker failure handling -> `AC-7` -> `T7`, `T8`
- staged snapshot semantics for manifest/skill checks -> `S-9`, `S-10` -> `T9`, `T10`

## Residual Open Issues

None.

## Final Verdict

LGTM
