# Idea-To-Ship Workflow Contracts

Shared contracts for idea-to-ship skills. Skills should cite this file for
cross-cutting runtime behavior while preserving their stage-specific gates.

## Runtime-Aware Review Routing

For design and code review loops:

1. Read `PRINCIPLES.md` before launching a reviewer.
2. Use a runtime-native review sub-agent only when the host permits sub-agents
   and the current user/host policy authorizes delegation.
3. In Claude Code, keep the existing Codex adversarial reviewer
   (`subagent_type: "codex:codex-rescue"`) when available and authorized.
4. Outside Claude Code, do not request Claude-only subagent types. Use the host
   runtime's native sub-agent mechanism for the same `ADVERSARIAL_REVIEWER`
   role only when authorized.
5. If no sub-agent route is available, run the same adversarial prompt in the
   main context and record the fallback reason in the review artifact.
6. If the selected model is unavailable or at capacity, do not keep retrying
   the same model. Continue with the fallback and record the capacity fallback.

The invariant is an independent, skeptical review pass with a recorded route,
not a specific model brand.

## Review Loop Shape

1. Verify required artifacts first. Missing `requirements.md` sends the user
   back to `/brainstorm --slug <slug>`.
2. Collect the current target (`architecture.md` or diff) fresh each iteration.
3. Treat `LGTM` as the clean sentinel.
4. Fix critical and warning findings in scope; skip or record nits unless they
   are trivially co-located.
5. Stop after five iterations unless the user explicitly asks to continue.
6. Run one holistic pass after the incremental loop.
