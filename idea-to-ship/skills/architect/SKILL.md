---
name: architect
description: Read requirements.md, explore the codebase, and produce an architecture document with 2-3 alternatives, tradeoffs, and a recommendation. Does not write production code. Writes .idea-to-ship/<slug>/architecture.md.
argument-hint: '[--slug <name>] [extra notes]'
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent]
---

# Architect — Design From Requirements

Turn `requirements.md` into a concrete architecture. The output is a document an implementer could pick up and build from without re-deriving any decisions. Multiple alternatives are explored so the tradeoffs are visible, not hidden.

## Arguments

Raw: `$ARGUMENTS`

Parse:
- Optional leading `--slug <name>`. Default slug: `current`.
- Remaining text → extra design notes / constraints the user wants honored.

## Workflow

### Step 1: Load Context

1. Resolve artifact dir `.idea-to-ship/<slug>/`.
2. Require `requirements.md` to exist. If it doesn't, stop and tell the user to run `/brainstorm` first.
3. Read `requirements.md` fully.
4. If `architecture.md` already exists, read it — this run is a revision. Ask the user whether to revise or start over.

### Step 2: Explore the Codebase

Use the **Agent tool with `subagent_type: "Explore"`** with thoroughness `medium`. Ask it:

- What are the existing modules/packages most relevant to the touch points in `requirements.md`?
- What layering conventions does this repo follow (e.g. handler/service/repo split, domain events, hexagonal, etc)?
- What tech stack constraints apply (frameworks, DI style, async model, DB, testing libraries)?
- Are there existing utilities or abstractions we should reuse instead of reinventing?

Ask for a concise report with file paths. Do not proceed without this grounding — the design must fit the codebase, not an imagined one.

### Step 3: Design — Multiple Alternatives

Enumerate **2–3 realistic approaches**. Do not invent a straw-man just to crown the favorite. Each approach must be something a sane engineer would actually build.

For each alternative, think through:

- Module boundaries — what gets created, what gets modified, what stays.
- Data flow — control + data from entry point to side effect.
- Data model / schema changes, if any.
- Public interfaces (function signatures, API shapes, event schemas).
- Failure handling — what can go wrong, where, and who handles it.
- Migration / rollout path — how does this land without breaking existing users?
- Test strategy implications — what will be unit-testable vs integration-only.

Then for each: **Pros**, **Cons**, **Risk**.

### Step 4: Recommend

Pick one. State the recommendation plainly in the first sentence of the section. Justify based on:

- Fit with the existing codebase (cite files).
- Blast radius (smallest that meets the requirements wins).
- Reversibility (is this easy to undo if wrong?).
- Tradeoffs accepted explicitly.

**Do not hedge.** If two options are genuinely equivalent, say so and state the tiebreaker.

### Step 5: Write `architecture.md`

Template:

```markdown
# Architecture — <short title>

**Slug:** <slug>
**Date:** <YYYY-MM-DD>
**Status:** draft
**References:** requirements.md

## Summary
<One paragraph. What we're building and the chosen approach in plain English.>

## Goals / Non-Goals
Pull from requirements.md; restate in design-relevant terms.

## Codebase Context
<Key existing modules this will touch, with file paths. Conventions we must honor.>

## Alternatives Considered

### Option A — <name>
<Description.>

**Module changes:** <files/packages>
**Data flow:** <sketch>
**Interfaces:** <key signatures>
**Pros:** ...
**Cons:** ...
**Risk:** ...

### Option B — <name>
...

### Option C — <name> (optional)
...

## Recommendation
**We pick Option <X>.** <2–3 sentences why.>

## Chosen Design — Detail

### Module Breakdown
- `path/to/new_module.ext` — <role>
- `path/to/existing.ext` — <modification>

### Data Flow
<Diagram-in-prose or ASCII. Who calls whom, what goes over the wire.>

### Interfaces
<Concrete signatures, API routes, event schemas. Be specific enough to implement.>

### Data / Schema Changes
<DDL, migrations, or "none">

### Failure Modes & Handling
- <scenario>: <behavior>

### Rollout / Migration
<How it ships without breaking prod. Feature flag? Backfill? Dual-write?>

### Test Strategy Hooks
<Seams that make testing easy. What will be unit-testable, what needs integration.>

## Staged Implementation Plan
Ordered, independently-shippable stages. Each stage should leave the system working.

1. **Stage 1 — <name>**: <what lands, what doesn't yet>
2. **Stage 2 — <name>**: ...
3. **Stage 3 — <name>**: ...

## Open Questions
<Things the design cannot settle without more info. Answers go here before /implement runs.>
```

### Step 6: Hand-off

1. Print a 5-bullet summary: chosen option, top tradeoff accepted, top risk, first stage, any open questions.
2. Tell the user: "Run `/review-design` next — Codex will tear this apart and we'll iterate."

## Notes

- **No code in this skill.** Signatures and schemas yes; implementations no.
- If requirements.md is thin in a section you need, write a concrete assumption into architecture.md and flag it under Open Questions rather than blocking on the user.
- If the design is forced into awkward shapes because requirements are wrong, say so — recommend the user revise requirements before architecting further.
