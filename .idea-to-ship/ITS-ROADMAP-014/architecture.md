# Architecture - Skill Topology Scan

**Slug:** ITS-ROADMAP-014
**Date:** 2026-05-16
**Status:** draft
**References:** requirements.md

## Summary

Add a standalone read-only topology scanner, `scripts/skill-topology-scan.py`,
that discovers local plugin skills, extracts deterministic skill references,
and emits a Markdown report with inventory, skill tree, broken references,
orphan skills, hub skills, and README catalog coverage. The chosen design keeps
the existing hygiene checker focused on advisory warnings while giving the
release gate a dedicated fixture check for topology report stability.

## Goals / Non-Goals

Goals:

- Produce a deterministic local skill graph report.
- Detect broken references and isolated skills without mutating files.
- Provide a generated Markdown skill-tree fragment grouped by plugin.
- Add fixture coverage and release-gate visibility.

Non-goals:

- No automatic README writes.
- No network scans or Kagenti repository dependency.
- No deletion or quality score authority from graph metrics.
- No changes to existing skill-hygiene warning IDs or semantics.

## Codebase Context

- `scripts/skill-hygiene-check.py` already owns advisory single-file checks and
  has fixture-heavy deterministic tests in `tests/skill-hygiene-check-fixtures.py`.
- `scripts/release-gate.sh` already runs advisory fixture commands based on
  touched scopes and supports strict-mode promotion of advisory warnings.
- Root `README.md` has a skill catalog with Markdown links such as
  `agent-playbook/skills/commit-changes/SKILL.md`; those links are the local
  README coverage source of truth.
- There is no existing graph/topology command, so a new read-only script avoids
  overloading the hygiene checker with report-only behavior.
- Codebase exploration was same-context because no current request authorized
  explorer sub-agents.

## Cross-Skill Routing

| Signal | Routed skill | Result | Design impact |
|---|---|---|---|
| Local report command, release-gate advisory, no external side effects | none | no architecture-stage routed skill needed | Keep implementation local, offline, and read-only. |

## Alternatives Considered

### Option A - Standalone Topology Scanner

Add `scripts/skill-topology-scan.py` plus dedicated fixtures and release-gate
advisory wiring.

**Module changes:** new scanner script, new fixture files, release-gate docs and
advisory check.

**Data flow:** discover skill files -> parse metadata -> extract references ->
build inbound/outbound graph -> compare README catalog links -> render
Markdown report.

**Interfaces:** `python3 scripts/skill-topology-scan.py <root>`.

**Pros:** Keeps report-only topology separate from existing warning-oriented
hygiene checks; easy to test; low blast radius.

**Cons:** Adds one more script and fixture command to maintain.

**Risk:** Low; read-only command with deterministic output.

### Option B - Extend `skill-hygiene-check.py`

Add topology scan flags to the existing hygiene checker.

**Module changes:** `scripts/skill-hygiene-check.py`, existing fixture suite,
release-gate docs.

**Data flow:** reuse existing skill discovery and add graph/report modes.

**Pros:** Reuses helper functions and keeps skill analysis in one script.

**Cons:** The hygiene checker already mixes advisory findings, repetition
candidate dumps, and dry-run baselines; adding Markdown reports increases
surface area and makes fixture failures harder to triage.

**Risk:** Medium; more chance of breaking unrelated hygiene checks.

### Option C - Generate README Sections Directly

Write a command that updates root README generated sections in place.

**Module changes:** new writer command and docs.

**Pros:** Keeps documentation current automatically.

**Cons:** Violates the roadmap's churn concern and creates mutation semantics
where a read-only report is sufficient for this item.

**Risk:** Medium-high; generated README churn can obscure code review.

## Recommendation

**We pick Option A.** A standalone scanner is the smallest change that satisfies
the roadmap's graph/reporting requirement without coupling topology output to
existing hygiene warning semantics. The accepted tradeoff is one additional
script and fixture command.

## Chosen Design - Detail

### Module Breakdown

- `scripts/skill-topology-scan.py` - read-only scanner and Markdown renderer.
- `tests/skill-topology-scan-fixtures.py` - deterministic fixture scenarios for
  broken refs, orphan skills, hub scoring, tree output, and README coverage.
- `tests/skill-topology-scan-fixtures.sh` - Bash wrapper matching existing test
  command style.
- `scripts/release-gate.sh` - advisory `skill-topology-fixtures` command,
  scoped to topology implementation/docs/tests and all-mode.
- `RELEASE-GATE.md` - documents the topology fixture command and scope.

### Data Flow

```
repo root
  -> discover */skills/*/SKILL.md
  -> parse plugin id + skill slug + frontmatter name/description
  -> extract references from body:
       $plugin:skill
       plugin:skill
       plugin/skills/skill/SKILL.md
  -> resolve references against discovered skill ids and paths
  -> calculate inbound/outbound degree
  -> compare README links to discovered skill paths
  -> render deterministic Markdown report
```

### Interfaces

```
python3 scripts/skill-topology-scan.py [--hub-threshold N] [root]
```

Default `hub-threshold` is `3`. Output is Markdown to stdout. Exit code is `0`
for a successful scan even when broken references or orphan skills are present,
because this command is report-only.

### Data / Schema Changes

None.

### Failure Modes & Handling

- Root is missing or not a directory: print a concise error to stderr and exit
  `2`.
- No skill files: emit a report with zero counts and empty sections.
- Broken references: render them under `## Broken References`; do not fail.
- README missing: render every skill as uncovered under README coverage.

### Rollout / Migration

Land as an additive report command and advisory release-gate fixture. Existing
skill files do not need migration.

### Test Strategy Hooks

- Fixture command creates temporary repos and asserts report content for broken
  references, orphan skills, hub skills, skill tree, and README coverage.
- Full verification runs:
  - `bash tests/skill-topology-scan-fixtures.sh`
  - `bash tests/skill-hygiene-check-fixtures.sh`
  - `scripts/release-gate.sh --mode all --strict`

## Staged Implementation Plan

1. **Stage 1 - Topology report command and fixtures**: Add the read-only
   scanner, fixture coverage, release-gate advisory wiring, docs, and
   idea-to-ship implementation evidence.

## Open Questions

- None blocking. Future work may turn selected topology findings into advisory
  hygiene warnings after report output proves stable.
