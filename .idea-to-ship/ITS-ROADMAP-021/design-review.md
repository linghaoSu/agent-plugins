# Design Review - Skill Cleaner Wrapper For Skill Stats

**Slug:** ITS-ROADMAP-021
**Date:** 2026-06-01
**Reviewer:** multi-agent: architecture correctness -> sub-agents; implementation/testability -> sub-agents; UI/UX -> not applicable
**Iterations:** 14
**Result:** clean
**Mode:** multi-agent
**Degradation reason:** none

## Issues Raised & Resolution

| # | Severity | Issue | Resolution |
|---|---|---|---|
| 1 | warning | External analyzer trust boundary was underspecified for local Node execution. | Clarified analyzer is trusted user-configured local code, invoked with `shell=False`, allowlisted flags, timeout, output caps, and identity checks. |
| 2 | warning | Report/apply scope could treat repo root as a broad mutation root. | Split discovery roots from mutation roots; whole repo root remains discovery-only and cannot authorize arbitrary child deletion. |
| 3 | warning | Log-source discovery was too implicit for Claude/Codex/OpenClaw logs. | Added first-class log-source resolution, caps, archive/deep exclusions, structured `skipped_logs`, and fixtures. |
| 4 | warning | Report-to-apply handoff risked reconstructing canonical paths from redacted display output. | Added canonical evidence bundle, machine-readable report fields, opaque action ids, and a rule forbidding text/path reconstruction. |
| 5 | warning | Plan approval could be bypassed or drift between display and apply. | Added local plan bundles, canonical JSON hashing, `approved-plan-sha`, TTL, repo/auth-input binding, and refusal of raw plan JSON. |
| 6 | warning | `report_id` was ambiguously described as a `preflight-plan` CLI argument. | Clarified the skill passes only `evidence_bundle.path` and selected action ids; `preflight-plan` validates `report_id` from the bundle. |
| 7 | warning | Config-disable rollback could corrupt pre-existing config values. | Required report-time absence, list hash, rollback snapshot hash, report-only behavior for existing values, and drift refusal. |
| 8 | warning | Public skill arguments did not align with wrapper arguments. | Aligned skill-facing `--config`, `--context-tokens`, and `--budget-percent` with detailed arguments and wrapper examples. |
| 9 | warning | Release-gate fixture obligations were easy to miss. | Added `skill-hygiene-release-gate-fixtures.sh --self-check` and full fixture command to implementation verification. |

## Review Rounds

| Round | Angle | Route | Verdict |
|---|---|---|---|
| 1-10 | architecture correctness | sub-agent | Warnings fixed across analyzer trust, roots, logs, evidence handoff, bundles, hashing, and release-gate coverage. |
| 1-10 | implementation testability | sub-agent | Warnings fixed across fixtureability, stable ids, plan/apply schema, config-disable safety, and verification commands. |
| 1-10 | UI/UX | not applicable | No `interface-design.md`; no UI surface. |
| 11 | architecture correctness | sub-agent | Warning on report handoff schema; fixed. |
| 11 | implementation testability | sub-agent | Warning on missing public `--config`; fixed. |
| 12 | architecture correctness | sub-agent | Warnings on `report_id` CLI ambiguity and artifact path wording; fixed. |
| 12 | implementation testability | sub-agent | LGTM. |
| 13 | architecture correctness | sub-agent | Warning on report-mode mutation wording and argument mismatch; fixed. |
| 13 | implementation testability | sub-agent | Warning on config-disable drift and omitted release-gate commands; fixed. |
| 14 | architecture correctness | sub-agent | LGTM. |
| 14 | implementation testability | sub-agent | LGTM. |
| 14 | UI/UX | not applicable | No `interface-design.md`; no UI surface. |

## Residual Open Issues

None.

## Design Drift

No UI contract applies. Requirements allow a local report artifact if architecture explicitly adds one; the chosen design does so through a wrapper-owned temp evidence bundle while keeping target/config/skill-root mutation out of report mode.

## Reviewer Final Verdicts

| Angle | Verdict |
|---|---|
| architecture correctness | LGTM |
| implementation testability | LGTM |
| UI/UX | not applicable |

## Self-Review Notes

The chosen Option B still fits after review: it adds the smallest deterministic guard layer around the external analyzer while keeping report-only default behavior and making apply safety machine-checkable. The staged implementation remains independently shippable: report wrapper first, public report mode second, apply gate third, release-gate wiring last.
