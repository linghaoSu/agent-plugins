# Requirements — Skill Cleaner Wrapper For Skill Stats

**Slug:** ITS-ROADMAP-021
**Date:** 2026-06-01
**Status:** complete

## Problem

The repo already has `skill-stats`, which reports local skill usage from
`~/.claude/skill-stats.jsonl`, but it does not help maintainers understand the
larger skill surface: installed roots, duplicate skills, stale or unused skills,
prompt-budget pressure, or cleanup candidates across Codex/plugin/personal
skill locations.

The external `skill-cleaner` skill from `steipete/agent-scripts` covers those
signals, but its cleanup behavior is too risky to copy directly into this repo:
it can suggest deletion/config-disable work against local skill roots and
personal directories. This repo needs a bounded wrapper that keeps report-only
as the default, uses explicit user-provided external-script configuration, and
requires a `/plan` confirmation gate before any apply behavior.

Claude Code dynamic workflows are a design influence, not a required runtime
dependency for this feature. The requirements should absorb the useful workflow
ideas: repeatable plans, reviewable execution steps, background/agent
orchestration awareness, report-before-apply staging, and cost/permission
visibility. The implementation must not require Claude Code dynamic workflows
or `.claude/workflows/` artifacts in the first pass.

## Users / Actors

- Maintainer: runs `skill-stats` to understand skill usage, duplicates,
  stale skills, and prompt-budget pressure before deciding cleanup.
- Cleanup applier: explicitly approves a generated cleanup plan through
  `/plan` before any file edit, deletion, or config disable happens.
- Reviewer: verifies that the wrapper is report-only by default, bounded, and
  covered by fixtures for missing scripts, malformed logs, roots, truncation,
  confirmation refusal, and apply safety.
- Adjacent audit skills: `agent-playbook:context-audit` may consume or cite the
  report, but does not own the user-facing cleanup workflow.

## In Scope

- Extend the existing `skill-stats` workflow rather than adding a new public
  skill.
- Add a report-only skill-cleaner mode that wraps a user-configured external
  `skill-cleaner` checkout/script path.
- Scan normal Codex/plugin/repo skill roots and recent Codex/OpenClaw/Claude
  style logs by default, with deep/archive logs off by default.
- Support additional personal roots only when explicitly provided with a
  root argument or configuration.
- Report skill budget, root summary, duplicate candidates, stale/unused
  candidates, and description-compaction candidates in bounded output.
- Add an apply path that can delete, edit, or disable only after a concrete
  `/plan` confirmation names every target and action.
- Split high-risk cleanup into two stages: report-only first, then apply only
  after explicit user confirmation.
- Update `skill-stats/WORKFLOW-CONTRACTS.md`, README/portfolio docs, and
  fixture coverage to reflect the new report-only and apply-confirm modes.

## Out of Scope / Non-Goals

- No required Claude Code dynamic workflow runtime in the first pass.
- No `.claude/workflows/` project workflow artifact in the first pass.
- No vendoring of the external `skill-cleaner` script in this requirements
  stage.
- No automatic deletion, editing, disabling, committing, or pushing.
- No cleanup of ignored or untracked skill directories unless the plan names
  the destination or confirms they are disposable.
- No repo release-gate blocker based on personal usage logs or personal skill
  roots.
- No replacement for `scripts/skill-hygiene-check.py` or
  `agent-playbook:context-audit`.
- No silent deep scan of archives, Dropbox-style folders, or arbitrary home
  directories.

## Functional Requirements

| ID | Requirement |
|---|---|
| FR-1 | `skill-stats` must gain a skill-cleaner report mode that remains non-mutating by default and returns `outputs_written: []` unless a future architecture explicitly adds a local report artifact. |
| FR-2 | The wrapper must require a user-configured external `skill-cleaner` script or checkout path. If the path is missing, unreadable, or not executable by the documented command, the skill must return `needs_user` or `degraded` with an actionable setup message. |
| FR-3 | The report mode must summarize skill budget pressure, root summary, duplicate candidates, stale/unused candidates, and description-compaction candidates. |
| FR-4 | Default scanning must include normal Codex/plugin/repo skill roots and recent relevant logs. Deep/archive logs must be opt-in. |
| FR-5 | Additional personal roots must be opt-in through an explicit root argument or configuration; they must never be scanned silently. |
| FR-6 | Usage evidence must be labeled heuristic. The report must distinguish "unused candidate" from "safe to delete." |
| FR-7 | Duplicate recommendations must verify the kept copy exists and is loaded before recommending deletion or disablement of another copy. |
| FR-8 | Apply mode must first produce a concrete cleanup plan suitable for `/plan` review. The plan must list every file/config target, action type, rationale, kept copy or destination, and rollback note where applicable. |
| FR-9 | Apply mode must not execute unless the user explicitly approves the concrete `/plan` in the current session. Confirmation of the general feature is not enough. |
| FR-10 | Apply mode may delete files, edit descriptions, or disable config only for targets named in the approved plan. It must not commit or push; committing remains owned by `agent-playbook:commit-changes`. |
| FR-11 | Report and apply modes must use the shared output/token/error contract, with separate `mode` values for report-only and apply-confirm behavior. |
| FR-12 | The implementation must include fixtures for malformed usage logs, missing external script, duplicate skill names, symlinked roots, explicit personal roots, truncation, report-only dry run, confirmation refusal, and apply target scoping. |
| FR-13 | README, portfolio, and `skill-stats/WORKFLOW-CONTRACTS.md` must document that `skill-stats` is no longer purely read-only when the explicit apply-confirm path is invoked. |
| FR-14 | The requirements and architecture must cite Claude Code dynamic workflows as design inspiration only: repeatable orchestration, plan approval, background/cost awareness, and no mid-run user input constraints. |

## Non-Functional Requirements

- **Performance:** Report mode should handle the normal local skill/log set in
  one interactive run. If roots or logs exceed budget, it must truncate with a
  continuation command rather than stream unbounded output.
- **Scale:** Default output should cap top-level sections to actionable lists:
  top budget pressures, highest-confidence duplicates, stale/unused candidates,
  and description candidates. Exact numeric caps may be set in architecture.
- **Reliability / failure mode:** Missing external script, malformed logs,
  unreadable roots, and unsupported Node/runtime errors must degrade to a clear
  report with typed errors. They must not be treated as cleanup authority.
- **Security / privacy:** Personal roots and local logs can expose private
  paths. Output must be bounded and should avoid dumping raw log content unless
  explicitly needed for a finding.
- **Platform / constraints:** The first pass should work with this repo's
  existing shell/Python fixture style and external Node-based analyzer wrapper.
  It must not require Claude Code dynamic workflows, `ultracode`, or paid-plan
  workflow availability.
- **Cost / orchestration:** Multi-agent or workflow-style review ideas should
  be reserved for architecture/review stages or optional future workflow
  artifacts; routine report mode should stay lightweight.

## Success Criteria

- `skill-stats` report-only mode can run with a configured external analyzer
  path and produce a bounded cleanup report -> verify with fixture or smoke
  command using a temp skill root and temp log.
- Missing analyzer path produces an actionable `needs_user` or `degraded`
  result -> verify with fixture covering missing path.
- Heuristic unused candidates are not labeled safe-to-delete -> verify report
  fixture text distinguishes candidate status from deletion authority.
- Apply mode refuses to run without a current-session `/plan` approval -> verify
  confirmation-refusal fixture leaves files/config unchanged.
- Approved apply mode touches only named plan targets and does not commit ->
  verify fixture with extra unapproved files plus `git status`/filesystem
  assertions.
- Explicit personal roots are scanned only when configured or passed -> verify
  default fixture excludes personal root and explicit-root fixture includes it.
- Symlinked roots do not create false duplicate roots -> verify fixture with
  realpath-deduped root pair.
- Release checks remain green -> verify `scripts/release-gate.sh --mode all
  --strict`.

## Open Questions

- Exact external analyzer configuration shape is open for architecture:
  environment variable, config file, argument, or all three.
- Exact output caps are open for architecture, but truncation and continuation
  behavior are required.
- Whether to write a local report artifact in addition to conversation output
  is open for architecture; default remains `outputs_written: []`.
- Whether a future `.claude/workflows/` artifact should be added after the
  wrapper stabilizes remains a follow-up candidate, not part of first-pass
  requirements.
- Exact handling of Claude/OpenClaw log locations should be discovered in the
  external analyzer and translated into bounded local behavior during
  architecture.

## Touch Points

- `skill-stats/skills/skill-stats/SKILL.md`
- `skill-stats/WORKFLOW-CONTRACTS.md`
- `skill-stats/scripts/track-skill.sh`
- `README.md`
- `PORTFOLIO.md`
- `tests/agent-playbook-eval-fixtures.py` or a new focused skill-stats fixture
  file, depending on architecture
- `scripts/release-gate.sh` only if architecture chooses to add a focused
  deterministic fixture to the release gate
- External user-configured `steipete/agent-scripts` `skill-cleaner` checkout or
  script path

## Source Notes

- Claude Code dynamic workflows: use as design input for repeatable scripted
  orchestration, plan approval before run, background progress/cost visibility,
  no mid-run user input, and workflow disablement constraints. Do not require
  the runtime in first-pass implementation.
- External `skill-cleaner` SKILL: use as the source for report categories,
  analyzer command shape, root/log scanning expectations, heuristic usage
  evidence, and cleanup caution rules.
