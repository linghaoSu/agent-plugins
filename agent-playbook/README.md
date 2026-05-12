# agent-playbook

A plugin that turns the best-practice literature for coding agents into
concrete, repo-level actions you can run.

Where `harness-engineering` is *design-time* (scaffolding a new agent) and
`idea-to-ship` is *flow-time* (taking one feature from idea to ship),
`agent-playbook` is *operator-time*: configuring your repo, reviewing
your tools, and handling repo-specific commit / draft PR hygiene so agents
work reliably day-to-day.

## Source material

Synthesized from:

- [Cursor — Best practices for coding with agents](https://cursor.com/blog/agent-best-practices)
- [Claude Code — Best Practices](https://code.claude.com/docs/en/best-practices)
- [Claude Code — How Claude remembers your project](https://code.claude.com/docs/en/memory)
- [OpenAI Codex — Best practices](https://developers.openai.com/codex/learn/best-practices/)
- [OpenAI Codex — AGENTS.md](https://developers.openai.com/codex/guides/agents-md/)
- [Anthropic — Building effective AI agents](https://www.anthropic.com/research/building-effective-agents)
- [Anthropic — Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Anthropic — Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [GitHub Copilot — Best practices](https://docs.github.com/en/copilot/get-started/best-practices)
- Peter Steinberger: [vibe coding](https://steipete.me/posts/2025/the-future-of-vibe-coding),
  [essential reading](https://steipete.me/posts/2025/essential-reading),
  [understanding codebases](https://steipete.me/posts/2025/understanding-codebases-with-ai-gemini-workflow),
  [Peekaboo 2.0 (CLI > MCP)](https://steipete.me/posts/2025/peekaboo-2-freeing-the-cli-from-its-mcp-shackles).

Distilled principles live in [`PRINCIPLES.md`](./PRINCIPLES.md). All skills
cite it.

## Commands

### `/bootstrap-project-memory [notes]`
Create or refine `CLAUDE.md` (and optionally `AGENTS.md`) for the current
repo via Socratic Q&A. Produces a short, specific, under-200-line memory
file keyed to *what agents cannot discover by reading code*: bash commands,
house conventions, env quirks, repo etiquette. Never dumps architecture or
self-evident style rules.

### `/context-audit [focus]`
Audit the repo's agent-context hygiene: CLAUDE.md/AGENTS.md size and
specificity, `.claude/rules/` layout, hook usage, tool sprawl, redundant
MCPs, and common failure patterns (over-specified memory, kitchen-sink
history). Writes a report with ranked fixes.

### `/tool-review <tool-name or path>`
Review a tool, CLI, or MCP definition against Anthropic's tool-writing
principles: boundary clarity, consolidation, namespacing, token-efficient
returns, error messages that guide, evaluation hooks. Produces a ranked
punch-list.

### `/vibe-coding-health-check [--scope diff|repo|agent|all] [--deep]`
Run a lightweight control check after fast AI-assisted coding. Scores the
current diff or repo for scope drift, missing requirement/test traceability,
resilience gaps, harness/state/recovery gaps, and agent-context hygiene. Routes
to the right deeper audit: `idea-to-ship`, `antifragile`, `harness-engineering`,
or `context-audit`.

Contract coverage for this workflow lives in
`tests/agent-playbook-eval-fixtures.sh`.

### `/commit-changes [message, scope, or draft PR request]`
Create a local git commit after reading the current repo's commit
requirements. Verifies the intended diff, runs required pre-commit checks,
and commits with only the human user's Git author/committer identity. When
asked to open a PR, reads the project's PR template and uses `gh pr create
--draft` with a filled body file. Never adds AI co-author or generated-by
trailers.

## Conventions

- **Artifact-first.** Reports land under `.agent-playbook/<slug>/` so you
  can diff changes over time. Default slug: `current`.
- **Read-only by default.** `/context-audit` and `/tool-review` never
  mutate your repo; `/bootstrap-project-memory` writes only after showing
  you the proposed file. `/commit-changes` mutates git history and creates
  GitHub draft PRs only when the user asks and the repo's checks pass.
- **Cite sources.** Every recommendation points at the specific article
  and section so you can sanity-check before applying.
