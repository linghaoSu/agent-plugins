# Code Principles — issue-evaluator

Shared principles every skill in this plugin that writes or reviews code must
apply. Inspired by [Karpathy's observations](https://x.com/karpathy/status/2015883857489522876)
on LLM coding pitfalls.

If you are a skill: read this file once before writing or reviewing any code.
Cite it when you push back on a reviewer comment, an issue description, or a
fix plan that violates it.

## 1. Think before coding

Don't assume. Don't hide confusion. Surface tradeoffs.

- **State assumptions explicitly** in the fix plan before making changes.
- **Push back** on the issue / comment if the requested change is based on a
  wrong premise (e.g. the reviewer misread the code, the issue describes
  behavior that doesn't reproduce).
- **Stop when confused.** If the root cause isn't clear, say so — don't guess
  your way into a fix.
- For issues: if the description is ambiguous, ask clarifying questions
  before writing code. For PR review comments: if the reviewer's claim is
  unclear, mark it `NEEDS_HUMAN` — do not guess.

## 2. Simplicity first

Minimum code that solves the reported problem. Nothing speculative.

- Fix exactly what the issue describes, not adjacent concerns.
- No new abstractions, config knobs, or "flexibility" the issue didn't ask
  for.
- No defensive error handling for impossible states.
- If a 5-line fix works, do not submit a 50-line fix.

## 3. Surgical changes

Touch only what you must.

- Don't improve adjacent code, comments, or formatting while you're "in the
  area".
- Don't refactor unrelated code.
- Match the repo's style (see `code-style.md` for this repo), even if you'd
  do it differently.
- Every changed line must trace to the issue being fixed or to a reviewer
  comment with a cited thread id.
- Pre-existing dead code stays. Mention it in the summary if you want — do
  not delete it.

## 4. Goal-driven execution

Define success criteria before coding. Loop until verified.

- **Before fixing:** state the verifiable behavior that defines "done" (e.g.
  "test `test_login_401_retry` passes", "issue's reproduction steps no longer
  reproduce the bug").
- **Prefer test-first:** write a failing test that captures the issue, then
  make it pass. This transforms "fix the bug" into an objective goal.
- **Verify, don't claim.** Run the test / reproduce the issue / check the
  behavior. Don't report "fixed" based on reasoning alone.

## Rebuttal discipline (issue-evaluator-specific)

When rejecting a reviewer comment or disputing an issue premise:

- Cite the actual code (file:line).
- State the concrete failure mode the reviewer feared and why it doesn't
  apply here.
- No emotional / evaluative framing ("I think this is fine"). Facts only.
- If the rebuttal takes more than 5 sentences, your reasoning is probably
  weak — either fold and accept the change or dig for harder evidence.

## Tradeoff

These principles bias toward **caution over speed**. For trivial fixes
(typo, one-line nit), judgment wins — not every change needs full rigor.
