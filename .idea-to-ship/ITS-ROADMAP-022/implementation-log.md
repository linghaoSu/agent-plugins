# Implementation Log - ITS-ROADMAP-022

**Architecture:** architecture.md
**Started:** 2026-06-02

## Stage Status
- [x] Stage 1 - Red then green router contract unit
- [ ] Stage 2 - Discovery surface verification
- [ ] Stage 3 - Verify and hand off

## Stage 1 - Red then green router contract unit
**Completed:** 2026-06-02 15:42 CST

### Pre-Stage Assumptions
- architecture.md: Stage 1 is limited to router contract text, parseable route-card examples, scenario fixtures, and the allowed-tools boundary.
- interface-design.md: not applicable; this stage does not touch UI.
- codebase: `agent-playbook/skills/workflow-router/SKILL.md` currently contains `Bash`, generic `harness-engineering`, `$harness-engineering:*`, and no `### Route Card Examples`; `tests/agent-playbook-eval-fixtures.py` has red-first Stage 1 fixture checks.

### Success Criteria
- `bash tests/agent-playbook-eval-fixtures.sh` passes after implementation without weakening the new Stage 1 fixture expectations.

### Files touched
- `agent-playbook/skills/workflow-router/SKILL.md` - removed shell access, split secret scan vs hook install routing, replaced harness wildcard/generic routing with concrete skills or `needs_clarification`, added parseable route-card examples for the architecture minimum scenario set, and documented the moderate-size hygiene exception.
- `tests/agent-playbook-eval-fixtures.py` - added route-card scenario parsing, expanded fixture-side expectations across the architecture minimum scenario set plus secret-redaction coverage, and updated route coverage expectations from harness wildcard to concrete harness skills.
- `.idea-to-ship/ITS-ROADMAP-022/implementation-log.md` - recorded Stage 1 implementation evidence.

### Decisions made during implementation
- Removed `Bash` from workflow-router allowed tools instead of policy-limiting it in prose, matching the architecture's stricter conversation-only boundary.
- Added parseable YAML route-card examples for the full architecture minimum scenario set rather than trying to simulate model classification.
- Kept route-card examples inside `SKILL.md` and added a `moderate-skill-bloat` hygiene exception because the fixtures intentionally parse the same public artifact as the route catalog to catch catalog/example drift.
- Kept Stage 2 discovery-surface trigger checks out of this stage; this stage only implements the router contract unit.

### Deviations from design artifacts
- none

### Adjacent issues noticed (NOT fixed here)
- Stage 2 still needs explicit discovery-surface fixture coverage and release-gate trigger-scope self-checks for `SKILLS.md` and `scripts/release-gate.sh`.

### Verification
- build: not applicable
- lint: `python3 scripts/skill-hygiene-check.py --mode all .` passed
- tests: `bash tests/agent-playbook-eval-fixtures.sh` passed; `python3 scripts/skill-topology-scan.py .` passed; `scripts/release-gate.sh --mode all --strict` passed
- tdd: `tdd-log.md` entry 2026-06-02 15:31 CST, failing test then passed (`bash tests/agent-playbook-eval-fixtures.sh`); Stage 1 implementation then expanded the same fixture pattern to the full architecture minimum route-card scenario set.

### Cross-Skill Checks
| Skill | Trigger | Result | Impact |
|---|---|---|---|
| `secret-scanner:scan-secrets --mode working` | Stage edits route-card examples and secret redaction wording. | Ran `python3 secret-scanner/scripts/scan.py --mode working --format json`; result `[]`. Strict release gate also passed `--mode all` secret scan. | No follow-up needed. |
| `harness-engineering:harness-audit` | Stage routes harness skills but does not implement harness behavior, state, retry, evaluator, or tool middleware. | Not triggered. | No impact. |
