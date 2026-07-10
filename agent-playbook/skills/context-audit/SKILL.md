---
name: context-audit
description: Audit repo instruction, rule, hook, and tool-context hygiene. Use for bloated or conflicting agent memory, MCP/CLI overlap, missing verification, or autonomous-readiness checks.
---

# Context Audit

Read the target and write only `.agent-playbook/<slug>/context-audit.md`.
Never change target behavior, Git, hooks, installed tools, or external systems.

## Workflow

1. Parse `--slug <name>` and optional focus: memory, tools, workflow, or
   failure-patterns. Apply `../../WORKFLOW-CONTRACTS.md` caps and errors.
2. Inventory repo/global instruction files, scoped rules, agent definitions,
   tool/MCP config, hooks, verification commands, and duplicated CLI surfaces.
3. Score memory specificity, contradictions, path scoping, tool output bounds,
   verification loops, and recovery signals as ok/weak/broken. Cite evidence.
4. Rank only repairs that change behavior. Generic reminders and preferences
   already enforced by tooling are not findings.
5. Write the report using `../../templates/context-audit-report.md`; preserve
   human notes and use a draft if merge safety is unclear.

## Completion

Print the top three repairs, skipped inputs, and truncation state. Route memory
edits to `bootstrap-project-memory` and individual tool analysis to
`$agent-playbook:tool-review`. Route memory edits to
`$agent-playbook:bootstrap-project-memory`. If evidence is healthy, say so.
