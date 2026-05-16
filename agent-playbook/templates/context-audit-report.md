# Context Audit - <repo name>

**Date:** <YYYY-MM-DD>
**Focus:** <full | memory | tools | workflow>
**Contract:** status=<success|needs_user|terminal|degraded>; mode=audit; outputs_written=<this file>; truncated=<true|false>

## Summary

<One paragraph. Top 3 issues, overall hygiene grade: A/B/C/D.>

## Scorecard

| Dimension | Status | Note |
|---|---|---|
| Memory size | ✅/⚠️/❌ | <line count vs. target> |
| Memory specificity | ✅/⚠️/❌ | <example> |
| Path-scoped rules | ✅/⚠️/❌ | ... |
| Tool sprawl | ✅/⚠️/❌ | ... |
| Verification loop | ✅/⚠️/❌ | ... |
| Hooks | ✅/⚠️/❌ | ... |
| Workflow hygiene | ✅/⚠️/❌ | ... |

## Ranked fixes

### 1. <highest-impact fix>

**Why:** <cite Principle N or article>
**How:** <concrete edit - file, line, what to change>
**Effort:** <S/M/L>

### 2. ...

## Noted but not fixing

<Things that look wrong but are justified by project context. Document why so
future audits do not re-raise them.>

## Next steps

<Suggest which fix to do first, and whether /bootstrap-project-memory or
/tool-review would help.>
