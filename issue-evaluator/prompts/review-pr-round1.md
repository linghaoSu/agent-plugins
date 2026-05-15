# Review PR Round 1 Prompts

Use in `issue-evaluator:review-pr` Round 1.

## Shared Constraints

- Follow `../../REVIEW-RUBRIC.md`.
- Review only the PR diff unless the role explicitly gathers context.
- Read-only on GitHub and git state.
- Do not post comments, submit reviews, push, commit, or mutate PR state.
- Style findings must cite the repo style checklist or an established local
  pattern.
- If no issues are found, respond with `LGTM`.

## Roles

### `ROUND_1_BUG_SECURITY`

Review for logic bugs, security issues, error handling gaps, edge cases, API
breakage, resource leaks, races, and regressions. Report severity, file/line,
specific failure mode, and fix.

### `ROUND_1_STYLE_QUALITY`

Review changed lines for repo-grounded naming, imports, error handling,
testing, organization, documentation, and idioms. Drop findings that cannot be
cited to the style checklist or surrounding code.

### `ROUND_1_EXISTING_CONTEXT`

Summarize existing review comments and inline comments, identify already
flagged issues, unresolved discussion, and unreviewed areas.

### `ROUND_1_INDEPENDENT`

Run an independent review with no access to primary reviewer conclusions.
Cover bugs, security, logic, and repo-grounded style. Be concise.

### `ROUND_1_ISSUE_COMPLIANCE`

Skip if `LINKED_ISSUES` is empty. For each linked issue, decide whether the PR
fully, partially, or does not address the issue requirements and edge cases.
For `fixes` relationships, missing coverage is critical.
