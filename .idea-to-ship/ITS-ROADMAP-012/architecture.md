# Architecture - Agent-Playbook Audit Report Templates

**Slug:** ITS-ROADMAP-012
**Date:** 2026-05-16
**Status:** draft
**References:** requirements.md

## Summary

Extract the three inline agent-playbook audit report skeletons into
`agent-playbook/templates/` and have each owning skill cite the corresponding
template at its report-writing step. The chosen approach preserves every
documented output path and safety boundary while moving only stable report
shape out of long `SKILL.md` files.

## Goals / Non-Goals

Goals:

- Reduce duplicated inline report boilerplate in `tool-review`,
  `context-audit`, and `vibe-coding-health-check`.
- Keep report output paths and contract fields stable.
- Add fixture checks that fail if a skill loses its template reference or a
  template loses load-bearing headings.
- Keep `.agent-playbook/<slug>/` generated reports local-only.

Non-goals:

- No runtime template renderer.
- No generic one-size-fits-all audit template.
- No generated `.agent-playbook/` sample reports.
- No change to review delegation, deep-audit routing, artifact ownership, or
  mutating workflow gates.

## Codebase Context

- `agent-playbook/WORKFLOW-CONTRACTS.md` already owns shared output/token/error,
  artifact ownership, frontmatter, and safety/evaluation contracts.
- `agent-playbook/skills/tool-review/SKILL.md:146-200` inlines the
  `.agent-playbook/<slug>/tool-review-<tool-name>.md` report skeleton.
- `agent-playbook/skills/context-audit/SKILL.md:116-158` inlines the
  `.agent-playbook/<slug>/context-audit.md` report skeleton.
- `agent-playbook/skills/vibe-coding-health-check/SKILL.md:145-190` inlines the
  `.agent-playbook/<slug>/vibe-health-check.md` report skeleton after artifact
  ownership rules.
- `tests/agent-playbook-eval-fixtures.py` uses regex contract checks for skill
  references and template files in nearby plugins. Existing issue-evaluator and
  idea-to-ship fixture patterns check both "skill references template" and
  "template contains required headings".

## Cross-Skill Routing

| Signal | Routed skill | Result | Design impact |
|---|---|---|---|
| Documentation/template extraction in agent skill infrastructure | none | no separate read-only audit needed before design | Use local fixture and release-gate verification. |

## Alternatives Considered

### Option A - Extract Three Dedicated Templates

Create one template file per audit report and replace inline fenced report
blocks in the owning skills with concise "use this template" instructions.

**Module changes:** `agent-playbook/templates/*.md`,
`agent-playbook/skills/*/SKILL.md`, `tests/agent-playbook-eval-fixtures.py`

**Data flow:** User invokes skill -> skill gathers/reviews -> skill writes the
same `.agent-playbook/<slug>/...` artifact using the named template contract.

**Interfaces:** Markdown template paths:

- `agent-playbook/templates/tool-review-report.md`
- `agent-playbook/templates/context-audit-report.md`
- `agent-playbook/templates/vibe-health-check.md`

**Pros:** Small diff, preserves local differences, matches existing template
patterns, fixtureable with existing test harness.

**Cons:** Three templates still contain some similar sections.

**Risk:** Low; stale references if skill or template is renamed without fixture
coverage.

### Option B - Add One Generic Audit Report Template

Create one `agent-playbook/templates/audit-report.md` with optional sections
for every audit skill.

**Module changes:** One template plus all three skills.

**Data flow:** Skills select applicable sections from a shared generic report
shape.

**Interfaces:** `agent-playbook/templates/audit-report.md`

**Pros:** Maximum extraction by line count.

**Cons:** Violates the roadmap no-go by flattening different audit outputs into
one generic shape; harder for future agents to know which sections apply.

**Risk:** Medium; likely to lose domain-specific report judgment.

### Option C - Keep Inline Blocks And Add Shared Checklist Only

Leave report skeletons inline and rely on `WORKFLOW-CONTRACTS.md` for shared
safety and output contracts.

**Module changes:** None or tests only.

**Data flow:** No change.

**Pros:** Lowest immediate risk.

**Cons:** Does not satisfy FR-1 through FR-4; report boilerplate remains in long
skill bodies.

**Risk:** Medium; future audit skills will keep copying inline report blocks.

## Recommendation

**We pick Option A.** Dedicated templates are the smallest change that satisfies
the roadmap while keeping tool review, context audit, and vibe health distinct.
The accepted tradeoff is that some generic headings remain repeated across
template files; that repetition is lower-cost than making one ambiguous report
contract.

## Chosen Design - Detail

### Module Breakdown

- `agent-playbook/templates/tool-review-report.md` - extracted report skeleton
  for `.agent-playbook/<slug>/tool-review-<tool-name>.md`.
- `agent-playbook/templates/context-audit-report.md` - extracted report
  skeleton for `.agent-playbook/<slug>/context-audit.md`.
- `agent-playbook/templates/vibe-health-check.md` - extracted report skeleton
  for `.agent-playbook/<slug>/vibe-health-check.md`.
- `agent-playbook/skills/tool-review/SKILL.md` - replace the inline template
  block with a reference to `../../templates/tool-review-report.md`.
- `agent-playbook/skills/context-audit/SKILL.md` - replace the inline template
  block with a reference to `../../templates/context-audit-report.md`.
- `agent-playbook/skills/vibe-coding-health-check/SKILL.md` - keep artifact
  ownership rules inline and reference `../../templates/vibe-health-check.md`
  for the report body.
- `tests/agent-playbook-eval-fixtures.py` - add checks for skill references and
  template content.

### Data Flow

```
skill workflow completes
  -> Step "Write report/artifact"
  -> skill names output path
  -> skill cites template file
  -> generated artifact is written under .agent-playbook/<slug>/
```

No runtime file loading is required. The templates are authoring/output
contracts that future agents read before writing the report.

### Interfaces

Template reference contract:

- Skill bodies must contain the relative template path from the skill directory:
  `../../templates/<name>.md`.
- Fixture checks must assert each skill references its template and each
  template contains the output heading, contract field, and required sections.

### Data / Schema Changes

None.

### Failure Modes & Handling

- Missing template file: `tests/agent-playbook-eval-fixtures.sh` fails.
- Skill loses the reference: fixture check fails.
- Template loses contract field or load-bearing section: fixture check fails.
- Accidental generated `.agent-playbook/` report: `.gitignore` and final git
  status audit catch the untracked artifact.

### Rollout / Migration

Land as a documentation/test refactor in one commit. No migration is required
because public skill names, arguments, output paths, and report semantics stay
the same.

### Test Strategy Hooks

- Stage TDD should add failing fixture checks for the new template references
  and template headings before templates/skill edits are made.
- Existing `bash tests/agent-playbook-eval-fixtures.sh` is the focused
  contract suite.
- `scripts/release-gate.sh --mode all --strict` verifies full repo release
  gates after implementation.

## Staged Implementation Plan

1. **Stage 1 - Extract agent-playbook audit report templates**: Add failing
   fixture checks, create three template files, replace inline report blocks in
   the three skills with template references, and verify fixture/release-gate
   coverage.

## Open Questions

- None blocking. Future extraction of non-audit reports is intentionally out of
  scope for this slug.
