# Requirements - Frontend Visual Testing And Orchestration Intake

**Slug:** ITS-ROADMAP-016-020
**Date:** 2026-05-17
**Status:** draft
**Source:** `.idea-to-ship/roadmap.md` items `ITS-ROADMAP-016` through `ITS-ROADMAP-020`

## Problem

The repo already requires UI design contracts and code-review visual QA, but it
does not have an executable workflow that tells an agent how to run visual
verification, capture screenshots, compare baselines, triage Playwright reports,
or record matrix coverage without dumping large artifacts into context.

The same roadmap batch also contains adjacent Kagenti patterns: stable selector
recipes, context-safe CI artifact RCA, matrix-driven verification loops, and a
repo orchestration/bootstrap flow. The first four are directly useful for a
local visual-test workflow. The repo orchestration pattern is broader and risks
conflicting with `idea-to-ship` and `agent-playbook`; it should be evaluated as
a spike before any new orchestrator skill exists.

## Users / Actors

- Frontend implementer: runs a visual QA workflow after UI changes and records
  screenshot, selector, matrix, and artifact evidence.
- Design reviewer: uses the visual-test report to decide whether the UI matches
  `interface-design.md` and whether baseline changes are intentional.
- Code reviewer: checks visual-test traceability without reading raw logs,
  screenshots, or Playwright reports inline.
- Plugin maintainer: verifies the new skill, templates, and orchestration
  boundary through deterministic fixture checks.

## In Scope

- Create `$idea-to-ship:visual-test` as the executable workflow for UI visual QA
  tied to `interface-design.md`, `test-plan.md`, and code review.
- Add templates for selector/state recipes, visual test matrix tracking,
  visual-test reports, and context-safe artifact RCA.
- Document hard visual-test gates: assertions before screenshots, no silent
  baseline updates, no unresolved loading captures, no ignored console/network
  failures without justification, and precise artifact paths.
- Add fixture coverage for the new skill, metadata, templates, matrix statuses,
  baseline policy, large-artifact handling, and README/catalog discoverability.
- Evaluate `ITS-ROADMAP-020` with a local spike artifact that decides whether to
  adopt, reject, or adapt a repo orchestration/bootstrap skill.

## Out of Scope / Non-Goals

- No new frontend app, Playwright runtime, browser automation implementation, or
  screenshot comparison engine in this repo.
- No new generic `frontend` plugin unless a future roadmap item chooses that
  boundary.
- No automatic visual baseline generation or update without user/design
  approval.
- No GitHub writes, PR comments, CI mutation, commits, pushes, deployments, or
  credential retrieval in the new workflow.
- No copying Kagenti's broad self-replicating orchestrator or auto-installing
  skills/plugins into target repos.
- No replacement of existing `ui-design`, `test`, `tdd`, `review-code`,
  `bootstrap-project-memory`, or `implementation-tournament` ownership.

## Functional Requirements

| ID | Roadmap | Requirement |
|---|---|---|
| FR-1 | 016 | Add an `idea-to-ship:visual-test` skill with valid metadata and catalog entries. |
| FR-2 | 016 | The skill must define when to use it, required inputs, artifact outputs, and a workflow that maps `interface-design.md` visual QA into screenshots, assertions, baselines, and reports. |
| FR-3 | 016 | The workflow must require assertions before capture and forbid baseline updates without explicit approval. |
| FR-4 | 017 | Add a selector/state recipe template that records stable selectors, auth/session setup, route/state preconditions, async/loading completion, known flaky states, and preferred role/test-id strategies. |
| FR-5 | 018 | Add context-safe CI and Playwright artifact RCA guidance: download or reference large artifacts by path, inspect bounded snippets, and summarize exact anchors instead of pasting raw logs. |
| FR-6 | 019 | Add a matrix template/report contract with `PASS`, `FAIL`, `FLAKY`, `MISS`, `NEEDS-RUN`, and `SKIP-with-reason` statuses. Missing coverage must not count as success; `SKIP-with-reason` is non-success for required coverage unless the source is explicitly de-scoped from required coverage. |
| FR-7 | 019 | The visual-test workflow must support carry-forward pass status only when code/config relevant to that matrix cell has not changed, including a content-sensitive workspace diff fingerprint for staged, unstaged, and relevant untracked local changes. |
| FR-8 | 016/019 | `review-code` must consume visual-test artifacts when present or when UI is touched, and must flag unresolved visual failures, missing matrix evidence, missing baseline approval, or weak artifact anchors. |
| FR-8a | 016/018/019 | Visual reports must include an aggregate verdict and console/network status fields; unresolved required cells, stale fingerprints, unapproved baselines, or unjustified console/network failures cannot be represented as passing. |
| FR-9 | 020 | Produce an orchestration spike artifact that evaluates adopt/reject/adapt, names overlaps with existing skills, and records hard boundaries against self-replication or broad autopilot behavior. |
| FR-10 | 020 | Fixture coverage must guard plugin skill/catalog surfaces so future work cannot silently add a broad repo orchestrator that commits, pushes, mutates GitHub, installs plugins, or copies skill trees. |
| FR-11 | all | Existing idea-to-ship, skill hygiene, topology, metadata, and strict release-gate checks must pass. |

## Non-Functional Requirements

- **Performance:** Fixture checks should remain lightweight static checks; full
  strict release gate must remain practical for local use.
- **Scale:** The workflow must handle large Playwright reports and CI logs by
  path/anchor summary rather than context dumps.
- **Reliability / failure mode:** Visual evidence must fail loud on missing
  screenshots, missing assertions, missing matrix cells, unresolved loading, and
  unapproved baseline changes.
- **Security / compliance:** Do not expose secrets from CI artifacts, auth state,
  screenshots, traces, or downloaded logs. Do not mutate git, GitHub, CI,
  deployments, or plugin caches.
- **Platform / constraints:** Reuse existing Markdown skill/template conventions,
  `agents/openai.yaml` metadata, README cataloging, and Python fixture style.

## Success Criteria

- New skill and templates are present -> verify by inspecting
  `idea-to-ship/skills/visual-test/SKILL.md`,
  `idea-to-ship/skills/visual-test/agents/openai.yaml`, and
  `idea-to-ship/templates/visual-test-*.md`.
- Visual-test contract is fixture-protected -> verify:
  `bash tests/idea-to-ship-eval-fixtures.sh`.
- Code review consumes visual evidence -> verify fixture coverage in
  `tests/idea-to-ship-eval-fixtures.py` for `review-code` visual-test artifact
  handling.
- Orchestration spike boundary is fixture-protected -> verify:
  `bash tests/agent-playbook-eval-fixtures.sh`.
- Skill hygiene and topology stay clean -> verify:
  `python3 scripts/skill-hygiene-check.py --mode working .` and
  `python3 scripts/skill-topology-scan.py .`.
- Full strict gate passes -> verify:
  `scripts/release-gate.sh --mode all --strict`.

## Open Questions

- Whether a future dedicated `frontend` plugin is useful remains open. This
  implementation defaults to `idea-to-ship:visual-test` because the workflow is
  anchored to `interface-design.md` and idea-to-ship artifacts.
- Whether orchestration should ever become an `agent-playbook` skill remains
  open. This stage produces a spike decision and fixture guardrails only.

## Touch Points

- `idea-to-ship/skills/visual-test/SKILL.md`
- `idea-to-ship/skills/visual-test/agents/openai.yaml`
- `idea-to-ship/templates/visual-test-report.md`
- `idea-to-ship/templates/visual-test-selectors.md`
- `idea-to-ship/templates/visual-test-matrix.md`
- `idea-to-ship/templates/visual-artifact-rca.md`
- `idea-to-ship/README.md`
- `README.md`
- `tests/idea-to-ship-eval-fixtures.py`
- `tests/agent-playbook-eval-fixtures.py`
- `.idea-to-ship/ITS-ROADMAP-020/orchestration-spike.md`
