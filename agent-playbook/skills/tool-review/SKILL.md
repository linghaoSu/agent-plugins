---
name: tool-review
description: Risk-scaled read-only review of one agent-facing tool, CLI, MCP server, REST endpoint, or schema. Checks boundaries, naming, output cost, errors, safety, and evaluation hooks.
---

# Tool Review

Review one tool surface and write `.agent-playbook/<slug>/tool-review.md`.
Do not edit the tool or mutate Git/external systems.

## Workflow

1. Resolve `--slug`, optional `--review-depth quick|standard|deep`, target,
   caller, and mutation boundary. Read source/schema and examples within the
   shared input budget.
2. Select the smallest intensity covering risk. Use the capability routing in
   `../../WORKFLOW-CONTRACTS.md`; never prescribe an execution product.
3. Review independent angles as required: interface/tool ergonomics,
   safety/error behavior, and evaluation/operability.
4. Check consolidated purpose, namespacing, natural identifiers, pagination
   and hard output caps, actionable errors, idempotency/confirmation, auth and
   secret handling, CLI-native alternatives, and realistic eval hooks.
5. Synthesize only evidence-backed findings. If the tool should not exist,
   recommend deletion or the existing native replacement.
6. Write `../../templates/tool-review-report.md` with intensity, mode,
   truncation, ranked punch-list, passed checks, and next action.

Same-context quick review is selected behavior, not degradation. Standard/deep
without independent roles must be marked `degraded`.

Use `$agent-playbook:context-audit` for a repo-wide context/tool suite.
