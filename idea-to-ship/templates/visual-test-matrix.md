# Visual Test Matrix - <slug>

## Status Vocabulary

`PASS`, `FAIL`, `FLAKY`, `MISS`, `NEEDS-RUN`, `SKIP-with-reason`

`SKIP-with-reason` is non-success for required coverage unless the source is
explicitly de-scoped with approver/source and rationale.

## Matrix

| cell_id | source_ids | required | route_or_screen | state | viewport | theme | browser_or_project | status | owner_or_approver |
|---|---|---|---|---|---|---|---|---|---|
| VT-001 | <IDs> | yes | <route> | <state> | <viewport> | <theme> | <browser> | NEEDS-RUN | <owner> |

## Cell Details

### VT-001

| Field | Value |
|---|---|
| assertion_command | <command or assertion> |
| screenshot_path | <path> |
| baseline_path | <path> |
| artifact_rca_link | <link> |
| verified_at | <timestamp> |
| source_commit | <sha> |
| comparison_range | <range> |
| git_status_snapshot | <status> |
| workspace_diff_fingerprint | <fingerprint> |
| untracked_files_manifest | <manifest link> |
| changed_paths_reviewed | <paths> |
| relevant_paths_or_config | <paths/config> |
| carry_forward_allowed | no |
| de_scope_approver_source | <approver/source or n/a> |
| de_scope_rationale | <required when status is SKIP-with-reason for required coverage> |
| prior_report_path | <previous visual-test-report.md or n/a> |
| prior_cell_id | <prior cell id or n/a> |
| previous_source_commit | <previous source commit or n/a> |
| relevant_paths_unchanged_evidence | <changed-path review evidence> |
| carry_forward_rationale | <rationale> |
| console_status | NOT_COLLECTED |
| network_status | NOT_COLLECTED |
| ignored_console_network_justification | <justification> |
| console_network_rca_link | <link> |

## Untracked Files Manifest

| path | classification | content_sha256 | exclusion_rationale |
|---|---|---|---|
| <path> | relevant / excluded | <sha or n/a> | <required when excluded> |

## Carry-Forward Rules

- A carried-forward `PASS` must cite previous report path, prior `cell_id`,
  previous `source_commit`, current `comparison_range`,
  `workspace_diff_fingerprint`, and changed paths reviewed.
- `FLAKY`, `FAIL`, `MISS`, `NEEDS-RUN`, and `SKIP-with-reason` cannot become
  `PASS` without fresh evidence.
- Unclassified untracked files block aggregate `PASS`.

## Aggregate Verdict Rules

| Condition | aggregate_verdict |
|---|---|
| All required cells are fresh or valid carried-forward `PASS`, baselines are approved, fingerprint matches, no unclassified untracked files, and console/network evidence is `PASS` or complete `IGNORED-with-justification` | PASS |
| Any required cell is `FAIL` or `FLAKY`, report-level console/network status is `FAIL`, or RCA has an unresolved product/test failure | FAIL |
| Any required cell is `MISS`, `NEEDS-RUN`, non-de-scoped `SKIP-with-reason`, stale fingerprint, unapproved baseline, `NOT_COLLECTED`, incomplete `IGNORED-with-justification`, or unclassified untracked file | NEEDS_USER |
