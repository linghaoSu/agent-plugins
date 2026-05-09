# Design Review - Executable Skill Eval Fixtures

**Slug:** ITS-ROADMAP-006
**Date:** 2026-05-09
**Reviewer:** main-context adversarial review fallback + self-review
**Iterations:** 1
**Result:** clean

## Issues Raised & Resolution

| # | Severity | Issue | Resolution |
|---|---|---|---|
| 1 | warning | The first draft could be read as proving live model behavior, but Stage 1 only validates skill instruction contracts. That would create false confidence. | Reworded requirements and architecture to use "contract fixture" language and added an explicit false-confidence guardrail. |
| 2 | warning | The design said assertions should avoid exact prose, but did not define how to keep them stable. That left the implementation open to brittle keyword scanning. | Added grouped invariant definitions for every Stage 1 check. |
| 3 | warning | Release-gate integration was still framed as an open decision, which could cause premature blocking checks before the fixture shape is proven. | Resolved the Stage 1 decision: manually runnable first; release-gate invocation belongs to Stage 3. |

## Residual Open Issues

None.

## Reviewer's Final Verdict

LGTM

## Self-Review Notes

Sub-agent delegation was not used in this turn because the current request did
not explicitly authorize a new parallel sub-agent. The review used the same
adversarial prompt shape in the main context and recorded that fallback here.
