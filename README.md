# Agent Plugins Linghao

Local marketplace for focused agent workflows. Plugin membership lives in
`.claude-plugin/marketplace.json`; release checks and ownership live in
`PORTFOLIO.md`. See `SKILLS.md` for triggers, examples, artifacts, and mutation
boundaries.

## Release checks

```bash
scripts/release-gate.sh --mode staged
scripts/release-gate.sh --mode all --strict
```

Skill authoring favors short routing descriptions, SKILL.md bodies under 150
lines, conditional references, deterministic scripts, explicit mutation gates,
and host-neutral capability roles.

## Skill catalog

### agent-playbook

- [`bootstrap-project-memory`](agent-playbook/skills/bootstrap-project-memory/SKILL.md)
- [`commit-changes`](agent-playbook/skills/commit-changes/SKILL.md)
- [`context-audit`](agent-playbook/skills/context-audit/SKILL.md)
- [`implementation-tournament`](agent-playbook/skills/implementation-tournament/SKILL.md)
- [`tool-review`](agent-playbook/skills/tool-review/SKILL.md)

### antifragile

- [`antifragile-audit`](antifragile/skills/antifragile-audit/SKILL.md)

### harness-engineering

- [`goal-mode`](harness-engineering/skills/goal-mode/SKILL.md)
- [`harness`](harness-engineering/skills/harness/SKILL.md)

### idea-to-ship

- [`architect`](idea-to-ship/skills/architect/SKILL.md)
- [`brainstorm`](idea-to-ship/skills/brainstorm/SKILL.md)
- [`grill`](idea-to-ship/skills/grill/SKILL.md)
- [`implement`](idea-to-ship/skills/implement/SKILL.md)
- [`review`](idea-to-ship/skills/review/SKILL.md)
- [`roadmap`](idea-to-ship/skills/roadmap/SKILL.md)
- [`test`](idea-to-ship/skills/test/SKILL.md)
- [`ui-design`](idea-to-ship/skills/ui-design/SKILL.md)
- [`visual-test`](idea-to-ship/skills/visual-test/SKILL.md)

### issue-evaluator

- [`evaluate-issue`](issue-evaluator/skills/evaluate-issue/SKILL.md)
- [`fix-issue`](issue-evaluator/skills/fix-issue/SKILL.md)
- [`fix-pr-comments`](issue-evaluator/skills/fix-pr-comments/SKILL.md)
- [`review-fix`](issue-evaluator/skills/review-fix/SKILL.md)
- [`review-pr`](issue-evaluator/skills/review-pr/SKILL.md)
- [`scan-issues`](issue-evaluator/skills/scan-issues/SKILL.md)

### focused utilities

- [`install-precommit-hook`](secret-scanner/skills/install-precommit-hook/SKILL.md)
- [`scan-secrets`](secret-scanner/skills/scan-secrets/SKILL.md)
- [`skill-stats`](skill-stats/skills/skill-stats/SKILL.md)
- [`clean-worktrees`](worktree-cleaner/skills/clean-worktrees/SKILL.md)

`auto-updater` remains hook-only.
