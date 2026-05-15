---
name: goal-mode
description: "Run long-horizon work as a persistent goal loop: define objective, externalize state, choose one next step, verify progress, checkpoint, and resume across sessions. Use when the user asks for goal mode, continuous iteration, long-running tasks, or multi-turn execution. Writes .harness-engineering/<slug>/goal/."
argument-hint: '[--slug <name>] [--resume|--status|--complete] [goal text]'
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash]
---

# Goal Mode - persistent goal loop

## Overview

Goal mode is an execution harness for tasks too large to finish safely from
chat history alone. It emulates tool-native goal mode by externalizing the
objective, current state, next action, verification evidence, blockers, and
handoff summary under `.harness-engineering/<slug>/goal/`.

This skill is for doing the work, not only planning it. If the user asks a
simple one-shot task, do the task directly and skip this skill.

## Arguments

Raw: `$ARGUMENTS`

Parse:
- Optional leading `--slug <name>` -> slug. Default: `current`.
- `--resume` -> continue an existing goal from persisted state.
- `--status` -> summarize state without changing files.
- `--complete` -> mark the goal complete after verification.
- Remaining text -> objective or update notes.

## Artifact layout

Create or update:

```text
.harness-engineering/<slug>/goal/
|-- objective.md       # canonical goal, success criteria, non-goals, constraints
|-- state.json         # machine-readable state and next action
|-- iteration-log.md   # append-only decisions, work, checks, blockers
`-- handoff.md         # compact resume prompt for a fresh session
```

Use `scripts/goal_state.py` for deterministic state creation, validation,
recording, and handoff generation.

## Workflow

### Step 1: Bootstrap or resume

Resolve `<slug>`, set `GOAL_STATE_SCRIPT` to the bundled
`scripts/goal_state.py` path relative to this skill directory, then run one of:

```bash
python3 "$GOAL_STATE_SCRIPT" init --slug <slug> --objective "<goal>"
python3 "$GOAL_STATE_SCRIPT" status --slug <slug>
python3 "$GOAL_STATE_SCRIPT" validate --slug <slug>
```

When starting a new goal, clarify only load-bearing ambiguity:
- Objective: one sentence that defines the end state.
- Success criteria: objective checks that prove completion.
- Non-goals: adjacent work that must not creep in.
- Constraints: approvals, budgets, deadlines, repo rules, external systems.

If the user already gave enough detail, make conservative assumptions and
write them to `objective.md`; do not block on cosmetic detail.

### Step 2: Pick exactly one next step

Before each work cycle:

1. Read `state.json`, `objective.md`, and the last 20 lines of
   `iteration-log.md`.
2. Choose one step that materially advances the objective and can be verified.
3. Keep the step small enough that failure is local and retryable.
4. Announce the step briefly, then execute it.

Do not juggle multiple unrelated goals in one loop. If the user adds a new
objective, record it as a candidate follow-up unless it is required by the
current success criteria.

### Step 3: Verify before recording progress

Every step needs evidence. Prefer, in order:

1. Machine checks: tests, typecheck, lint, schema validation, browser checks.
2. Structural checks: files exist, required sections present, links resolve.
3. Clean-context review: only for subjective criteria.
4. User confirmation: when the result depends on user judgment or authority.

If no meaningful check exists, record that as a risk in `iteration-log.md` and
make the next step reduce that risk.

### Step 4: Checkpoint after each step

Record the outcome immediately after verification:

```bash
python3 "$GOAL_STATE_SCRIPT" record \
  --slug <slug> \
  --step "<what changed>" \
  --result "<observed result>" \
  --verification "<command/check and outcome>" \
  --next-action "<single next step>"
```

If blocked:

```bash
python3 "$GOAL_STATE_SCRIPT" record \
  --slug <slug> \
  --status blocked \
  --step "<attempted step>" \
  --result "<where it stopped>" \
  --blocker "<specific blocker>" \
  --next-action "<what would unblock it>"
```

When a later step resolves known blockers, add `--clear-blockers` to the
record command and include verification evidence for the unblock.

The script rewrites `handoff.md` on every update. Treat `handoff.md` as the
minimum resume context for a fresh agent.

### Step 5: Decide whether to continue, reset, or stop

After each checkpoint:

- Continue if the next step is clear and still fits the current context.
- Run `/resilience-plan` if the goal spans more than one context window, has
  critical state, or needs programmatic reset/consolidation outside this skill.
- Stop and ask the user if progress requires external approval, destructive
  action, credentials, production changes, or a product decision.
- Mark complete only when every success criterion has verification evidence.

Completion command:

```bash
python3 "$GOAL_STATE_SCRIPT" complete \
  --slug <slug> \
  --summary "<why the goal is done>" \
  --verification "<final evidence>"
```

## State rules

- `state.json` is the source of truth for status and next action.
- `iteration-log.md` is append-only; do not rewrite history to make progress
  look cleaner.
- `handoff.md` must be short enough to paste into a new session.
- Record unresolved uncertainty as a blocker or risk, not as completed work.
- Never load the whole historical log when a compact tail and state file are
  enough.

## Hand-off

When pausing or finishing, tell the user:

- current status: `running`, `blocked`, `complete`, or `failed`
- latest verification evidence
- next action, if any
- path to `.harness-engineering/<slug>/goal/handoff.md`
