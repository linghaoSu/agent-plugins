# Test Plan - Agent-Playbook Workflow Router

**Slug:** ITS-ROADMAP-022
**Date:** 2026-06-02
**Status:** stage-tdd

## Stage TDD Slices

| Stage | Story | Acceptance | Scenario | Test | Expected Initial Result | Command |
|---|---|---|---|---|---|---|
| Stage 1 | US-ROUTER-1: A maintainer can verify workflow-router route cards from deterministic examples before implementation changes. | AC-1: `SKILL.md` exposes parseable route-card examples that match fixture-owned expectations for critical routing and ambiguity cases. | S-1 happy: secret scan, pre-commit hook install, local fix review, and broad harness ambiguity examples are parsed and checked against expected workflows/prompts/fields. | TDD-1 `workflow-router-route-card-scenarios` | fail: `agent-playbook/skills/workflow-router/SKILL.md` has no `### Route Card Examples` section and still allows/uses old routes. | `bash tests/agent-playbook-eval-fixtures.sh` |
| Stage 1 | US-ROUTER-2: The router cannot claim conversation-only behavior while exposing mutating shell capability. | AC-2: workflow-router frontmatter excludes `Bash` from `allowed-tools`. | S-2 failure: fixture inspects workflow-router frontmatter and rejects `Bash`. | TDD-2 `workflow-router-frontmatter-disallows-bash` | fail: current workflow-router frontmatter still contains `Bash`. | `bash tests/agent-playbook-eval-fixtures.sh` |
| Stage 1 | US-ROUTER-3: Harness and secret routes fail closed when they would leak unsafe or non-invocable handoffs. | AC-3: route examples and route catalog reject wildcard/generic harness handoffs and secret-like echoing. | S-3 edge: generic harness requests use `needs_clarification`; scanner-safe secret-shaped input is redacted in route output. | TDD-3 `workflow-router-harness-and-secret-safety` | fail: current catalog still includes generic `harness-engineering` / `$harness-engineering:*` and has no redaction scenario. | `bash tests/agent-playbook-eval-fixtures.sh` |

## Results

| Date | Mode | Command | Result | Notes |
|---|---|---|---|---|
| 2026-06-02 | stage-tdd | `bash tests/agent-playbook-eval-fixtures.sh` | expected fail | Red-first gate failed on `workflow-router-frontmatter-disallows-bash`, harness wildcard/generic owner checks, missing `### Route Card Examples`, and missing route-card scenarios. |
