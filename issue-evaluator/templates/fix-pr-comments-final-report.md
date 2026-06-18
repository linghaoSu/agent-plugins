# Fix PR Comments Final Report Template

```markdown
## PR Review Comments Triaged: #<number> "<pr-title>"

**PR**: #<number> by @<author> -> <baseRefName> <- <headRefName>
**State**: <open/merged/closed> | Review decision: <approved/changes_requested/review_required/none>
**Worktree**: `<FIX_WORKTREE>` (detached HEAD on `<short-sha>`)
**Pipeline**: analysis -> executor -> multi-agent adversarial review
**Review intensity**: <quick|standard|deep> (<auto|forced>: <reason>)
**Review mode**: <selected-quick-same-context | multi-agent | degraded-same-context-review>
**Degradation reason**: <none | explicit unsupported runtime | user forbade reviewer sub-agents | reviewer/model unavailable or at capacity>
**Comments triaged**: <total> total -> <actionable> actionable -> <accepted> accepted, <rejected> rejected, <deferred> deferred, <answered> answered, <human> need-input
**Adversarial review verdict**: <CLEAN / NEEDS_TOUCHUP / NEEDS_REWORK>
**Contract:** include the fields from `../../WORKFLOW-CONTRACTS.md` with
mode `comment-triage`, `inputs_resolved` set to repo, PR number, and
`--include-resolved`, `outputs_written` set to the scratch worktree path or
`[]` when report-only, skipped comments/edits/checks, typed errors, one
`next_action`, and the correct `truncated` value.

> **No commits were made. No changes were posted to GitHub.** All edits are uncommitted modifications in the worktree above. All rebuttal text is below — you decide whether to post any of it.

### Accepted & Implemented (uncommitted edits in worktree)
| # | Thread | Reviewer | Category | File | Change |
|---|---|---|---|---|---|
| 1 | [link](<html_url>) | @alice | BUG | `src/foo.go:42` | <one-line> |
| ... | ... | ... | ... | ... | ... |

To inspect: `cd <FIX_WORKTREE> && git diff`

### Rejected — Rebuttals to Post Manually
For each REJECT verdict, provide suggested reply text the user can paste into
the discussion. This skill never posts to GitHub itself.

#### Thread [<id>](<html_url>) — @bob, `src/bar.go:18`
> <original comment, blockquoted>

**Reply**:
> <3-5 sentence technical rebuttal with evidence — file:line citations included>

### Deferred — Follow-Up Suggestions
- Thread [<id>](<html_url>) by @carol — <why deferred and what follow-up issue to file>
  - Reply (optional):
    > <polite reply text>

### Answered — Replies to Questions
- Thread [<id>](<html_url>) by @dan — question about <topic>
  - Reply:
    > <direct answer based on the code>

### Needs Your Input
- Thread [<id>](<html_url>) by @eve — <the specific question that needs human judgment>

### Files Modified (in worktree only)
- `path/to/file1.ext` — <what and why, citing thread id>
- `path/to/file2.ext` — <what and why, citing thread id>

### Adversarial Review
**Verdict**: <CLEAN / NEEDS_TOUCHUP / NEEDS_REWORK>
**Angles**: plan_trace_scope, correctness_regression_security, completeness_tests

**Issues found by adversarial review** (none of these were auto-applied):
- **[critical|warning|nit]** `file:line` (thread <id> | scope creep | new bug) — <what's wrong> -> <suggested correction>

**Missed from the plan**:
- thread <id>: <file> — <what was missing>

**Disputed verdicts**:
- thread <id>: <adversarial review reasoning>

Omit empty subsections.

### Verification
<test/lint result if Step 9 was run, or "verification skipped">

### Next Steps
- Inspect the edits: `cd <FIX_WORKTREE> && git diff`
- If you like them, stage and commit yourself.
- For each REJECT, paste the rebuttal into the discussion on GitHub manually.
- Resolve threads on GitHub manually after the reviewer agrees.
- When done, remove the worktree manually.
```
