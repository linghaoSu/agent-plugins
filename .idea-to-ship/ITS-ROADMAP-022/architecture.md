# Architecture - Agent-Playbook Workflow Router

**Slug:** ITS-ROADMAP-022
**Date:** 2026-06-02
**Status:** draft
**References:** requirements.md

## Summary

Build the workflow router as a surgical extension of the existing
agent-playbook skill pattern: a Markdown `SKILL.md` route catalog, parseable
route-card examples, documented Start Here entries, and deterministic contract
fixtures. The chosen approach is to repair the two review-discovered routing
defects in the current catalog, then make fixtures parse canonical examples so
hook-install requests, style drift, repo-memory creation, and harness wildcard
regressions cannot pass the strict release gate.

## Goals / Non-Goals

Goals:

- Expose `$agent-playbook:workflow-router` as the Start Here entry for
  ambiguous workflow ownership.
- Keep the router conversation-only: it selects and explains the owner, but
  does not execute downstream skills or mutate repo, git, GitHub, hooks, tools,
  credentials, or runtime configuration.
- Make every `next_prompt` copy-pasteable by naming concrete skill invocations
  or a documented ordered workflow.
- Split secret scanning from pre-commit hook installation.
- Replace harness wildcard routing with concrete harness-engineering skills by
  intent.
- Make ambiguous routing explicit through assumptions and clarification
  questions instead of returning an authoritative-looking handoff.
- Verify the contract through local fixtures and the repo release gate.

Non-goals:

- No broad orchestrator, autonomous chaining, background execution, or
  downstream skill invocation.
- No route artifacts or persisted router state.
- No unrelated public skill renames or behavior changes.
- No generated route registry or docs generation in this stage.

## Codebase Context

Main-context exploration fallback: no explorer sub-agent was spawned because
the available `multi_agent_v1.spawn_agent` tool is restricted to requests where
the user explicitly asks for sub-agents or delegation. The architecture uses
local `rg` and bounded file reads instead.

- `agent-playbook/skills/workflow-router/SKILL.md` is the new user-facing
  router. It already follows the repo's skill format: frontmatter,
  conversation workflow, signal table, route catalog, route-card output schema,
  and boundary rules. It must also include a parseable `Route Card Examples`
  section that fixtures treat as the scenario source of truth.
- `tests/agent-playbook-eval-fixtures.py` is the existing deterministic
  contract fixture file for agent-playbook. It uses `ContractCheck` and
  `InvariantGroup` regex groups for positive contract checks, plus
  `ForbiddenPatternCheck` for banned text. The current workflow-router coverage
  still asserts `$harness-engineering:*`, so it must be updated with the fix.
- `tests/agent-playbook-eval-fixtures.sh` is a thin wrapper that runs the
  Python fixture helper.
- `scripts/release-gate.sh` includes `AGENT_PLAYBOOK_FIXTURE_TARGETS`, which
  already cover `agent-playbook`, plugin docs/metadata, skill files,
  `agents/openai.yaml`, and the agent-playbook fixture files.
- `README.md`, `SKILLS.md`, `agent-playbook/README.md`,
  `.claude-plugin/marketplace.json`, and
  `agent-playbook/.claude-plugin/plugin.json` are required public discovery
  and marketplace surfaces for the new Start Here entry. They must be checked
  explicitly, not treated as incidental docs.
- `agent-playbook/PRINCIPLES.md` and `agent-playbook/WORKFLOW-CONTRACTS.md`
  define the local safety style the router must follow: choose narrow owners,
  state assumptions, fail loud on ambiguity, and keep conversation-only skills
  at `outputs_written: []`.
- The current router frontmatter allows `Bash`, but the requirements do not
  require shell execution. The design should remove `Bash` from the router's
  allowed tools and rely on `Read`, `Glob`, and `Grep` for bounded inspection.

## Cross-Skill Routing

| Signal | Routed skill | Result | Design impact |
|---|---|---|---|
| Router produces structured route cards and routes harness-engineering work. | `harness-engineering:harness-design` / `harness-engineering:sprint-contract` applicability check | Not run; feature is a static router skill, not a new autonomous agent, evaluator loop, or persistent harness. | Keep route-card shape as the contract; do not introduce harness state, retries, evaluators, or orchestration. Name concrete harness skills in the catalog. |
| Requirements mention secret scan and pre-commit hook installation routing. | `secret-scanner:scan-secrets` guidance, not a scan | Not run at architecture stage; no secret material or auth/config examples are being designed. | Treat secret actions as routed owners. Do not embed credentials, hook bodies with secrets, or mutation behavior in the router. Implementation verification may run the scanner if generated examples/config are added. |
| No persistence, external API, irreversible side effect, or target-system runtime behavior in the chosen design. | none | No antifragile-system route required. | Failure handling stays at routing-contract level and release-gate verification. |

## Alternatives Considered

### Option A - Surgical Markdown Catalog And Fixture Repair

Keep the router as a Markdown skill, but add a parseable route-card example
section that deterministic fixtures can validate.

**Module changes:** `agent-playbook/skills/workflow-router/SKILL.md`,
`tests/agent-playbook-eval-fixtures.py`, `scripts/release-gate.sh`, and the
required discovery surfaces: `README.md`, `SKILLS.md`,
`agent-playbook/README.md`, `.claude-plugin/marketplace.json`, and
`agent-playbook/.claude-plugin/plugin.json`.

**Data flow:** User invokes `$agent-playbook:workflow-router` with free-form
intent -> the skill classifies signals -> the skill chooses one primary owner
or ordered sequence -> the skill emits a route card and a concrete
`next_prompt`. Fixtures do not execute the model; they parse canonical examples
from `SKILL.md` to verify that representative route cards stay correct.

**Interfaces:** The public interface is the route-card YAML shape:
`recommended_workflow`, `steps`, `required_inputs`, `mutation_points`,
`stop_conditions`, and `next_prompt`, with conditional `assumptions` and
`clarifying_questions` fields for ambiguous routing.

**Pros:** Smallest blast radius, matches current repo conventions, directly
fixes both P2 findings, strengthens scenario-level fixtures without adding a
new runtime path, and is easy to review.

**Cons:** The route catalog and canonical examples must be kept in sync.
Scenario fixtures verify representative route cards, but they are still offline
contract checks, not an executable router engine.

**Risk:** Medium. A future wording change could weaken a route without failing
fixtures unless the invariant groups and canonical examples are kept specific.

### Option B - Structured Route Registry With Generated Skill Sections

Introduce a route registry, such as `agent-playbook/skills/workflow-router/routes.yaml`,
and generate or validate the signal table, route catalog, and fixture
expectations from that source.

**Module changes:** New route registry file, a validation or generation script,
updates to `SKILL.md`, release-gate wiring, and fixture changes.

**Data flow:** User still invokes the Markdown skill, but the route catalog is
validated against a machine-readable registry during release checks.

**Interfaces:** Route entries would have fields like `intent`, `owner`,
`required_inputs`, `mutation_points`, `stop_conditions`, and
`next_prompt_template`.

**Pros:** Stronger single source of truth, easier future route additions, and
more precise fixture generation if the router grows.

**Cons:** Larger change than the current requirements need, introduces a new
maintenance path, and risks generated-doc churn across public skill text.

**Risk:** Medium-high for this patch. The schema could become a shallow module:
more machinery than route complexity currently justifies.

## Recommendation

**We pick Option A.** It satisfies every requirement with the smallest blast
radius and fits the existing skill authoring and fixture style. The tradeoff is
that route behavior remains text-and-fixture driven rather than schema-driven;
that is acceptable because the current scope is a Start Here route card and two
concrete routing defects, not a large dynamic router.

## Chosen Design - Detail

### Module Breakdown

- `agent-playbook/skills/workflow-router/SKILL.md` - canonical router contract,
  signal table, route catalog, output shape, and boundary rules. Its
  frontmatter should remove `Bash` so the conversation-only boundary is
  tool-enforced rather than policy-only. Add `### Route Card Examples` with
  fenced YAML blocks that include a `scenario_id`, `intent`, and full route-card
  fields for representative cases.
- `agent-playbook/skills/workflow-router/agents/openai.yaml` - model metadata
  for the skill; no behavior change expected unless validation requires it.
- `tests/agent-playbook-eval-fixtures.py` - deterministic contract checks for
  route-card fields, owner coverage, secret hook split, concrete harness routes,
  scenario-level example parsing, docs coverage, and forbidden wildcard/generic
  harness regressions.
- `tests/agent-playbook-eval-fixtures.sh` - wrapper used by local verification;
  no behavior change expected.
- `scripts/release-gate.sh` - update `AGENT_PLAYBOOK_FIXTURE_TARGETS` to include
  `SKILLS.md` and `scripts/release-gate.sh` so staged/working release gates
  rerun the agent-playbook fixtures when the public skill catalog or the
  release-gate trigger list changes.
- `README.md`, `SKILLS.md`, `agent-playbook/README.md`,
  `.claude-plugin/marketplace.json`, and
  `agent-playbook/.claude-plugin/plugin.json` - discovery surfaces. Each must
  expose `$agent-playbook:workflow-router` accurately and preserve
  conversation-only language.

### Data Flow

```text
user intent
  -> $agent-playbook:workflow-router
  -> Step 1 intake: goal, references, mutation risk
  -> Step 2 classify signal using most-specific owner
  -> Step 3 choose canonical sequence or concrete skill
  -> Step 4 emit one route card
  -> user or next assistant invokes next_prompt directly
```

The router never crosses the handoff boundary. It names the next owner and
mutation points, then stops.

### Interfaces

Route-card schema:

```yaml
recommended_workflow: <plugin-qualified skill or ordered workflow name>
steps:
  - <plugin-qualified skill invocation or named phase>
required_inputs:
  - <issue URL, slug, PR number, artifact, focus, approval, or "none">
mutation_points:
  - <which steps write artifacts, tests, code, git, GitHub, hooks, or none>
stop_conditions:
  - <missing requirement, unsafe mutation, ambiguous owner, failed gate, or none>
next_prompt: "<copy-paste prompt for the next skill>"
assumptions:
  - <assumption used to choose the route; required when ownership is ambiguous>
clarifying_questions:
  - <short question; include only when a safe default is not available>
```

The original six fields are required for every route card. `assumptions` is
required when the router chooses a safe default from ambiguous input.
`clarifying_questions` is required when no safe default exists. These two
fields are conditional interface extensions, not replacements for the required
route-card fields.

Clarification-only route cards use a sentinel:

```yaml
recommended_workflow: needs_clarification
steps:
  - ask clarifying questions
required_inputs:
  - user's answers to clarifying_questions
mutation_points:
  - none
stop_conditions:
  - ambiguous owner
next_prompt: "$agent-playbook:workflow-router <redacted original request plus answers>"
clarifying_questions:
  - <question 1>
```

The fixture must reject clarification cards with more than three questions and
must reject mutating downstream next prompts when `recommended_workflow` is
`needs_clarification`.

Critical route mappings:

| Intent | Route |
|---|---|
| New product idea, fuzzy requirement, UX, architecture, or implementation plan | `$idea-to-ship:brainstorm` through the documented idea-to-ship sequence |
| Monetization, ICP, pricing, packaging, or roadmap prioritization | `$idea-to-ship:commercialize` then `$idea-to-ship:roadmap` |
| GitHub issue, issue number, concrete bug, or local fix request | `$issue-evaluator:evaluate-issue`, then `$issue-evaluator:fix-issue` and `$issue-evaluator:review-fix` when fixing is requested |
| Review an existing local fix / current diff | `$issue-evaluator:review-fix` |
| PR review | `$issue-evaluator:review-pr` |
| PR reviewer-comment handling | `$issue-evaluator:fix-pr-comments` |
| PR or repo-specific style-rule drift | `$issue-evaluator:update-code-style` |
| Create or refine repo memory such as `CLAUDE.md` or `AGENTS.md` | `$agent-playbook:bootstrap-project-memory` |
| Audit repo memory, context hygiene, suite-level tool sprawl, or fast-coding drift | `$agent-playbook:context-audit` or `$agent-playbook:vibe-coding-health-check` by intent |
| One tool, CLI, MCP server, REST endpoint, or schema surface | `$agent-playbook:tool-review` |
| Agent/plugin/hook/skill infrastructure fragility | `$antifragile:antifragile-agent` |
| Target app/system resilience, fallback, data safety, or observability | `$antifragile:antifragile-system` |
| Secret scan, leak scan, staged/working/recent/full-repo credential audit | `$secret-scanner:scan-secrets` |
| Install or enforce secret scanning through a pre-commit hook | `$secret-scanner:install-precommit-hook` |
| New autonomous-agent harness design | `$harness-engineering:harness-design` |
| Existing harness, autonomous agent, or pipeline audit | `$harness-engineering:harness-audit` |
| Long-horizon checkpointed execution loop | `$harness-engineering:goal-mode` |
| Context reset or memory consolidation routine | `$harness-engineering:resilience-plan` |
| Generator/evaluator success contract | `$harness-engineering:sprint-contract` |
| Broad "harness work" without enough intent to choose one concrete skill | Ask a clarification question; do not route to generic `harness-engineering` |
| Stale worktree cleanup after PR merge/closure | `$worktree-cleaner:clean-worktrees` |
| Finished local diff needs local commit or draft PR | `$agent-playbook:commit-changes` |

Overlap precedence:

1. Specific owner beats broad family: PR comments beat generic PR review; one
   tool surface beats suite-level context audit; hook installation beats secret
   scan.
2. Safety owner comes before delivery owner only for credential/secret-scanning
   hook install or enforcement, destructive cleanup, or recovery risk.
3. Hook fragility / state pollution / recovery gaps still route to
   `$antifragile:antifragile-agent`, not to secret-scanning.
4. When the owner still cannot be selected safely, return a route card with
   `clarifying_questions` and no mutating next step.

Fixture hooks:

- Update `workflow-router-route-coverage-contract` so harness coverage requires
  concrete harness skill names, not `$harness-engineering:*`.
- Add a parseable `### Route Card Examples` section to
  `agent-playbook/skills/workflow-router/SKILL.md`. Each example is a fenced
  YAML block with `scenario_id`, `intent`, `recommended_workflow`, `steps`,
  `required_inputs`, `mutation_points`, `stop_conditions`, `next_prompt`, and
  conditional `assumptions` / `clarifying_questions`.
- Add scenario-level fixtures that parse those YAML examples and validate every
  route-card field against a fixture-side expectation table, not only token
  presence. The expectation table owns fixed `scenario_id` values, expected
  `recommended_workflow`, required `next_prompt` token, required
  `mutation_points` signals, required `stop_conditions` signals, and whether
  `assumptions` or `clarifying_questions` are required. Minimum scenarios:
  feature idea, commercial roadmap, GitHub issue/bug, PR review, PR reviewer
  comments, local fix review, style-rule drift, bootstrap repo memory, context
  audit/tool sprawl, single tool review, vibe-coding health check, antifragile
  agent audit, antifragile system audit, secret scan, pre-commit hook
  install/enforcement, harness design, harness audit, goal mode, resilience
  plan, sprint contract, ambiguous broad harness request, ambiguous secret
  concern, worktree cleanup, and commit handoff.
- Mutating downstream routes, including hook installation, worktree cleanup
  apply mode, and commit handoff, must list downstream mutation points and
  approval or stop conditions in their examples.
- Add a section-aware forbidden check that rejects wildcard or generic harness
  handoffs in route outputs while still permitting negative documentation that
  names the bad pattern. It must fail on `$harness-engineering:*` and on a
  generic `harness-engineering` owning route for user-facing handoffs.
- Add a frontmatter/tool-boundary check that rejects `Bash` in the
  workflow-router allowed-tools list.
- Keep route-card field and conversation-only boundary checks.
- Add explicit discovery-surface checks for `README.md`, `SKILLS.md`,
  `agent-playbook/README.md`, `.claude-plugin/marketplace.json`, and
  `agent-playbook/.claude-plugin/plugin.json`.
- Add a catalog/example consistency fixture that parses the critical route
  table in `SKILL.md` and compares it with the `scenario_id` expectation table.
  The fixture must fail on contradictory owners, prompts, or mutation
  boundaries.
- Add a release-gate self-check fixture that asserts `SKILLS.md` and
  `scripts/release-gate.sh` are included in `AGENT_PLAYBOOK_FIXTURE_TARGETS`;
  `--mode all --strict` alone is not enough to prove staged/working trigger
  scope.

### Data / Schema Changes

No persistence, database schema, or generated registry changes. There is one
public route-card interface extension: the original six route-card fields remain
required, while `assumptions` and `clarifying_questions` are conditional fields
for ambiguous routing. There is one fixture source-of-truth addition: parseable
YAML route-card examples inside `SKILL.md`.

### Failure Modes & Handling

- **Ambiguous secret request:** if the user says only "secret concern", route to
  scan by default and include hook installation as a plausible follow-up only
  when the wording mentions install, enforce, hook, pre-commit setup, or local
  hook configuration.
- **Hook install sent to read-only scanner:** fixture coverage must fail until
  `$secret-scanner:install-precommit-hook` is present in the router catalog.
- **Harness wildcard regression:** forbidden-pattern coverage must fail if the
  router emits `$harness-engineering:*` or generic `harness-engineering` as a
  route-card owner or next prompt.
- **Router becomes an executor:** boundary checks continue to assert
  conversation-only behavior, no route artifacts, and no git/GitHub/hook/tool
  mutation. Removing `Bash` from allowed tools makes this boundary enforceable
  by frontmatter as well as prose.
- **Docs/catalog drift:** discovery checks keep Start Here docs aligned with
  the skill's boundary and route-card fields.
- **Fixture examples drift from route catalog:** scenario examples must live in
  the same `SKILL.md` as the catalog and must be checked against a fixture-side
  expectation table. If the catalog and examples disagree, the fixture should
  fail on the affected `scenario_id`. Fixture failures block closure through
  `scripts/release-gate.sh --mode all --strict`. Non-strict advisory output is
  not sufficient for this roadmap item.
- **Secret echo in route cards:** route cards and `next_prompt` must not copy
  secret-like user input. Required inputs should say "redacted secret material"
  or "affected file/path/ref" instead. Add a scanner-safe fake secret-shaped
  scenario that verifies redaction without embedding a contiguous secret-like
  token in the file or fixture.

### Rollout / Migration

No migration is required. Land the router skill, docs, and fixture updates as
the red/green units below. Existing public skills remain valid; the router only
points to them.

### Test Strategy Hooks

- `bash tests/agent-playbook-eval-fixtures.sh` must pass and include the new
  parseable route-card examples, route split, wildcard/generic-harness
  forbidden checks, tool-boundary check, and discovery-surface checks.
- `python3 scripts/skill-hygiene-check.py --mode all .` must pass to validate
  skill metadata/frontmatter.
- `python3 scripts/skill-topology-scan.py .` must pass to verify catalog
  discoverability and references.
- `scripts/release-gate.sh --mode all --strict` must pass before closure.

## Staged Implementation Plan

1. **Stage 1 - Red then green router contract unit:**
   - Red: add failing fixture IDs for route-card example parsing,
     fixture-side scenario expectations, `needs_clarification`, secret
     redaction, forbidden wildcard/generic harness handoffs, local fix review,
     and no `Bash` in workflow-router frontmatter.
   - Green: update `agent-playbook/skills/workflow-router/SKILL.md` with
     parseable examples, route fixes, clarification sentinel behavior, redaction
     guidance, and allowed-tools changes until those fixtures pass.
2. **Stage 2 - Red then green discovery verification:**
   - Red: add failing fixture IDs for each discovery surface and for
     `SKILLS.md` plus `scripts/release-gate.sh` membership in
     `AGENT_PLAYBOOK_FIXTURE_TARGETS`.
   - Green: update or confirm `README.md`, `SKILLS.md`,
     `agent-playbook/README.md`, `.claude-plugin/marketplace.json`,
     `agent-playbook/.claude-plugin/plugin.json`, and `scripts/release-gate.sh`
     until the discovery and trigger-scope fixtures pass.
3. **Stage 3 - Verify and hand off:** run agent-playbook fixtures, skill
   hygiene, topology scan, and strict release gate; then rerun
   `$idea-to-ship:review-code --slug ITS-ROADMAP-022`.

## Open Questions

None blocking. Implementation may tune exact route wording and regex granularity
as long as the critical mappings, route-card contract, and conversation-only
boundary remain testable.
