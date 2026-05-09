# Architecture - Portfolio Inventory

**Slug:** ITS-ROADMAP-005
**Date:** 2026-05-09
**Status:** draft
**References:** requirements.md

## Summary

Add a root-level `PORTFOLIO.md` that owns operational portfolio metadata not
captured by plugin manifests: lifecycle, owner, decision owner, release checks,
and review/deprecation notes. The marketplace remains the source of installable
plugin membership; the inventory is the source for maintenance decisions.

## Goals / Non-Goals

Goals:

- Make the plugin portfolio scannable in one place.
- Keep ownership and release expectations explicit.
- Capture hook/stateful risk without bloating README files.
- Avoid changing plugin manifest schema for an operational doc need.

Non-goals:

- Machine-enforced owner schema.
- CI or GitHub automation.
- Per-plugin ownership delegation beyond the known marketplace owner.

## Codebase Context

- `.claude-plugin/marketplace.json` lists nine plugins and has root owner
  `linghao`.
- Every plugin has `*/.claude-plugin/plugin.json`.
- `RELEASE-GATE.md` defines the global local release gate.
- `tests/idea-to-ship-eval-fixtures.sh` adds a plugin-specific check for
  `idea-to-ship` skill contract changes.
- `auto-updater` and `skill-stats` include hooks and stateful scripts, so their
  operational notes need to be more explicit than README summaries.

## Alternatives Considered

### Option A - Root Markdown Inventory

Add `PORTFOLIO.md` with controlled statuses, global checks, and one row per
plugin.

**Module changes:** add `PORTFOLIO.md`; update roadmap artifacts.

**Data flow:** maintainers update marketplace membership in
`.claude-plugin/marketplace.json` and operational metadata in `PORTFOLIO.md`.

**Interfaces:** humans read/edit Markdown; release gate validates markdown only
through existing whitespace/secret checks.

**Pros:** lowest blast radius, easy to review, no schema migration.

**Cons:** not machine-enforced; can drift if maintainers forget to update it.

**Risk:** low - mostly documentation drift.

### Option B - Extend Plugin Manifests

Add owner/status/check fields to every `plugin.json`.

**Module changes:** all plugin manifests; maybe release-gate schema checks.

**Data flow:** marketplace/plugin metadata carries operational fields directly.

**Interfaces:** JSON manifests become the inventory source.

**Pros:** closer to machine-readable enforcement.

**Cons:** invents manifest fields whose consumer is unclear and increases
schema churn across every plugin.

**Risk:** medium - external plugin tooling may ignore or reject unknown fields.

### Option C - Per-Plugin OWNER Files

Add a small owner/status file inside each plugin directory.

**Module changes:** one new file per plugin.

**Data flow:** each plugin owns its local operational metadata.

**Interfaces:** humans must scan many files or tooling must aggregate them.

**Pros:** local to each plugin.

**Cons:** poor portfolio scanability and more files to keep consistent.

**Risk:** medium - fragmentation recreates the original problem.

## Recommendation

**We pick Option A.** A root Markdown inventory is enough for the current
maintenance problem and preserves the plugin manifest contract. The accepted
tradeoff is manual drift risk, mitigated by explicit update rules and release
gate references.

## Chosen Design - Detail

### Module Breakdown

- `PORTFOLIO.md` - root operational inventory and ownership model.
- `.idea-to-ship/ITS-ROADMAP-005/implementation-log.md` - records decisions and
  verification.
- `.idea-to-ship/roadmap.md` - marks the roadmap item complete after review.

### Inventory Shape

Sections:

1. Source of truth and update rules.
2. Controlled lifecycle statuses.
3. Global release checks.
4. Plugin inventory table.
5. Review/deprecation policy.

Table columns:

- Plugin
- Lifecycle
- Owner
- Decision owner
- Purpose
- Required checks
- Review / deprecation notes

### Data / Schema Changes

None. No JSON manifest changes.

### Failure Modes & Handling

- Marketplace plugin missing from inventory: release review should reject the
  diff; future release-gate stage may automate this.
- Inventory duplicates README prose: keep purpose to one sentence and put
  operational decisions in checks/notes.
- False owner assignment: default to marketplace owner `linghao`; only add row
  overrides when explicit.

### Rollout / Migration

Stage 1 lands the Markdown inventory and roadmap update. Future work can decide
whether inventory completeness becomes a release-gate check.

### Test Strategy Hooks

- Manual count: every marketplace plugin appears exactly once.
- `scripts/release-gate.sh --mode working` and `--mode all` verify JSON,
  frontmatter, whitespace, and secret safety.

## Staged Implementation Plan

1. **Stage 1 - Root inventory:** Add `PORTFOLIO.md`, implementation log, code
   review, and roadmap status update.
2. **Stage 2 - Optional enforcement:** If drift appears, add a release-gate
   check comparing marketplace plugin names to `PORTFOLIO.md`.

## Open Questions

- None blocking. Per-plugin owner overrides should wait for explicit user
  decisions.
