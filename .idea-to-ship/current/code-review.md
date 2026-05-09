# Code Review — current

**Date:** 2026-05-09
**Reviewer:** Codex self-review, multi-angle pass (no sub-agent launched)
**Iterations:** 2
**Result:** clean
**Diff size:** 9 tracked files changed plus new `idea-to-ship/skills/roadmap/SKILL.md`

## Issues Raised & Resolution

| # | Severity | File:line | Issue | Resolution |
|---|---|---|---|---|
| 1 | critical | `idea-to-ship/skills/test/SKILL.md:26` | `/test` does not read an existing `test-plan.md`, but Step 6 writes `test-plan.md` and Step 10 appends results. On a rerun, the skill can overwrite or silently ignore a human/agent-maintained test plan, losing story/acceptance/scenario/test traceability. | Fixed. Step 1 reads `test-plan.md`; Step 1.5 defines ownership, stable-ID merge, human-content preservation, and draft/ask behavior. |
| 2 | warning | `idea-to-ship/skills/test/SKILL.md:61` | The story derivation rule says to stop when requirements are vague, while the same skill also allows `reverse-engineered diff` as a source and says to derive scope from diff/git when `architecture.md` is missing. Mature projects often have no fresh requirements artifact, so the workflow can dead-end instead of producing a clearly labeled provisional test plan. | Fixed. Step 2 now defines fallback order from requirements through diff/git and marks reverse-engineered stories as provisional. |
| 3 | warning | `idea-to-ship/skills/roadmap/SKILL.md:66` | Source authority ranks recent git history above goal-tied GitHub milestones, active PRs, and current issues. That conflicts with the confidence rules, where explicit goal-linked milestone/issue evidence is high confidence and recent commits are only medium. In a live project this can mis-rank "what people happened to commit" over "what the team explicitly committed to ship." | Fixed. Goal-tied GitHub milestones, active PRs, and current issues now outrank recent git; git is defined as freshness/completion/drift evidence, not a planning override. |
| 4 | warning | `idea-to-ship/skills/implement/SKILL.md:97` | `--tdd` can create or update `test-plan.md` inside implementation, but it does not inherit `/test`'s story-matrix gates or any preservation rule for an existing plan. That creates two incompatible owners for the same artifact and can leave review-code treating a stage-local sketch as complete traceability. | Fixed. `--tdd` now updates only stage-local rows/slices, preserves stable IDs, asks/drafts before unsafe replacement, and tells users to run `/test` for broad coverage plans. |
| 5 | warning | `idea-to-ship/skills/review-code/SKILL.md:24` | `test-plan.md` is optional and absence is only "noted", but the new review contract depends on requirement -> story -> acceptance criterion -> scenario -> test evidence. A behavior-changing diff with no `test-plan.md` should be an explicit verification gap, not just missing context. | Fixed. `review-code` now carries `TEST_PLAN_MISSING` context and requires warning/critical verification-gap findings for behavior-changing diffs without a plan. |
| 6 | warning | `idea-to-ship/skills/review-code/SKILL.md:10` | The updated idea-to-ship review path still hard-codes `codex:codex-rescue` as the reviewer and only falls back to self-review. That does not satisfy the runtime-aware multi-model validation design discussed earlier: use the current runtime when appropriate, otherwise route to a sub-agent review loop. | Fixed. Added runtime-aware agent routing to `PRINCIPLES.md`, `review-code`, and `review-design`; README and architect hand-off now describe the runtime-aware reviewer. |
| 7 | nit | `idea-to-ship/skills/roadmap/SKILL.md:172` | `WRITE_TARGET` is recorded as `roadmap.md` or `roadmap.draft.md`, which is ambiguous in slug mode and portfolio mode. Agents can report or update the wrong file when both `.idea-to-ship/roadmap.md` and `.idea-to-ship/<slug>/roadmap.md` exist. | Fixed. `WRITE_TARGET` now records the full resolved portfolio or slug path, including draft paths. |

## Out-of-Scope Issues Skipped

- None. The findings above are within the newly added roadmap skill or the companion skill changes in this diff.

## Design Drift

- No local `requirements.md` / `architecture.md` exists for this change. Review was checked against the prior roadmap/TDD/traceability design discussion and the current diff.

## Test Traceability

- `/test` now owns the full verification artifact and preserves existing
  content by stable ID.
- `/implement --tdd` now owns only stage-local TDD slices unless a full
  `test-plan.md` already exists and can be safely merged.
- `/review-code` now treats missing `test-plan.md` on behavior-changing diffs
  as an explicit verification gap.

## Residual Open Issues

None.

## Final Verdict

LGTM. The roadmap skill and companion idea-to-ship skills now cover roadmap evidence ordering, write-target safety, acceptance checks, test-plan ownership, mature-project test derivation, TDD boundaries, and runtime-aware adversarial review routing.
