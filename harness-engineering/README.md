# harness-engineering

A plugin for designing and hardening the scaffolding *around* autonomous agents —
the harness that constrains inputs, externalizes state, verifies every step, and
recovers from failure. Agents don't fail because models are weak; they fail
because the surrounding system is undefined.

Based on the harness-engineering framework described in
[Your AI Isn't "Stupid" — It Just Needs a Better Harness](https://blog.ltbase.dev/posts/agents/harness-engineering).

All artifacts land under `.harness-engineering/<slug>/` at the repo root:

```
.harness-engineering/<slug>/
├── harness-design.md     # from /harness-design
├── harness-audit.md      # from /harness-audit
├── sprint-contract.md    # from /sprint-contract
├── resilience-plan.md    # from /resilience-plan
└── goal/                 # from /goal-mode
    ├── objective.md
    ├── state.json
    ├── iteration-log.md
    └── handoff.md
```

The default `<slug>` is `current`. Pass `--slug <name>` to any skill to switch.

## Commands

### `/harness-design [notes]`
Design the 7-layer harness for a new autonomous agent. Walks through Cognition,
Tools, Contracts, Orchestration, Memory & State, Evaluation, and Recovery —
then drops a concrete "Day 1 MVP" (state.json schema, retry wrapper, schema
validator, tool-output truncation). Writes `harness-design.md`.

### `/harness-audit [target]`
Audit an existing agent or multi-step pipeline against the 7-layer stack and
the four canonical anti-patterns (self-grading illusion, optimizing for the
illusion of correctness, context anxiety, memory bloat). Scores each layer,
flags concrete gaps, and prescribes minimum-invasive fixes. Writes
`harness-audit.md`.

### `/sprint-contract [task]`
Draft a Sprint Contract between a Generator agent and an independent
Evaluator — concrete, testable success criteria agreed before work begins.
Forces objective verification (compilers, tests, schema checks) over
LLM-as-judge for anything non-subjective. Writes `sprint-contract.md`.

### `/resilience-plan [notes]`
Design the two routines that keep long-horizon agents alive: programmatic
Context Reset (save state → kill instance → relaunch fresh) and Memory
Consolidation (periodic compression, dedup, contradiction resolution). Writes
`resilience-plan.md`.

### `/goal-mode [--slug <name>] [--resume|--status|--complete] [goal]`
Run a long-horizon task as a persistent execution loop. Captures the objective,
success criteria, current step, verification evidence, blockers, and compact
handoff under `.harness-engineering/<slug>/goal/` so another session can resume
without relying on chat history.

## Core principles (enforced by all skills)

1. **Constrain, don't instruct.** A schema validator is a guarantee; a prompt
   instruction is a hope.
2. **Externalize state.** Anything task-critical must live outside the context
   window.
3. **Make every step verifiable.** Validation must come from something other
   than the model that produced the output.
4. **Fail locally, not globally.** Granular state → retry one step, not the
   whole pipeline.

## Conventions

- **Slug**: all skills accept `--slug <name>` as the first token of their
  arguments. If omitted, uses `current`.
- **Artifact-first**: skills prefer updating the markdown artifact over
  chatting. Read the file to see what they did.
- **Design first where appropriate**: `/harness-design`, `/harness-audit`,
  `/sprint-contract`, and `/resilience-plan` produce design / audit artifacts.
  `/goal-mode` is execution-oriented and checkpoints task progress while work
  proceeds.
