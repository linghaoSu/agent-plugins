# Requirements - Agent-Playbook Workflow Router

**Slug:** ITS-ROADMAP-022
**Date:** 2026-06-02
**Status:** draft

## Problem

The plugin suite now has many specialized workflows: idea-to-ship, issue
evaluation, agent-playbook audits, antifragile audits, harness-engineering,
secret scanning, worktree cleanup, and commit/PR handoff. Users who know the
goal but not the owning plugin can start in the wrong place, skip required
artifacts, or ask a mutating workflow to do read-only triage.

The current workflow-router implementation is intended to be the "Start Here"
entry point, but review found two user-facing routing bugs: pre-commit hook
installation can be handed to the read-only secret scanner, and harness work can
emit `$harness-engineering:*`, which is not a copy-pasteable skill invocation.
The router must give precise handoffs without becoming an executor or broad
orchestrator.

## Users / Actors

- Plugin operator: asks which workflow should handle a feature, issue, PR,
  audit, resilience, secret, worktree, or commit-readiness request.
- Next agent or assistant turn: consumes the route card and invokes the named
  owner directly.
- Maintainer/reviewer: checks the catalog, docs, and fixtures to ensure the
  router does not drift into a mutating or non-invocable workflow.

## In Scope

- Add `$agent-playbook:workflow-router` as the documented Start Here workflow
  for ambiguous ownership across the local plugin suite.
- Produce exactly one primary route card with `recommended_workflow`, `steps`,
  `required_inputs`, `mutation_points`, `stop_conditions`, and `next_prompt`.
- Route feature/product work, issue/bug work, PR work, context/tool governance,
  resilience/safety work, secret work, worktree cleanup, and commit-readiness
  work to their owning workflows.
- Distinguish read-only secret scanning from pre-commit hook installation or
  enforcement.
- Route harness-engineering requests to concrete skills instead of wildcard
  plugin names.
- Document the router in root docs, skill catalogs, agent-playbook docs, and
  plugin marketplace metadata.
- Add or update fixtures so the route-card contract and critical routing
  distinctions are checked by local verification.

## Out of Scope / Non-Goals

- Do not execute downstream skills from the router.
- Do not write route artifacts; the router is conversation-only.
- Do not mutate target code, tests, git state, GitHub, hooks, credentials,
  installed tools, or runtime/plugin configuration.
- Do not replace downstream workflow-specific intake, review, test, or commit
  skills.
- Do not introduce a broad autonomous orchestrator that chains work without the
  user invoking the owner.
- Do not change unrelated plugin behavior or public skill names except where
  docs/catalog entries are needed for the router.
- Do not write final roadmap lanes for this item; the roadmap has only approved
  candidate intake and current-task sync.

## Functional Requirements

1. **FR-1 - Start Here entry.** The repo must expose
   `$agent-playbook:workflow-router` as the Start Here entry point when the user
   is unsure which plugin owns the work.
2. **FR-2 - Route-card output.** The router must answer with one primary route
   card containing `recommended_workflow`, `steps`, `required_inputs`,
   `mutation_points`, `stop_conditions`, and `next_prompt`.
3. **FR-3 - Copy-pasteable next prompt.** Every `next_prompt` must use a
   concrete plugin-qualified skill invocation or ordered workflow name that the
   user can run directly.
4. **FR-4 - Conversation-only boundary.** The router must not execute
   downstream skills or perform mutating work; it may inspect only enough local
   context to disambiguate routing.
5. **FR-5 - Feature/product routing.** New ideas, fuzzy requirements, UX,
   implementation plans, commercial questions, and roadmap prioritization must
   route to the appropriate `idea-to-ship` sequence.
6. **FR-6 - Issue and PR routing.** GitHub issue, concrete bug, local fix
   review, PR review, reviewer-comment handling, and style-rule drift must
   route to the appropriate `issue-evaluator` workflow.
7. **FR-7 - Agent/tool governance routing.** Repo memory, context hygiene, MCP
   or tool sprawl, single tool/CLI/MCP review, and fast-coding drift must route
   to the appropriate `agent-playbook` workflow.
8. **FR-8 - Resilience and harness routing.** Agent/plugin fragility, target
   system resilience, harness design, harness audit, sprint contracts,
   long-horizon goal mode, and recovery planning must route to concrete
   `antifragile` or `harness-engineering` skills by request intent.
9. **FR-9 - Secret routing split.** Secret scan or leak-audit requests must
   route to `$secret-scanner:scan-secrets`, while pre-commit hook installation
   or enforcement requests must route to
   `$secret-scanner:install-precommit-hook`.
10. **FR-10 - Worktree and commit routing.** Stale worktree cleanup must route
    to `$worktree-cleaner:clean-worktrees`, and finished local diffs that need a
    human-authored commit or draft PR must route to
    `$agent-playbook:commit-changes`.
11. **FR-11 - Ambiguity handling.** If several owners are plausible, the router
    must choose the narrow owner first, list assumptions, and include stop
    conditions or at most three short clarification questions when a safe
    default is not available.
12. **FR-12 - Catalog/docs coverage.** Root docs, `SKILLS.md`, agent-playbook
    docs, plugin metadata, and marketplace metadata must make the router
    discoverable without overstating its authority or mutation ability.
13. **FR-13 - Regression fixtures.** Local fixtures must cover the route-card
    fields, the major owner categories, hook-install routing, scan routing,
    concrete harness routing, and the no-execution/no-mutation boundary.

## Non-Functional Requirements

- **Performance:** Not latency critical; local inspection should stay bounded
  and should not perform repo-wide scans unless needed to disambiguate routing.
- **Scale:** The route catalog must remain readable as the local plugin suite
  grows; additions should prefer narrow owner entries over catch-all wildcards.
- **Reliability / failure mode:** When routing cannot be decided safely, the
  router must fail loud with stop conditions or short questions instead of
  guessing a mutating owner.
- **Security / compliance:** The router must not install hooks, rotate secrets,
  expose secret material, change credentials, or mutate security tooling. It
  must route security actions to the owning secret-scanner skill.
- **Platform / constraints:** The implementation lives in this repo's plugin
  skill markdown, docs/catalog files, plugin metadata, and deterministic
  fixture/release-gate checks. No network dependency is required.

## Success Criteria

- Start Here discovery works -> verify `README.md`, `SKILLS.md`,
  `agent-playbook/README.md`, `.claude-plugin/marketplace.json`, and
  `agent-playbook/.claude-plugin/plugin.json` mention the router accurately.
- Route-card contract is present -> verify
  `tests/agent-playbook-eval-fixtures.py` checks all six required route-card
  fields in `agent-playbook/skills/workflow-router/SKILL.md`.
- Router remains conversation-only -> verify docs and fixtures assert that it
  does not execute downstream skills or mutate code, git, GitHub, hooks, or
  installed tools.
- Hook-install requests route to the installer -> verify a fixture or invariant
  distinguishes `$secret-scanner:install-precommit-hook` from
  `$secret-scanner:scan-secrets`.
- Secret scan requests still route to the scanner -> verify a fixture or
  invariant keeps `$secret-scanner:scan-secrets` for leak scan/audit requests.
- Harness routing is concrete -> verify no route-card or catalog path requires
  users to invoke `$harness-engineering:*`; harness intents name concrete
  skills such as `$harness-engineering:harness-design`,
  `$harness-engineering:harness-audit`,
  `$harness-engineering:resilience-plan`, `$harness-engineering:goal-mode`, or
  `$harness-engineering:sprint-contract`.
- Major owner categories are covered -> verify fixture coverage includes
  idea-to-ship, issue-evaluator, PR handling, agent-playbook governance,
  antifragile, harness-engineering, secret-scanner, worktree-cleaner, and
  commit-changes routing.
- Local verification passes after the review fixes -> verify
  `bash tests/agent-playbook-eval-fixtures.sh`,
  `python3 scripts/skill-hygiene-check.py --mode all .`,
  `python3 scripts/skill-topology-scan.py .`, and
  `scripts/release-gate.sh --mode all --strict` pass.

## Open Questions

- None blocking for requirements. Architecture and implementation may choose
  the exact route table wording and fixture granularity as long as the routing
  distinctions and boundaries above remain testable.

## Touch Points

- `agent-playbook/skills/workflow-router/SKILL.md`
- `agent-playbook/skills/workflow-router/agents/openai.yaml`
- `tests/agent-playbook-eval-fixtures.py`
- `tests/agent-playbook-eval-fixtures.sh`
- `README.md`
- `SKILLS.md`
- `agent-playbook/README.md`
- `.claude-plugin/marketplace.json`
- `agent-playbook/.claude-plugin/plugin.json`
- `agent-playbook/PRINCIPLES.md`
- `agent-playbook/WORKFLOW-CONTRACTS.md`
