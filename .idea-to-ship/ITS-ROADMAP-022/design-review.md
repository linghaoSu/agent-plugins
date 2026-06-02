# Design Review - Agent-Playbook Workflow Router

**Slug:** ITS-ROADMAP-022
**Date:** 2026-06-02
**Reviewer:** multi-agent rounds 1-4; degraded same-context round 5
**Iterations:** 5
**Result:** clean
**Mode:** degraded-same-context-review
**Degradation reason:** iteration 5 reviewer sub-agents errored with usage limit / reviewer unavailable: "try again at 2:46 PM"; final required angles were rerun in same context.

## Issues Raised & Resolution

| # | Severity | Issue | Resolution |
|---|---|---|---|
| 1 | critical | Route-card interface did not support FR-11 assumptions or clarification questions. | Added conditional `assumptions` and `clarifying_questions` fields, plus a `needs_clarification` sentinel shape. |
| 2 | critical | Scenario fixtures were token-presence checks, not real route-card verification. | Required parseable `### Route Card Examples` in `SKILL.md` and fixture-side expectation tables for all route-card fields. |
| 3 | critical | Markdown examples could self-certify wrong owners. | Added fixture-side expected outcomes and a catalog/example consistency check. |
| 4 | critical | Major owner categories were not covered by scenario-level route cards. | Expanded minimum scenarios to feature, commercial, issue, PR, local fix review, governance, antifragile, secret, harness, worktree, and commit routes. |
| 5 | critical | Ambiguous no-safe-default routing had no exact card shape. | Defined `recommended_workflow: needs_clarification`, non-mutating steps, max-three questions, and sanitized router re-entry prompt. |
| 6 | critical | FR-6 style-rule drift was omitted. | Added `$issue-evaluator:update-code-style` mapping and fixture scenario requirement. |
| 7 | warning | Repo-memory creation was collapsed into context audit. | Split creation/refinement to `$agent-playbook:bootstrap-project-memory`; kept audit/sprawl on context-audit. |
| 8 | warning | Local fix review could be routed through evaluate/fix instead of review. | Added direct route to `$issue-evaluator:review-fix` and scenario coverage. |
| 9 | warning | Harness routing only banned wildcard, not generic family handoffs. | Required concrete harness skills or `needs_clarification`; fixtures reject wildcard and generic harness route-card owners. |
| 10 | warning | Full-file forbidden wildcard check would block useful negative documentation. | Required section-aware checks scoped to route outputs and examples. |
| 11 | warning | Conversation-only boundary was prose-only while `Bash` was allowed. | Architecture now removes `Bash` from router allowed tools and adds a frontmatter fixture. |
| 12 | warning | Docs/catalog surfaces were treated as conditional. | Made README, SKILLS, agent-playbook README, marketplace, and plugin metadata explicit fixture targets. |
| 13 | warning | `SKILLS.md` release-gate trigger scope was not self-verified. | Added fixture requirement for `SKILLS.md` and `scripts/release-gate.sh` membership in `AGENT_PLAYBOOK_FIXTURE_TARGETS`. |
| 14 | warning | Red/green stages were not clearly red first. | Split Stage 1 and Stage 2 into explicit red fixture additions followed by green source/doc updates. |
| 15 | warning | Secret-like user input could be echoed into route cards. | Added redaction rule and scanner-safe fake secret-shaped scenario requirement. |
| 16 | warning | Hook precedence could blur secret hook installation and hook fragility audit. | Narrowed safety precedence and preserved hook fragility routing to `$antifragile:antifragile-agent`. |

## Review Rounds

| Round | Angle | Route | Verdict |
|---|---|---|---|
| 1 | architecture correctness | sub-agent | 1 critical, 4 warnings; fixed |
| 1 | implementation/testability | sub-agent | 1 critical, 4 warnings; fixed |
| 2 | architecture correctness | sub-agent | 2 critical, 3 warnings; fixed |
| 2 | implementation/testability | sub-agent | 1 critical, 2 warnings; fixed |
| 3 | architecture correctness | sub-agent | 1 critical, 3 warnings; fixed |
| 3 | implementation/testability | sub-agent | 2 critical, 3 warnings; fixed |
| 4 | architecture correctness | sub-agent | 3 warnings; fixed |
| 4 | implementation/testability | sub-agent | 4 warnings; fixed |
| 5 | architecture correctness | degraded same-context | LGTM |
| 5 | implementation/testability | degraded same-context | LGTM |
| 5 | UI/UX | not applicable | no `interface-design.md` |

## Residual Open Issues

Empty.

## Design Drift

Empty. No `interface-design.md` exists for this slug. The final architecture remains aligned with `requirements.md`; the route-card interface extension preserves the original six required fields and adds only conditional ambiguity fields required by FR-11.

## Reviewer Final Verdicts

| Angle | Verdict |
|---|---|
| architecture correctness | LGTM |
| implementation/testability | LGTM |
| UI/UX | not applicable |

## Self-Review Notes

The recommendation still holds: Option A is the right scope for this patch, but only after strengthening it with parseable route-card examples and fixture-side expectations. Option B remains unnecessary because the design now gets deterministic coverage without adding a generated registry.
