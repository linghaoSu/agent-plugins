---
name: resilience-plan
description: Design the two routines that keep long-horizon agents alive — programmatic Context Reset (save state → kill instance → relaunch fresh) and Memory Consolidation (periodic compression, dedup, contradiction resolution). Writes .harness-engineering/<slug>/resilience-plan.md.
argument-hint: '[--slug <name>] [notes about the long-horizon task]'
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash]
---

# Resilience Plan — context reset + memory consolidation

Two failure modes kill long-horizon agents:

1. **Context anxiety**: past ~70% of the context window, the model starts
   skipping steps and declaring premature success. The fix is *not* a bigger
   window — it's a programmatic reset that saves state, terminates the
   instance, and relaunches a fresh one.
2. **Memory bloat**: the persistent state / log file accumulates contradictory,
   redundant entries over time. Agents reading it later get confused by their
   own past. The fix is a scheduled consolidation routine.

This skill designs both routines for a specific agent.

## Arguments

Raw: `$ARGUMENTS`

Parse:
- Optional leading `--slug <name>` → slug. Default: `current`.
- Remaining text → notes on the long-horizon task. If empty, ask.

## Workflow

### Step 1: Bootstrap

1. Resolve `<slug>` and artifact dir:
   ```bash
   ARTIFACT_DIR=".harness-engineering/<slug>"
   mkdir -p "$ARTIFACT_DIR"
   ```
2. If `harness-design.md` exists, read it — the reset + consolidation
   routines must line up with the declared `state.json` schema.
3. If the task description is empty, ask:
   - Expected runtime (minutes / hours / days)?
   - How many total steps, roughly? How many context windows does that span?
   - What is *the minimum state* the agent needs to resume from a cold start?
   - Is the agent allowed to run in parallel with itself, or strictly serial?

If the task fits comfortably in one context window with margin, tell the
user this skill is overkill — recommend the Day 1 MVP instead.

### Step 2: Design the Context Reset routine

Decide:

- **Trigger**: token-count threshold (e.g. 70% of window), step-count
  threshold, wall-clock, or manual. Usually token count.
- **Checkpoint contents**: exactly what is written to persistent state before
  termination. Must be sufficient to resume without re-reading the full
  history. Cite the `state.json` schema from the design doc.
- **Termination**: who kills the instance? The harness (preferred) or the
  agent voluntarily (risky — may not fire under anxiety).
- **Relaunch**: fresh process / fresh context. What subset of state does the
  new instance load? (Usually: task brief + current step + last few results,
  not the whole history.)
- **Continuity check**: the new instance verifies the checkpoint is sane
  before proceeding (e.g. last step's output matches schema).

### Step 3: Design the Memory Consolidation routine

Decide:

- **Trigger**: step-count (every N steps), time-based (every N minutes), or
  size-based (when the log passes N KB). Size-based is usually safest.
- **Scope**: what gets consolidated. Typically: event logs, intermediate
  findings, retrieved documents. Never: the task brief, the current step
  pointer, schema-validated artifacts.
- **Operations**:
  - **Dedup** — identical / near-identical entries collapsed.
  - **Compress** — multi-entry sequences summarized, with originals moved
    to a cold archive (not deleted — the consolidator could be wrong).
  - **Contradiction resolution** — when two entries disagree, the later one
    usually wins, but flag it explicitly in the consolidated note.
- **Safety**: consolidation runs on clean context with only the log as
  input. Output validated against a schema before replacing the live state.
  Keep the pre-consolidation file as `.prev` until the next cycle.

### Step 4: Write `resilience-plan.md`

Template:

```markdown
# Resilience Plan — <agent name>

**Slug:** <slug>
**Date:** <YYYY-MM-DD>
**Design doc:** <link to harness-design.md, or "none">
**Expected horizon:** <steps / context windows / wall-clock>

## Context Reset

### Trigger
<Token count threshold (e.g. 70% of 200k = 140k), step count, or hybrid.
State how the harness measures and enforces it.>

### Checkpoint contents
Written to `state.json` before termination:
- `task_id`, `current_step`, `steps_completed`
- <any other load-bearing fields from the design doc>

### Termination
<Who kills the process. Preferred: harness observes the trigger and kills the
child process. Voluntary self-termination is a fallback only.>

### Relaunch
New instance loads:
- Task brief (static)
- `current_step` and last N step results from `state.json`
- <anything else genuinely necessary — keep this list short>

### Continuity check
Before the new instance runs its first step:
- [ ] Checkpoint schema validates
- [ ] Last step's output matches its declared schema
- [ ] No lock file from a still-running prior instance

## Memory Consolidation

### Trigger
<Size / step count / time. Be specific.>

### Scope
- Consolidated: <event log, retrieved docs, intermediate findings>
- Never touched: <task brief, current step pointer, validated artifacts>

### Operations
1. **Dedup** — <rule for "same enough">
2. **Compress** — <summary length target; archive path for originals>
3. **Contradiction resolution** — <tie-breaking rule + flagging requirement>

### Safety
- Consolidation runs on clean context.
- Output validated against `schemas/consolidated-memory.json`.
- Pre-consolidation file retained as `state.json.prev` until next cycle.
- Rollback procedure: <describe>

## Worked example
<A concrete scenario: "at step 42, token usage hits 140k, reset fires.
Checkpoint contains X. New instance loads Y. Runs step 43 successfully.">

## Failure modes covered
- [ ] Context anxiety at high token counts
- [ ] Memory bloat over long runs
- [ ] Mid-step process crash (covered by checkpoint granularity)
- [ ] Consolidation corrupting state (covered by .prev rollback)

## Failure modes NOT covered
<Be honest. E.g. "network partition during checkpoint write — out of scope;
assume local filesystem is reliable.">

## Open questions
```

### Step 5: Hand-off

1. Print: reset trigger, consolidation trigger, and the list of covered vs.
   not-covered failure modes.
2. Suggest: update `harness-design.md` to cite this plan under Layer 5
   (Memory & State) and Layer 7 (Constraints & Recovery).

## Notes

- Reset and consolidation must be **programmatic**, not instructed. A prompt
  that says "reset yourself when context is full" is the exact failure this
  is meant to prevent.
- Keep the relaunch state minimal. Loading the full history defeats the
  purpose of the reset — you're back where you started.
- Consolidation is lossy. Always keep `.prev` until the next cycle so a bad
  consolidation can be rolled back.
