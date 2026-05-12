# Test Plan - Mandatory Brainstorm Gate

**Date:** 2026-05-09
**Target:** `idea-to-ship/README.md`, `idea-to-ship/skills/*/SKILL.md`,
`tests/idea-to-ship-eval-fixtures.py`
**Framework:** Python standard-library contract fixture plus release gate
**Run command:** `bash tests/idea-to-ship-eval-fixtures.sh`

## Scope

This plan covers the mandatory brainstorm contract. It verifies that README and
downstream skills require `requirements.md` from `/brainstorm`, and that the
contract fixture guards against regression. It does not add runtime execution
for live model behavior.

## User Stories

| Story ID | Actor | Goal | Preconditions | Trigger | Expected Outcome | Source |
|---|---|---|---|---|---|---|
| US-1 | Maintainer | Start a new slug with brainstorm before design or implementation. | No `requirements.md` exists for the slug. | Run a downstream skill. | Skill stops and points to `/brainstorm --slug <slug>`. | FR-1, FR-2 |
| US-2 | Reviewing agent | Avoid inferring requirements from diffs when testing or reviewing. | A diff exists but requirements are missing. | Run `/test` or `/review-code`. | Skill refuses to treat diff-derived intent as requirements. | FR-3, FR-4 |
| US-3 | Roadmap author | Sequence portfolio work without replacing requirements. | Portfolio candidates exist. | Run `/roadmap`. | Roadmap can plan candidates but marks brainstorm as the next action before downstream work. | FR-5 |

## Acceptance Criteria

| AC ID | Story ID | Criterion | Verification Method | Source |
|---|---|---|---|---|
| AC-1 | US-1 | README and brainstorm skill state brainstorm is mandatory. | Contract fixture checks README and brainstorm skill. | FR-1 |
| AC-2 | US-1 | Architect/test/review-code enforce `requirements.md` and point to `/brainstorm --slug <slug>`. | Contract fixture checks downstream skill files. | FR-2, FR-4 |
| AC-3 | US-2 | `/test` says diffs/logs are not substitutes for brainstormed requirements. | Contract fixture checks test skill. | FR-3 |
| AC-4 | US-3 | `/roadmap` states it does not replace brainstorm and slug mode requires requirements. | Contract fixture checks roadmap skill. | FR-5 |

## Scenario Matrix

| Scenario ID | Story ID | Type | Sequence | Inputs / Setup | Expected | Failure Signal | Source |
|---|---|---|---|---|---|---|---|
| S-1 | US-1 | happy | Run eval fixtures after skill updates. | Updated README/skills. | Exit `0`; mandatory brainstorm checks pass. | none | AC-1, AC-2 |
| S-2 | US-2 | regression | Remove mandatory brainstorm language from a checked skill. | Temporary copied fixture. | Eval fixture exits `1`. | failed contract id | AC-2, AC-3 |
| S-3 | US-3 | happy | Run release gate after docs/skill changes. | Current repo. | Exit `0`; skill frontmatter and secret scan pass. | release gate failure | AC-4 |

## Test Matrix

### Integration

| # | Scenario | Case | Setup | Expected | Source |
|---|---|---|---|---|---|
| I1 | S-1 | Mandatory brainstorm contract fixtures pass. | `bash tests/idea-to-ship-eval-fixtures.sh` | Exit `0`; 13 contract checks pass. | AC-1..AC-4 |
| I2 | S-3 | Release gate working passes. | `scripts/release-gate.sh --mode working` | Exit `0`. | AC-4 |
| I3 | S-3 | Release gate all passes. | `scripts/release-gate.sh --mode all` | Exit `0`. | AC-4 |

## Out Of Scope

- Live agent execution.
- Proving `requirements.md` origin through metadata.

## Results

- `bash tests/idea-to-ship-eval-fixtures.sh`: pass, 13 contract checks.
- Negative smoke with removed mandatory brainstorm wording: pass, helper exits
  `1` and reports `FAIL brainstorm-mandatory-skill-contract`.
- `python3 -m py_compile tests/idea-to-ship-eval-fixtures.py`: pass.
- `git diff --check`: pass.
- `scripts/release-gate.sh --mode working`: pass.
- `scripts/release-gate.sh --mode all`: pass.
