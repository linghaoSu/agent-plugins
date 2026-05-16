# Code Review - ITS-ROADMAP-014

**Date:** 2026-05-16
**Reviewer:** multi-agent: correctness/security -> Pascal, Bohr, James; traceability/testability -> Godel, Helmholtz, Turing; maintainability/repo-fit -> Hypatia, Hilbert, McClintock
**Iterations:** 3
**Result:** clean
**Mode:** multi-agent
**Degradation reason:** none
**Diff target:** staged diff
**Diff size:** 11 files changed, 1094 insertions(+), 1 deletion(-) before writing this review artifact

## Issues Raised & Resolution

| # | Severity | File:line | Issue | Resolution |
|---|---|---|---|---|
| 1 | warning | `scripts/skill-topology-scan.py:220` | Broken-reference rows lacked the source file path required by FR-4. | Added a `Source Path` column and fixture assertions for source paths. |
| 2 | warning | `scripts/skill-topology-scan.py:91` | Explicit unknown-plugin references such as `$missing-plugin:ghost` were dropped instead of reported as broken. | Report explicit `$plugin:skill` refs even when the plugin is absent; keep bare `plugin:skill` guarded to reduce prose false positives. |
| 3 | warning | `scripts/skill-topology-scan.py:103` | Unknown-plugin path references such as `missing-plugin/skills/ghost/SKILL.md` were dropped. | Always collect path-form skill references and let unresolved targets render as broken refs. |
| 4 | warning | `scripts/release-gate.sh:767` | Staged topology fixture checks could validate unstaged worktree code because there was no topology infra drift guard. | Added blocking `skill-topology-infra-drift` mirroring the existing hygiene drift guard. |
| 5 | warning | `tests/skill-topology-scan-fixtures.py:97` | FR-2 inventory output was not directly asserted by fixtures. | Added inventory section and representative parent/leaf row assertions. |
| 6 | warning | `.idea-to-ship/ITS-ROADMAP-014/test-plan.md:20` | FR-10 had live green gate evidence but lacked durable release-gate run/skip/drift fixture coverage. | Extended `tests/skill-hygiene-release-gate-fixtures.sh` for topology pass/warn/fail, skip routing, and staged drift. |
| 7 | warning | `tests/skill-hygiene-release-gate-fixtures.sh:524` | Release-gate fixture coverage still lacked the staged topology happy path. | Added a staged topology pass scenario asserting `skill-topology-infra-drift` blocking/pass and `skill-topology-fixtures` advisory/pass. |

## Out-of-Scope Issues Skipped

None.

## Design Drift

None. The implementation still follows the accepted standalone-scanner design. The review fixes strengthened the same design by making broken-reference rows more actionable and by matching the repo's existing staged-gate drift convention.

## Test Traceability

Clean.

| Requirement | Evidence |
|---|---|
| FR-1 deterministic read-only Markdown scan | `scripts/skill-topology-scan.py` emits Markdown to stdout; `python3 scripts/skill-topology-scan.py .` succeeds without mutation. |
| FR-2 inventory with id/path/name/role | `## Skill Inventory` output plus fixture assertions for representative parent and leaf rows. |
| FR-3 reference detection | Fixture covers `$plugin:skill`, explicit unknown `$plugin:skill`, known path refs, and unknown-plugin path refs. |
| FR-4 broken refs with source path and target evidence | Broken-reference table includes `Source Path`, `Target`, and `Evidence`; fixture asserts all forms. |
| FR-5 orphan skills | Fixture asserts `plugin:orphan` is listed and linked `plugin:leaf` is not. |
| FR-6 hub skills | Fixture asserts `plugin:hub` degree scoring. |
| FR-7 README catalog coverage gaps | Fixture asserts missing README rows for hub and orphan skills. |
| FR-8 skill-tree Markdown | Fixture asserts grouped tree rows by plugin. |
| FR-9 broken/orphan fixture | `bash tests/skill-topology-scan-fixtures.sh` covers both. |
| FR-10 release-gate advisory wiring | `bash tests/skill-hygiene-release-gate-fixtures.sh` covers all/working/staged pass, warning/fail, skip, and staged drift; staged/all strict gates pass. |

## Residual Open Issues

None.

## Final Verdict

| Angle | Verdict |
|---|---|
| correctness/security | LGTM |
| traceability/testability | LGTM |
| maintainability/repo-fit | LGTM |
| UI/UX | not applicable |

## Holistic Pass

- The final diff matches requirements and architecture.
- No UI diff.
- No public release-gate CLI change.
- The scanner remains local, offline, read-only, and dependency-free.
- Verification after fixes:
  - `bash tests/skill-topology-scan-fixtures.sh`
  - `bash tests/skill-hygiene-release-gate-fixtures.sh`
  - `scripts/release-gate.sh --mode all --strict`
  - `scripts/release-gate.sh --mode staged --strict`
  - `git diff --cached --check`
  - `git diff --check`
