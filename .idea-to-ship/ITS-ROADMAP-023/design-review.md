# Design Review - Roadmap External PM Export

**Slug:** ITS-ROADMAP-023
**Date:** 2026-06-17
**Reviewer:** multi-agent: architecture correctness -> sub-agent; implementation testability -> sub-agent; UI/UX -> not applicable
**Iterations:** 4
**Result:** clean
**Mode:** multi-agent
**Degradation reason:** none

## Issues Raised & Resolution

| # | Severity | Issue | Resolution |
|---|---|---|---|
| 1 | critical | Candidate eligibility could export Candidate Brief / backlog blocks by broad heading match. | Fixed in `architecture.md` Parser Strategy with section-aware eligibility, explicit `**External Export:** Approved` marker, blocked reasons, and candidate fixtures. |
| 2 | critical | Manifest and mapping schemas lacked provider target identity, scope identity, mapping hash, and duplicate remote representation. | Fixed in `architecture.md` Interfaces, Manifest, and Failure Modes with `provider_target`, `mapping_hash`, `remote_refs`, conflict data, and deterministic merge rules. |
| 3 | warning | Cross-skill routing recorded routes as not run without a valid degradation reason. | Fixed in `architecture.md` Cross-Skill Routing with applied guidance and scoped-out rationale. |
| 4 | critical | JSONL records did not structurally preserve required FR-6 roadmap evidence. | Fixed with common JSONL schema, `roadmap_fields`, `provider_fields`, and source fields. |
| 5 | critical | Required vs optional Linear/GitLab mappings were undefined. | Fixed with provider mapping contract: Linear `team` and GitLab `project_path` hard fail, optional fields warn when valid. |
| 6 | critical | Manifest merge/classification lacked a deterministic state table. | Fixed with merge precedence table and local-only vs remote-backed status/action semantics. |
| 7 | critical | Determinism and hash inputs were underspecified. | Fixed with canonical hashing, source normalization, sorted JSON, stable ordering, timestamp seam, and hash exclusions. |
| 8 | warning | Atomic multi-file writes were underspecified. | Fixed with temp-dir publish, rollback journal, manifest-last commit marker, and cleanup rules. |
| 9 | critical | CLI could allow omitting required Markdown or JSONL output. | Fixed by making Markdown and JSONL unconditional and using additive `--csv` only. |
| 10 | critical | Rollback could leave newly-created importable files after first-run publish failure. | Fixed with absence markers and reverse journal replay that unlinks newly-created outputs. |
| 11 | warning | New export fixture would not trigger staged release-gate checks by itself. | Fixed by requiring `scripts/release-gate.sh` trigger-path update. |
| 12 | warning | Overview metadata required by FR-4 was implicit. | Fixed with required `overview_fields` and overview fixture coverage. |
| 13 | warning | Local-only reruns without remote refs incorrectly suppressed create instructions. | Fixed by keeping `unchanged` local exports as `action: create`; only remote-backed entries use `reuse`. |
| 14 | warning | Output size/item count budget was missing. | Fixed with `--max-items`, `--max-output-bytes`, hard-fail retry guidance, and fixture coverage. |
| 15 | critical | Generated timestamps in `body_markdown` could perturb `content_hash`. | Fixed by canonicalizing body timestamps before hashing and adding a fixture for generated-at-only changes. |
| 16 | warning | `scope` was not unique enough for slug roadmaps and alternate sources. | Fixed with `scope_type`, `scope_id`, source-path identity, and `overview:<scope_type>:<scope_id>` IDs. |
| 17 | warning | `--csv` was included in `mapping_hash` despite being additive. | Fixed by excluding output toggles from mapping identity and adding CSV-toggle fixture coverage. |

## Review Rounds

| Round | Angle | Route | Verdict |
|---|---|---|---|
| 1 | architecture correctness | sub-agent | 2 critical, 1 warning |
| 1 | implementation testability | sub-agent | 5 critical, 1 warning |
| 1 | UI/UX | not applicable | no `interface-design.md` |
| 2 | architecture correctness | sub-agent | 3 warnings |
| 2 | implementation testability | sub-agent | 2 critical, 2 warnings |
| 2 | UI/UX | not applicable | no `interface-design.md` |
| 3 | architecture correctness | sub-agent | 1 critical, 3 warnings |
| 3 | implementation testability | sub-agent | 1 warning |
| 3 | UI/UX | not applicable | no `interface-design.md` |
| 4 | architecture correctness | sub-agent | LGTM |
| 4 | implementation testability | sub-agent | LGTM |
| 4 | UI/UX | not applicable | no `interface-design.md` |

## Residual Open Issues

None.

## Design Drift

No interface design artifact exists for this slug. Requirements and architecture are aligned after review.

## Reviewer Final Verdicts

| Angle | Verdict |
|---|---|
| architecture correctness | LGTM |
| implementation testability | LGTM |
| UI/UX | not applicable |

## Self-Review Notes

The chosen Option A still fits after review. The design is more explicit but remains a deterministic local exporter owned by `$idea-to-ship:roadmap`, with no provider API writes and no separate public skill surface.

Implementation remains staged and independently shippable: core exporter and schemas first, provider mapping and publish transaction second, roadmap skill and release-gate integration third.
