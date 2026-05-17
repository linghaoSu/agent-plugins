# Test Plan - Frontend Visual Testing And Orchestration Intake

**Slug:** ITS-ROADMAP-016-020
**Date:** 2026-05-17
**Status:** complete

## Stage TDD Slices

| Stage | Red-First Check | Expected Initial Result |
|---|---|---|
| 1 - Visual-test contracts | `bash tests/idea-to-ship-eval-fixtures.sh` | Fails until `visual-test` skill, metadata, templates, README entries, and `review-code` handoff exist. |
| 1 - Orchestration boundary | `bash tests/agent-playbook-eval-fixtures.sh` | Fails until the ITS-ROADMAP-020 spike and broad-orchestrator guard fixtures exist. |

## Verification Commands

| Command | Purpose |
|---|---|
| `bash tests/idea-to-ship-eval-fixtures.sh` | Contract and scenario fixtures for visual-test artifacts and review-code handoff. |
| `bash tests/agent-playbook-eval-fixtures.sh` | Contract and scenario fixtures for the orchestration spike boundary. |
| `python3 scripts/skill-hygiene-check.py --mode working .` | Skill authoring hygiene for the new skill. |
| `python3 scripts/skill-topology-scan.py .` | Skill reference and README topology. |
| `python3 secret-scanner/scripts/scan.py --mode working --format json` | Secret scan for changed content. |
| `scripts/release-gate.sh --mode working --strict` | Working-tree strict release gate. |
| `scripts/release-gate.sh --mode all --strict` | Full strict release gate. |
