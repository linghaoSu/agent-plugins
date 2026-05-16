# Design Review - Skill Authoring Standards

**Slug:** ITS-ROADMAP-015
**Date:** 2026-05-16
**Reviewer:** multi-agent: architecture correctness -> sub-agent; implementation/testability -> sub-agent
**Iterations:** 5
**Result:** clean
**Mode:** multi-agent
**Degradation reason:** none

## Issues Raised & Resolution

| # | Severity | Issue | Resolution |
|---|---|---|---|
| 1 | critical | Initial `all` mode target was added/untracked-only, so a committed weak new skill would no longer be checked. | Fixed in `architecture.md` Data Flow by introducing `scripts/skill-authoring-baseline.txt` and durable all-mode target selection. |
| 2 | warning | Workflow/router classification, task tracking, Mermaid diagram, related-skill validation, and command safety were underspecified. | Fixed in `architecture.md` Deterministic Authoring Rules with exact headings, signals, Mermaid shape, related-skill scope, staged inventory behavior, command fence languages, risky patterns, and placeholder explanation rules. |
| 3 | warning | Baseline could become a second waiver path for weak touched skills. | Fixed by defining baseline as legacy-only, requiring visible `## Hygiene Exception` for touched-skill exceptions, and requiring fixtures proving dirty/new paths bypass baseline. |
| 4 | warning | Baseline file was missing from skill-hygiene infra drift scope. | Fixed by adding `scripts/skill-authoring-baseline.txt` to the release-gate and fixture infra target requirements in the architecture. |
| 5 | warning | Staged related-skill inventory needed explicit staged-added, staged-deleted, and worktree-only behavior. | Fixed in Known skill inventory and Test Strategy Hooks. |
| 6 | warning | Existing fixture helpers would produce unrelated authoring findings after the new checks. | Fixed by requiring fixture helper migration: default authoring-compliant helper plus explicit weak helper or fixture baselines. |
| 7 | warning | New authoring target selection could be misread as weakening existing hygiene checks. | Fixed by stating existing checks keep `changed_skill_files(root, mode)` behavior and only new authoring checks use `authoring_target_skill_files`. |
| 8 | warning | Committed `all` mode cannot prove a baseline was not incorrectly updated with a weak skill after the fact. | Fixed by scoping the non-waiver guarantee to staged/working mode and the all-mode guarantee to unbaselined committed weak skills. |
| 9 | warning | Related-skill self-reference rules were ambiguous for single-skill fixture repos. | Fixed with an exact fixture-only note: `No other local related skills in this fixture repo.` |

## Review Rounds

| Round | Angle | Route | Verdict |
|---|---|---|---|
| 1 | architecture correctness | sub-agent | 1 critical, 3 warnings |
| 1 | implementation/testability | sub-agent | 1 critical, 3 warnings |
| 2 | architecture correctness | sub-agent | 2 warnings |
| 2 | implementation/testability | sub-agent | 4 warnings |
| 3 | architecture correctness | sub-agent | 2 warnings |
| 3 | implementation/testability | sub-agent | 2 warnings |
| 4 | architecture correctness | sub-agent | LGTM |
| 4 | implementation/testability | sub-agent | 2 warnings |
| 5 | architecture correctness | sub-agent | LGTM |
| 5 | implementation/testability | sub-agent | LGTM |

## Residual Open Issues

None.

## Design Drift

None detected between `requirements.md` and `architecture.md`; the architecture was tightened in place to preserve the roadmap scope.

## Reviewer Final Verdicts

| Angle | Verdict |
|---|---|
| architecture correctness | LGTM |
| implementation/testability | LGTM |

## Self-Review Notes

The chosen option remains Option A. The baseline addition increases implementation complexity, but it is justified because it keeps legacy strict all-mode green without letting newly edited skills bypass authoring checks.
