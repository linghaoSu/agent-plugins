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
- `<skill or "none">` - <trigger/result/impact>
```
