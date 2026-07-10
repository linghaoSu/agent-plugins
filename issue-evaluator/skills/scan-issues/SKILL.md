---
name: scan-issues
description: Read-only scan for high-value unattended GitHub issues, expanding the time window when needed and ranking confirmed, unclaimed, non-duplicate work. Never modifies issues.
---

# Scan Issues

Use `gh` only for reads. Never assign, label, comment, close, edit, or create an
issue or PR.

## Workflow

1. Resolve repo and optional initial lookback. Confirm authentication and read
   repo contribution instructions.
2. Query open non-PR issues in expanding windows, fetching bounded metadata,
   comments, assignees, linked PRs/timeline, labels, and recency. Stop at the
   shared item/token cap and disclose truncation.
3. Exclude issues with an open/closed fixing PR, recent credible claim,
   maintainer block, duplicate/superseded status, insufficient reproduction,
   or code evidence that the problem is already fixed.
4. For survivors, inspect relevant code/history and score impact, confidence,
   reproducibility, scope, verification path, maintainer readiness, and claim
   risk. Penalize broad architecture work and unclear ownership.
5. Present a short ranked table with issue link, evidence, why unattended,
   likely files, reproduction/acceptance, risk, and recommended next action.

If no issue survives after the maximum window, report the searched windows and
exclusion counts. Do not loosen safety criteria to fill the list. Recommend
`$issue-evaluator:evaluate-issue` for one selected candidate.
