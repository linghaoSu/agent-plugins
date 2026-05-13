# Code Principles — issue-evaluator

Shared principles every skill in this plugin that writes or reviews code must
apply. Inspired by [Karpathy's observations](https://x.com/karpathy/status/2015883857489522876)
on LLM coding pitfalls.

If you are a skill: read this file once before writing or reviewing any code.
Cite it when you push back on a reviewer comment, an issue description, or a
fix plan that violates it.

## Multi-agent review routing

Do not assume the host runtime is Claude Code.

- **Claude Code runtime:** keep the existing model split when available:
  Opus for load-bearing analysis/synthesis, Sonnet for broad analysis or
  mechanical execution, Haiku for an independent lightweight check, and Codex
  (`codex:codex-rescue`) for adversarial review.
- **Non-Claude runtime:** do not request Claude model names or Claude-only
  `subagent_type` values. Use the host's native sub-agent mechanism instead
  and preserve the same review roles: primary analysis, independent second
  opinion, adversarial review, executor, and final synthesis. Label outputs by
  role rather than model name.
- **Review delegation is pre-authorized:** invoking a review workflow is
  standing authorization to launch multiple reviewer and synthesis sub-agents.
  Do not ask for fresh multi-agent authorization and do not use its absence as
  a reason to review in the main context.
- **Review means multi-agent, multi-angle, multi-round by default:** every
  review workflow must preserve distinct reviewer angles such as
  correctness/security, repo style/scope, and issue/test/plan traceability,
  and must rerun the required angles after fixes or touchups.
- Fall back to same-context review only when reviewer sub-agents are
  explicitly unsupported by the host/runtime, the user explicitly forbids
  reviewer sub-agents, or the selected reviewer/model is explicitly unavailable
  or at capacity. Record `degraded-same-context-review` and the exact reason,
  and do not present the result as independent multi-agent review. Degraded
  mode still preserves the same angles and rounds; it only loses independent
  agents.
- Non-review analysis or executor phases may use a degraded main-context
  fallback only when the skill explicitly defines one, and must record the loss
  of independent validation.

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
