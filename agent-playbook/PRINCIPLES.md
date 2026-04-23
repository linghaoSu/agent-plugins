# Agent-Playbook Principles

Shared principles every skill in this plugin applies. These are the
load-bearing claims from the best-practice literature — anything that
survives across Cursor, Claude Code, Codex, and Anthropic engineering.

If you are a skill: read this file once before auditing, reviewing, or
writing a memory file. Cite it when you recommend a change.

## 1. Context is finite and rots

Performance degrades as the window fills. Architectural cost is n² in
pairwise relationships between tokens, so "just load more" is not free.

- **Prune aggressively.** CLAUDE.md/AGENTS.md should target <200 lines;
  if Claude already does the right thing without an instruction, delete
  the instruction.
- **Just-in-time retrieval.** Keep identifiers (paths, URLs, query keys)
  and let the agent fetch on demand, rather than preloading everything.
- **Fresh context beats long context.** For unrelated tasks, `/clear`;
  for investigation, delegate to a subagent so findings come back as a
  summary.

Source: [Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents),
[Claude Code best practices](https://code.claude.com/docs/en/best-practices).

## 2. Explore → Plan → Code → Verify

Skipping exploration or planning produces plausible-looking code that
solves the wrong problem. Skipping verification ships it.

- **Plan mode, saved plans.** For anything multi-file or unfamiliar,
  separate planning from execution. Save the plan (Cursor writes to
  `.cursor/plans/`, Claude Code uses Plan Mode, Codex uses Plan mode).
- **Verification signal on every loop.** Tests, typechecker, linter,
  screenshot diff. If you can't verify it, don't claim it's done.
- **Root cause, not symptom.** When a build fails, fix the cause; never
  suppress the error or silence the test.

Source: [Cursor best practices](https://cursor.com/blog/agent-best-practices),
[Claude Code best practices](https://code.claude.com/docs/en/best-practices#explore-first-then-plan-then-code).

## 3. Persistent memory beats re-explaining

Things the agent cannot discover by reading code — build commands, house
conventions, env quirks, repo etiquette — belong in a memory file, not
in every prompt.

- **One fact, one place.** Hierarchy: global (`~/.claude/CLAUDE.md`,
  `~/.codex/AGENTS.md`) → project root → subdirectory overrides.
- **Specific and verifiable.** "Use 2-space indentation" beats "format
  nicely"; "run `pnpm test --filter X` before commit" beats "test your
  changes".
- **Move sometimes-relevant content to skills or `.claude/rules/`.**
  CLAUDE.md loads every session; a skill loads on demand.
- **Prune on a cadence.** A 500-line CLAUDE.md is worse than a 50-line
  one: important rules get lost in noise.

Source: [Claude Code memory docs](https://code.claude.com/docs/en/memory),
[Codex AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md/).

## 4. Tools are a contract, not a wrapper

A tool is what the non-deterministic agent sees of your deterministic
system. Design it for the agent, not for convenience of exposure.

- **Fewer, consolidated tools.** One `schedule_event` beats three
  separate `list_users`/`list_events`/`create_event` tools.
- **Namespace.** `asana_search`, `asana_projects_search` — prevents
  cross-service ambiguity.
- **Token-efficient returns.** Paginate, filter, and offer a
  `response_format` enum (`concise|detailed`). Anthropic caps tool
  responses at 25k tokens for Claude Code.
- **Errors that guide.** Return a sentence, not an opaque code.
- **CLI before MCP.** If a CLI already covers the capability, prefer
  it — CLIs compose and do not permanently occupy context. Reserve
  MCP for genuinely stateful/complex protocols (browser automation,
  database sessions).

Source: [Anthropic writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents),
[Peekaboo 2.0](https://steipete.me/posts/2025/peekaboo-2-freeing-the-cli-from-its-mcp-shackles).

## 5. Prefer simple composable patterns over frameworks

Most production agents are single LLM calls plus a verification loop. Of
the rest, most are prompt chaining or routing. Full-autonomy agents are
expensive and error-compounding — use them only when steps cannot be
hardcoded.

The six patterns (prompt chaining, routing, parallelization, orchestrator-
workers, evaluator-optimizer, agent) exist to give you names. Start at the
simplest one that solves the problem.

Source: [Anthropic building effective agents](https://www.anthropic.com/research/building-effective-agents).

## 6. Verification must come from outside the model

Self-review in the same context is biased toward what just got produced.
Objective verifiers (compilers, tests, schema validators, browser
automation) are strictly better than LLM-as-judge for anything non-
subjective. When you need a second opinion, use a *fresh* context — a
subagent or a different session.

Source: [Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents),
[harness-engineering PRINCIPLES](../harness-engineering/README.md).

## Anti-patterns (name them when you see them)

| Name | Symptom | Fix |
|------|---------|-----|
| Kitchen-sink session | Unrelated tasks in one thread; context full of irrelevant reads | `/clear` between tasks |
| Correcting over and over | Same issue re-fixed 3+ times; prior failed attempts pollute context | Restart with a tighter prompt |
| Over-specified memory | CLAUDE.md > 200 lines; rules ignored | Prune; convert hard rules to hooks |
| Trust-then-verify gap | Plausible code that breaks on edges | Demand a test/screenshot/lint signal |
| Infinite exploration | Unbounded "investigate X" fills context | Scope narrowly; delegate to subagent |
| Framework bloat | Abstraction layers hide the prompt | Drop to direct API calls until you know what you need |
| MCP sprawl | 20 MCPs loaded; half duplicate CLIs | Prefer CLI; keep MCP only where protocol justifies it |

Source: [Claude Code failure patterns](https://code.claude.com/docs/en/best-practices#avoid-common-failure-patterns),
[Anthropic building effective agents](https://www.anthropic.com/research/building-effective-agents).
