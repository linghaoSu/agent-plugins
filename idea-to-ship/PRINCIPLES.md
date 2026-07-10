# Code Principles — idea-to-ship

Shared principles every skill in this plugin that writes or reviews code must
apply. Principles 1–4 are inspired by [Karpathy's observations](https://x.com/karpathy/status/2015883857489522876)
on LLM coding pitfalls. Principle 5 distills context-window guidance from
[Anthropic's context-engineering note](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
and the [Claude Code best-practices guide](https://code.claude.com/docs/en/best-practices).

If you are a skill: read this file once before writing or reviewing any code.
Cite it when you push back on a request that violates it.

## Local 12-rule execution contract

These project rules are binding for non-trivial work unless a higher-priority
instruction explicitly overrides them. For trivial one-line work, use judgment
without hiding skipped checks.

1. **Think before coding.** State assumptions, list plausible interpretations
   when ambiguity exists, ask instead of guessing, and push back on simpler or
   safer alternatives.
2. **Simplicity first.** Minimum code, no speculative features, no one-use
   abstractions.
3. **Surgical changes.** Touch only what the selected requirement, stage, or
   fix needs; clean up only changes introduced by this run.
4. **Goal-driven execution.** Define success criteria and loop until the
   criteria are verified or a blocker is explicit.
5. **Use model judgment only where needed.** Let deterministic tools, scripts,
   tests, and parsers handle routing, retries, transforms, and checks.
6. **Respect token budgets.** Default budget is 4,000 tokens per task and
   30,000 per session; if a run approaches or breaches it, say so, summarize,
   and restart with the compact state.
7. **Surface conflicts.** When patterns or instructions contradict, choose the
   more recent, tested, or local authority and name the rejected alternative.
8. **Read before writing.** Inspect exports, immediate callers, shared
   utilities, and nearby tests before editing.
9. **Tests verify intent.** Tests should encode why the behavior matters, not
   only assert incidental output.
10. **Checkpoint significant steps.** Record what changed, what was verified,
    and what remains before moving to the next major step.
11. **Match conventions.** Follow the codebase's local style even when another
    style seems cleaner.
12. **Fail loud.** Never claim completion, passing tests, or skipped work
    without naming what actually happened.

## Capability routing

Use the role and capability schema in `WORKFLOW-CONTRACTS.md`. Review
invocation authorizes independent reviewer roles unless the user forbids them.
Non-review delegation still follows host and user policy. Select
`quick|standard|deep` by risk, preserve required angles, and record `degraded`
when independent execution is unavailable. Never name or require a particular
model, vendor, coding agent, or host-specific agent type.

## 1. Think before coding

Don't assume. Don't hide confusion. Surface tradeoffs.

- **State assumptions explicitly.** If uncertain, ask rather than guess. When
  multiple interpretations are plausible, list them and pick — don't pick
  silently.
- **Push back.** If a simpler approach exists, or the user's instruction
  contradicts an earlier constraint, say so before typing code.
- **Stop when confused.** Name what's unclear in one sentence and ask.
- **Never "just go with it".** A wrong assumption committed to code costs
  more than a clarifying question.

## 2. Simplicity first

Minimum code that solves the problem. Nothing speculative.

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" / configurability that wasn't requested.
- No error handling for impossible scenarios (validate at system boundaries,
  trust internal code).
- If 200 lines could be 50, rewrite it.

**Self-test:** would a senior engineer call this overcomplicated? If yes,
simplify.

## 3. Surgical changes

Touch only what you must. Clean up only your own mess.

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, **mention it, don't delete it**.
- Remove imports / variables / functions that *your* changes made unused —
  not pre-existing dead code.

**Self-test:** every changed line must trace directly to the user's request
or to the architecture doc for this slug.

## 4. Goal-driven execution

Define success criteria. Loop until verified.

Transform imperative tasks into verifiable goals:

| Instead of...        | Transform to...                                          |
|----------------------|----------------------------------------------------------|
| "Add validation"     | "Write tests for invalid inputs, then make them pass"    |
| "Fix the bug"        | "Write a test that reproduces it, then make it pass"     |
| "Refactor X"         | "Ensure tests pass before and after"                     |

For multi-step tasks, state a brief plan with a verification check per step:

```
1. <step> → verify: <check>
2. <step> → verify: <check>
```

Strong success criteria let the agent loop independently. Weak criteria
("make it work") require constant clarification.

## 5. Context is a finite resource

Treat the context window like RAM, not a hard drive. Performance degrades as
it fills — this is not a prompt problem, it's a token problem.

- **Verify over vibe.** Every non-trivial change needs a check a *different*
  system can run: tests, linter, typechecker, screenshot diff. If you can't
  verify it, don't claim it's done.
- **Address root cause, not symptom.** Don't suppress the error, silence the
  test, or paper over the failure. Find why it happened.
- **Clear between unrelated tasks.** A long session polluted with prior
  corrections is worse than a fresh session with a better prompt.
- **Delegate exploration.** Broad "investigate X" sweeps should go to a
  subagent — its findings come back summarized, not as a dump of every file
  it read.
- **Don't correct twice and hope.** If the same issue resurfaces after two
  corrections, stop; the failed-approach residue is the problem. Restart
  with a tighter prompt.

**Self-test:** would a fresh session with a clean prompt do better than
continuing this one? If yes, restart.

## Failure patterns to recognize

From [Claude Code best practices](https://code.claude.com/docs/en/best-practices#avoid-common-failure-patterns).
If you notice any of these, name it and course-correct:

- **Kitchen-sink session** — unrelated tasks piled in one thread. Fix: `/clear`.
- **Correcting over and over** — context is full of failed attempts. Fix:
  restart with a prompt that incorporates what you learned.
- **Over-specified memory file** — CLAUDE.md/AGENTS.md so long that rules
  get lost in noise. Fix: ruthless prune; convert hard rules to hooks.
- **Trust-then-verify gap** — plausible-looking code that doesn't handle
  edge cases. Fix: demand a verification signal before accepting.
- **Infinite exploration** — unbounded "investigate" consumes context. Fix:
  scope narrowly or delegate to a subagent.

## Tradeoff

These principles bias toward **caution over speed**. For trivial edits (typo
fix, one-line comment, obvious one-liner), judgment wins — not every change
needs the full rigor. The point is to reduce costly mistakes on non-trivial
work, not to slow down simple tasks.
