# Implementation Log Template

Use this template when creating or appending
`.idea-to-ship/<slug>/implementation-log.md`.

```markdown
# Implementation Log - <slug>

**Architecture:** architecture.md
**Started:** <YYYY-MM-DD>

## Stage Status
- [ ] Stage 1 - <name>
- [ ] Stage 2 - <name>
- [ ] ...

## Stage <N> - <name>
**Completed:** <YYYY-MM-DD HH:MM>

### Pre-Stage Assumptions
- architecture.md: <assumption checked, or "none beyond the stage contract">
- interface-design.md: <UI assumption checked, "not applicable", or required UI contract path>
- codebase: <current-state assumption verified before editing>

### Success Criteria
- <command, test, or observable behavior that proves this stage is complete>

### Files touched
- `path/to/file.ext` - <what changed, 1 line>

### Decisions made during implementation
- <decision>: <reasoning>

### Deviations from design artifacts
- <none | or: "did X instead of architecture.md/interface-design.md because Z">

### Adjacent issues noticed (NOT fixed here)
- <bullet or "none">

### Verification
- build: ok / fail (fixed: <what>)
- lint: ok / skipped / ...
- tests: N passed, M skipped, 0 failed
- tdd: `tdd-log.md` entry <timestamp>, failing test then passed (`<command>`) / not applicable (`<reason>`)

### Cross-Skill Checks
| Skill | Trigger | Result | Impact |
|---|---|---|---|
| `<skill or "none">` | <why it applied, or "no trigger"> | <ran/skipped/recommended and outcome> | <fix/follow-up/no impact> |
```
