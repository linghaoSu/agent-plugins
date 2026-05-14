# Agent Plugins Linghao

Local plugin marketplace for agent workflows. The marketplace membership lives
in `.claude-plugin/marketplace.json`; operational status and release checks live
in `PORTFOLIO.md`.

## Release Checks

Run the release gate before committing or publishing plugin changes:

```bash
scripts/release-gate.sh --mode staged
scripts/release-gate.sh --mode all
```

See `RELEASE-GATE.md` for mode details.

## Skill Catalog

Use skills through their plugin-qualified names, for example
`$idea-to-ship:brainstorm` or `$issue-evaluator:review-pr`.

### agent-playbook

| Skill | Purpose |
|---|---|
| [`bootstrap-project-memory`](agent-playbook/skills/bootstrap-project-memory/SKILL.md) | Create or refine repo agent memory such as `CLAUDE.md` and optional `AGENTS.md` through focused Q&A. |
| [`commit-changes`](agent-playbook/skills/commit-changes/SKILL.md) | Verify the intended diff, run repo commit checks, create a local commit, and optionally open a draft PR. |
| [`context-audit`](agent-playbook/skills/context-audit/SKILL.md) | Audit agent-context hygiene: repo memories, rules, hooks, MCP/tool sprawl, and verification signals. |
| [`implementation-tournament`](agent-playbook/skills/implementation-tournament/SKILL.md) | Run an explicit best-of-N implementation tournament with isolated candidates, shared verification, independent review, and adopt/merge/reject decisions. |
| [`tool-review`](agent-playbook/skills/tool-review/SKILL.md) | Multi-agent review of an agent tool, CLI, or MCP server for boundaries, naming, token cost, errors, safety, and eval hooks. |
| [`vibe-coding-fix`](agent-playbook/skills/vibe-coding-fix/SKILL.md) | Apply bounded local fixes from a vibe-coding health-check report, then verify. |
| [`vibe-coding-health-check`](agent-playbook/skills/vibe-coding-health-check/SKILL.md) | Audit a repo or current diff after fast AI-assisted coding for drift, fragility, missing verification, and context/tool hygiene. |

### antifragile

| Skill | Purpose |
|---|---|
| [`antifragile-agent`](antifragile/skills/antifragile-agent/SKILL.md) | Audit agent plugin, hook, and skill infrastructure for robustness gaps. |
| [`antifragile-system`](antifragile/skills/antifragile-system/SKILL.md) | Audit a target project for resilience gaps such as weak fallbacks, unsafe state, missing observability, and single points of failure. |

### harness-engineering

| Skill | Purpose |
|---|---|
| [`goal-mode`](harness-engineering/skills/goal-mode/SKILL.md) | Run long-horizon work as a checkpointed goal loop with externalized state and resumable next steps. |
| [`harness-audit`](harness-engineering/skills/harness-audit/SKILL.md) | Audit an existing autonomous agent or pipeline against the 7-layer harness stack and common anti-patterns. |
| [`harness-design`](harness-engineering/skills/harness-design/SKILL.md) | Design a 7-layer harness for a new autonomous agent, including a concrete Day 1 scaffold. |
| [`resilience-plan`](harness-engineering/skills/resilience-plan/SKILL.md) | Design context reset and memory consolidation routines for long-horizon agents. |
| [`sprint-contract`](harness-engineering/skills/sprint-contract/SKILL.md) | Draft a testable contract between a generator agent and an independent evaluator. |

### idea-to-ship

| Skill | Purpose |
|---|---|
| [`architect`](idea-to-ship/skills/architect/SKILL.md) | Turn brainstormed requirements into an architecture document with alternatives, tradeoffs, and a recommendation. |
| [`brainstorm`](idea-to-ship/skills/brainstorm/SKILL.md) | Mandatory first stage that turns a vague idea into a concrete `requirements.md`. |
| [`commercialize`](idea-to-ship/skills/commercialize/SKILL.md) | Expand fuzzy product ideas into commercial scenarios, run skeptical multi-angle commercialization review, and produce roadmap inputs. |
| [`implement`](idea-to-ship/skills/implement/SKILL.md) | Implement `architecture.md` stage by stage, requiring TDD evidence, stopping before missing UI design contracts, and optionally routing `--compete` to implementation tournament. |
| [`review-code`](idea-to-ship/skills/review-code/SKILL.md) | Multi-agent, multi-angle, multi-round review/fix loop for the current implementation diff. |
| [`review-design`](idea-to-ship/skills/review-design/SKILL.md) | Multi-agent, multi-angle, multi-round adversarial review of `architecture.md`. |
| [`roadmap`](idea-to-ship/skills/roadmap/SKILL.md) | Build or refresh an evidence-backed Now/Next/Later roadmap for a slug or portfolio. |
| [`tdd`](idea-to-ship/skills/tdd/SKILL.md) | Create failing tests before implementation for a stage, or backfill missing tests for existing code. |
| [`test`](idea-to-ship/skills/test/SKILL.md) | Produce a story-driven test plan, implement tests, and run them until green. |
| [`ui-design`](idea-to-ship/skills/ui-design/SKILL.md) | Design the UI/UX contract from requirements, architecture, existing UI, design-system evidence, and structured visual references. |

### issue-evaluator

| Skill | Purpose |
|---|---|
| [`evaluate-issue`](issue-evaluator/skills/evaluate-issue/SKILL.md) | Evaluate a GitHub issue or free-form bug description against the current repo and produce diagnosis plus fix plan. |
| [`fix-issue`](issue-evaluator/skills/fix-issue/SKILL.md) | Implement a GitHub issue fix from an evaluation report or issue description, optionally routing `--compete` to implementation tournament. |
| [`fix-pr-comments`](issue-evaluator/skills/fix-pr-comments/SKILL.md) | Triage PR review comments, apply accepted fixes as local unstaged edits, and run multi-agent review. |
| [`review-fix`](issue-evaluator/skills/review-fix/SKILL.md) | Multi-agent review/fix loop for current code changes, ending with a holistic review. |
| [`review-pr`](issue-evaluator/skills/review-pr/SKILL.md) | Local multi-agent PR review for bugs, security, issue coverage, and repo-specific style. |
| [`scan-issues`](issue-evaluator/skills/scan-issues/SKILL.md) | Scan the current project for high-value unattended GitHub issues. |
| [`update-code-style`](issue-evaluator/skills/update-code-style/SKILL.md) | Regenerate the repo-specific code style guide from source and PR review comments. |

### secret-scanner

| Skill | Purpose |
|---|---|
| [`install-precommit-hook`](secret-scanner/skills/install-precommit-hook/SKILL.md) | Install the secret scanner as a local git pre-commit hook, with overwrite safety. |
| [`scan-secrets`](secret-scanner/skills/scan-secrets/SKILL.md) | Scan staged, working, recent, ranged, or full-repo content for leaked credentials. |

### skill-stats

| Skill | Purpose |
|---|---|
| [`skill-stats`](skill-stats/skills/skill-stats/SKILL.md) | Display local skill usage statistics, including call counts, last used time, and unused skills. |

### worktree-cleaner

| Skill | Purpose |
|---|---|
| [`clean-worktrees`](worktree-cleaner/skills/clean-worktrees/SKILL.md) | List git worktrees, check PR status, and remove worktrees whose PRs are merged or closed. |

## Hook-Only Plugins

`auto-updater` currently provides hooks and scripts rather than user-invoked
skills.
