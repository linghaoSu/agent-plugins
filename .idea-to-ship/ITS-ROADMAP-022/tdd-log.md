# TDD Log - Agent-Playbook Workflow Router

## 2026-06-02 15:31 CST - stage-tdd

**Stage:** Stage 1 - Red then green router contract unit
**Mode:** stage-tdd
**Authority:** requirements.md + architecture.md + design-review.md
**Files touched:** `.idea-to-ship/ITS-ROADMAP-022/test-plan.md`, `tests/agent-playbook-eval-fixtures.py`, `.idea-to-ship/ITS-ROADMAP-022/tdd-log.md`
**Scenarios:** happy / edge / failure: parseable route-card examples, fixture-side route expectations, `needs_clarification`, secret redaction, local fix review, forbidden harness wildcard/generic handoff, no `Bash` in workflow-router frontmatter
**Command:** `bash tests/agent-playbook-eval-fixtures.sh`
**Initial Result:** expected failing result. New Stage 1 fixture failures:
`workflow-router-frontmatter-disallows-bash`, `workflow-router-forbidden-harness-wildcard`,
`workflow-router-forbidden-generic-harness-owner`, `workflow-router-route-card-examples-parse`,
`workflow-router-route-card-scenario-secret-scan`, `workflow-router-route-card-scenario-secret-hook-install`,
`workflow-router-route-card-scenario-local-fix-review`, `workflow-router-route-card-scenario-harness-ambiguous`,
and `workflow-router-route-card-scenario-secret-redaction`.
**Implementation Gate:** ready for `/implement`; production/doc changes must make `bash tests/agent-playbook-eval-fixtures.sh` pass without weakening the new fixture expectations.
