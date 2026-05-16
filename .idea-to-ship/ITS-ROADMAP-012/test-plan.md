# Test Plan - ITS-ROADMAP-012

**Slug:** ITS-ROADMAP-012
**Date:** 2026-05-16
**Status:** draft

## Stage TDD Slices

| Stage | Story | Acceptance | Scenario | Test | Expected Initial Result | Command |
|---|---|---|---|---|---|---|
| Stage 1 - Extract agent-playbook audit report templates | Maintainer extracts audit report skeletons without changing report semantics | FR-1, FR-2, FR-3, FR-4, FR-5, FR-8 | Agent-playbook fixture suite requires each audit skill to reference its extracted template, and each template to preserve required headings/contract fields | TDD-1 | fail: template files and skill references do not exist yet | `bash tests/agent-playbook-eval-fixtures.sh` |

## Results

| Test | Command | Result | Notes |
|---|---|---|---|
| TDD-1 red gate | `bash tests/agent-playbook-eval-fixtures.sh` | failed as expected | `tool-review-template-reference-contract` missing template reference; `agent-playbook/templates/tool-review-report.md` missing. |
| TDD-1 green gate | `bash tests/agent-playbook-eval-fixtures.sh` | passed | New template reference and template content contract checks passed. |
| Release gate | `scripts/release-gate.sh --mode all --strict` | passed | Full strict gate passed, including agent-playbook fixture coverage. |
| Review fix 1 | `bash tests/agent-playbook-eval-fixtures.sh` | passed | Strengthened template checks so each required token is its own invariant and added forbidden inline-skeleton guards. |
