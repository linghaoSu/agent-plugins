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
cite it. Shared output, token, error, safety, and evaluation contracts live in
[`WORKFLOW-CONTRACTS.md`](./WORKFLOW-CONTRACTS.md).

## Commands

### `/workflow-router [goal, issue, PR, audit, cleanup, or "which workflow?"]`
Start here when the owning capability is unclear. Produces a conversation-only
route card with `recommended_workflow`, `steps`, `required_inputs`,
`mutation_points`, `stop_conditions`, and `next_prompt`. It does not execute
downstream skills or mutate code, git, GitHub, hooks, or installed tools.

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

### `/tool-review [--slug <name>] [--review-depth quick|standard|deep] <tool-name or path>`
Review a tool, CLI, or MCP definition against Anthropic's tool-writing
principles: boundary clarity, consolidation, namespacing, token-efficient
returns, error messages that guide, evaluation hooks. By default it auto-selects
`quick`, `standard`, or `deep` from tool risk; pass `--review-depth` to force a
tier. `deep` keeps the full multi-agent, multi-angle, multi-round review.
Produces a ranked punch-list that records the selected intensity and whether it
was automatic or forced.

### `/vibe-coding-health-check [--scope diff|repo|agent|all] [--deep]`
Run a lightweight control check after fast AI-assisted coding. Scores the
current diff or repo for scope drift, missing requirement/test traceability,
resilience gaps, harness/state/recovery gaps, and agent-context hygiene. Routes
to the right deeper audit: `idea-to-ship`, `antifragile`, `harness-engineering`,
or `context-audit`.

Contract coverage for this workflow lives in
`tests/agent-playbook-eval-fixtures.sh`.

### `/vibe-coding-fix [--slug <name>] [--dry-run|--apply]`
Consumes `.agent-playbook/<slug>/vibe-health-check.md`, classifies every
finding, applies safe local cleanup when explicitly authorized, and writes
`.agent-playbook/<slug>/vibe-fix-log.md`. It routes domain-specific or unsafe
work to the owning skill instead of becoming a generic autopilot.

### `/implementation-tournament [--slug <name>] [--candidates N]`
Runs an explicit best-of-N implementation tournament. It creates isolated
candidate worktrees, asks independent workers to implement the same fixed
contract, verifies every candidate with the same checks, runs independent
review angles, and adopts, merges, or rejects candidates with reasons. This is
optional high-cost mode used by workflows such as `idea-to-ship/implement` and
`issue-evaluator/fix-issue` only when the user asks for competing
implementations.

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
  mutate your repo or external systems, but they may write their documented
  local report artifacts. `/workflow-router` is conversation-only and writes no
  route artifact. `/bootstrap-project-memory` writes only after showing you the
  proposed file. `/vibe-coding-fix` applies only bounded local cleanup from a
  prior health check when explicitly authorized.
  `/implementation-tournament` mutates only when explicitly invoked: it creates
  isolated candidate worktrees and applies the selected patch back to the
  caller worktree, but it does not commit or push. `/commit-changes` mutates
  git history and creates GitHub draft PRs only when the user asks and the
  repo's checks pass.
- **Cite sources.** Every recommendation points at the specific article
  and section so you can sanity-check before applying.
