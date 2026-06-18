# Test Plan - ITS-ROADMAP-023

## Stage TDD Slices

| Stage | Story | Acceptance | Scenario | Test | Expected Initial Result | Command |
|---|---|---|---|---|---|---|
| Stage 1 | Plugin maintainer exports a portfolio roadmap locally | Overview, child JSONL, manifest, required Markdown/JSONL, blocked unapproved candidate, and timestamp-stable content hashes are produced without provider APIs | Happy path portfolio roadmap with one eligible lane item and one unapproved candidate | TDD-1 | fail: `idea-to-ship/scripts/roadmap_export.py` is not implemented | `python3 tests/idea-to-ship-roadmap-export-fixtures.py "$PWD"` |
| Stage 1 | Plugin maintainer gets a hard failure for invalid lane data | Missing required roadmap fields halt before final artifacts and include retry guidance | Now item missing `Release Gate` | TDD-2 | fail: `idea-to-ship/scripts/roadmap_export.py` is not implemented | `python3 tests/idea-to-ship-roadmap-export-fixtures.py "$PWD"` |

## Backfill Test Slices

| Source | Gap | Scenario | Test | Expected Result | Command |
|---|---|---|---|---|---|

## Results

| Date | Command | Result | Notes |
|---|---|---|---|
| 2026-06-17 | `python3 tests/idea-to-ship-roadmap-export-fixtures.py "$PWD"` | failed as expected | Missing `idea-to-ship/scripts/roadmap_export.py`; ready for Stage 1 implementation. |
| 2026-06-17 | `python3 tests/idea-to-ship-roadmap-export-fixtures.py "$PWD"` | passed | Stage 1 exporter core implemented. |
