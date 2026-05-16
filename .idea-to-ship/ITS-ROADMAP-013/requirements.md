# Requirements - ITS-ROADMAP-013

**Slug:** ITS-ROADMAP-013
**Date:** 2026-05-16
**Status:** draft
**Source:** `.idea-to-ship/roadmap.md`

## Problem

The release gate currently validates `SKILL.md` frontmatter structurally: it
checks delimiters and non-empty `name` / `description` keys with regular
expressions. That is not enough to catch loader-visible YAML syntax problems.
The roadmap identifies a concrete regression class: unquoted bracket-style
`argument-hint` text such as `[--apply] [--all] [--force]` can look reasonable
to humans but is invalid YAML unless quoted.

This matters because skill frontmatter is parsed by runtime/plugin loaders
before the skill body is useful. A source tree that passes the release gate can
still produce installed-cache warnings or loader failures if the release gate
does not parse frontmatter with YAML semantics.

## Users / Actors

- Plugin maintainer: gets a blocking local release-gate failure before invalid
  `SKILL.md` frontmatter ships.
- Skill author: sees actionable evidence when scalar frontmatter fields need
  quoting.
- Plugin releaser: can trust `scripts/release-gate.sh --mode all --strict` to
  catch real frontmatter parse errors.
- Runtime operator: avoids installed-cache drift surprises by following a
  documented source-vs-cache expectation.

## In Scope

- Parse `SKILL.md` frontmatter with real YAML semantics in the release-gate
  `skill-frontmatter` blocking check.
- Preserve existing required-key validation for `name` and `description`.
- Add fixture coverage for `argument-hint: [--apply] [--all] [--force]`.
- Preserve staged-mode behavior: staged validation reads the index snapshot, not
  the repaired worktree.
- Update release-gate documentation to describe YAML parsing, the PyYAML
  requirement, and source-vs-installed-cache expectations.
- Run focused release-gate fixtures and the strict full release gate.

## Out of Scope / Non-Goals

- Mutating installed plugin caches or global runtime files.
- Network access or dependency installation during normal release-gate runs.
- Validating every possible semantic field in skill frontmatter beyond parse
  correctness and required `name` / `description`.
- Changing skill-hygiene advisory checks.
- Rewriting existing skill frontmatter unless it is necessary for this gate to
  pass.

## Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| FR-1 | `skill-frontmatter` must parse each `*/skills/*/SKILL.md` frontmatter block with YAML semantics and fail blocking on parse errors. | roadmap ITS-ROADMAP-013 |
| FR-2 | The gate must keep failing when required `name` or `description` fields are missing or empty after YAML parsing. | existing release-gate behavior |
| FR-3 | Staged mode must validate frontmatter from the Git index, not the worktree. | existing staged frontmatter fixture |
| FR-4 | A fixture must prove `argument-hint: [--apply] [--all] [--force]` fails frontmatter validation. | roadmap evidence required |
| FR-5 | Valid existing list-style frontmatter fields such as `allowed-tools: [Read]` must continue to pass. | current fixture baseline |
| FR-6 | Missing YAML parser support must fail loudly as a release-gate usage/dependency problem, not silently pass structural regex validation. | real YAML semantics requirement |
| FR-7 | Release-gate docs must describe YAML parsing and document that normal checks validate source/current checkout, while installed-cache synchronization remains a separate user action. | roadmap installed-cache drift note |

## Non-Functional Requirements

- **Performance:** Frontmatter validation must remain fast enough for staged and
  all-mode release gate use on the current repo.
- **Scale:** Must handle every current `*/skills/*/SKILL.md` file.
- **Reliability / failure mode:** YAML parse errors should include the affected
  file and a compact parser message in release-gate evidence.
- **Security / compliance:** The gate remains local, offline, and
  non-mutating. It must not inspect or modify installed plugin caches.
- **Platform / constraints:** Uses the existing Bash/Python release-gate flow
  and the locally available PyYAML module.

## Success Criteria

- Invalid unquoted bracket argument hint is blocked -> verify:
  `bash tests/release-gate-stage1.sh` includes a staged fixture that fails
  `skill-frontmatter`.
- Existing valid frontmatter still passes -> verify:
  `test_valid_repo_passes` in `tests/release-gate-stage1.sh`.
- Staged mode still reads the index -> verify:
  existing staged frontmatter snapshot fixture remains passing.
- Full repo gate is clean -> verify:
  `scripts/release-gate.sh --mode all --strict` passes.
- Documentation is updated -> verify:
  `RELEASE-GATE.md` names YAML parsing, PyYAML, and installed-cache sync
  expectations.

## Open Questions

- Should future work validate optional field types (`allowed-tools` list,
  `argument-hint` string, `description` string) beyond YAML parse correctness?
  This item intentionally limits scope to parse validity and required keys.

## Touch Points

- `scripts/release-gate.sh`
- `tests/release-gate-stage1.sh`
- `RELEASE-GATE.md`
- `.idea-to-ship/ITS-ROADMAP-013/`
