# Skill Usage Guide

Use plugin-qualified names. Review depth (`quick|standard|deep`) describes
workflow risk, while delegated roles use host-neutral
`routine|reasoning|critical` capabilities.

| Skill | Use when | Example | Mutation boundary |
|---|---|---|---|
| `$agent-playbook:bootstrap-project-memory` | Repo instructions lack non-obvious commands or gotchas | `$agent-playbook:bootstrap-project-memory --agents-md` | Writes approved repo instruction files |
| `$agent-playbook:commit-changes` | Completed work should be committed or published as a draft PR | `$agent-playbook:commit-changes` | Stages/commits; pushes/PR only when requested |
| `$agent-playbook:context-audit` | Agent memory, rules, hooks, or tools are bloated/conflicting | `$agent-playbook:context-audit --slug current` | Writes one local audit artifact |
| `$agent-playbook:implementation-tournament` | User explicitly wants competing implementations | `$agent-playbook:implementation-tournament --slug option-test` | Isolated patches; applies winner only within authorization |
| `$agent-playbook:tool-review` | One CLI/MCP/tool/schema needs risk review | `$agent-playbook:tool-review --review-depth standard tool/path` | Read-only on target; writes one report |
| `$antifragile:antifragile-audit` | App or agent infrastructure needs resilience analysis | `$antifragile:antifragile-audit --scope system` | Read-only stdout report |
| `$harness-engineering:harness` | Design/audit/recovery/acceptance scaffolding is needed | `$harness-engineering:harness --mode design --slug worker` | Writes selected harness artifact only |
| `$harness-engineering:goal-mode` | Long work needs persistent verified state | `$harness-engineering:goal-mode --slug migration objective` | Writes goal state/log/handoff |
| `$idea-to-ship:brainstorm` | A vague idea needs batch requirement discovery | `$idea-to-ship:brainstorm --slug feature` | Writes requirements artifact |
| `$idea-to-ship:grill` | Existing plan/design needs one-decision-at-a-time pressure | `$idea-to-ship:grill --slug feature --with-docs` | Conversation-only by default; flag permits domain docs |
| `$idea-to-ship:architect` | Approved requirements need architecture | `$idea-to-ship:architect --slug feature` | Writes architecture only |
| `$idea-to-ship:roadmap` | Evidence-backed prioritization is needed | `$idea-to-ship:roadmap --commercial --slug portfolio` | Writes roadmap/commercial artifacts |
| `$idea-to-ship:ui-design` | UI requirements need an implementation contract | `$idea-to-ship:ui-design --slug feature` | Writes interface design only |
| `$idea-to-ship:implement` | One approved architecture stage should be built | `$idea-to-ship:implement --slug feature --stage 1` | Local code/tests/log; no commit/push |
| `$idea-to-ship:test` | Need red gate, full story tests, or backfill | `$idea-to-ship:test --mode gate --slug feature` | Tests/artifacts only in gate; tests may change in other modes |
| `$idea-to-ship:review` | Architecture or implementation needs risk review | `$idea-to-ship:review --target code --review-depth standard` | Approved severe repairs only |
| `$idea-to-ship:visual-test` | UI states need artifact-first visual QA | `$idea-to-ship:visual-test --slug feature` | Visual evidence/artifacts; no baseline self-approval |
| `$issue-evaluator:evaluate-issue` | Issue/bug needs diagnosis and fix-ready plan | `$issue-evaluator:evaluate-issue #123` | Read-only on production code/GitHub |
| `$issue-evaluator:fix-issue` | Confirmed issue should be fixed in isolation | `$issue-evaluator:fix-issue #123` | Isolated local fix and commit; no push |
| `$issue-evaluator:review-pr` | GitHub PR needs local read-only review | `$issue-evaluator:review-pr 123` | No GitHub or code mutation |
| `$issue-evaluator:review-fix` | Current local fix needs review/approved repair | `$issue-evaluator:review-fix --review-depth standard` | Local approved repairs; no commit/push |
| `$issue-evaluator:fix-pr-comments` | PR comments need triage and selected local fixes | `$issue-evaluator:fix-pr-comments 123` | GitHub read-only; approved local uncommitted edits |
| `$issue-evaluator:scan-issues` | Find high-value unclaimed GitHub issues | `$issue-evaluator:scan-issues --days 30` | GitHub read-only |
| `$secret-scanner:scan-secrets` | Changed/history content needs credential scanning | `$secret-scanner:scan-secrets --working` | Strictly read-only |
| `$secret-scanner:install-precommit-hook` | Install repo-local secret prevention | `$secret-scanner:install-precommit-hook --native` | Explicit repo-local hook/config writes |
| `$skill-stats:skill-stats` | Inspect skill usage or cleanup candidates | `$skill-stats:skill-stats` | Read-only unless exact apply plan is approved |
| `$worktree-cleaner:clean-worktrees` | Report/remove stale worktrees safely | `$worktree-cleaner:clean-worktrees --apply` | Dry-run default; confirmed normal removals only |
