---
name: brainstorm
description: Turn a vague idea into a concrete requirements document via Socratic Q&A. Asks clarifying questions in batches until the problem, users, constraints, and success criteria are unambiguous. Writes .idea-to-ship/<slug>/requirements.md.
argument-hint: '[--slug <name>] [free-form description of the idea]'
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash]
---

# Brainstorm — Socratic Requirement Mining

Take a fuzzy idea and drill into it until the requirements are concrete enough to architect. The output is `.idea-to-ship/<slug>/requirements.md` — a document that a different engineer could act on without needing to ask the user anything.

## Arguments

Raw: `$ARGUMENTS`

Parse:
- Optional leading `--slug <name>` → use as slug. Default slug: `current`.
- Remaining text → initial idea description. May be empty (then ask the user for it in Step 1).

## Workflow

### Step 1: Bootstrap

1. Resolve `<slug>` and artifact directory:
   ```bash
   ARTIFACT_DIR=".idea-to-ship/<slug>"
   mkdir -p "$ARTIFACT_DIR"
   ```
2. Check for existing `requirements.md`:
   - If it exists → read it and ask: "Existing requirements found. Continue refining, or start over?"
   - If not → proceed.
3. If the initial idea description is empty, ask: "What are you thinking about building? Give me the rough shape — I'll dig in."

### Step 2: Socratic Questioning

The goal is a concrete, actionable spec. Ask questions in **batches of 3–5** (not one-at-a-time — that is annoying). Stop asking only when every section below can be filled in without guessing.

Cover these dimensions, but do not robotically walk them — prioritize whatever is most ambiguous:

- **Problem**: What hurts today? Whose pain? How do you know it hurts? (If the user can't articulate the pain, the feature is probably premature.)
- **Users / actors**: Who triggers this? Who consumes the output? Internal only, or external?
- **Scope boundaries**: What is explicitly *out* of scope? (Forcing an out-of-scope list cuts 80% of bloat.)
- **Constraints**: Performance, latency, cost, compliance, platform, existing-tech-stack lock-in.
- **Integrations**: What existing systems must this touch? What stays untouched?
- **Success criteria**: How do you know it worked? What's the metric, threshold, or user behavior change?
- **Failure modes**: What's the worst acceptable outcome when it breaks? Silent fail, degraded mode, hard error?
- **Non-goals**: Things that look related but are explicitly not this feature.

**Be blunt.** If the user's answer is vague ("it should be fast"), push back ("fast = p50 under what? 100ms? 1s? what's the budget?"). Do not accept handwaves. If the user says "I don't know", offer 2–3 concrete options and make them pick.

**Challenge the premise.** If the idea itself seems wrong — wrong scope, solving a non-problem, already solved by existing code — say so directly before mining requirements for a bad idea. Reference the codebase when relevant: use Grep/Glob to check if something already exists.

**Batch format:**
```
Got it. Before I can write this up I need to nail down a few things:

1. <question>
2. <question>
3. <question>

(Feel free to answer "don't care" or "default" if any of these don't matter — I'll fill in a reasonable choice.)
```

### Step 3: Write `requirements.md`

Once the picture is clear, write the document. Template:

```markdown
# Requirements — <short title>

**Slug:** <slug>
**Date:** <YYYY-MM-DD>
**Status:** draft

## Problem
<1–2 paragraphs. What's broken / missing, who feels it, and why it matters now.>

## Users / Actors
- <role>: <what they do with this>

## In Scope
- <bullet>

## Out of Scope / Non-Goals
- <bullet — be generous here, this is where bloat dies>

## Functional Requirements
<Numbered list. Each item is a testable, user-visible behavior. No implementation details.>

1. <FR-1>
2. <FR-2>

## Non-Functional Requirements
- **Performance:** <concrete number or "not critical">
- **Scale:** <expected load>
- **Reliability / failure mode:** <what happens when it breaks>
- **Security / compliance:** <if any>
- **Platform / constraints:** <tech stack, env, etc>

## Success Criteria
<How we measure success. Each criterion must be **verifiable** — a concrete
check an engineer (or a test) can run, not a vibe. Prefer the form
`<behavior> → verify: <check>`.>

Examples of good criteria:
- `p50 cache lookup < 5ms → verify: benchmark in bench_cache.go reports ≤5ms`
- `401 retries succeed silently → verify: test_login_401_retry passes`
- `no breaking change to public API → verify: api-diff job is clean on PR`

Examples of weak criteria (rewrite these):
- "it should be fast"
- "make it work"
- "users are happy"

## Open Questions
<Anything the user deferred or said "don't care" to. Being explicit lets the architect stage handle them.>

## Touch Points
<Existing files/modules/systems this will likely interact with. Not a design — just orientation hints for the architect.>
```

### Step 4: Review & Hand-off

1. Tell the user the file was written and print 3–5 bullet summary of the key decisions.
2. Ask: "Anything off? Otherwise run `/architect` next."
3. Do **not** start architecting yourself — that's a separate skill.

## Notes

- Do not write code in this skill. Ever.
- Do not invent requirements the user didn't state. If unknown, put in "Open Questions".
- If the user pushes you to skip questions, honor it — but write explicit "assumption" entries in Open Questions so the next stage knows what was guessed.

## Anti-Patterns

- **Leading questions.** "Don't you think we should use a cache here?" is not a question — it's a suggestion wearing a question mark. Ask "What's the latency budget?" and let the user's answer drive the design.
- **Requirements inflation.** Adding requirements the user never stated because "we'll probably need it." If the user didn't say it and the codebase doesn't demand it, it goes in Open Questions at most — not in Functional Requirements.
- **Accepting handwaves.** "It should be fast" is not a requirement. "It should handle errors gracefully" is not a requirement. Push until there's a number, a behavior, or a testable condition.
- **One-at-a-time questioning.** Asking one question per turn is slow and annoying. Batch 3-5. If you need 15 questions, you're overcomplicating it — group by theme and ask the highest-leverage ones first.
- **Interviewing when the codebase has the answer.** If the user says "integrate with the existing auth system," don't ask "what auth system do you use?" — grep the codebase and find out. Only ask what the code can't tell you.

## Phase Gates

- **⛔ GATE before Step 3 (Write requirements.md):** Every section in the template must be fillable without guessing. If Problem, Users, or Success Criteria still have gaps, ask another batch. Do not write a requirements doc with "TBD" in critical sections.

## Techniques worth stealing

- **Let the agent interview** — for a complex feature, use `AskUserQuestion`
  (if available) rather than free-form chat. Structured prompts force the
  user to think about edges they'd otherwise skip. See the "Let Claude
  interview you" pattern in [Claude Code best practices](https://code.claude.com/docs/en/best-practices#let-claude-interview-you).
- **Two-context critique** — when the spec feels soft, spawn a fresh subagent
  (clean context) with the prompt: *"Take this requirements doc apart. Give
  me 20 points that are underspecified, weird, or inconsistent."* Feed the
  critique back into this skill's Q&A. Credit: Peter Steinberger's
  [Gemini workflow](https://steipete.me/posts/2025/understanding-codebases-with-ai-gemini-workflow).
  Do this instead of asking the same model to self-review — self-review in
  the same context is biased toward what it just wrote.
