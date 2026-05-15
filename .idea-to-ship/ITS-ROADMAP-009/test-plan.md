# Test Plan - ITS-ROADMAP-009

## Stage TDD Slices

| Stage | Story | Acceptance | Scenario | Test | Expected Initial Result | Command |
|---|---|---|---|---|---|---|
| Stage 1 | US-1 prompt extraction preserves evaluate-issue behavior | FR-1 through FR-12 | Missing extracted artifacts fail the contract fixture before production edits | TDD-1 | fail: `issue-evaluator/prompts/evaluate-issue-round2-adversarial.md` is missing after fixture checks are added | `bash tests/agent-playbook-eval-fixtures.sh` |

## Results

- 2026-05-15 13:36 - `python3 -m py_compile tests/agent-playbook-eval-fixtures.py` passed.
- 2026-05-15 13:36 - `bash tests/agent-playbook-eval-fixtures.sh` failed as expected before implementation: missing `issue-evaluator/prompts/evaluate-issue-round2-adversarial.md` and missing `evaluate-issue` extracted artifact references.
- 2026-05-15 13:36 - `bash tests/agent-playbook-eval-fixtures.sh` passed after implementation.
