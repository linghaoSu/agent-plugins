# Requirements - Roadmap External PM Export

**Slug:** ITS-ROADMAP-023
**Date:** 2026-06-17
**Status:** draft

## Problem

`idea-to-ship` roadmaps already capture the planning data needed to create
actionable work items: stable item IDs, status, work type, evidence class,
source anchors, release gates, evidence required, dependencies, and risk. That
information currently lives in local markdown, so maintainers cannot easily
turn it into Linear or GitLab issue lists without manually copying fields and
losing traceability.

Letting `/roadmap` write directly to Linear or GitLab would be too risky for
the first pass. Live writes introduce provider authentication, remote state
overwrites, duplicate issue creation, conflicts with human-edited issue text,
and non-deterministic release checks. The first stage must solve the safer
local export problem: produce reviewable, import-ready, retryable, and
deduplicated issue/item artifacts while keeping the roadmap as the source of
truth.

## Users / Actors

- Plugin maintainer: generates Linear/GitLab-ready local issue lists from an
  `idea-to-ship` roadmap and reviews them before any external import.
- Project operator: uses the exported overview issue/item and linked child
  items to create an external project-management view.
- Import executor: manually imports the local export plan, or later runs a
  separate sync workflow. If some resources already exist, they rely on stable
  IDs and the manifest to avoid duplicate creation.
- Reviewer: verifies that the export preserves roadmap evidence, release
  gates, risk, dependencies, and mutation boundaries without requiring live
  provider API writes.

## In Scope

- Provide an export-only first-stage capability for `idea-to-ship` roadmaps.
- Support Linear-ready and GitLab-ready local issue/item list exports.
- Use a shared internal issue schema with first-class Linear and GitLab
  provider mappings.
- Generate one overview issue/item for the selected roadmap export scope.
- Represent eligible roadmap items as child issue/item records linked to the
  overview issue/item.
- Require Markdown issue list and JSONL output; CSV is optional.
- Export final roadmap lane items and explicitly approved candidate items that
  have concrete source anchors.
- Preserve the stable roadmap item ID as the primary key for export, retry,
  and deduplication.
- Write a local manifest or sidecar mapping that records overview and child
  items, provider target, content hash, optional remote ID, and export status.
- On retry, read the manifest, stable IDs, and optional remote ID mapping to
  avoid generating duplicate create actions for already-created or already
  mapped resources.
- Hard fail when required fields are missing, mappings are ambiguous, or
  duplicate existing resources are detected.
- Include actionable retry guidance for every hard failure.
- Keep `/roadmap` and the export workflow from calling live Linear, GitLab, or
  GitHub APIs.

## Out of Scope / Non-Goals

- No live creation, update, close, delete, archive, comment, assignment, or
  milestone/cycle changes in Linear or GitLab for the MVP.
- No live sync or write-back in the MVP.
- No external PM tool may replace `requirements.md`, `architecture.md`,
  `test-plan.md`, `implementation-log.md`, `code-review.md`, or the roadmap as
  the source of truth.
- Do not export `Unverified Signals`, `Low` confidence, `Unknown` confidence,
  inferred-only items, or items without concrete source anchors by default.
- Do not treat the full Candidate Backlog as an external backlog import queue.
- Do not guess assignee, team, project, milestone, cycle, or label mappings.
  Missing required mappings hard fail. Missing optional mappings may warn or
  remain blank only when the target provider format remains valid.
- Do not use title-only matching for deduplication.
- Do not include live provider calls in the release gate.
- Do not commit or push export artifacts automatically; git remains owned by
  the existing commit workflow.

## Functional Requirements

| ID | Requirement |
|---|---|
| FR-1 | Export workflow must run in export-only mode for the MVP and must not call live Linear, GitLab, GitHub, Jira, or other PM provider APIs. |
| FR-2 | Export workflow must accept a roadmap source scope, at minimum the portfolio roadmap `.idea-to-ship/roadmap.md`; slug-level roadmap support may be included if architecture can keep the same schema. |
| FR-3 | Export workflow must parse roadmap items only from structured roadmap sections or approved candidate/lane item data that preserve stable item IDs. |
| FR-4 | Export workflow must generate one overview issue/item for the selected roadmap scope. The overview item must summarize the roadmap goal, scope, exported item count, provider target, export timestamp, and source roadmap path. |
| FR-5 | Export workflow must generate child issue/item records for eligible roadmap items and must express their relationship to the overview item in the exported artifacts. |
| FR-6 | Exported child records must preserve roadmap item ID, title, status, work type, evidence class, confidence, source anchors, lane or candidate rationale, release gate, evidence required, dependencies, risk, owner, and decision owner when present. |
| FR-7 | Linear and GitLab mappings must be first-class outputs over a shared internal issue schema. Provider-specific fields may differ, but no provider mapping may drop required roadmap evidence silently. |
| FR-8 | Required output formats are Markdown issue list and JSONL. CSV is optional and must not be the only machine-readable format. |
| FR-9 | The export must produce or update a local manifest/sidecar mapping that records stable roadmap ID, provider, overview/child role, content hash, export status, and optional remote ID / URL if supplied by the user or a future importer. |
| FR-10 | Reruns must use stable roadmap IDs plus the manifest/sidecar mapping to classify each item as new, unchanged, changed, skipped-existing, conflict, or needs-user. |
| FR-11 | If the manifest says a resource already exists, the export must not generate a duplicate create action for that roadmap ID. It must either emit a reuse/update instruction in the local plan or hard fail if the existing mapping conflicts with the current provider/scope. |
| FR-12 | If duplicate existing resources are detected through manifest data, remote IDs supplied by the user, or future fake-provider metadata, the export must hard fail with a `needs_user`-style resolution message instead of choosing one by title. |
| FR-13 | Items from `Unverified Signals`, `Low`, `Unknown`, inferred-only evidence, or missing source anchors must be excluded from executable child issue output by default and listed in a blocked/skipped section with reasons. |
| FR-14 | Missing required fields, ambiguous provider mapping, invalid item schema, duplicate stable IDs, or missing overview-link data must hard fail before writing final export artifacts. |
| FR-15 | Missing optional assignee/project/milestone/cycle mappings may produce warnings only when the exported provider format can still be valid without those fields. |
| FR-16 | Every hard failure must include a retry path: which input, mapping, manifest entry, or roadmap field to fix before rerunning. |
| FR-17 | Export artifacts must be deterministic: same roadmap input and same mapping config produce stable ordering, stable IDs, and stable content hashes except for explicit timestamp fields. |
| FR-18 | The workflow must clearly separate export-only MVP behavior from future live sync/write-back behavior in docs and hand-off text. |
| FR-19 | Tests or fixtures must cover overview item generation, child item association, blocked weak-signal items, hard-fail missing required fields, warning-only optional fields, rerun idempotency, duplicate prevention, and provider-free execution. |

## Non-Functional Requirements

- **Performance:** Not latency critical. Export should handle the normal
  `.idea-to-ship/roadmap.md` size in one local run. If item count or artifact
  size grows beyond a practical budget, the workflow should fail with a bounded
  message rather than stream unbounded output.
- **Scale:** MVP should support dozens of roadmap items in one export. The
  schema must not assume only `Now / Next / Later`; it must also represent an
  approved candidate item when explicitly allowed.
- **Reliability / failure mode:** Required-data problems hard fail before
  writing final export output. Partial or ambiguous state must not silently
  produce importable issue records.
- **Security / compliance:** No provider tokens, no live API calls, no remote
  mutation, and no secret material in exported artifacts. If future config
  needs provider auth, it belongs outside the MVP.
- **Platform / constraints:** Follow this repo's artifact-first markdown
  workflow, deterministic fixture style, and release-gate expectations. No
  network access is required for the MVP.
- **Idempotency:** Stable roadmap IDs and manifest content hashes are mandatory
  for retry. Title matching alone is not acceptable.
- **Human-edit preservation:** If export artifacts are rerun and contain
  human-owned sections, the workflow must use generated markers, a draft
  fallback, or another explicit preservation strategy before replacing content.

## Success Criteria

- Export-only boundary is enforced -> verify tests/fixtures confirm no live
  Linear/GitLab/GitHub API command is required or invoked.
- Overview issue/item is generated -> verify export output contains exactly one
  overview record for the selected roadmap scope with source path, scope,
  timestamp, provider target, and item count.
- Child items link to overview -> verify every executable child record includes
  the overview reference or provider-specific relationship instruction.
- Roadmap evidence is preserved -> verify sample exported Linear/GitLab records
  include roadmap ID, source anchors, release gate, evidence required,
  dependencies, and risk.
- Markdown and JSONL are produced -> verify fixture output includes both human
  readable and machine readable artifacts.
- Weak or unverified items are blocked -> verify fixture with `Unverified
  Signals`, `Low`, `Unknown`, and missing anchors excludes those records from
  executable issue output and explains why.
- Required-field errors hard fail -> verify missing stable ID, title, source
  anchors, release gate, or provider target exits non-zero and writes no final
  importable issue list.
- Optional mapping gaps are warnings when valid -> verify missing assignee,
  project, milestone, or cycle mapping does not fail if the target provider
  format can omit it.
- Retry avoids duplicates -> verify rerun with an existing manifest/remote ID
  mapping does not emit another create action for the same roadmap ID.
- Ambiguous duplicate state hard fails -> verify fixture with two existing
  remote IDs for one roadmap ID exits with a needs-user resolution.
- Deterministic output -> verify repeated export from identical input produces
  stable ordering and stable content hashes except for explicit timestamp
  metadata.
- Release checks remain green -> verify `bash tests/idea-to-ship-eval-fixtures.sh`
  and `scripts/release-gate.sh --mode all --strict` pass after implementation.

## Open Questions

- Exact artifact paths are open for architecture. Candidate default:
  `.idea-to-ship/<slug>/exports/<provider>/`.
- Exact command or skill entry point is open for architecture: extend
  `$idea-to-ship:roadmap` with an export mode, add a focused helper under
  `idea-to-ship`, or keep export as a script invoked by a future skill. The
  requirements only require the behavior and safety boundary.
- Exact Linear relationship representation is open for architecture: parent,
  related issue, project, or custom field, depending on provider capability.
- Exact GitLab relationship representation is open for architecture: epic,
  parent/child task, related issue, or label/link, depending on provider
  capability and edition constraints.
- Whether CSV should be implemented in the MVP remains optional unless a
  downstream importer requires it.
- Whether future live sync reads provider metadata is a post-MVP question. MVP
  may accept user-supplied remote IDs in the manifest but must not fetch them.

## Touch Points

- `.idea-to-ship/roadmap.md`
- `.idea-to-ship/ITS-ROADMAP-023/`
- `idea-to-ship/skills/roadmap/SKILL.md`
- `idea-to-ship/templates/roadmap-item-schema.md`
- `idea-to-ship/templates/roadmap-candidate-brief.md`
- `idea-to-ship/templates/roadmap-final.md`
- `idea-to-ship/WORKFLOW-CONTRACTS.md`
- `tests/idea-to-ship-eval-fixtures.py`
- `tests/idea-to-ship-eval-fixtures.sh`
- `scripts/release-gate.sh` only if architecture adds focused deterministic
  fixtures to the staged/all release gate
