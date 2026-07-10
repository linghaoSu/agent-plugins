# Harness Engineering

| Skill | Purpose |
|---|---|
| `harness --mode design` | Write `harness-design.md` across seven layers |
| `harness --mode audit` | Write `harness-audit.md` from evidence |
| `harness --mode resilience` | Write `resilience-plan.md` |
| `harness --mode contract` | Write pre-generation `sprint-contract.md` |
| `goal-mode` | Execute a persistent objective/state/checkpoint/handoff loop |

Artifacts live under `.harness-engineering/<slug>/`. Harness modes design or
audit scaffolding; they do not implement the target agent. Capability
requirements are host-neutral and deterministic verification is preferred.
