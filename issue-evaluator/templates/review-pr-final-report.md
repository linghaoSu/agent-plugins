# Review PR Final Report Template

```markdown
## PR Review: <pr-title>

**PR**: #<number> by @<author>
**Base**: <base-branch> <- <head-branch>
**Files changed**: <count> (+<additions> -<deletions>)
**Status**: <open/merged/closed> | Review decision: <approved/changes_requested/review_required/none>
**Linked issues**: <#N (fixes), #M (references), ... or "None">
**Review mode**: <multi-agent | degraded-same-context-review>
**Degradation reason**: <none | explicit unsupported runtime | user forbade reviewer sub-agents | reviewer/model unavailable or at capacity>
**Review pipeline**: Round 1 (primary review + independent review + IDE Diagnostics + Issue Compliance) -> Round 2 (adversarial review + evaluation) -> Round 3 (final synthesis)
**Contract:** include the fields from `../../WORKFLOW-CONTRACTS.md` with
mode `read-only-review`, `inputs_resolved` set to repo and PR number,
`outputs_written: []`, skipped roles or linked issues with reasons, typed
errors, one `next_action`, and the correct `truncated` value.

### Summary
<2-3 sentence summary of what this PR does>

<Round 3 structured output follows: Critical Issues, Warnings, Nits, Disputed & Dropped, Already Flagged, Linked Issue Compliance, Positive Notes, Verdict>
```

Omit empty sections.
