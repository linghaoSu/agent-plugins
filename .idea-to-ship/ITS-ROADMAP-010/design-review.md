# Design Review - Skill Hygiene Repetition And Bloat Checks

**Slug:** ITS-ROADMAP-010
**Date:** 2026-05-15
**Reviewer:** multi-agent: architecture correctness -> sub-agent; implementation/testability -> sub-agent; UI/UX -> not applicable
**Iterations:** 22
**Result:** clean
**Mode:** multi-agent
**Degradation reason:** none

## Issues Raised & Resolution

| # | Severity | Issue | Resolution |
|---|---|---|---|
| 1 | critical | Staged-mode design could mix index and worktree reads, skip worktree-deleted staged skills, or treat legacy skills as newly added. | Added a mode-aware snapshot/listing contract for targets, references, and added-skill metadata in `architecture.md` Chosen Design. |
| 2 | critical | Cross-file duplicate reporting could miss changed targets when the target path sorted before the reference source. | Made staged/working reporting emit for any selected target that duplicates another file, independent of canonical sort order. |
| 3 | critical | Prompt/template extraction and classification were too broad and could turn ordinary sections into repeated-inline candidates. | Added trigger-only extraction, internal-heading allowlists, candidate de-overlap, and dominant-family scoring rules. |
| 4 | critical | Fuzzy near-duplicate matching lacked bounded, observable runtime semantics. | Added per-family `FuzzyBudget`, per-file and whole-run caps, pair-cost limits, deterministic scan-limit findings, and fixture hooks. |
| 5 | critical | `repetition-scan-limited` strict behavior conflicted with FR-6 and could surprise maintainers. | Kept unsuppressed findings on the existing `skill-hygiene` advisory path with strict upgrade, then added a narrow evidence-backed exception contract for self-contained candidate-heavy skills. |
| 6 | warning | Release-gate fixture coverage was not itself release-gated without recursion. | Added separate `skill-hygiene-release-gate-fixtures` advisory with a non-recursive `--self-check` subset. |
| 7 | warning | Fixture suites could grow too slow for routine release-gate use. | Split fast release-gated fixture subsets from full explicit meta/performance verification and added runtime targets. |
| 8 | warning | Stage 3 combined extraction, classification, masking, dry-run baseline, and triage into one hard-to-verify slice. | Split rollout into `Candidate Inventory Slice` and `Baseline Dry Run And Contract Masking Slice`. |
| 9 | warning | Staged infrastructure drift guard was too broad and could block unrelated ordinary skill changes. | Scoped `skill-hygiene-infra-drift` to staged gates only when the staged diff touches canonical hygiene infrastructure paths. |
| 10 | warning | Existing `inline-output-contract` behavior and repeated-inline masking could conflict. | Preserved existing file-level `inline-output-contract` behavior and added a separate owned-subspan detector only for masking repetition evidence. |
| 11 | warning | Moderate-bloat findings did not explicitly satisfy FR-4 actionability. | Added message contract requiring path, line count, threshold, and extraction/shared-contract recommendation. |
| 12 | warning | Moderate-bloat fixtures did not assert the FR-4 message contract or invalid exception behavior. | Added fixture requirements for message invariants plus empty/malformed/unrelated `## Hygiene Exception` negatives. |

## Review Rounds

| Round | Angle | Route | Verdict |
|---|---|---|---|
| 1-18 | architecture correctness | sub-agent | Findings on staged mode, reporting semantics, extraction/classification, output-contract masking, scan-limit, and release-gate wiring; patched incrementally. |
| 1-18 | implementation/testability | sub-agent | Findings on stage slicing, fixtures, runtime caps, strict-upgrade behavior, and release-gate self-verification; patched incrementally. |
| 19 | architecture correctness | sub-agent | LGTM. |
| 19 | implementation/testability | sub-agent | Four warnings on release-gate self-protection, scan-limit strict edge cases, fixture runtime budget, and Stage 3 size; fixed. |
| 20 | architecture correctness | sub-agent | One FR-4 warning on moderate-bloat message actionability; fixed. |
| 20 | implementation/testability | sub-agent | LGTM. |
| 21 | architecture correctness | sub-agent | LGTM. |
| 21 | implementation/testability | sub-agent | One FR-4 fixture warning on message invariants and invalid exceptions; fixed. |
| 22 | architecture correctness | sub-agent | LGTM. |
| 22 | implementation/testability | sub-agent | LGTM. |
| all | UI/UX | not applicable | `interface-design.md` is not present. |

## Residual Open Issues

None.

## Design Drift

No interface design artifact exists for this slug, so there is no UI/UX design drift to reconcile. The final architecture still implements the requirements by extending the existing hygiene checker and preserving the existing `skill-hygiene` release-gate path for actual hygiene findings.

## Reviewer Final Verdicts

| Angle | Verdict |
|---|---|
| architecture correctness | LGTM |
| implementation/testability | LGTM |
| UI/UX | not applicable |

## Self-Review Notes

The final design still favors Option A: extending the existing checker keeps mode handling, finding IDs, and release-gate semantics in one place. The rollout is now independently shippable: snapshot safety, fixture-gate wiring, candidate inventory, dry-run baseline, moderate bloat, exact prompt/template checks, bounded fuzzy checks, and final regression can each be verified before enabling broader behavior.

Implementation should pay particular attention to the non-recursive release-gate fixture self-check, the narrow scan-limit exception contract, and the FR-4 moderate-bloat message invariants because those were the final areas where reviewers found ambiguity.
