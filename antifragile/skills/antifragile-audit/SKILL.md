---
name: antifragile-audit
description: Read-only resilience audit for an application or agent infrastructure. Use --scope system for runtime dependencies/data safety or --scope agent for hooks, skills, state, and recovery.
---

# Antifragile Audit

Audit the current target without changing code, config, Git, hooks, or external
systems. Print a ranked report; write no artifact.

## Arguments

Require `--scope system|agent`. Reject an ambiguous scope instead of mixing the
two checklists. Apply `../../WORKFLOW-CONTRACTS.md` for output caps and errors.

## Workflow

1. Identify the target and its repo instructions. Inspect at most the shared
   contract’s file budget and disclose truncation.
2. Trace critical paths rather than listing every file.
3. For each finding, cite path/line, trigger, consequence, existing guard, and
   the smallest repair. Do not report generic best practices without evidence.
4. Rank `critical`, `warning`, then `info`; list important checks that passed.

### System scope

Check external dependency timeouts/retries/fallbacks, error propagation,
single points of failure, data validation/atomicity/rollback, observability,
configuration defaults, startup failure, and degraded operation. Treat
security-specific analysis as out of scope unless it directly changes
resilience or data safety.

### Agent scope

Check hook failure isolation, missing dependency guards, state pollution,
partial writes, concurrent runs, uninstall behavior, stale references,
checkpoint/schema integrity, recovery after interruption, and cross-plugin
assumptions. Distinguish application resilience from agent infrastructure.

## Output

For each severity, report a compact table of evidence and repair. End with
`scope`, files inspected, skipped inputs, truncation, and one next action. If no
material gap exists, say so; never invent findings to fill the report.

Use `$harness-engineering:harness --mode audit` for orchestration layers.
