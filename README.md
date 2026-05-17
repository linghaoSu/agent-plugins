# Agent Plugins Linghao

Local plugin marketplace for agent workflows. The marketplace membership lives
in `.claude-plugin/marketplace.json`; operational status and release checks live
in `PORTFOLIO.md`.

## Release Checks

Run the release gate before committing or publishing plugin changes:

```bash
scripts/release-gate.sh --mode staged
scripts/release-gate.sh --mode all --strict
```

See `RELEASE-GATE.md` for mode details.

`--strict` turns advisory skill hygiene and eval fixture regressions into
blocking failures. In `staged` and `working` mode, the gate also runs the
agent-playbook or idea-to-ship fixture suite when the corresponding plugin or
fixture files are touched.

## Naming And Boundaries

Use plugin-qualified names in docs and handoffs, for example
`$agent-playbook:tool-review` and `$issue-evaluator:review-pr`.

For new flat/global skill names, use `<domain>-<verb>` or `<resource>-<verb>`
so the responsibility is obvious without plugin context. Existing public
entries keep their current names for compatibility.

Every read-only skill must say what "read-only" means: no target mutation, no
GitHub mutation, no git mutation, and whether it writes a local artifact. Skills
that read large diffs, comments, logs, or repo-wide data must declare token
budgets and report `truncated: true` when caps are hit.

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
| [`antifragile-agent`](antifragile/skills/antifragile-agent/SKILL.md) | Read-only stdout audit of agent/plugin/hook/skill infrastructure: guards, state pollution, recovery, and tool fragility. Not for target app resilience. |
| [`antifragile-system`](antifragile/skills/antifragile-system/SKILL.md) | Read-only stdout audit of a target application/system for resilience gaps such as weak fallbacks, unsafe state, missing observability, and single points of failure. Not for agent infrastructure. |

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
| [`tdd`](idea-to-ship/skills/tdd/SKILL.md) | Create a stage-local red-first gate before `/implement`, or explicitly backfill missing tests. Writes test evidence only; not the full story test plan. |
| [`test`](idea-to-ship/skills/test/SKILL.md) | Produce the full story-driven test plan from stories, acceptance criteria, and scenario matrices, then implement and run tests. Not a stage-local red-first gate. |
| [`ui-design`](idea-to-ship/skills/ui-design/SKILL.md) | Design the UI/UX contract from requirements, architecture, existing UI, design-system evidence, and structured visual references. |
| [`visual-test`](idea-to-ship/skills/visual-test/SKILL.md) | Run artifact-first frontend visual QA from interface-design/test-plan contracts, producing selector recipes, matrix evidence, bounded RCA, and visual-test reports. |

### issue-evaluator

| Skill | Purpose |
|---|---|
| [`evaluate-issue`](issue-evaluator/skills/evaluate-issue/SKILL.md) | Evaluate a GitHub issue or free-form bug description against the current repo and produce diagnosis plus fix plan. |
| [`fix-issue`](issue-evaluator/skills/fix-issue/SKILL.md) | Implement a GitHub issue fix in an isolated worktree with scoped staging; stops if worktree setup fails. |
| [`fix-pr-comments`](issue-evaluator/skills/fix-pr-comments/SKILL.md) | Triage PR review comments, apply accepted fixes as local unstaged edits, and run multi-agent review. |
| [`review-fix`](issue-evaluator/skills/review-fix/SKILL.md) | Multi-agent review/fix loop for current code changes, ending with a holistic review. |
| [`review-pr`](issue-evaluator/skills/review-pr/SKILL.md) | Local multi-agent PR review for bugs, security, issue coverage, and repo-specific style. |
| [`scan-issues`](issue-evaluator/skills/scan-issues/SKILL.md) | Conversation-only read-only scan for high-value unattended GitHub issues. |
| [`update-code-style`](issue-evaluator/skills/update-code-style/SKILL.md) | Regenerate the repo-specific code style guide from source and PR review comments. |

### secret-scanner

| Skill | Purpose |
|---|---|
| [`install-precommit-hook`](secret-scanner/skills/install-precommit-hook/SKILL.md) | Install the secret scanner as a local git pre-commit hook, with overwrite safety. |
| [`scan-secrets`](secret-scanner/skills/scan-secrets/SKILL.md) | Scan staged, working, recent, ranged, or full-repo content for leaked credentials. |

### skill-stats

| Skill | Purpose |
|---|---|
| [`skill-stats`](skill-stats/skills/skill-stats/SKILL.md) | Conversation-only read of local skill usage statistics: call counts, last-used time, unused skills, and truncation status. Never edits logs or hooks. |

### worktree-cleaner

| Skill | Purpose |
|---|---|
| [`clean-worktrees`](worktree-cleaner/skills/clean-worktrees/SKILL.md) | Report stale git worktrees with PR and local-change safety checks; dry-run by default and requires `--apply` plus confirmation before removal. |

## Hook-Only Plugins

`auto-updater` currently provides hooks and scripts rather than user-invoked
skills.
