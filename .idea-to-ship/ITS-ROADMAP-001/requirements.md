# Requirements - ITS-ROADMAP-001 Release Gates

**Date:** 2026-05-09
**Source:** `.idea-to-ship/roadmap.md` item `ITS-ROADMAP-001`
**Status:** accepted for architecture

## Problem

The repository now contains multiple Claude/Codex-oriented plugins, skills,
hooks, and scripts. Release checks are currently run manually and are easy to
skip or apply inconsistently. This creates drift risk across plugin manifests,
skill frontmatter, hook behavior, secret scanning, and runtime-aware review
language.

## Goal

Define a repeatable repo-wide release gate for plugin marketplace changes.
The gate must be simple enough to run before every commit/push, but explicit
enough that future plugin changes do not rely on memory or ad hoc commands.

## Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| FR-1 | Validate all marketplace and plugin JSON manifests. | `.claude-plugin/marketplace.json:6-50` |
| FR-2 | Validate all skill frontmatter structurally before release. | `idea-to-ship/skills/*/SKILL.md`; prior manual validation |
| FR-3 | Run whitespace/diff hygiene with `git diff --check`. | prior manual validation |
| FR-4 | Include a secret-scan gate using the existing deterministic scanner. | `secret-scanner/scripts/scan.py:1-24`, `secret-scanner/scripts/scan.py:332-368` |
| FR-5 | Include hook robustness checks or a clear hook-audit handoff for SessionStart/PostToolUse hooks. | `auto-updater/hooks/hooks.json:1-13`; `skill-stats/hooks/hooks.json:1-17`; `antifragile/skills/antifragile-agent/SKILL.md:16-47` |
| FR-6 | Detect stale runtime-aware review wording that implies Codex-only behavior where the implementation is runtime-aware. | `issue-evaluator/README.md:9-12`; `issue-evaluator/.claude-plugin/plugin.json:1-7`; `.claude-plugin/marketplace.json:8-10` |
| FR-7 | Separate blocking checks from advisory checks so the gate can be adopted incrementally. | `.idea-to-ship/roadmap.md:73-79` |
| FR-8 | Avoid network access and avoid mutating repo or user machine state by default. | `.idea-to-ship/roadmap.md:76` |

## Non-Goals

- Do not implement the release gate in this step.
- Do not install pre-commit hooks in this step.
- Do not add CI configuration in this step.
- Do not require GitHub API access in the first gate.
- Do not force every advisory roadmap item into the initial blocking gate.

## Success Criteria

- Architecture compares 2-3 realistic approaches and recommends one.
- Recommendation states a concrete command/interface for a future implementer.
- The design names which checks are blocking in the first release gate and
  which are advisory.
- The design explains rollout, failure handling, and test strategy.
- No production code or release script is written during this design step.

## Constraints

- Repo is mostly markdown, JSON, shell, and Python; no package manager or CI
  framework is currently present.
- Existing reusable checks are command-line oriented.
- Existing hooks must not be made more fragile.
- Secret scanner is already self-contained and supports `--mode staged`,
  `--mode working`, `--mode all`, and `--format json`.

## Open Questions

- Should the eventual gate be mandatory before every push, or only before
  commits that touch plugin/skill/hook files?
- Should secret scanning become blocking immediately, or start as advisory for
  markdown-only changes?
- Should hook robustness be checked by static heuristics in the release gate or
  by running the `antifragile-agent` skill and attaching its report?
