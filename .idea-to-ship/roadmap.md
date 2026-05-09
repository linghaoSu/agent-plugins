---
goal: "让 agent-plugins 可持续演进"
horizon: "next 4 weeks (2026-05-09 to 2026-06-06)"
generated_at: "2026-05-09 13:49 CST"
repo_head: "1514e2b796fe20200854ff430219566ab2647c17"
dirty_worktree: "only .idea-to-ship/roadmap.md"
mode: "portfolio"
source_scope: "local+git"
write_target: ".idea-to-ship/roadmap.md"
final_lanes_written: "yes"
priority_approval: "user-approved Now/Next/Later ordering in current request"
---

# Roadmap - 让 agent-plugins 可持续演进

## Human-Owned Sections

### Strategic Objective

让 `agent-plugins` 在未来 4 周内从快速扩展进入可持续演进模式：插件目录、skill 工作流、hook、验证链路和发布节奏都要更容易审查、复用、回滚和继续迭代。

### Manual Overrides

- Approved Now: `ITS-ROADMAP-001`, `ITS-ROADMAP-003`, `ITS-ROADMAP-004`.
- Approved Next: `ITS-ROADMAP-006`, `ITS-ROADMAP-005`, `ITS-ROADMAP-007`.
- Approved Later: `ITS-ROADMAP-002`.

### Out of Scope / Non-Goals

- No GitHub issue, PR, or milestone scan in this run because `--include-github` was not provided.
- No TODO/FIXME mining in this run because `--include-todos` was not provided.
- GitHub and TODO/FIXME inputs remain out of scope for this version of the roadmap.

<!-- idea-to-ship:roadmap generated:start -->

## What Changed Since Last Roadmap

- Added final Now/Next/Later lanes from user-approved priority order.
- Promoted `ITS-ROADMAP-001`, `ITS-ROADMAP-003`, and `ITS-ROADMAP-004` to `Now`.
- Promoted `ITS-ROADMAP-006`, `ITS-ROADMAP-005`, and `ITS-ROADMAP-007` to `Next`.
- Moved `ITS-ROADMAP-002` to `Later` because idea-to-ship dogfooding is already happening through this roadmap and does not need to block release hardening.
- Completed `ITS-ROADMAP-001` Stage 1 release gate in commit `17460a5`.
- Completed `ITS-ROADMAP-003` runtime-aware marketplace/plugin metadata patch.
- Completed `ITS-ROADMAP-004` hook/state audit with low-risk hardening.
- Completed `ITS-ROADMAP-006` Stage 1 idea-to-ship contract fixtures.
- Completed `ITS-ROADMAP-005` portfolio inventory and ownership model.

## Inputs

- Goal: "让 agent-plugins 可持续演进" from user request.
- Horizon: `next 4 weeks`, interpreted as 2026-05-09 through 2026-06-06.
- Priority approval: user-provided Now/Next/Later list in current request.
- Repo HEAD: `1514e2b796fe20200854ff430219566ab2647c17`.
- Source scope: local repo docs/manifests/artifacts plus `--include-git`.
- Idea-to-ship artifact: `.idea-to-ship/current/code-review.md`.
- Repo docs/manifests: `.claude-plugin/marketplace.json`, plugin `plugin.json` files, README files for `idea-to-ship`, `agent-playbook`, `harness-engineering`, `issue-evaluator`, and `secret-scanner`.
- Git history considered:
  - `1514e2b` 2026-05-09 `feat(idea-to-ship): add roadmap and verification workflow`
  - `de16602` 2026-05-09 `feat: add antifragile and skill stats plugins`
  - `31c7189` 2026-05-09 `fix(issue-evaluator): route validation by runtime`
  - `b35abe3` 2026-04-29 `feat: add shared reference files, anti-patterns, and phase gates to skills`
  - `4100d91` 2026-04-23 `Init commit`

Excluded:

- GitHub milestones, issues, and PRs because `--include-github` was not provided.
- TODO/FIXME scan because `--include-todos` was not provided.

## Now

### ITS-ROADMAP-001 - Establish repo-wide plugin release gates
**Status:** Done
**Work Type:** Maintenance
**Evidence Class:** Artifact
**Confidence:** High
**Source Anchors:** `.claude-plugin/marketplace.json:6-50`; `harness-engineering/README.md:50-57`; `secret-scanner/scripts/scan.py:1-24`; `1514e2b`
**Why Now / Why Next / Why Later:** This is the highest-leverage sustainability step. The repo now has multiple plugins, hooks, and skills, but release checks are still manual and easy to skip.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: current manifest/skill validation commands are known. Exit: one documented or scripted release gate covers JSON manifests, skill frontmatter, `git diff --check`, hook robustness, and secret scanning. No-go: gate requires network or mutates repo state without explicit approval.
**Evidence Required:** Completed: `scripts/release-gate.sh`; `RELEASE-GATE.md`; `tests/release-gate-stage1.sh`; `.idea-to-ship/ITS-ROADMAP-001/code-review.md`; commit `17460a5`.
**Dependencies:** None
**Risk:** medium - a too-heavy gate can slow small edits; a too-light gate preserves current manual drift.

### ITS-ROADMAP-003 - Normalize runtime-aware review language across manifests
**Status:** Done
**Work Type:** Maintenance
**Evidence Class:** Artifact
**Confidence:** High
**Source Anchors:** `issue-evaluator/README.md:9-12`; `issue-evaluator/skills/review-fix/SKILL.md:18-29`; `issue-evaluator/.claude-plugin/plugin.json:1-7`; `.claude-plugin/marketplace.json:8-10`
**Why Now / Why Next / Why Later:** Metadata still advertises Codex-only review in places while the skill behavior is runtime-aware. That mismatch affects installed plugin discovery and user expectations.
**Owner:** Unassigned
**Decision Owner:** None
**Release Gate:** Entry: identify all stale Codex-only descriptions. Exit: marketplace and plugin metadata consistently describe runtime-aware validation without overclaiming model availability. No-go: docs imply unavailable model names are mandatory outside Claude Code.
**Evidence Required:** Completed: targeted stale wording scan; JSON manifest validation; release gate `working`/`all`; `.idea-to-ship/ITS-ROADMAP-003/implementation-log.md`.
**Dependencies:** None
**Risk:** low - mostly metadata, but misleading docs can cause wrong execution mode.

### ITS-ROADMAP-004 - Audit and harden hooks/stateful scripts
**Status:** Done
**Work Type:** Spike
**Evidence Class:** Repo
**Confidence:** Medium
**Source Anchors:** `auto-updater/hooks/hooks.json:1-13`; `auto-updater/scripts/check-update.sh:19-47`; `skill-stats/hooks/hooks.json:1-17`; `skill-stats/scripts/track-skill.sh:7-23`; `antifragile/skills/antifragile-agent/SKILL.md:16-47`
**Why Now / Why Next / Why Later:** Hooks run during normal agent sessions and can silently degrade or pollute state. Before adding more release automation, hook robustness should be audited.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: run antifragile-agent audit focused on hooks and state. Exit: accepted findings are either fixed or explicitly deferred with rationale. No-go: hook changes that can block SessionStart/PostToolUse on optional dependency failure.
**Evidence Required:** Completed: `.idea-to-ship/ITS-ROADMAP-004/antifragile-audit.md`; timeout/disable hardening in `auto-updater/scripts/check-update.sh`; non-blocking state write hardening in `skill-stats/scripts/track-skill.sh`; portable analysis docs in `skill-stats/skills/skill-stats/SKILL.md`.
**Dependencies:** ITS-ROADMAP-001 can define the standard checks, but this spike can run independently.
**Risk:** medium - hook changes can affect every session if failure isolation is wrong.

## Next

### ITS-ROADMAP-006 - Add executable eval fixtures for critical skill workflows
**Status:** Done
**Work Type:** Spike
**Evidence Class:** Artifact
**Confidence:** Medium
**Source Anchors:** `idea-to-ship/skills/roadmap/SKILL.md:395-413`; `idea-to-ship/README.md:72-77`; `.idea-to-ship/current/code-review.md:29-36`
**Why Now / Why Next / Why Later:** After release gates and metadata consistency, the next bottleneck is proving skill behavior with repeatable fixtures instead of manual markdown review.
**Owner:** Unassigned
**Decision Owner:** None
**Release Gate:** Entry: choose fixture harness shape. Exit: smoke fixtures cover `/roadmap`, `/test`, and `/review-code` critical paths: first run, rerun preservation, missing test plan, and final-without-approval. No-go: fixtures require live GitHub or mutate user repo state.
**Evidence Required:** Completed: `.idea-to-ship/ITS-ROADMAP-006/architecture.md`; `tests/idea-to-ship-eval-fixtures.sh`; `tests/idea-to-ship-eval-fixtures.py`; `RELEASE-GATE.md`; `bash tests/idea-to-ship-eval-fixtures.sh`; negative contract smoke recorded in `.idea-to-ship/ITS-ROADMAP-006/implementation-log.md`.
**Dependencies:** ITS-ROADMAP-001 should define where eval fixtures sit in release checks.
**Risk:** medium - poorly scoped evals become brittle markdown golden files.

### ITS-ROADMAP-005 - Define portfolio inventory and ownership model
**Status:** Done
**Work Type:** Docs
**Evidence Class:** Repo
**Confidence:** Medium
**Source Anchors:** `.claude-plugin/marketplace.json:6-50`; `agent-playbook/README.md:53-61`; `idea-to-ship/README.md:122-124`; `de16602`
**Why Now / Why Next / Why Later:** The repo is now a plugin portfolio. A lightweight inventory makes ownership, lifecycle, and verification expectations explicit after the immediate release gates exist.
**Owner:** Unassigned
**Decision Owner:** None
**Release Gate:** Entry: plugin list from marketplace is current. Exit: each plugin has purpose, maintenance status, owner/decision owner, release checks, and deprecation/review notes. No-go: inventory duplicates README content without operational decisions.
**Evidence Required:** Completed: `PORTFOLIO.md`; `.idea-to-ship/ITS-ROADMAP-005/implementation-log.md`; inventory coverage check against `.claude-plugin/marketplace.json`; release gate `working`/`all`.
**Dependencies:** ITS-ROADMAP-001 can provide release-check categories for the inventory.
**Risk:** low - docs can drift if not tied to release gate.

### ITS-ROADMAP-007 - Promote secret scanning from available tool to release gate
**Status:** Planned
**Work Type:** Maintenance
**Evidence Class:** Repo
**Confidence:** Medium
**Source Anchors:** `secret-scanner/README.md:92-100`; `secret-scanner/scripts/scan.py:1-24`; `.gitignore:1`
**Why Now / Why Next / Why Later:** Secret scanning exists, but the repo does not yet require it as part of plugin release. It should become a release gate after the general gate shape is agreed.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: ITS-ROADMAP-001 release gate draft exists. Exit: secret scanning is included as a documented mandatory local check or installed hook. No-go: hook installation overwrites existing hooks without confirmation.
**Evidence Required:** `secret-scanner/scripts/scan.py --mode staged` or equivalent documented command; hook decision recorded.
**Dependencies:** ITS-ROADMAP-001
**Risk:** low - main risk is false positives or adding friction to small markdown-only changes.

## Later

### ITS-ROADMAP-002 - Dogfood idea-to-ship as the planning backbone
**Status:** Deferred
**Work Type:** Feature
**Evidence Class:** Artifact
**Confidence:** High
**Source Anchors:** `idea-to-ship/README.md:40-49`; `.idea-to-ship/current/code-review.md:42-44`; `1514e2b`; `.idea-to-ship/roadmap.md`
**Why Now / Why Next / Why Later:** The repo is already dogfooding idea-to-ship through this roadmap. Keep it as a later process improvement after release gates, metadata consistency, hook hardening, and eval fixtures are in place.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: at least one Now item completed. Exit: future portfolio work consistently uses requirements/architecture/roadmap/review/test artifacts where useful. No-go: process overhead exceeds the value of the change.
**Evidence Required:** At least one subsequent feature uses the full idea-to-ship flow and records artifacts.
**Dependencies:** ITS-ROADMAP-001; ITS-ROADMAP-006
**Risk:** low - main risk is process bloat.

## Milestones

### Milestone 1 - Release Discipline Baseline
**Target:** Week 1 of horizon
**Scope:** `ITS-ROADMAP-001`, `ITS-ROADMAP-003`
**Owner:** Unassigned
**Dependencies:** None
**Release Gate:** Entry: current repo on `main` at `1514e2b`. Exit: release checks are documented/scripted and runtime-aware metadata is consistent. Evidence required: manifest validation, frontmatter validation, diff whitespace check, stale wording scan.
**Risk Level:** medium

### Milestone 2 - Hook Robustness And Evaluation Shape
**Target:** Weeks 2-3 of horizon
**Scope:** `ITS-ROADMAP-004`, `ITS-ROADMAP-006`
**Owner:** Unassigned
**Dependencies:** `ITS-ROADMAP-001`
**Release Gate:** Entry: release gate baseline exists. Exit: hook audit findings are triaged and first eval fixtures are runnable or explicitly scoped. Evidence required: antifragile audit output, fixture command output, reviewed diff.
**Risk Level:** medium

### Milestone 3 - Portfolio Operating Model
**Target:** Week 4 of horizon
**Scope:** `ITS-ROADMAP-005`, `ITS-ROADMAP-007`, revisit `ITS-ROADMAP-002`
**Owner:** Unassigned
**Dependencies:** `ITS-ROADMAP-001`, `ITS-ROADMAP-006`
**Release Gate:** Entry: release/eval baseline exists. Exit: plugin inventory has owners/status/checks and secret scanning is part of the release gate or explicitly deferred. Evidence required: inventory artifact, secret-scan command/hook decision, updated roadmap.
**Risk Level:** low

## Dependency Order

1. `ITS-ROADMAP-001` should land first because it defines the checks used by later changes.
2. `ITS-ROADMAP-003` can run in parallel with `ITS-ROADMAP-001`; it has no hard dependency.
3. `ITS-ROADMAP-004` can start after or during `ITS-ROADMAP-001`, but accepted hook fixes should obey the release gate once it exists.
4. `ITS-ROADMAP-006` depended on `ITS-ROADMAP-001` for where eval fixtures fit into release checks; Stage 1 now lands as a manually runnable command before release-gate integration.
5. `ITS-ROADMAP-005` and `ITS-ROADMAP-007` follow the release gate baseline so they do not create separate, drifting process rules.
6. `ITS-ROADMAP-002` remains later until there is a proven baseline worth codifying.

## Dependency Hypotheses

- Eval fixtures required a small local harness script. Stage 1 validated the contract-fixture shape; artifact-level fixtures remain a possible later extension.
- Secret scanning may be better as a documented release command before becoming a hook. The hook path depends on user tolerance for local workflow friction.
- Hook hardening may uncover issues that should move ahead of metadata consistency if any hook can block sessions or corrupt state.

## Critical Path

`ITS-ROADMAP-001` -> `ITS-ROADMAP-006` (done) -> `ITS-ROADMAP-005` / `ITS-ROADMAP-007`

`ITS-ROADMAP-003` and `ITS-ROADMAP-004` are important parallel work but are not on the validated hard-dependency chain unless the hook audit finds a blocking issue.

## Risks / Spikes

- Hook changes have high blast radius because SessionStart/PostToolUse failures affect normal agent operation.
- Markdown skill evals can become brittle if they assert exact prose instead of behavioral invariants.
- The roadmap currently excludes GitHub issues/PRs/milestones, so active external planning may be missing.
- Capacity is unknown; the Now lane assumes one maintainer can complete three small-to-medium work items inside the horizon.

## Status By Feature

| Slug/ID | Status | Next Action | Blockers | Evidence |
|---|---|---|---|---|
| ITS-ROADMAP-001 | Done | None - release gate Stage 1 committed and pushed | None | `scripts/release-gate.sh`; `RELEASE-GATE.md`; `tests/release-gate-stage1.sh`; `.idea-to-ship/ITS-ROADMAP-001/code-review.md`; `17460a5` |
| ITS-ROADMAP-003 | Done | None - stale manifest wording patched | None | `.claude-plugin/marketplace.json:8-10`; `issue-evaluator/.claude-plugin/plugin.json:1-7`; `.idea-to-ship/ITS-ROADMAP-003/implementation-log.md` |
| ITS-ROADMAP-004 | Done | None - audit complete and low-risk fixes applied | None | `.idea-to-ship/ITS-ROADMAP-004/antifragile-audit.md`; `auto-updater/scripts/check-update.sh`; `skill-stats/scripts/track-skill.sh` |
| ITS-ROADMAP-006 | Done | None - contract fixture command implemented | None | `tests/idea-to-ship-eval-fixtures.sh`; `tests/idea-to-ship-eval-fixtures.py`; `.idea-to-ship/ITS-ROADMAP-006/implementation-log.md` |
| ITS-ROADMAP-005 | Done | None - portfolio inventory added | None | `PORTFOLIO.md`; `.idea-to-ship/ITS-ROADMAP-005/implementation-log.md` |
| ITS-ROADMAP-007 | Planned | Decide command vs hook for scan gate | Release gate baseline | `secret-scanner/README.md:92-100` |
| ITS-ROADMAP-002 | Deferred | Revisit after baseline work | Process overhead risk | `idea-to-ship/README.md:40-49`; `.idea-to-ship/roadmap.md` |

## Candidate Backlog

- No additional candidates from this run. GitHub and TODO sources were intentionally excluded.

## Open Decisions

| Decision | Options | Recommended Option | Decision Owner | Needed By | Impact If Delayed |
|---|---|---|---|---|---|
| Should the next roadmap refresh include GitHub signals? | A: local only; B: include GitHub read-only; C: include GitHub plus TODO scan | B | User | Before release planning beyond this local repo snapshot | Roadmap may miss active PRs/issues/milestones that should override repo-internal guesses. |
| How strict should release gates be after baseline? | A: advisory checklist; B: required local command set; C: pre-commit/pre-push hooks | B first, revisit C after one release | User | Before implementing `ITS-ROADMAP-007` | Too loose gives weak verification; too strict may slow small skill edits. |

## Acceptance Checks

- First run: passed. `.idea-to-ship/roadmap.md` existed as a generated Candidate Brief and contained generated markers before finalization.
- Rerun with human content: passed. Human-owned sections were preserved and `Manual Overrides` was updated from the user's explicit approval.
- `--final` without priority approval: not applicable; priority approval was provided in the current request.
- `--include-github`: not applicable; GitHub was not used.
- Conflicting evidence: passed. Metadata conflict is recorded through `ITS-ROADMAP-003`, and no unapproved GitHub/TODO signals were used.
- Weak signals: passed. `Now` contains only High/Medium confidence items approved by the user.

<!-- idea-to-ship:roadmap generated:end -->
