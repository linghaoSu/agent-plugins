# Test Plan - ITS-ROADMAP-014

**Slug:** ITS-ROADMAP-014
**Date:** 2026-05-16
**Status:** draft

## Stage TDD Slices

| Stage | Story | Acceptance | Scenario | Test | Expected Initial Result | Command |
|---|---|---|---|---|---|---|
| Stage 1 - Topology report command and fixtures | Plugin maintainer inspects skill graph health locally | FR-1 through FR-9 | Fixture repo has valid skill links, broken skill refs, an orphan skill, a hub skill, and README coverage gaps; report must expose each section deterministically | TDD-1 | fail: `scripts/skill-topology-scan.py` is not implemented | `bash tests/skill-topology-scan-fixtures.sh` |
| Stage 1 - Topology report command and fixtures | Plugin releaser keeps topology fixtures wired through release gate | FR-10 | Release gate all-mode runs the topology fixture advisory command | TDD-2 | fail until release-gate wiring is implemented | `scripts/release-gate.sh --mode all --strict` |

## Results

| Test | Command | Result | Notes |
|---|---|---|---|
| TDD-1 red gate | `bash tests/skill-topology-scan-fixtures.sh` | failed as expected | `scripts/skill-topology-scan.py` was missing, so the fixture exited with topology scan expected exit `0`, got `2`. |
| TDD-1 green gate | `bash tests/skill-topology-scan-fixtures.sh` | passed | Fixture covers broken refs, orphan skills, self-reference handling, hub scoring, skill tree output, and README coverage gaps. |
| TDD-2 release gate | `scripts/release-gate.sh --mode all --strict` | passed | Full release gate runs `skill-topology-fixtures` as an advisory check and passes under strict mode. |
| Review fix release-gate fixture | `bash tests/skill-hygiene-release-gate-fixtures.sh` | passed | Added durable JSON fixture coverage for `skill-topology-fixtures` all/working/staged pass, warn/fail routing, skip routing, and `skill-topology-infra-drift` staged drift failure. |
