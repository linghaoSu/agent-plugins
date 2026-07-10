---
name: review-pr
description: Risk-scaled local review of a GitHub pull request for correctness, security, issue coverage, scope, repo standards, and tests. Read-only on GitHub and never applies fixes.
---

# Review Pull Request

Review locally and report findings to the user. Do not submit reviews, comments,
approvals, labels, merges, pushes, or code changes.

## Workflow

1. Resolve PR URL/number and optional `--review-depth quick|standard|deep`.
   Fetch metadata, issue links, commits, files, checks, and review state with
   `gh`. Apply GitHub read-only safety from `../../WORKFLOW-CONTRACTS.md`.
2. Create or reuse a clean read-only worktree at the PR head. Verify base/head
   SHAs and compute the merge-base diff including submodules/generated files.
   Stop on unsafe checkout state or changed head.
3. Load repo instructions, contribution rules, issue/spec, and internal
   code-style cache. Separate source requirements from reviewer opinions.
4. Select intensity by risk. Review axes independently:
   - correctness, security, failure behavior, and regressions
   - issue/spec coverage and unrequested scope
   - repo standards, maintainability, and generated/artifact policy
   - tests and CI evidence at public seams
5. Quick is same-context. Standard/deep use independent `reasoning` reviewers
   where available; deep adds adversarial challenge and final arbitration.
   Record `degraded` if independence is unavailable.
6. Every finding requires severity, tight path/line, causal evidence, user
   consequence, and minimal fix. Suppress speculative risks, tooling-enforced
   style, and unrelated pre-existing issues. Keep Standards and Spec totals
   separate so one cannot mask the other.
7. Run safe focused checks when feasible. Do not claim remote CI or skipped
   tests passed. Use `../../templates/review-pr-final-report.md` for the report.
8. Remove only the temporary worktree created by this run and only when clean;
   otherwise leave it and report why.

## Completion

Report reviewed SHAs, intensity/mode, findings by axis, checks, limitations,
truncation, and verdict. A clean verdict requires evidence from every required
axis on the current head.

Use `$issue-evaluator:fix-pr-comments` when selected feedback should be addressed.
