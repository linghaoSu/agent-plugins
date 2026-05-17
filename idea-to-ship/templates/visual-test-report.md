# Visual Test Report - <slug>

## Summary

| Field | Value |
|---|---|
| aggregate_verdict | PASS / FAIL / NEEDS_USER |
| blocking_reasons | <none or list> |
| residual_risk | <known visual-test caveats or none> |
| next_action | <next action> |

## Inputs

| Field | Value |
|---|---|
| requirements | <path> |
| interface-design | <path or missing> |
| test-plan | <path or missing> |
| app root / URL | <target> |
| baseline mode | compare / create-requested / update-requested |

## Gate Results

| Gate | Status | Evidence |
|---|---|---|
| Gate 1 - Input Contract | <status> | <evidence> |
| Gate 2 - Tooling Discovery | <status> | <evidence> |
| Gate 3 - Selector/State Readiness | <status> | visual-test-selectors.md |
| Gate 4 - Matrix Derivation | <status> | visual-test-matrix.md |
| Gate 5 - Assert Before Capture | <status> | <assertions> |
| Gate 6 - Capture And Compare | <status> | <screenshots/baselines> |
| Gate 7 - Artifact RCA | <status> | visual-artifact-rca.md |
| Gate 8 - Matrix Closure | <status> | <verdict basis> |
| Gate 9 - Report Handoff | <status> | this file |

## Matrix Coverage

| Field | Value |
|---|---|
| matrix_status_counts | PASS=<n>, FAIL=<n>, FLAKY=<n>, MISS=<n>, NEEDS-RUN=<n>, SKIP-with-reason=<n> |
| required_cell_status_counts | PASS=<n>, FAIL=<n>, FLAKY=<n>, MISS=<n>, NEEDS-RUN=<n>, SKIP-with-reason=<n> |
| matrix link | visual-test-matrix.md |

## Freshness

| Field | Value |
|---|---|
| workspace_diff_fingerprint | <fingerprint> |
| git_status_snapshot | <status> |
| untracked_files_manifest | <manifest summary or link> |

## Baseline Decisions

| Field | Value |
|---|---|
| baseline_approval_summary | <approved / missing / requested> |
| approver/source | <person, issue, PR, design artifact, or missing> |
| date | <YYYY-MM-DD or missing> |
| baseline path | <path> |
| diff summary | <visual diff summary> |
| before artifact | <path> |
| after artifact | <path> |
| linked matrix cells | <cell IDs> |
| rationale | <why baseline is accepted or requested> |
| approval requests | <requests> |

## Console / Network

| Field | Value |
|---|---|
| console_status | PASS / FAIL / NOT_COLLECTED / IGNORED-with-justification |
| network_status | PASS / FAIL / NOT_COLLECTED / IGNORED-with-justification |
| console_network_summary | <summary and RCA links> |
| console_ignored_justification | <required when console_status is IGNORED-with-justification> |
| console_ignored_owner_or_source | <owner/source> |
| console_ignored_rca_link | <RCA link> |
| network_ignored_justification | <required when network_status is IGNORED-with-justification> |
| network_ignored_owner_or_source | <owner/source> |
| network_ignored_rca_link | <RCA link> |

## Artifact RCA

| Field | Value |
|---|---|
| artifact_rca_summary | <summary> |
| RCA link | visual-artifact-rca.md |

## Failures, Flakes, Missing Evidence

- <FAIL / FLAKY / MISS / NEEDS_USER items or none>

## Review Handoff

- `review-code` should flag unresolved failures, stale fingerprint, missing
  matrix evidence, missing baseline approval, weak artifact anchors, and
  unjustified console/network failures.
