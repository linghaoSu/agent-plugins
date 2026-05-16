# Requirements - ITS-ROADMAP-014

**Slug:** ITS-ROADMAP-014
**Date:** 2026-05-16
**Status:** draft
**Source:** `.idea-to-ship/roadmap.md`

## Problem

The repo has release-gate and hygiene checks for individual skill files, but it
does not yet expose a deterministic view of the skill system as a graph. A
maintainer can see that a specific `SKILL.md` is too large or has noisy
frontmatter, but cannot cheaply answer which skills reference each other, which
references are broken, which skills are isolated, which skills behave like
hubs, or whether the root README catalog covers every skill.

This matters because the plugin catalog is growing. Without topology evidence,
skill-system drift is reviewed by hand and cross-skill references can become
stale without a local, offline signal.

## Users / Actors

- Plugin maintainer: runs a local report to inspect skill graph health before
  publishing or reviewing a roadmap item.
- Skill author: sees broken references and catalog coverage gaps for skills
  they add or edit.
- Plugin releaser: can rely on a dedicated fixture and release-gate advisory
  command to keep topology reporting deterministic.

## In Scope

- Add a read-only topology scan command for local plugin skill files.
- Inventory plugins, skills, parent/leaf classification, outbound references,
  inbound references, broken references, orphan skills, hub skills, and README
  catalog coverage.
- Produce deterministic Markdown output with a skill-tree section suitable as a
  generated documentation fragment.
- Add fixtures for broken references and orphan skills.
- Wire the new fixture command into the release gate as an advisory check when
  the topology scan implementation, fixtures, or docs are touched.

## Out of Scope / Non-Goals

- Mutating README or generated docs automatically.
- Treating orphan or hub metrics as deletion authority.
- Network access or remote Kagenti scans.
- Changing existing skill-hygiene warning semantics.
- Enforcing topology findings as blocking release-gate failures in this item.

## Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| FR-1 | A deterministic command must scan `*/skills/*/SKILL.md` files and emit a Markdown topology report without network access or file mutation. | roadmap ITS-ROADMAP-014 |
| FR-2 | The report must inventory each plugin and skill with a stable skill id, path, display name, and classification as parent or leaf. | roadmap entry schema |
| FR-3 | The report must detect references to known skills through plugin-qualified `$plugin:skill` mentions and `plugin/skills/skill/SKILL.md` paths. | roadmap related/referenced skills |
| FR-4 | The report must list broken skill references with source path and target evidence. | roadmap broken references |
| FR-5 | The report must list orphan skills that have neither inbound nor outbound skill references. | roadmap orphan skills |
| FR-6 | The report must list hub skills using deterministic degree scoring. | roadmap hub skills / usefulness signal |
| FR-7 | The report must list README catalog coverage gaps for skills missing from the root README skill catalog links. | roadmap missing category coverage / generated docs |
| FR-8 | The report must include a deterministic skill-tree Markdown section grouped by plugin. | roadmap generated skill-tree docs |
| FR-9 | A dedicated fixture must cover at least one broken reference and one orphan skill. | roadmap evidence required |
| FR-10 | The release gate must run or skip the topology fixture deterministically as an advisory check. | release-gate evidence |

## Non-Functional Requirements

- **Performance:** Full-repo scan should remain fast enough for `scripts/release-gate.sh --mode all --strict`.
- **Scale:** Must handle the current repo's plugin/skill count and stable ordering as new skills are added.
- **Reliability / failure mode:** Missing files or malformed paths should produce deterministic report rows, not stack traces in normal use.
- **Security / compliance:** The scan is local, offline, and read-only. Fixtures must not contain credentials.
- **Platform / constraints:** Use the repo's existing Python and Bash test style; no new third-party dependency.

## Success Criteria

- Topology command emits a Markdown report with inventory, tree, broken refs,
  orphan skills, hub skills, and README coverage sections -> verify:
  `python3 scripts/skill-topology-scan.py .`.
- Broken-reference and orphan fixtures are covered -> verify:
  `bash tests/skill-topology-scan-fixtures.sh`.
- Release gate includes the topology fixture as an advisory check -> verify:
  `scripts/release-gate.sh --mode all --strict` and staged gate output contain
  `skill-topology-fixtures` when topology files are staged.
- Existing hygiene fixtures still pass -> verify:
  `bash tests/skill-hygiene-check-fixtures.sh`.

## Open Questions

- Parent/leaf classification is implemented locally as graph role: a skill with
  outbound references is a parent, otherwise it is a leaf. This is a pragmatic
  repo-local definition and not a Kagenti semantic import.
- Hub threshold is a fixed degree threshold chosen in architecture rather than
  a deletion/rewrite recommendation.

## Touch Points

- `scripts/skill-topology-scan.py`
- `tests/skill-topology-scan-fixtures.py`
- `tests/skill-topology-scan-fixtures.sh`
- `scripts/release-gate.sh`
- `RELEASE-GATE.md`
- `.idea-to-ship/ITS-ROADMAP-014/`
