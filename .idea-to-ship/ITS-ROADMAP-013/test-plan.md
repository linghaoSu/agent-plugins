# Test Plan - ITS-ROADMAP-013

**Slug:** ITS-ROADMAP-013
**Date:** 2026-05-16
**Status:** draft

## Stage TDD Slices

| Stage | Story | Acceptance | Scenario | Test | Expected Initial Result | Command |
|---|---|---|---|---|---|---|
| Stage 1 - Parse skill frontmatter with YAML semantics | Plugin maintainer catches loader-invalid skill frontmatter before release | FR-1, FR-4, FR-5 | Staged skill has `argument-hint: [--apply] [--all] [--force]`; release gate must fail `skill-frontmatter` | TDD-1 | fail: current structural validator lets invalid YAML pass | `bash tests/release-gate-stage1.sh` |

## Results

| Test | Command | Result | Notes |
|---|---|---|---|
| TDD-1 red gate | `bash tests/release-gate-stage1.sh` | failed as expected | `invalid yaml frontmatter` expected exit `1` but got `0`; current structural frontmatter validation passed the invalid YAML. |
| TDD-1 green gate | `bash tests/release-gate-stage1.sh` | passed | PyYAML frontmatter parsing rejects the invalid unquoted bracket `argument-hint` fixture and preserves existing release-gate stage 1 fixtures. |
| Full release gate | `scripts/release-gate.sh --mode all --strict` | passed | Full repo gate passed with `skill-frontmatter` using YAML frontmatter validation. |
