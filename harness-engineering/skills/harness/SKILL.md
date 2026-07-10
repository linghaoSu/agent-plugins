---
name: harness
description: Design or audit an autonomous-agent harness, its long-horizon recovery, or its generator/evaluator acceptance contract. Use --mode design|audit|resilience|contract.
---

# Harness

Produce one bounded harness artifact. This skill designs and audits scaffolding;
it does not implement the target agent.

## Arguments

- `--slug <name>`: artifact directory; default `current`.
- `--mode design|audit|resilience|contract`: required.
- Remaining text: agent/task notes.

Use role/capability language, never model, vendor, coding-agent, or
host-specific execution names. Prefer objective validators over model judgment.

## Shared intake

Read repo instructions and existing `.harness-engineering/<slug>/` artifacts.
Resolve objective, horizon, tools, failure tolerance, cost/time constraints,
and worst credible failure. Preserve human edits; write a draft rather than
overwrite an unmergeable artifact.

## Modes

### Design

Write `harness-design.md` across seven layers: cognition, tools, contracts,
orchestration, memory/state, evaluation/observation, constraints/recovery.
For each layer name constraints, externalized state, verifier, and recovery.
Commit to a Day-1 floor: validated `state.json`, bounded tool output, schema
validation, and retry rules. Recommend no harness for a genuinely short,
single-shot workflow.

### Audit

Write `harness-audit.md`. Inspect the implemented pipeline, score the seven
layers, trace state transitions and failure paths, and rank missing guards by
payoff. Cite executable evidence. Do not confuse a prompt instruction with a
programmatic constraint.

### Resilience

Write `resilience-plan.md`. Require a multi-context or long-running workload.
Define programmatic reset trigger, atomic checkpoint, termination/relaunch,
continuity validation, consolidation trigger, dedup/compression/contradiction
rules, rollback, concurrency lock, and failure modes not covered. Keep resume
context minimal; never reload the full history.

### Contract

Write `sprint-contract.md` before generation starts. Define deliverable, exact
inputs, out-of-scope work, and acceptance tiers: machine-checkable, structural,
then subjective clean-context judgment only where unavoidable. Specify
structured accept/reject feedback, retry caps, rollback, and escalation. If all
criteria are subjective, push for objective proxies.

## Completion

Validate required headings and cross-artifact links. Report output path,
load-bearing decisions/findings, skipped evidence, and the next action. Never
claim implementation or runtime verification from a design-only mode.

Use `$harness-engineering:goal-mode` to execute a persistent loop and
`$antifragile:antifragile-audit` for resilience evidence.
