# Test Plan - ITS-ROADMAP-001

**Date:** 2026-05-09
**Target:** `scripts/release-gate.sh`, `RELEASE-GATE.md`
**Framework:** shell fixture tests
**Run command:** `bash tests/release-gate-stage1.sh`

## Scope

Stage 1 covers the first blocking release gate only: manifest JSON validation,
skill frontmatter structural validation, git diff whitespace validation, and
secret scanning through the existing deterministic scanner. Advisory scans,
hooks, CI, and full fixture coverage for `--json` are out of scope for this
stage.

## User Stories

| Story ID | Actor | Goal | Preconditions | Trigger | Expected Outcome | Source |
|---|---|---|---|---|---|---|
| US-1 | Release author | Run one local gate before committing or releasing plugin changes. | Repo has plugin manifests, skill files, git, jq, python3, and the secret scanner. | Execute `scripts/release-gate.sh --mode <mode>`. | Blocking checks are grouped, exit code reflects pass/fail/usage, and no repo state is mutated. | FR-1, FR-2, FR-3, FR-4, FR-8 |

## Acceptance Criteria

| AC ID | Story ID | Criterion | Verification Method | Source |
|---|---|---|---|---|
| AC-1 | US-1 | Valid manifests, skill frontmatter, clean diff, and no staged secrets return exit `0`. | `T1` valid fixture passes. | FR-1..FR-4 |
| AC-2 | US-1 | Malformed plugin JSON returns exit `1` and reports `manifest-json`. | `T2` malformed manifest fixture. | FR-1 |
| AC-3 | US-1 | Missing skill frontmatter required keys returns exit `1` and reports `skill-frontmatter`. | `T3` malformed skill fixture. | FR-2 |
| AC-4 | US-1 | Staged whitespace errors are detected with cached diff semantics. | `T4` staged trailing whitespace fixture. | FR-3 |
| AC-5 | US-1 | Working-tree whitespace errors are detected in `--mode working`. | `T5` unstaged trailing whitespace fixture. | FR-3 |
| AC-6 | US-1 | Staged secret findings are blocking and reported without preventing the grouped report. | `T6` staged secret fixture. | FR-4 |
| AC-7 | US-1 | Usage errors and missing blocking checker files return exit `2`. | `T7` invalid mode and `T8` missing scanner fixtures. | architecture § Failure Modes & Handling |

## Scenario Matrix

| Scenario ID | Story ID | Type | Sequence | Inputs / Setup | Expected | Failure Signal | Source |
|---|---|---|---|---|---|---|---|
| S-1 | US-1 | happy | Create valid fixture repo, run staged gate. | Valid marketplace, plugin manifest, skill, clean git index. | Exit `0`, all Stage 1 checks pass. | none | AC-1 |
| S-2 | US-1 | invalid-input | Corrupt and stage one plugin manifest, run staged gate. | Staged plugin manifest contains invalid JSON. | Exit `1`, manifest check fails. | `FAIL manifest-json` | AC-2 |
| S-3 | US-1 | invalid-input | Remove and stage a required skill frontmatter field, run staged gate. | Staged skill frontmatter lacks `description`. | Exit `1`, frontmatter check fails. | `FAIL skill-frontmatter` | AC-3 |
| S-4 | US-1 | corner | Stage a whitespace error, run staged gate. | New staged file has trailing whitespace. | Exit `1`, cached diff whitespace check fails. | `FAIL diff-whitespace` | AC-4 |
| S-5 | US-1 | corner | Leave a whitespace error unstaged, run working gate. | Tracked working-tree file has trailing whitespace. | Exit `1`, working diff whitespace check fails. | `FAIL diff-whitespace` | AC-5 |
| S-6 | US-1 | failure-mode | Stage a deterministic secret pattern, run staged gate. | Staged file has a generic secret assignment. | Exit `1`, secret scan fails but report still prints. | `FAIL secret-scan` | AC-6 |
| S-7 | US-1 | invalid-input | Run the gate with an invalid mode. | `--mode banana`. | Exit `2`, usage error is printed. | `Invalid --mode` | AC-7 |
| S-8 | US-1 | failure-mode | Remove the secret scanner, run staged gate. | `secret-scanner/scripts/scan.py` missing. | Exit `2`, grouped report still includes secret-scan failure. | `FAIL secret-scan` | AC-7 |
| S-9 | US-1 | regression | Stage invalid manifest JSON, then fix only the worktree before running staged gate. | Index is invalid; worktree is valid. | Exit `1`, proving staged gate reads the index. | `FAIL manifest-json` | AC-2 |
| S-10 | US-1 | regression | Stage invalid skill frontmatter, then fix only the worktree before running staged gate. | Index is invalid; worktree is valid. | Exit `1`, proving staged gate reads the index. | `FAIL skill-frontmatter` | AC-3 |

## Test Matrix

### Integration

| # | Scenario | Case | Setup | Expected | Source |
|---|---|---|---|---|---|
| T1 | S-1 | valid fixture passes | Temporary git repo with valid plugin data. | exit `0`; `PASS` for all Stage 1 checks. | AC-1 |
| T2 | S-2 | malformed plugin JSON fails | Replace and stage plugin manifest with invalid JSON. | exit `1`; report includes `FAIL manifest-json`. | AC-2 |
| T3 | S-3 | malformed skill frontmatter fails | Remove and stage `description` from skill frontmatter. | exit `1`; report includes `FAIL skill-frontmatter`. | AC-3 |
| T4 | S-4 | staged whitespace fails | Stage file with trailing whitespace. | exit `1`; report includes `FAIL diff-whitespace`. | AC-4 |
| T5 | S-5 | working whitespace fails | Modify tracked file with trailing whitespace but do not stage. | exit `1`; report includes `FAIL diff-whitespace`. | AC-5 |
| T6 | S-6 | staged secret fails | Stage generic secret assignment. | exit `1`; report includes `FAIL secret-scan`. | AC-6 |
| T7 | S-7 | invalid mode fails as usage | Run `--mode banana`. | exit `2`; stderr includes `Invalid --mode`. | AC-7 |
| T8 | S-8 | missing scanner fails as usage | Remove `secret-scanner/scripts/scan.py`. | exit `2`; report includes `FAIL secret-scan`. | AC-7 |
| T9 | S-9 | staged manifest snapshot wins over worktree | Stage invalid manifest JSON, then repair the worktree. | exit `1`; report includes `FAIL manifest-json`. | AC-2 |
| T10 | S-10 | staged frontmatter snapshot wins over worktree | Stage invalid frontmatter, then repair the worktree. | exit `1`; report includes `FAIL skill-frontmatter`. | AC-3 |

## Traceability

| Requirement | Story | Acceptance Criteria | Scenarios | Tests |
|---|---|---|---|---|
| FR-1 | US-1 | AC-1, AC-2 | S-1, S-2, S-9 | T1, T2, T9 |
| FR-2 | US-1 | AC-1, AC-3 | S-1, S-3, S-10 | T1, T3, T10 |
| FR-3 | US-1 | AC-1, AC-4, AC-5 | S-1, S-4, S-5 | T1, T4, T5 |
| FR-4 | US-1 | AC-1, AC-6 | S-1, S-6 | T1, T6 |
| FR-8 | US-1 | AC-1, AC-7 | S-1, S-7, S-8 | T1, T7, T8 |

## Out Of Scope

- Advisory runtime-aware wording and hook robustness scans belong to Stage 2.
- Full `--json` fixture assertions belong to Stage 3.
- Hook installation and CI enforcement are not part of ITS-ROADMAP-001 Stage 1.

## Fixtures & Test Data

`tests/release-gate-stage1.sh` builds temporary git repositories and copies the
repo's release gate script and secret scanner into each fixture. Fixtures are
removed after the test process exits.

## Risk Notes

- The tests require `git`, `jq`, and `python3`, matching the Stage 1 gate's
  blocking tool requirements.

## Stage TDD Slices

Stage 1 TDD is covered by integration fixture tests `T1` through `T10`.

## Results

**Completed:** 2026-05-09 15:02 CST

- Tests added: 10 integration fixture cases.
- All pass: yes.
- Changed-file line coverage: not measured; no coverage tooling exists in this
  repo.
- Production fixes triggered by tests: implemented `scripts/release-gate.sh`;
  adjusted secret-scanner documentation examples after `--mode all` exposed
  scanner-matching sample credentials.
