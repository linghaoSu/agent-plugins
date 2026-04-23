---
name: harness-design
description: Design the 7-layer harness for a new autonomous agent — Cognition, Tools, Contracts, Orchestration, Memory & State, Evaluation, Recovery — plus a concrete "Day 1 MVP" scaffold (state.json, retry wrapper, schema validator, tool-output truncation). Writes .harness-engineering/<slug>/harness-design.md.
argument-hint: '[--slug <name>] [free-form notes about the agent being built]'
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash]
---

# Harness Design — the scaffolding around the model

The model sits *inside* the harness. Inputs are filtered on the way in, outputs
are validated on the way out. The model never talks directly to users or
external systems. This skill produces the design doc for that harness.

## Arguments

Raw: `$ARGUMENTS`

Parse:
- Optional leading `--slug <name>` → slug. Default: `current`.
- Remaining text → free-form notes about the agent (task, tools, expected
  runtime, failure tolerance). May be empty — then ask in Step 1.

## Workflow

### Step 1: Bootstrap

1. Resolve `<slug>` and artifact directory:
   ```bash
   ARTIFACT_DIR=".harness-engineering/<slug>"
   mkdir -p "$ARTIFACT_DIR"
   ```
2. If `harness-design.md` already exists, read it and ask: "Existing design
   found. Continue refining, or start over?"
3. If notes are empty, ask the user (in one batch):
   - What is the agent supposed to do, end-to-end?
   - Single-shot or long-horizon (>10 steps / >1 context window)?
   - What tools does it need? Any that return unbounded payloads (web, docs,
     filesystem dumps)?
   - What's the failure tolerance — silent degradation OK, or must it halt?
   - Any deadlines / cost budget?

### Step 2: Walk the 7 layers

Fill each layer below. For every layer, decide: *what do we constrain, what do
we externalize, what do we verify, what do we recover from?* If a layer is not
applicable, say so explicitly — don't leave it blank.

1. **Cognition** — role definition and task brief. Prefer narrow, localized
   briefs over encyclopedic system prompts. Decide: single role, or
   Generator/Evaluator split?
2. **Tools** — every tool call goes through middleware: ranking
   (embedding/BM25), dedup, hard token cap. List each tool, its expected
   payload size, and the cap. Apply the tool-design checklist from
   [Anthropic's writing-tools-for-agents note](https://www.anthropic.com/engineering/writing-tools-for-agents):
   *fewer, consolidated tools* over many overlapping ones; *namespace* related
   tools (e.g. `asana_projects_search`); return *natural-language identifiers*
   over cryptic UUIDs; expose a `response_format` enum (`concise|detailed`)
   when outputs are large. Prefer an existing CLI over a new MCP when the
   capability is already covered — CLIs are composable and don't permanently
   occupy context ([Peekaboo 2.0](https://steipete.me/posts/2025/peekaboo-2-freeing-the-cli-from-its-mcp-shackles)).
3. **Contracts & Interfaces** — JSON schema or typed signature at every
   boundary. Schema drift kills silently; catch it here. Name each schema
   and where it's enforced.
4. **Orchestration** — explicit state machine or DAG of legal step
   transitions. The model *proposes* the next step; the harness *decides*.
   Sketch the states and transitions.
5. **Memory & State** — two tiers: working memory (in-context) and persistent
   state (e.g. `state.json`). Define the persistent schema and which fields
   are load-bearing across restarts.
6. **Evaluation & Observation** — heterogeneous validators. Prefer objective
   (compiler, tests, schema check, browser automation) over LLM-as-judge. Use
   LLM-as-judge only for genuinely subjective output, and even then on clean
   context.
7. **Constraints & Recovery** — idempotency rules. Which steps are safe to
   retry? Which require compensating actions? What's the blast radius of a
   single-step failure?

### Step 3: Commit to a Day 1 MVP

Before shipping anything sophisticated, commit to these four components. They
are cheap, and they prevent the most common 10-step collapse:

1. **`state.json`** — structured task state. Define the schema inline in the
   design doc (fields, types, invariants, when written, when read).
2. **Retry wrapper** — every tool call wrapped in try/catch with automatic
   retry + exponential backoff. Name the wrapper and list which tools it
   guards.
3. **Schema validator** — every LLM structured output validated; on failure,
   retry with the validator error as feedback instead of crashing.
4. **Tool-output truncation** — hard cap (token count) applied to every tool
   payload before it reaches the model. Specify the cap per tool.

### Step 4: Write `harness-design.md`

Template:

```markdown
# Harness Design — <agent name>

**Slug:** <slug>
**Date:** <YYYY-MM-DD>
**Status:** draft

## Agent Summary
<1 paragraph: what it does, horizon, failure tolerance.>

## Four Principles (commitments)
- Constrain, don't instruct: <where this applies here>
- Externalize state: <what lives in state.json>
- Verify every step: <how>
- Fail locally: <granularity of retry>

## Layer 1 — Cognition
<Role(s), brief(s). Single role or Generator/Evaluator split and why.>

## Layer 2 — Tools
| Tool | Payload source | Ranking/dedup | Hard token cap |
|------|----------------|---------------|----------------|
| ...  | ...            | ...           | ...            |

## Layer 3 — Contracts & Interfaces
<Each boundary + the schema enforced there. Name the schema files.>

## Layer 4 — Orchestration
<State machine or DAG. List states and legal transitions. Describe how the
harness decides vs. how the model proposes.>

## Layer 5 — Memory & State
### `state.json` schema
```json
{
  "task_id": "string",
  "status": "pending|running|complete|failed",
  "current_step": "string",
  "steps_completed": ["..."],
  "artifacts": { "...": "..." }
}
```
<Invariants: when each field is written and by whom.>

## Layer 6 — Evaluation & Observation
<Per-step validators. Objective first (compiler, test, schema, browser).
LLM-as-judge only where listed, with justification and clean-context rule.>

## Layer 7 — Constraints & Recovery
<Idempotency rules per step. Compensating actions for non-idempotent steps.
Blast radius analysis.>

## Day 1 MVP checklist
- [ ] `state.json` with schema above, loaded at start, written after each step
- [ ] Retry wrapper on tools: <list>
- [ ] Schema validator on LLM structured outputs: <list>
- [ ] Tool-output truncation with per-tool caps in table above

## Open Questions
<Anything deferred.>

## Non-goals (for this design)
<Things explicitly not in scope — e.g. "not adding context reset yet; see
/resilience-plan later".>
```

### Step 5: Hand-off

1. Tell the user the file was written; print a 3–5 bullet summary of the
   load-bearing decisions.
2. Suggest next steps:
   - `/sprint-contract` — if the design uses a Generator/Evaluator split
   - `/resilience-plan` — if long-horizon (>1 context window)
   - `/harness-audit` — once there's an implementation to check against this
     design

## Notes

- This skill designs, it does not implement. Write no code here beyond the
  schema snippets in the doc.
- Be blunt. If the user's plan is "let the model decide", push back and force
  a state machine or an explicit free-for-all justification.
- If the agent is genuinely single-shot and <10 steps, say so and recommend
  skipping most of this — harness overhead is only worth it when the
  10-step collapse is a real risk.
