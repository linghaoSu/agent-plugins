---
name: harness-audit
description: Audit an existing autonomous agent or pipeline against the 7-layer harness stack and canonical anti-patterns. Writes .harness-engineering/<slug>/harness-audit.md.
argument-hint: '[--slug <name>] [path/glob or description of the agent code to audit]'
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash]
---

# Harness Audit — find where the scaffolding is missing

The failure mode to find: the model looks fine in isolation, but the system
around it has no retries, no schema enforcement, no persistent state, and no
independent verification. When asked to run for 10 steps, it collapses silently.

This skill reviews existing code against the 7-layer harness stack and the
four anti-patterns, then writes a prioritized gap report.

## Arguments

Raw: `$ARGUMENTS`

Parse:
- Optional leading `--slug <name>` → slug. Default: `current`.
- Remaining text → path/glob or description of the agent to audit. If empty,
  ask in Step 1.

## Workflow

### Step 1: Bootstrap

1. Resolve `<slug>` and artifact dir:
   ```bash
   ARTIFACT_DIR=".harness-engineering/<slug>"
   mkdir -p "$ARTIFACT_DIR"
   ```
2. If `harness-audit.md` exists, read it and ask: "Existing audit found.
   Refresh, or start a new one?"
3. If the target is empty, ask: "What agent are we auditing? Point me at the
   entry file, the tool-calling module, and the state store if you have one."
4. If a design doc exists (`.harness-engineering/<slug>/harness-design.md`),
   read it — the audit compares implementation against declared design.

### Step 2: Reconnaissance

Map the system before scoring. Use Read / Grep / Glob to answer:

- **Entry point**: where does the agent loop start? How is a step defined?
- **Tool calls**: which functions call external services / LLMs / the
  filesystem? Are they wrapped?
- **State**: is there a `state.json` or equivalent? Where is it read/written?
- **Schemas**: is there structured-output validation, or does the code
  `JSON.parse` and hope?
- **Prompts**: one mega system prompt, or localized briefs?
- **Control flow**: explicit state machine / DAG, or "whatever the model says
  next"?
- **Self-grading**: does the same agent judge its own output anywhere?

Record findings inline as you go.

### Step 3: Score the 7 layers

For each layer, give a grade (A / B / C / D / F) and a 1-sentence rationale
citing a file path + line number where possible. Be concrete; "looks OK" is
not an audit finding.

1. **Cognition** — localized vs. encyclopedic prompts; role clarity
2. **Tools** — ranking / dedup / hard token cap on payloads
3. **Contracts & Interfaces** — JSON schemas / typed signatures at boundaries
4. **Orchestration** — explicit state machine or DAG; harness-decides vs.
   model-decides
5. **Memory & State** — persistent state file; invariants; resumability
6. **Evaluation & Observation** — objective validators present; LLM-as-judge
   sparingly and on clean context
7. **Constraints & Recovery** — retry wrappers; idempotency; blast radius

### Step 4: Scan for anti-patterns

Check each. For every "yes", cite the evidence.

- **Self-grading illusion** — does the generating agent evaluate its own
  output? Look for same-context "did we succeed?" prompts.
- **Optimizing for the illusion of correctness** — are prompts giving
  emotional / evaluative feedback ("try harder", "be careful") rather than
  objective signal (compiler error, test name, schema field)?
- **Context anxiety** — any step that runs past ~70% of the context window
  with no reset mechanism? Grep for token-count guards; absence is itself a
  finding.
- **Memory bloat** — does the state / log file grow unboundedly? Any
  consolidation routine? If not, that's a finding.

### Step 5: Prescribe fixes, ordered by payoff

Rank fixes by *risk reduction per hour of work*. The Day 1 MVP almost always
tops the list if it isn't already present:

1. `state.json` (if missing) — biggest resumability win.
2. Retry wrapper on tool calls — stops transient failures from killing runs.
3. Schema validator on structured LLM output — stops schema drift.
4. Tool-output truncation — stops unbounded payloads from eating context.

Everything else (state machine, Generator/Evaluator split, context reset,
memory consolidation) comes after those four.

### Step 6: Write `harness-audit.md`

Template:

```markdown
# Harness Audit — <agent name>

**Slug:** <slug>
**Date:** <YYYY-MM-DD>
**Target:** <paths audited>
**Design doc:** <link to harness-design.md, or "none">

## TL;DR
<2–3 sentences: headline grade, single biggest risk, one-line fix priority.>

## Layer scores

| Layer | Grade | Evidence (file:line) | Gap |
|-------|-------|----------------------|-----|
| 1. Cognition              | X | ... | ... |
| 2. Tools                  | X | ... | ... |
| 3. Contracts              | X | ... | ... |
| 4. Orchestration          | X | ... | ... |
| 5. Memory & State         | X | ... | ... |
| 6. Evaluation             | X | ... | ... |
| 7. Constraints & Recovery | X | ... | ... |

## Anti-patterns found
- [ ] Self-grading illusion — <evidence or "not observed">
- [ ] Illusion-of-correctness feedback — <evidence>
- [ ] Context anxiety risk — <evidence>
- [ ] Memory bloat — <evidence>

## Fix plan (ordered by payoff)
1. **<fix>** — <why it's first; files to touch; ~effort>
2. ...

## Day 1 MVP status
- [ ] `state.json` with loaded/saved invariants
- [ ] Retry wrapper on tool calls
- [ ] Schema validator on structured LLM output
- [ ] Tool-output truncation

## Deferred / non-blocking
<Things worth fixing eventually but not now.>

## Open Questions
<Things the audit couldn't determine from code alone.>
```

### Step 7: Hand-off

1. Print the headline grade and the top 3 fixes.
2. Offer: "Run `/harness-design` to sketch the target state, or hand this
   audit to your implementation flow to start fixing."

## Notes

- Cite file paths and line numbers. An audit without evidence is an opinion.
- Do not suggest a rewrite. The article's point is that most agents need
  *scaffolding added around the existing code*, not a rebuild.
- If the agent is simple single-shot (<10 steps, fits in one context), say
  so — most of this audit won't apply, and flagging it as "over-engineered
  target" is a valid finding.
