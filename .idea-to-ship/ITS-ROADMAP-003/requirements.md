# Requirements - ITS-ROADMAP-003 Runtime-Aware Metadata

**Date:** 2026-05-09
**Source:** `.idea-to-ship/roadmap.md` item `ITS-ROADMAP-003`
**Status:** accepted for metadata patch

## Problem

`issue-evaluator` runtime behavior is already runtime-aware: Claude Code can
keep its model-specific role split, while non-Claude runtimes should use native
sub-agents by role. Some plugin metadata still describes the final review as
running "via Codex", which makes Codex sound mandatory outside Claude Code.

## Goal

Normalize marketplace and plugin manifest descriptions so installed plugin
discovery communicates runtime-aware adversarial review without overclaiming
model availability.

## Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| FR-1 | Replace stale "via Codex" review wording in `issue-evaluator` manifest metadata. | `issue-evaluator/.claude-plugin/plugin.json` |
| FR-2 | Replace the same stale wording in the root marketplace inventory. | `.claude-plugin/marketplace.json` |
| FR-3 | Keep the wording accurate: do not remove Claude/Codex-specific details where docs explicitly describe Claude Code behavior. | `issue-evaluator/README.md:9-12`; `issue-evaluator/skills/review-fix/SKILL.md:18-29` |
| FR-4 | Keep the change metadata-only; no skill behavior or agent routing implementation changes in this item. | `.idea-to-ship/roadmap.md` |

## Success Criteria

- Marketplace and plugin JSON remain valid.
- Targeted stale wording scan has no matches in marketplace/plugin metadata.
- Release gate passes in `working` and `all` modes.

## Non-Goals

- Do not change issue-evaluator execution logic.
- Do not rewrite historical idea-to-ship artifacts that mention the stale
  wording as evidence.
- Do not remove accurate descriptions of Claude Code's Codex reviewer role.
