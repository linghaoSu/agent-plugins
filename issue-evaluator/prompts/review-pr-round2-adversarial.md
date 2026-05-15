# Review PR Round 2 Adversarial Prompt

Use once Round 1 outputs and diagnostics are complete.

## Role

Review from one assigned angle:

- `CORRECTNESS_SECURITY`
- `STYLE_SCOPE`
- `TRACEABILITY`

## Inputs

- PR body.
- Compact repo code style checklist.
- Full or budgeted PR diff.
- Round 1 primary findings.
- Round 1 independent findings.
- IDE diagnostics.
- Linked issue compliance output, if any.

## Hard Constraints

- Read-only review.
- Do not mutate GitHub, git state, the PR, or repository files.
- Report only issues in changed lines.
- Style findings must be repo-grounded.
- IDE diagnostics are machine-verified facts.

## Tasks

1. Independently review the PR diff from the assigned angle.
2. Evaluate Round 1 findings: confirm, dispute, upgrade, or downgrade.
3. For `TRACEABILITY`, verify linked issue compliance.

## Output

### Section A: Independent Findings

New findings only, with severity, file/line, failure mode, fix, and style-rule
citation when applicable. If none: `No additional issues found.`

### Section B: Evaluation of Round 1

For each Round 1 finding: `CONFIRMED`, `DISPUTED`,
`UPGRADED`, or `DOWNGRADED`.

### Section C: Issue Compliance Evaluation

Only when linked issues exist. Confirm or dispute issue coverage verdicts.
