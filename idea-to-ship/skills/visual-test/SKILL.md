---
name: visual-test
description: Run artifact-first frontend visual QA from interface and test contracts. Produces selector, matrix, screenshot/baseline, comparison, and bounded RCA evidence.
---

# Visual Test

Verify declared UI states with assertions before screenshots. Do not invent
coverage from attractive images.

## Workflow

1. Resolve `--slug`; require interface design and relevant test plan. Read
   route/state contracts, existing visual tooling, baseline policy, and artifact
   ownership rules.
2. Discover the smallest supported browser/screenshot path. If tooling is
   absent, record the gap; do not add a framework without authorization.
3. Produce selector recipes and a matrix across required route, state,
   viewport, theme, and interaction. Every contract item must map to a cell or
   explicit approved de-scope.
4. For each cell, navigate/setup deterministically and assert route, DOM,
   visibility, content, accessibility state, and critical network/console
   conditions before capture.
5. Capture current evidence and compare to approved baselines or contract
   invariants. A missing baseline is `unapproved`, not pass.
6. For failures, perform bounded artifact RCA: selector/setup, rendering,
   contract drift, baseline drift, environment, or product defect. Link before
   and after evidence; do not self-approve baselines.
7. Write the existing selector, matrix, RCA, and report templates. Preserve
   human approvals and prior evidence.

## Completion

Close every matrix cell as pass, fail, blocked, or approved de-scope. Report
commands, artifacts, baseline status, residual gaps, and next action.

Feed visual evidence to `$idea-to-ship:review --target code`.
