# Skill Usage Guide

This file is the operator-facing guide for the skills currently shipped by this
plugin marketplace. Use plugin-qualified names in prompts, for example
`$idea-to-ship:brainstorm --slug ITS-123 ...`.

The examples below are prompt text for an agent session, not shell commands.
Read-only skills may still write their documented local report artifact; they
must not mutate target code, git state, GitHub, hooks, or installed tools unless
their entry explicitly says so.

## Common Invocation Pattern

```text
$<plugin>:<skill> [flags] [free-form task notes]
```

- Prefer plugin-qualified names such as `$agent-playbook:tool-review`.
- Use `--slug <name>` when the skill writes artifacts and the work should be
  resumable.
- Use review skills before shipping risky changes; review workflows in this
  repo are adversarial by design.
- Use the owning commit workflow for commits and pushes:
  `$agent-playbook:commit-changes`.

## agent-playbook

Operational hygiene for repos, tools, fast AI-assisted work, and commits.

| Skill | Use When | Typical Prompt | Output / Boundary |
|---|---|---|---|
| `$agent-playbook:bootstrap-project-memory` | A repo needs a compact `CLAUDE.md` and optionally `AGENTS.md` that captures durable agent context. | `$agent-playbook:bootstrap-project-memory --agents-md key repo constraints` | Writes repo memory files only after focused Q&A and diff review; avoids broad docs or discoverable facts. |
| `$agent-playbook:commit-changes` | Finished local changes need a verified commit, and optionally a draft PR when explicitly requested. | `$agent-playbook:commit-changes feat(scope): subject` | Inspects diff, reads repo commit rules, verifies human git identity, runs required gates, commits intended paths only. |
| `$agent-playbook:context-audit` | You need a ranked audit of agent-context hygiene: memories, rules, hooks, tools, MCP sprawl, and verification signals. | `$agent-playbook:context-audit --slug repo-context --scope all` | Read-only against repo behavior; writes `.agent-playbook/<slug>/context-audit.md`. |
| `$agent-playbook:implementation-tournament` | The user explicitly wants competing implementations or a best-of-N patch selection. | `$agent-playbook:implementation-tournament --slug feature-x --candidates 3 goal` | High-cost workflow; creates isolated candidates, verifies each, independently reviews, and records adopt/merge/reject decisions. |
| `$agent-playbook:tool-review` | An agent tool, CLI, MCP server, or schema needs a safety and usability review. | `$agent-playbook:tool-review --slug tool-audit path/to/tool` | Multi-agent read-only review; writes a ranked punch-list focused on boundaries, naming, token cost, errors, and eval hooks. |
| `$agent-playbook:vibe-coding-fix` | A prior vibe-coding health-check produced bounded local fixes to apply. | `$agent-playbook:vibe-coding-fix --slug current --apply` | Mutates only accepted local fixes from the report, verifies each, and routes unsafe/domain-specific work to owning skills. |
| `$agent-playbook:vibe-coding-health-check` | Fast AI-assisted coding needs a quick drift, fragility, and verification control check. | `$agent-playbook:vibe-coding-health-check --slug current --scope diff` | Writes `.agent-playbook/<slug>/vibe-health-check.md`; routes to deeper audits when risk is high. |

## antifragile

Read-only resilience audits with a strict boundary between agent infrastructure
and target application systems.

| Skill | Use When | Typical Prompt | Output / Boundary |
|---|---|---|---|
| `$antifragile:antifragile-agent` | Agent/plugin/hook/skill infrastructure may be fragile: state pollution, missing guards, recovery gaps, or brittle tool boundaries. | `$antifragile:antifragile-agent hooks and skill wrapper focus` | Read-only stdout/conversation audit; not for target application resilience. |
| `$antifragile:antifragile-system` | A target app or service needs resilience review: fallbacks, error handling, data safety, observability, and single points of failure. | `$antifragile:antifragile-system api` | Read-only stdout/conversation audit; not for agent/plugin infrastructure. |

## harness-engineering

Design and audit the harness around long-running or autonomous agents.

| Skill | Use When | Typical Prompt | Output / Boundary |
|---|---|---|---|
| `$harness-engineering:goal-mode` | Work is long-horizon, multi-turn, or needs resumable state and checkpoints. | `$harness-engineering:goal-mode --slug migration finish the migration safely` | Writes `.harness-engineering/<slug>/goal/` state and drives a persistent next-step loop. |
| `$harness-engineering:harness-audit` | An existing autonomous agent or pipeline needs review against harness layers and anti-patterns. | `$harness-engineering:harness-audit --slug agent-audit path/to/agent` | Writes `.harness-engineering/<slug>/harness-audit.md` with prioritized gaps. |
| `$harness-engineering:harness-design` | A new autonomous agent needs its cognition, tools, contracts, orchestration, memory, evaluation, and recovery designed. | `$harness-engineering:harness-design --slug support-agent agent notes` | Writes `.harness-engineering/<slug>/harness-design.md` plus a Day 1 scaffold recommendation. |
| `$harness-engineering:resilience-plan` | A long-horizon agent needs context reset and memory consolidation routines. | `$harness-engineering:resilience-plan --slug long-runner task notes` | Writes `.harness-engineering/<slug>/resilience-plan.md`. |
| `$harness-engineering:sprint-contract` | A generator/evaluator pair needs concrete success criteria before implementation starts. | `$harness-engineering:sprint-contract --slug sprint-1 target output` | Writes `.harness-engineering/<slug>/sprint-contract.md`; favors objective checks over self-judgment. |

## idea-to-ship

End-to-end artifact workflow from fuzzy idea to shipped implementation. For a
new slug, start with `$idea-to-ship:brainstorm`; do not skip directly to
architecture or implementation.

| Skill | Use When | Typical Prompt | Output / Boundary |
|---|---|---|---|
| `$idea-to-ship:brainstorm` | A new idea is vague and needs concrete requirements, constraints, users, risks, and success criteria. | `$idea-to-ship:brainstorm --slug ITS-123 idea text` | Mandatory first stage; writes `.idea-to-ship/<slug>/requirements.md` after Socratic Q&A. |
| `$idea-to-ship:commercialize` | Product, pricing, ICP, GTM, monetization, or roadmap impact needs analysis. | `$idea-to-ship:commercialize --slug ITS-123 pricing notes` | Writes commercialization artifacts and hands evidence to roadmap; does not replace requirements. |
| `$idea-to-ship:architect` | Requirements exist and need architecture alternatives, tradeoffs, and a recommended design. | `$idea-to-ship:architect --slug ITS-123 extra constraints` | Writes `.idea-to-ship/<slug>/architecture.md`; does not write production code. |
| `$idea-to-ship:review-design` | `architecture.md` needs adversarial multi-agent review before implementation. | `$idea-to-ship:review-design --slug ITS-123 concurrency focus` | Writes design review evidence and loops fix/review until clean or budget exhausted. |
| `$idea-to-ship:ui-design` | A product UI needs a buildable interface contract before frontend implementation. | `$idea-to-ship:ui-design --slug ITS-123 --write-design-md` | Writes `.idea-to-ship/<slug>/interface-design.md`; no production code. |
| `$idea-to-ship:tdd` | A stage needs red-first tests before production or behavior-changing implementation. | `$idea-to-ship:tdd --slug ITS-123 --stage 1` | Writes/updates `test-plan.md` and `tdd-log.md`; edits tests and fixtures only, not production code. |
| `$idea-to-ship:implement` | Reviewed architecture is ready to build stage by stage. | `$idea-to-ship:implement --slug ITS-123 stage 1` | Edits local code according to `architecture.md`; logs to `implementation-log.md`; never commits or pushes. |
| `$idea-to-ship:test` | The feature needs a full story-driven test plan and implemented test coverage. | `$idea-to-ship:test --slug ITS-123 edge cases` | Writes/updates test strategy artifacts, implements tests, and runs verification; broader than stage-local TDD. |
| `$idea-to-ship:visual-test` | A frontend change needs visual QA evidence from interface/test contracts. | `$idea-to-ship:visual-test --slug ITS-123 http://localhost:3000` | Writes selector recipes, matrix evidence, RCA, and visual-test reports; does not add production code. |
| `$idea-to-ship:review-code` | Current implementation diff needs adversarial multi-agent code review before shipping. | `$idea-to-ship:review-code --slug ITS-123 security focus` | Loops fix/review across required angles until clean; writes `.idea-to-ship/<slug>/code-review.md`. |
| `$idea-to-ship:roadmap` | A project or slug needs an evidence-backed Now/Next/Later roadmap. | `$idea-to-ship:roadmap --portfolio --include-git --final` | Writes `.idea-to-ship/roadmap.md` or `.idea-to-ship/<slug>/roadmap.md`; roadmap review decisions should remain adversarial. |

## issue-evaluator

GitHub issue and PR workflows. GitHub review skills are read-only on GitHub
unless a skill explicitly says otherwise; local worktrees may be created for
safe inspection or implementation.

| Skill | Use When | Typical Prompt | Output / Boundary |
|---|---|---|---|
| `$issue-evaluator:evaluate-issue` | A GitHub issue URL/number or bug description needs diagnosis and a fix plan. | `$issue-evaluator:evaluate-issue #123` | Reads repo and issue context; produces diagnosis, reproduction notes, and implementation plan. |
| `$issue-evaluator:fix-issue` | A GitHub issue or concrete bug description should be fixed locally. | `$issue-evaluator:fix-issue #123` | Implements in an isolated worktree with scoped staging expectations; no automatic push. |
| `$issue-evaluator:fix-pr-comments` | PR review comments need triage and accepted local fixes. | `$issue-evaluator:fix-pr-comments 45 --include-resolved` | Read-only on GitHub; applies accepted fixes as local unstaged edits and reports rebuttals for rejected comments. |
| `$issue-evaluator:review-fix` | Current local changes need runtime-aware adversarial review/fix looping. | `$issue-evaluator:review-fix concurrency and tests` | Multi-agent review/fix loop for current diff, ending with holistic review. |
| `$issue-evaluator:review-pr` | A GitHub PR needs local multi-agent review for bugs, security, issue coverage, and style. | `$issue-evaluator:review-pr 45` | Read-only on GitHub; output stays in conversation and temporary local worktrees only. |
| `$issue-evaluator:scan-issues` | You want high-value unattended issues to consider. | `$issue-evaluator:scan-issues 2w` | Conversation-only, read-only GitHub scan; never edits issues. |
| `$issue-evaluator:update-code-style` | The repo-specific code style guide should be regenerated from source and PR review comments. | `$issue-evaluator:update-code-style --force` | Writes/updates the local style guide; uses runtime-aware analysis agents. |

## secret-scanner

Credential leak detection and optional local hook installation.

| Skill | Use When | Typical Prompt | Output / Boundary |
|---|---|---|---|
| `$secret-scanner:scan-secrets` | Staged, working, recent, ranged, or full-repo content needs credential scanning. | `$secret-scanner:scan-secrets --mode staged` | Read-only scan; deterministic scanner plus false-positive triage; never rewrites files or history. |
| `$secret-scanner:install-precommit-hook` | A repo should install the secret scanner as a local pre-commit hook. | `$secret-scanner:install-precommit-hook --framework native --abort-on-findings` | Mutates local hook/config files only after overwrite safety; hook installation is opt-in. |

## skill-stats

Skill usage reporting plus guarded skill-cleaner integration.

| Skill | Use When | Typical Prompt | Output / Boundary |
|---|---|---|---|
| `$skill-stats:skill-stats` | You need local skill call counts, stale/unused skill data, or a guarded skill-cleaner report. | `$skill-stats:skill-stats` or `$skill-stats:skill-stats --cleaner --analyzer /path/to/skill-cleaner.ts` | Default usage report is conversation-only. `--cleaner` report mode may write a wrapper-owned temp evidence bundle but does not mutate skill roots. Mutating cleanup requires `--apply`, exact current-session `/plan` approval, and checked plan hash. |

## worktree-cleaner

Safe stale worktree reporting and optional cleanup.

| Skill | Use When | Typical Prompt | Output / Boundary |
|---|---|---|---|
| `$worktree-cleaner:clean-worktrees` | Git worktrees may be stale after PR merge/closure, or no-PR worktrees need review. | `$worktree-cleaner:clean-worktrees` or `$worktree-cleaner:clean-worktrees --apply --all` | Dry-run by default. Removal requires `--apply`, safety summary review, and confirmation; `--force` is only for explicitly confirmed candidates. |

## Hook-Only Plugins

`auto-updater` has no user-invoked skill. It provides SessionStart update hooks
and scripts for Claude and Codex plugin directories.
