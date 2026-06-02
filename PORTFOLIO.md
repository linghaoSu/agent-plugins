# Plugin Portfolio

This file is the operational inventory for the plugin marketplace. It does not
replace `.claude-plugin/marketplace.json`; the marketplace remains the source
of installable plugin membership. This file owns lifecycle status, ownership,
release checks, and review/deprecation notes.

## Source Of Truth

- Marketplace membership: `.claude-plugin/marketplace.json`
- Plugin package metadata: `*/.claude-plugin/plugin.json`
- Operational status and release expectations: this file
- Portfolio roadmap: `.idea-to-ship/roadmap.md`

Default owner and decision owner are `linghao`, inherited from the root
marketplace owner. Add row-level overrides only when ownership is explicit.

## Lifecycle Statuses

| Status | Meaning |
|---|---|
| Active | Maintained and expected to receive feature or hardening work. |
| Experimental | Useful, but behavior or operating model is still being proven. |
| Maintenance | Stable utility; changes should be compatibility, safety, or docs driven. |
| Deprecated | Kept only for migration/removal; do not add new behavior. |

## Global Release Checks

Run these before publishing or pushing portfolio-level changes:

```bash
scripts/release-gate.sh --mode working
scripts/release-gate.sh --mode all
```

For staged commit review, run:

```bash
scripts/release-gate.sh --mode staged
```

Additional plugin-specific checks are listed in the inventory table.

## Inventory

| Plugin | Lifecycle | Owner | Decision Owner | Purpose | Required Checks | Review / Deprecation Notes |
|---|---|---|---|---|---|---|
| `agent-playbook` | Active | linghao | linghao | Operator-facing repo, tool, implementation-tournament, vibe-coding health, commit, and draft PR hygiene playbook. | Global release checks; `bash tests/agent-playbook-eval-fixtures.sh` for workflow contract changes. | Review when source-practice guidance changes or skills start duplicating `harness-engineering` / `idea-to-ship`. |
| `antifragile` | Active | linghao | linghao | Provides separate read-only audits for agent/plugin infrastructure (`antifragile-agent`) and target application resilience (`antifragile-system`). | Global release checks. | Keep audit criteria aligned with hook/state findings from `.idea-to-ship/ITS-ROADMAP-004/antifragile-audit.md`; do not blur agent-infrastructure findings with target-system findings. |
| `auto-updater` | Experimental | linghao | linghao | SessionStart hook that refreshes Claude and Codex directory-marketplace plugins when each runtime is present. | Global release checks; `bash -n auto-updater/scripts/check-update.sh`; `AUTO_UPDATER_DISABLE=1 auto-updater/scripts/check-update.sh`; `bash tests/auto-updater-fixtures.sh`. | Stateful hook with install-state side effects. Keep timeout and disable controls working; consider advisory-only behavior if it causes session friction. |
| `harness-engineering` | Active | linghao | linghao | Designs and audits the harness around autonomous agents. | Global release checks. | Maintain artifact-first behavior under `.harness-engineering/<slug>/`; avoid drifting into implementation work. |
| `idea-to-ship` | Active | linghao | linghao | End-to-end workflow from requirements and commercialization through UI design, architecture, roadmap, implementation, visual evidence, review, and tests. | Global release checks; `bash tests/idea-to-ship-eval-fixtures.sh` for skill contract changes. | Treat as release-critical because it drives portfolio planning. Preserve commercialization evidence, UI design contracts, visual-test evidence, story/test traceability, and runtime-aware review routing. |
| `issue-evaluator` | Active | linghao | linghao | Evaluates and fixes GitHub issues and reviews PR-related changes. | Global release checks; review runtime-aware wording when review/fix skills change. | Keep metadata aligned with runtime-aware behavior; avoid Codex-only wording unless describing a Claude Code-specific path. |
| `secret-scanner` | Active | linghao | linghao | Detects leaked credentials in staged, working, recent, ranged, or full-repo scopes. | Global release checks; `python3 secret-scanner/scripts/scan.py --mode all --format json`. | Release-critical. Enforcement is command-based through `scripts/release-gate.sh`; hook installation remains explicit local opt-in. |
| `skill-stats` | Experimental | linghao | linghao | Tracks skill invocations via PostToolUse, exposes a conversation-only usage report, and can run a report-only by default skill-cleaner report with a wrapper-owned evidence bundle. | Global release checks; `bash -n skill-stats/scripts/track-skill.sh`; `bash tests/skill-stats-cleaner-fixtures.sh`; temp-`HOME` smoke for JSONL append. | Stateful hook writes JSONL. The default user-facing skill is read-only; `--cleaner` report mode does no target mutation and writes only the temp evidence bundle. Mutating cleanup is apply-confirm only through `--apply`, exact plan approval, and scoped wrapper validation. Retention/rotation and malformed JSONL recovery are deferred from ITS-ROADMAP-004. |
| `worktree-cleaner` | Maintenance | linghao | linghao | Cleans merged or closed Git worktrees and reports no-PR worktrees. | Global release checks. | Keep destructive behavior gated by PR state, user decision, or dry-run output. Do not auto-remove open or ambiguous worktrees. |

## Update Rules

Update this file when:

- A plugin is added to or removed from `.claude-plugin/marketplace.json`.
- A plugin's lifecycle status changes.
- A plugin gains a hook, stateful script, network dependency, or destructive
  operation.
- Release checks change in `RELEASE-GATE.md`.
- A roadmap item changes ownership, deprecation, or release expectations.

If this file and marketplace membership disagree, treat the marketplace as the
membership source and update this file before release.
