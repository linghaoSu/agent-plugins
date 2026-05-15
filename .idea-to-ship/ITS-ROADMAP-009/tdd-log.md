# TDD Log - ITS-ROADMAP-009

## 2026-05-15 13:36 - stage-tdd
**Stage:** Stage 1 - Extract and Guard Evaluate-Issue Prompts
**Mode:** stage-tdd
**Authority:** requirements.md and architecture.md
**Files touched:** `tests/agent-playbook-eval-fixtures.py`, `.idea-to-ship/ITS-ROADMAP-009/test-plan.md`
**Scenarios:** failure path for missing extracted prompt/template artifacts and missing `evaluate-issue` references
**Command:** `bash tests/agent-playbook-eval-fixtures.sh`
**Initial Result:** failed as expected with missing `issue-evaluator/prompts/evaluate-issue-round2-adversarial.md` and missing extracted-reference invariants
**Implementation Gate:** ready for /implement
