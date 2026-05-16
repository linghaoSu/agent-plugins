# Requirements - ITS-ROADMAP-015

**Slug:** ITS-ROADMAP-015
**Date:** 2026-05-16
**Status:** draft
**Source:** `.idea-to-ship/roadmap.md`

## Problem

The repo has strong release-gate coverage for plugin manifests, skill
frontmatter, metadata, repetition, moderate skill bloat, and skill topology, but
it does not yet validate several authoring standards that make skills cheap to
review and safe to run. A maintainer can catch oversized files and broken
references, but cannot cheaply catch weak command examples, missing task
tracking guidance in workflow skills, missing related-skill links, or missing
workflow diagrams where the skill describes a multi-step flow.

This matters because new skills are expected to be actionable operating
instructions. If actionability and workflow metadata are reviewed only by hand,
skill quality drifts and the release gate misses problems that are visible from
local source alone.

## Users / Actors

- Skill author: gets local feedback before committing a new or changed skill.
- Plugin maintainer: reviews authoring-standard findings with deterministic
  check IDs and fixture evidence.
- Plugin releaser: runs the release gate in strict mode and sees authoring
  standard warnings promoted to failures before publishing.

## In Scope

- Extend local skill hygiene validation with conservative advisory checks for
  skill actionability and authoring structure.
- Validate workflow/router skills for task-tracking guidance and embedded
  Mermaid workflow diagrams.
- Validate command examples for risky chained shell forms and unexplained
  placeholders that reduce copy-paste actionability.
- Validate related-skill sections and broken related-skill references using the
  repo's plugin-qualified skill reference conventions.
- Keep the existing moderate skill-size budget and document the new standards
  in release-gate guidance.
- Add deterministic fixtures for the new checks and run the local release gate.

## Out of Scope / Non-Goals

- No Claude-specific colon-directory requirement; this repo uses
  `plugin/skills/<slug>/SKILL.md` paths and plugin-qualified references.
- No auto-approve settings updates, `.claude/settings.json` checks, or runtime
  permission mutation.
- No automatic README or generated diagram writes.
- No semantic proof that every diagram edge exactly matches prose; this item
  should catch missing/obviously weak workflow diagrams and document the manual
  text-match expectation.
- No change to public skill names or plugin routing.
- No creation of a new local `skill-creator` plugin unless the codebase already
  has one.

## Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| FR-1 | The hygiene checker must warn when a new or changed skill lacks an actionable usage section such as `When to Use`, `Workflow`, `Steps`, or `Usage`. | roadmap ITS-ROADMAP-015 / Kagenti authoring standard |
| FR-2 | The hygiene checker must warn when a workflow/router skill lacks task-tracking guidance. | Kagenti task tracking standard |
| FR-3 | The hygiene checker must warn when a workflow/router skill lacks an embedded Mermaid workflow diagram. | Kagenti workflow diagram standard |
| FR-4 | The hygiene checker must warn when a changed skill lacks a `Related Skills` section. | Kagenti related-skill standard |
| FR-5 | The hygiene checker must warn when a `Related Skills` section references an unknown local skill by plugin-qualified id or skill path. | ITS-ROADMAP-014 topology conventions |
| FR-6 | The hygiene checker must warn on command examples that are likely unsafe or hard to approve locally: chained shell commands, heredocs, or destructive commands without nearby approval/safety language. | Kagenti command safety, translated to this repo |
| FR-7 | The hygiene checker must warn when fenced commands contain unexplained placeholder tokens. | Kagenti copy-pasteable command standard |
| FR-8 | Release-gate documentation must describe the stronger authoring checks and clarify that they are advisory unless strict mode promotes them. | roadmap suggested action |
| FR-9 | Fixtures must cover positive findings and non-finding cases for the new authoring checks. | roadmap evidence required |
| FR-10 | Existing hygiene, topology, idea-to-ship, agent-playbook, and release-gate checks must continue to pass in strict all mode. | release gate |

## Non-Functional Requirements

- **Performance:** The full checker must remain fast enough for
  `scripts/release-gate.sh --mode all --strict`.
- **Scale:** Checks must work across the current plugin/skill count without
  network access or new third-party dependencies.
- **Reliability / failure mode:** Findings should be conservative, deterministic
  advisory messages. False positives should be suppressible only through the
  existing visible `## Hygiene Exception` pattern when appropriate.
- **Security / compliance:** The implementation must not execute commands found
  in skills and must not mutate plugin caches or runtime settings.
- **Platform / constraints:** Use existing Python and Bash fixture style. Keep
  checks local, offline, and source-based.

## Success Criteria

- Authoring-standard fixture scenarios pass -> verify:
  `bash tests/skill-hygiene-check-fixtures.sh`.
- Release-gate fixture wiring still passes -> verify:
  `bash tests/skill-hygiene-release-gate-fixtures.sh --self-check`.
- Full strict release gate passes -> verify:
  `scripts/release-gate.sh --mode all --strict`.
- The new checks are documented in `RELEASE-GATE.md` -> verify by inspecting the
  `skill-hygiene` advisory description and Skill Hygiene Fixtures section.
- No local `skill-creator` source was silently invented -> verify:
  `rg -n "skill-creator|skill creator" . --glob '*.md' --glob '*.py' --glob '*.sh'`.

## Open Questions

- The roadmap says "local `skill-creator` / release-gate guidance", but this
  source repo appears not to contain a local `skill-creator` plugin. The working
  assumption is to implement the item as repo-wide authoring guidance plus
  `skill-hygiene` validation unless codebase exploration finds an editable
  local skill-creator source.

## Touch Points

- `scripts/skill-hygiene-check.py`
- `tests/skill-hygiene-check-fixtures.py`
- `tests/skill-hygiene-release-gate-fixtures.sh`
- `RELEASE-GATE.md`
- `.idea-to-ship/ITS-ROADMAP-015/`
