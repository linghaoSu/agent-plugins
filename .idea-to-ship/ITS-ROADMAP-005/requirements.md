# Requirements - ITS-ROADMAP-005

**Date:** 2026-05-09
**Status:** draft
**Source:** `.idea-to-ship/roadmap.md`

## Problem

The repository is now a portfolio of plugins, not a single plugin. The
marketplace lists the installable plugins, but it does not capture operational
decisions: lifecycle status, owner, decision owner, release checks, hook risk,
or deprecation notes. Without a lightweight inventory, future release and
maintenance work will drift across README files and manifests.

## Scope

In scope:

- Add a root-level portfolio inventory artifact.
- Use `.claude-plugin/marketplace.json` and plugin manifests as the plugin list
  source.
- Record lifecycle status, owner, decision owner, purpose, release checks, and
  review/deprecation notes for every marketplace plugin.
- Define maintenance rules for when the inventory must be updated.

Out of scope:

- Changing the plugin manifest schema.
- Creating GitHub CODEOWNERS or issue templates.
- Assigning different human owners without user approval.
- Duplicating each README in full.

## Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| FR-1 | The inventory must include every plugin listed in `.claude-plugin/marketplace.json`. | `.claude-plugin/marketplace.json` |
| FR-2 | Each plugin row must include purpose, lifecycle status, owner, decision owner, release checks, and review/deprecation notes. | `.idea-to-ship/roadmap.md` ITS-ROADMAP-005 |
| FR-3 | The inventory must define controlled lifecycle statuses so future updates are consistent. | `.idea-to-ship/roadmap.md` ITS-ROADMAP-005 |
| FR-4 | The inventory must distinguish global release checks from plugin-specific checks. | `RELEASE-GATE.md`; ITS-ROADMAP-001 |
| FR-5 | The inventory must avoid pretending unknown ownership is known; use the marketplace owner as the default and note row-level overrides only when explicit. | `.claude-plugin/marketplace.json` owner |
| FR-6 | The inventory must say when it needs updating. | `.idea-to-ship/roadmap.md` ITS-ROADMAP-005 |

## Success Criteria

- `PORTFOLIO.md` exists at the repo root.
- All nine marketplace plugins appear exactly once in the inventory table.
- Hook/stateful plugins have explicit operational notes.
- `scripts/release-gate.sh --mode working` and `--mode all` pass.

## Constraints

- Keep the inventory concise enough to be maintained manually.
- Do not add a new data parser or schema for Stage 1.
- Do not make ownership claims beyond the root marketplace owner unless a
  source exists.
