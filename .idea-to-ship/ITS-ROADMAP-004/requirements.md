# Requirements - ITS-ROADMAP-004 Hook/State Hardening

**Date:** 2026-05-09
**Source:** `.idea-to-ship/roadmap.md` item `ITS-ROADMAP-004`
**Status:** accepted for audit and targeted hardening

## Problem

The repo contains hooks that run during normal agent sessions. Hook failures,
unbounded commands, or noisy state writes can degrade every session even when
the underlying plugin feature is optional.

## Goal

Run the `antifragile-agent` style audit against hook and stateful script
surfaces, then fix low-risk findings that improve failure isolation without
changing the plugin's user-facing behavior.

## Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| FR-1 | Audit all `hooks.json` files and referenced scripts. | `auto-updater/hooks/hooks.json`; `skill-stats/hooks/hooks.json` |
| FR-2 | Identify hook robustness risks: missing guards, unbounded external commands, input validation, and risky shell flags. | `antifragile/skills/antifragile-agent/SKILL.md` |
| FR-3 | Identify state pollution risks for files written under user state. | `skill-stats/scripts/track-skill.sh` |
| FR-4 | Apply low-risk fixes that keep hooks non-blocking. | roadmap `ITS-ROADMAP-004` release gate |
| FR-5 | Defer fixes that require a product decision or non-trivial concurrency/rotation design. | roadmap `ITS-ROADMAP-004` risk |

## Success Criteria

- Audit report records critical, warning, info, and passed findings.
- Accepted low-risk fixes are implemented and verified.
- Hook scripts pass shell syntax checks.
- Release gate passes in `working` and `all` modes.

## Non-Goals

- Do not install or remove hooks.
- Do not change where plugins are installed.
- Do not introduce a background daemon or persistent process.
- Do not add log rotation with weak locking semantics.
