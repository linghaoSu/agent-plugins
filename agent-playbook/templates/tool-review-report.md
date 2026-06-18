# Tool Review - <tool name>

**Date:** <YYYY-MM-DD>
**Type:** <MCP | CLI | REST>
**Source:** <path or repo>
**Review intensity:** <quick|standard|deep> (<auto|forced>: <reason>)
**Review mode:** <selected-quick-same-context | multi-agent | degraded-same-context-review>
**Degradation reason:** <none | explicit unsupported runtime | user forbade reviewer sub-agents | reviewer/model unavailable or at capacity>
**Contract:** status=<success|needs_user|terminal|degraded>; mode=review; outputs_written=<this file>; truncated=<true|false>

## Review Rounds

| Round | Angle / role | Verdict |
|---|---|---|
| 1 | BOUNDARIES_NAMES | ... |
| 1 | IO_ERRORS_TOKENS | ... |
| 1 | EVAL_SAFETY | ... |
| 2 | Synthesis | ... |
| 3 | Sanity pass | ... |

## Summary

<One paragraph. Overall grade: A/B/C/D. Biggest issue in one sentence.>

## Scorecard

| Dimension | Status | Note |
|---|---|---|
| Purpose & boundaries | ✅/⚠️/❌ | ... |
| Namespacing | ✅/⚠️/❌ | ... |
| Inputs | ✅/⚠️/❌ | ... |
| Outputs / token cost | ✅/⚠️/❌ | ... |
| Errors | ✅/⚠️/❌ | ... |
| CLI-vs-MCP choice | ✅/⚠️/❌ | ... |
| Evaluation | ✅/⚠️/❌ | ... |

## Ranked fixes

### 1. <issue>

**Why:** <cite checklist item / source>
**How:** <concrete diff - rename, split, add param, etc.>
**Effort:** <S/M/L>
**Risk:** <breaking change? behind a feature flag?>

### 2. ...

## Kill candidates

<If the tool duplicates existing functionality, say so. Recommend deletion or
consolidation with the existing tool.>

## Keep as-is

<Decisions that look wrong at first glance but are intentional.>
