# Requirements - ITS-ROADMAP-012

**Slug:** ITS-ROADMAP-012
**Date:** 2026-05-16
**Status:** draft
**Source:** `.idea-to-ship/roadmap.md`

## Problem

The `agent-playbook` audit skills still inline report skeletons inside long
`SKILL.md` files. The repo already has shared safety and workflow contracts for
audit behavior, but the generated report shapes for tool review, context audit,
and vibe-coding health checks are still maintained as embedded markdown blocks.

This matters because these skills are operator-facing contracts. Keeping report
templates inline increases token load, makes normal wording changes harder to
review, and encourages future audit skills to copy nearby report boilerplate
instead of referencing a stable template artifact.

## Users / Actors

- Agent-playbook maintainer: updates report layouts in one template location
  instead of editing long skill bodies.
- Audit skill author: follows the existing template-reference pattern when a
  new audit skill writes `.agent-playbook/<slug>/` artifacts.
- Reviewer: can verify that report output contracts remain stable without
  reading long inline markdown blocks in each skill.
- Operator running an audit skill: still gets the same documented artifact path,
  read-only boundary, and output fields.

## In Scope

- Add template files under `agent-playbook/templates/` for the report skeletons
  currently embedded in audit skills.
- Update the audit skills to reference the new template files instead of
  inlining the full report body.
- Preserve each skill's artifact path, read-only or diagnostic-only semantics,
  and output/error contract.
- Add or update deterministic fixture coverage so required template references
  and template fields are checked.
- Run the existing agent-playbook fixture suite and strict release gate.

## Out of Scope / Non-Goals

- Committing generated `.agent-playbook/current/` reports.
- Changing the meaning or required sections of the audit reports beyond moving
  stable skeleton text into templates.
- Combining tool-review, context-audit, and vibe-health reports into one generic
  template.
- Changing multi-agent review routing, deep-audit routing, artifact ownership,
  or read-only safety boundaries.
- Adding a report-rendering engine or runtime template loader.
- Touching unrelated plugins unless a test fixture needs a reference update.

## Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| FR-1 | `agent-playbook` must contain reusable report template files under `agent-playbook/templates/` for audit outputs currently inlined in `SKILL.md` files. | roadmap ITS-ROADMAP-012 |
| FR-2 | `tool-review` must reference an extracted tool-review report template while preserving `.agent-playbook/<slug>/tool-review-<tool-name>.md` as the output artifact. | `agent-playbook/skills/tool-review/SKILL.md:146-180` |
| FR-3 | `context-audit` must reference an extracted context-audit report template while preserving `.agent-playbook/<slug>/context-audit.md` as the output artifact. | `agent-playbook/skills/context-audit/SKILL.md:116-158` |
| FR-4 | `vibe-coding-health-check` must reference an extracted vibe-health report template while preserving `.agent-playbook/<slug>/vibe-health-check.md` and append/draft artifact ownership behavior. | `agent-playbook/skills/vibe-coding-health-check/SKILL.md:145-190` |
| FR-5 | The extracted templates must keep the load-bearing report sections and contract fields that downstream users rely on. | roadmap release gate |
| FR-6 | Skills must still distinguish read-only target analysis, local artifact writes, diagnostic-only behavior, and mutating-workflow handoffs after the extraction. | ITS-ROADMAP-011 dependency and roadmap no-go |
| FR-7 | Generated report artifacts under `.agent-playbook/current/` or other `.agent-playbook/<slug>/` paths must remain ignored/local-only and must not be added as sample output. | `.gitignore:2`; roadmap no-go |
| FR-8 | Agent-playbook fixture coverage must assert both skill references and template content for the extracted report skeletons. | roadmap evidence required |

## Non-Functional Requirements

- **Performance:** No runtime performance requirement; this is a documentation
  and contract extraction.
- **Scale:** The template layout should support additional agent-playbook audit
  report templates without changing skill discovery.
- **Reliability / failure mode:** If a template is missing or empty, fixture
  checks should fail before release.
- **Security / compliance:** No secrets, generated reports, or external data
  should be introduced.
- **Platform / constraints:** Markdown-only templates; no new runtime
  dependency.

## Success Criteria

- Template files exist -> verify: `test -f agent-playbook/templates/tool-review-report.md`
  and equivalent files for context audit and vibe health.
- Tool-review references its template -> verify:
  `rg "templates/tool-review-report.md" agent-playbook/skills/tool-review/SKILL.md`.
- Context-audit references its template -> verify:
  `rg "templates/context-audit-report.md" agent-playbook/skills/context-audit/SKILL.md`.
- Vibe health references its template -> verify:
  `rg "templates/vibe-health-check.md" agent-playbook/skills/vibe-coding-health-check/SKILL.md`.
- Template content preserves report contracts -> verify:
  `bash tests/agent-playbook-eval-fixtures.sh` checks required headings and
  contract fields in each template.
- Release readiness remains intact -> verify:
  `scripts/release-gate.sh --mode all --strict` passes.
- No generated reports are committed -> verify:
  `git status --short --untracked-files=all` shows no `.agent-playbook/`
  report artifacts.

## Open Questions

- Should `commit-changes` or other non-audit report bodies later move to
  templates too? This item intentionally limits scope to audit reports named in
  the roadmap.
- Should future skills load templates verbatim at runtime or only cite them as
  authoring contracts? This item uses citation only, matching existing
  issue-evaluator and idea-to-ship template patterns.

## Touch Points

- `agent-playbook/skills/tool-review/SKILL.md`
- `agent-playbook/skills/context-audit/SKILL.md`
- `agent-playbook/skills/vibe-coding-health-check/SKILL.md`
- `agent-playbook/templates/`
- `tests/agent-playbook-eval-fixtures.py`
- `.idea-to-ship/ITS-ROADMAP-012/`
