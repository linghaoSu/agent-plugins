#!/usr/bin/env python3
"""Offline contract fixtures for critical agent-playbook workflows."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable


@dataclass(frozen=True)
class InvariantGroup:
    name: str
    patterns: tuple[str, ...]


@dataclass(frozen=True)
class ContractCheck:
    check_id: str
    relative_path: str
    groups: tuple[InvariantGroup, ...]


@dataclass(frozen=True)
class ForbiddenPatternCheck:
    check_id: str
    relative_path: str
    patterns: tuple[str, ...]


@dataclass(frozen=True)
class WorktreeCleanupScenario:
    name: str
    apply: bool
    confirmed: bool
    pr_status: str
    has_local_changes: bool = False
    has_unpushed_commits: bool = False
    force: bool = False
    state_known: bool = True
    expected: str = ""


@dataclass(frozen=True)
class FixIssueWorktreeScenario:
    name: str
    primary_add_ok: bool
    fallback_add_ok: bool
    expected: str


@dataclass(frozen=True)
class PrCommentGateScenario:
    name: str
    approved_to_edit: bool
    report_only: bool
    accepted_count: int
    expected: str


@dataclass(frozen=True)
class BroadOrchestratorEntry:
    entry_id: str
    route_token: str
    text: str
    source_ref: str = ""


@dataclass(frozen=True)
class BroadOrchestratorScenario:
    name: str
    entry: BroadOrchestratorEntry
    expected: str


CHECKS: tuple[ContractCheck, ...] = (
    ContractCheck(
        "agent-playbook-output-token-error-contract",
        "agent-playbook/WORKFLOW-CONTRACTS.md",
        (
            InvariantGroup("status field", (r"status:\s+success \| needs_user \| terminal \| degraded",)),
            InvariantGroup("mode field", (r"mode:",)),
            InvariantGroup("inputs resolved", (r"inputs_resolved:",)),
            InvariantGroup("outputs written", (r"outputs_written:",)),
            InvariantGroup("skipped field", (r"skipped:",)),
            InvariantGroup("typed errors", (r"retryable \| terminal \| needs_user \| degraded",)),
            InvariantGroup("next action", (r"next_action:",)),
            InvariantGroup("truncated field", (r"truncated:\s+true \| false",)),
            InvariantGroup("regex smoke tests only", (r"regex fixtures as contract smoke tests",)),
        ),
    ),
    ContractCheck(
        "tool-review-template-reference-contract",
        "agent-playbook/skills/tool-review/SKILL.md",
        (
            InvariantGroup("template reference", (r"\.\./\.\./templates/tool-review-report\.md",)),
            InvariantGroup("artifact path preserved", (r"\.agent-playbook/<slug>/tool-review-<tool-name>\.md",)),
        ),
    ),
    ContractCheck(
        "tool-review-report-template-contract",
        "agent-playbook/templates/tool-review-report.md",
        (
            InvariantGroup("header", (r"# Tool Review",)),
            InvariantGroup("tool placeholder", (r"<tool name>",)),
            InvariantGroup("contract field", (r"\*\*Contract:\*\*",)),
            InvariantGroup("outputs written placeholder", (r"outputs_written=<this file>",)),
            InvariantGroup("review rounds", (r"## Review Rounds",)),
            InvariantGroup("boundaries angle", (r"BOUNDARIES_NAMES",)),
            InvariantGroup("io angle", (r"IO_ERRORS_TOKENS",)),
            InvariantGroup("eval angle", (r"EVAL_SAFETY",)),
            InvariantGroup("scorecard", (r"## Scorecard",)),
            InvariantGroup("purpose dimension", (r"Purpose & boundaries",)),
            InvariantGroup("output dimension", (r"Outputs / token cost",)),
            InvariantGroup("ranked fixes", (r"## Ranked fixes",)),
            InvariantGroup("why field", (r"\*\*Why:\*\*",)),
            InvariantGroup("how field", (r"\*\*How:\*\*",)),
            InvariantGroup("kill candidates", (r"## Kill candidates",)),
            InvariantGroup("keep as is", (r"## Keep as-is",)),
        ),
    ),
    ContractCheck(
        "context-audit-template-reference-contract",
        "agent-playbook/skills/context-audit/SKILL.md",
        (
            InvariantGroup("template reference", (r"\.\./\.\./templates/context-audit-report\.md",)),
            InvariantGroup("artifact path preserved", (r"\.agent-playbook/<slug>/context-audit\.md",)),
        ),
    ),
    ContractCheck(
        "context-audit-report-template-contract",
        "agent-playbook/templates/context-audit-report.md",
        (
            InvariantGroup("header", (r"# Context Audit",)),
            InvariantGroup("repo placeholder", (r"<repo name>",)),
            InvariantGroup("contract field", (r"\*\*Contract:\*\*",)),
            InvariantGroup("outputs written placeholder", (r"outputs_written=<this file>",)),
            InvariantGroup("summary", (r"## Summary",)),
            InvariantGroup("grade prompt", (r"overall hygiene grade",)),
            InvariantGroup("scorecard", (r"## Scorecard",)),
            InvariantGroup("memory size dimension", (r"Memory size",)),
            InvariantGroup("tool sprawl dimension", (r"Tool sprawl",)),
            InvariantGroup("workflow hygiene dimension", (r"Workflow hygiene",)),
            InvariantGroup("ranked fixes", (r"## Ranked fixes",)),
            InvariantGroup("why field", (r"\*\*Why:\*\*",)),
            InvariantGroup("how field", (r"\*\*How:\*\*",)),
            InvariantGroup("noted but not fixing", (r"## Noted but not fixing",)),
            InvariantGroup("next steps", (r"## Next steps",)),
        ),
    ),
    ContractCheck(
        "vibe-health-template-reference-contract",
        "agent-playbook/skills/vibe-coding-health-check/SKILL.md",
        (
            InvariantGroup("template reference", (r"\.\./\.\./templates/vibe-health-check\.md",)),
            InvariantGroup("artifact path preserved", (r"\.agent-playbook/<slug>/vibe-health-check\.md",)),
        ),
    ),
    ContractCheck(
        "vibe-health-report-template-contract",
        "agent-playbook/templates/vibe-health-check.md",
        (
            InvariantGroup("header", (r"# Vibe Coding Health Check",)),
            InvariantGroup("target placeholder", (r"<repo or target>",)),
            InvariantGroup("decision field", (r"\*\*Decision:\*\*",)),
            InvariantGroup("decision options", (r"<Continue\|Slow down\|Stop>",)),
            InvariantGroup("scorecard", (r"## Scorecard",)),
            InvariantGroup("evidence column", (r"Evidence",)),
            InvariantGroup("why it matters column", (r"Why It Matters",)),
            InvariantGroup("checks run", (r"## Checks Run",)),
            InvariantGroup("command column", (r"Command",)),
            InvariantGroup("result column", (r"Result",)),
            InvariantGroup("routed audits", (r"## Routed Audits",)),
            InvariantGroup("recommended skill column", (r"Recommended Skill",)),
            InvariantGroup("findings", (r"## Red / Yellow Findings",)),
            InvariantGroup("next steps", (r"## Next Steps",)),
        ),
    ),
    ContractCheck(
        "antifragile-output-token-error-contract",
        "antifragile/WORKFLOW-CONTRACTS.md",
        (
            InvariantGroup("status field", (r"`status`", r"success`, `needs_user`, `terminal`, or `degraded")),
            InvariantGroup("outputs written", (r"`outputs_written`", r"\[\]")),
            InvariantGroup("typed errors", (r"`retryable`, `terminal`, `needs_user`, or `degraded`",)),
            InvariantGroup("next action", (r"`next_action`",)),
            InvariantGroup("truncated field", (r"`truncated`", r"`true` or `false`")),
            InvariantGroup("token budget", (r"Default token budget", r"100 source/config/hook/script/skill files")),
        ),
    ),
    ContractCheck(
        "skill-stats-output-token-error-contract",
        "skill-stats/WORKFLOW-CONTRACTS.md",
        (
            InvariantGroup("read-only boundary", (r"read-only and conversation-only",)),
            InvariantGroup("outputs written", (r"`outputs_written`", r"\[\]")),
            InvariantGroup("typed errors", (r"`retryable`, `terminal`, `needs_user`, or `degraded`",)),
            InvariantGroup("truncated field", (r"`truncated`", r"`true` or `false`")),
            InvariantGroup("token budget", (r"top 20 skills", r"50 never-called skills")),
        ),
    ),
    ContractCheck(
        "worktree-cleaner-output-token-error-contract",
        "worktree-cleaner/WORKFLOW-CONTRACTS.md",
        (
            InvariantGroup("dry-run default", (r"report-only by default",)),
            InvariantGroup("apply confirmation", (r"`--apply`", r"explicit user confirmation")),
            InvariantGroup("outputs written", (r"`outputs_written`", r"\[\]")),
            InvariantGroup("typed errors", (r"`retryable`, `terminal`, `needs_user`, or `degraded`",)),
            InvariantGroup("truncated field", (r"`truncated`", r"`true` or `false`")),
            InvariantGroup("token budget", (r"100 worktrees", r"20 changed-file stat lines", r"5 commit subjects")),
        ),
    ),
    ContractCheck(
        "clean-worktrees-safe-default-contract",
        "worktree-cleaner/skills/clean-worktrees/SKILL.md",
        (
            InvariantGroup("dry-run default", (r"report-only by default", r"Default mode is dry-run")),
            InvariantGroup("apply required", (r"--apply", r"removes worktrees only when")),
            InvariantGroup("confirmation required", (r"explicitly confirmed", r"Confirm Before Removal")),
            InvariantGroup("no default force", (r"Never use `git worktree remove --force` as the default",)),
            InvariantGroup("uncommitted changes checked", (r"uncommitted changes",)),
            InvariantGroup("unpushed commits checked", (r"unpushed commits",)),
            InvariantGroup("closed not merged protected", (r"CLOSED_NOT_MERGED",)),
            InvariantGroup("detached protected", (r"DETACHED", r"detached HEAD")),
            InvariantGroup("no pr protected", (r"NO_PR",)),
            InvariantGroup("dirty closed pr protected", (r"CLOSED_NOT_MERGED.*NO_PR.*DETACHED.*NO_UPSTREAM.{0,160}uncommitted changes or unpushed commits",)),
            InvariantGroup("shared contract cited", (r"\.\./\.\./WORKFLOW-CONTRACTS\.md", r"mode `dry-run`")),
        ),
    ),
    ContractCheck(
        "fix-issue-worktree-stop-contract",
        "issue-evaluator/skills/fix-issue/SKILL.md",
        (
            InvariantGroup("isolated worktree required", (r"isolated worktree",)),
            InvariantGroup("worktree failure stops", (r"If that also fails, \*\*stop\*\*", r"status: terminal")),
            InvariantGroup("no current directory fallback", (r"Do not fall back to the\s+current directory",)),
            InvariantGroup("scoped staging", (r"Stage only files intentionally changed", r"git add <files-touched-by-this-fix>")),
            InvariantGroup("diff summary before commit", (r"Before committing, produce a diff summary", r"git diff --stat")),
            InvariantGroup("truncation contract", (r"truncated: true", r"Token budget")),
        ),
    ),
    ContractCheck(
        "pr-comment-fix-human-gate-contract",
        "issue-evaluator/skills/fix-pr-comments/SKILL.md",
        (
            InvariantGroup("confirmation step", (r"Confirm With User Before Touching Code",)),
            InvariantGroup("do not skip gate", (r"Do not skip this step",)),
            InvariantGroup("local write boundary", (r"Local write boundary", r"unstaged edits")),
            InvariantGroup("token budget", (r"Token budget", r"truncated: true")),
            InvariantGroup("final template reference", (r"fix-pr-comments-final-report\.md",)),
            InvariantGroup("analyst prompt reference", (r"fix-pr-comments-analyst\.md",)),
            InvariantGroup("reconciler prompt reference", (r"fix-pr-comments-reconciler\.md",)),
            InvariantGroup("executor prompt reference", (r"fix-pr-comments-executor\.md",)),
            InvariantGroup("reviewer prompt reference", (r"fix-pr-comments-adversarial-reviewer\.md",)),
        ),
    ),
    ContractCheck(
        "high-risk-token-budget-contract",
        "issue-evaluator/skills/review-pr/SKILL.md",
        (
            InvariantGroup("token budget", (r"Token budget",)),
            InvariantGroup("truncated marker", (r"truncated:\s*true",)),
            InvariantGroup("next action", (r"next_action",)),
            InvariantGroup("final template reference", (r"review-pr-final-report\.md",)),
            InvariantGroup("round 1 prompt reference", (r"review-pr-round1\.md",)),
            InvariantGroup("round 2 prompt reference", (r"review-pr-round2-adversarial\.md",)),
            InvariantGroup("round 3 prompt reference", (r"review-pr-round3-synthesis\.md",)),
        ),
    ),
    ContractCheck(
        "evaluate-issue-extracted-reference-contract",
        "issue-evaluator/skills/evaluate-issue/SKILL.md",
        (
            InvariantGroup("artifact inventory round 2", (r"evaluate-issue-round2-adversarial\.md",)),
            InvariantGroup("artifact inventory round 3", (r"evaluate-issue-round3-synthesis\.md",)),
            InvariantGroup("artifact inventory final template", (r"evaluate-issue-final-report\.md",)),
            InvariantGroup("round 2 workflow reference", (r"#### Round 2[\s\S]*evaluate-issue-round2-adversarial\.md",)),
            InvariantGroup("round 3 workflow reference", (r"#### Round 3[\s\S]*evaluate-issue-round3-synthesis\.md",)),
            InvariantGroup("step 4 workflow reference", (r"### Step 4[\s\S]*evaluate-issue-final-report\.md",)),
            InvariantGroup("missing or empty stop condition", (r"missing or empty",)),
            InvariantGroup("terminal stop", (r"terminal",)),
            InvariantGroup("no reconstruction", (r"do not reconstruct",)),
            InvariantGroup("no improvisation", (r"do not improvise",)),
        ),
    ),
    ContractCheck(
        "evaluate-issue-round2-prompt-contract",
        "issue-evaluator/prompts/evaluate-issue-round2-adversarial.md",
        (
            InvariantGroup("root cause angle", (r"ROOT_CAUSE",)),
            InvariantGroup("fix plan testability angle", (r"FIX_PLAN_TESTABILITY",)),
            InvariantGroup("regression scope angle", (r"REGRESSION_SCOPE",)),
            InvariantGroup("assigned angle placeholder", (r"Assigned angle: <ANGLE>",)),
            InvariantGroup("read only", (r"READ-ONLY",)),
            InvariantGroup("no file mutation", (r"Do NOT modify any files",)),
            InvariantGroup("no github mutation", (r"Do NOT modify any files or post anything to GitHub",)),
            InvariantGroup("issue details input", (r"## Issue Details",)),
            InvariantGroup("code style input", (r"## Code Style Guide",)),
            InvariantGroup("round 1 primary input", (r"ROUND_1_PRIMARY",)),
            InvariantGroup("round 1 independent input", (r"ROUND_1_INDEPENDENT",)),
            InvariantGroup("round 1 diagnostics input", (r"ROUND_1_DIAGNOSTICS",)),
            InvariantGroup("diagnostics section", (r"IDE Diagnostics",)),
            InvariantGroup("diagnostics facts", (r"machine-verified facts",)),
            InvariantGroup("section a", (r"### Section A: Independent Diagnosis",)),
            InvariantGroup("section b", (r"### Section B: Evaluation of Round 1",)),
            InvariantGroup("confirmed verdict", (r"CONFIRMED",)),
            InvariantGroup("disputed verdict", (r"DISPUTED",)),
            InvariantGroup("incomplete verdict", (r"INCOMPLETE",)),
            InvariantGroup("already fixed handling", (r"already fixed",)),
            InvariantGroup("fixed commit placeholder", (r"<sha>",)),
        ),
    ),
    ContractCheck(
        "evaluate-issue-round3-prompt-contract",
        "issue-evaluator/prompts/evaluate-issue-round3-synthesis.md",
        (
            InvariantGroup("runtime aware synthesis", (r"runtime-aware multi-pass issue diagnosis pipeline",)),
            InvariantGroup("diagnostics ground truth", (r"IDE Diagnostics findings are \*\*ground truth\*\*",)),
            InvariantGroup("three source confidence rule", (r"3\+ independent review sources",)),
            InvariantGroup("two source confidence rule", (r"2 independent review sources",)),
            InvariantGroup("tie break by reading code", (r"re-examine the code yourself",)),
            InvariantGroup("round 1 primary input", (r"ROUND_1_PRIMARY",)),
            InvariantGroup("round 1 independent input", (r"ROUND_1_INDEPENDENT",)),
            InvariantGroup("round 1 diagnostics input", (r"ROUND_1_DIAGNOSTICS",)),
            InvariantGroup("round 2 diagnosis input", (r"ROUND_2_DIAGNOSIS",)),
            InvariantGroup("already fixed status", (r"already-fixed status",)),
            InvariantGroup("already fixed verification", (r"verify by reading the code",)),
            InvariantGroup("status section", (r"### Status",)),
            InvariantGroup("root cause section", (r"### Root Cause",)),
            InvariantGroup("reproduction section", (r"### Reproduction",)),
            InvariantGroup("suggested fix section", (r"### Suggested Fix",)),
            InvariantGroup("risks section", (r"### Risks & Edge Cases",)),
            InvariantGroup("disputed section", (r"### Disputed & Resolved",)),
            InvariantGroup("affected files section", (r"### Affected Files",)),
        ),
    ),
    ContractCheck(
        "evaluate-issue-final-template-contract",
        "issue-evaluator/templates/evaluate-issue-final-report.md",
        (
            InvariantGroup("issue heading", (r"## Issue Evaluation: <issue-title>",)),
            InvariantGroup("description mode line", (r"\*\*Mode\*\*: description-based evaluation \(no GitHub issue\)",)),
            InvariantGroup("issue number", (r"\*\*Issue\*\*: #<number>",)),
            InvariantGroup("review mode", (r"\*\*Review mode\*\*:",)),
            InvariantGroup("degradation reason", (r"\*\*Degradation reason\*\*:",)),
            InvariantGroup("pipeline field", (r"\*\*Diagnosis pipeline\*\*:",)),
            InvariantGroup("pipeline round 1", (r"Round 1",)),
            InvariantGroup("pipeline round 2", (r"Round 2",)),
            InvariantGroup("pipeline round 3", (r"Round 3",)),
            InvariantGroup("round 3 insertion point", (r"<Round 3 structured output follows>",)),
        ),
    ),
    ContractCheck(
        "fix-pr-comments-analyst-prompt-contract",
        "issue-evaluator/prompts/fix-pr-comments-analyst.md",
        (
            InvariantGroup("analysis only", (r"analysis only",)),
            InvariantGroup("read only github", (r"Read-only with respect to GitHub",)),
            InvariantGroup("no github writes", (r"Do not run `gh pr review`, `gh pr comment`, or `gh api` write methods",)),
            InvariantGroup("no edits", (r"Do not edit files",)),
            InvariantGroup("no git mutations", (r"Do not run `git add`, `git commit`, `git stash`, or `git push`",)),
            InvariantGroup("load bearing verdicts", (r"ACCEPT", r"REJECT", r"NEEDS_HUMAN")),
        ),
    ),
    ContractCheck(
        "fix-pr-comments-reconciler-prompt-contract",
        "issue-evaluator/prompts/fix-pr-comments-reconciler.md",
        (
            InvariantGroup("approval gate", (r"user approves", r"before any file is edited")),
            InvariantGroup("deduplicated plan", (r"deduplicated implementation plan",)),
            InvariantGroup("accepted only", (r"For `ACCEPT` and `ACCEPT_PARTIAL` only",)),
            InvariantGroup("needs human carried forward", (r"NEEDS_HUMAN", r"specific questions")),
        ),
    ),
    ContractCheck(
        "fix-pr-comments-executor-prompt-contract",
        "issue-evaluator/prompts/fix-pr-comments-executor.md",
        (
            InvariantGroup("after confirmation only", (r"Use only after the user confirms",)),
            InvariantGroup("scratch worktree only", (r"Work only inside the scratch worktree",)),
            InvariantGroup("main workdir protected", (r"Never touch the user's main working directory",)),
            InvariantGroup("no git mutations", (r"Do not run `git add`, `git commit`, `git commit --amend`, `git stash`, or", r"`git push`")),
            InvariantGroup("no github writes", (r"Do not run GitHub write commands",)),
            InvariantGroup("approved plan only", (r"Do not edit files outside the approved fix plan",)),
            InvariantGroup("no improvisation", (r"`INFEASIBLE`", r"Do not improvise")),
        ),
    ),
    ContractCheck(
        "fix-pr-comments-adversarial-prompt-contract",
        "issue-evaluator/prompts/fix-pr-comments-adversarial-reviewer.md",
        (
            InvariantGroup("read only", (r"Read-only review",)),
            InvariantGroup("no git or github writes", (r"Do not run `git add`, `git commit`, `git stash`, `git push`, or GitHub write",)),
            InvariantGroup("no auto apply", (r"Do not auto-apply suggested corrections",)),
            InvariantGroup("plan trace", (r"Every diff hunk must trace to an approved thread id",)),
            InvariantGroup("strict verdicts", (r"`CLEAN`, `NEEDS_TOUCHUP`, or `NEEDS_REWORK`",)),
        ),
    ),
    ContractCheck(
        "review-pr-final-template-contract",
        "issue-evaluator/templates/review-pr-final-report.md",
        (
            InvariantGroup("review header", (r"## PR Review: <pr-title>",)),
            InvariantGroup("contract fields", (r"mode `read-only-review`", r"`outputs_written: \[\]`")),
            InvariantGroup("truncated field", (r"`truncated`",)),
            InvariantGroup("pipeline", (r"Round 1", r"Round 2", r"Round 3")),
        ),
    ),
    ContractCheck(
        "fix-pr-comments-final-template-contract",
        "issue-evaluator/templates/fix-pr-comments-final-report.md",
        (
            InvariantGroup("triage header", (r"## PR Review Comments Triaged",)),
            InvariantGroup("no github writes", (r"No changes were posted to GitHub",)),
            InvariantGroup("no commits", (r"No commits were made",)),
            InvariantGroup("contract fields", (r"mode `comment-triage`", r"`outputs_written`")),
            InvariantGroup("manual next steps", (r"manually", r"Inspect the edits")),
        ),
    ),
    ContractCheck(
        "review-pr-round1-prompt-contract",
        "issue-evaluator/prompts/review-pr-round1.md",
        (
            InvariantGroup("rubric reference", (r"\.\./\.\./REVIEW-RUBRIC\.md",)),
            InvariantGroup("read only", (r"Read-only on GitHub and git state",)),
            InvariantGroup("no mutation", (r"Do not post comments, submit reviews, push, commit, or mutate PR state",)),
            InvariantGroup("repo grounded style", (r"Style findings must cite the repo style checklist or an established local",)),
            InvariantGroup("lgtm sentinel", (r"respond with `LGTM`",)),
            InvariantGroup("role coverage", (r"ROUND_1_BUG_SECURITY", r"ROUND_1_STYLE_QUALITY", r"ROUND_1_INDEPENDENT")),
        ),
    ),
    ContractCheck(
        "review-pr-round2-prompt-contract",
        "issue-evaluator/prompts/review-pr-round2-adversarial.md",
        (
            InvariantGroup("angle coverage", (r"CORRECTNESS_SECURITY", r"STYLE_SCOPE", r"TRACEABILITY")),
            InvariantGroup("read only", (r"Read-only review",)),
            InvariantGroup("no mutation", (r"Do not mutate GitHub, git state, the PR, or repository files",)),
            InvariantGroup("changed lines only", (r"Report only issues in changed lines",)),
            InvariantGroup("repo grounded style", (r"Style findings must be repo-grounded",)),
            InvariantGroup("diagnostics ground truth", (r"IDE diagnostics are machine-verified facts",)),
        ),
    ),
    ContractCheck(
        "review-pr-round3-prompt-contract",
        "issue-evaluator/prompts/review-pr-round3-synthesis.md",
        (
            InvariantGroup("local only", (r"Local review only; do not post to GitHub",)),
            InvariantGroup("repo grounded style", (r"Style findings must cite the repo style guide or established local patterns",)),
            InvariantGroup("diagnostics ground truth", (r"IDE diagnostics are ground truth",)),
            InvariantGroup("principles check", (r"Think Before Coding", r"Simplicity First", r"Surgical Changes", r"Goal-Driven Execution")),
            InvariantGroup("fix pr criticality", (r"For `fix:` PRs", r"unverifiable fixes are critical")),
            InvariantGroup("verdicts", (r"`LGTM`, `Approve with nits`, or `Request changes`",)),
        ),
    ),
    ContractCheck(
        "scan-issues-readonly-output-contract",
        "issue-evaluator/skills/scan-issues/SKILL.md",
        (
            InvariantGroup("read only", (r"strictly read-only",)),
            InvariantGroup("no local report", (r"writes no local report artifact", r"outputs_written: \[\]")),
            InvariantGroup("token budget", (r"Default budget", r"truncated: true")),
        ),
    ),
    ContractCheck(
        "skill-stats-output-budget-contract",
        "skill-stats/skills/skill-stats/SKILL.md",
        (
            InvariantGroup("conversation only", (r"conversation-only",)),
            InvariantGroup("no writes", (r"outputs_written: \[\]",)),
            InvariantGroup("shared contract cited", (r"\.\./\.\./WORKFLOW-CONTRACTS\.md",)),
        ),
    ),
    ContractCheck(
        "antifragile-readonly-budget-contract",
        "antifragile/skills/antifragile-agent/SKILL.md",
        (
            InvariantGroup("read only", (r"read-only",)),
            InvariantGroup("stdout only", (r"stdout",)),
            InvariantGroup("shared contract cited", (r"\.\./\.\./WORKFLOW-CONTRACTS\.md",)),
            InvariantGroup("agent-playbook checklist", (r"agent-playbook audits", r"boundary truth")),
        ),
    ),
    ContractCheck(
        "vibe-health-bootstrap-contract",
        "agent-playbook/skills/vibe-coding-health-check/SKILL.md",
        (
            InvariantGroup("principles loaded", (r"../../PRINCIPLES\.md",)),
            InvariantGroup("tracked diff", (r"git diff --name-only HEAD",)),
            InvariantGroup("staged diff", (r"git diff --cached --name-only",)),
            InvariantGroup("untracked diff", (r"git ls-files --others --exclude-standard",)),
            InvariantGroup("changed-file union", (r"changed-file union",)),
        ),
    ),
    ContractCheck(
        "vibe-health-scorecard-contract",
        "agent-playbook/skills/vibe-coding-health-check/SKILL.md",
        (
            InvariantGroup("change size", (r"Change size",)),
            InvariantGroup("scope control", (r"Scope control",)),
            InvariantGroup("requirement traceability", (r"Requirement traceability",)),
            InvariantGroup("test verification", (r"Test/verification",)),
            InvariantGroup("error resilience", (r"Error/resilience",)),
            InvariantGroup("state recovery", (r"State/recovery",)),
            InvariantGroup("context tool hygiene", (r"Context/tool hygiene",)),
        ),
    ),
    ContractCheck(
        "vibe-health-safe-routing-contract",
        "agent-playbook/skills/vibe-coding-health-check/SKILL.md",
        (
            InvariantGroup("deep is read-only", (r"--deep.{0,160}read-only",)),
            InvariantGroup("mutating workflows identified", (r"mutating\s+workflows",)),
            InvariantGroup("mutating workflows gated", (r"recommended, not executed",)),
            InvariantGroup("test not autorun", (r"idea-to-ship:test.{0,120}No, may write tests or fixes",)),
            InvariantGroup("commit not autorun", (r"agent-playbook:commit-changes.{0,140}No, mutates git",)),
            InvariantGroup("explicit authorization", (r"explicitly gives.{0,80}authorization",)),
        ),
    ),
    ContractCheck(
        "vibe-health-artifact-ownership-contract",
        "agent-playbook/skills/vibe-coding-health-check/SKILL.md",
        (
            InvariantGroup("canonical artifact", (r"vibe-health-check\.md",)),
            InvariantGroup("append dated run", (r"append a new.{0,80}Run - <YYYY-MM-DD HH:MM>",)),
            InvariantGroup("preserve human notes", (r"Preserve human notes",)),
            InvariantGroup("draft fallback", (r"vibe-health-check\.draft\.md",)),
        ),
    ),
    ContractCheck(
        "vibe-health-stop-rules-contract",
        "agent-playbook/skills/vibe-coding-health-check/SKILL.md",
        (
            InvariantGroup("release gate failure stops", (r"Release gate or required verification command fails",)),
            InvariantGroup("missing tests stop", (r"behavior-changing diff lacks both test coverage",)),
            InvariantGroup("mixed goals stop", (r"mixes unrelated goals",)),
            InvariantGroup("in-memory state stop", (r"Critical state is only in memory",)),
            InvariantGroup("agent loop stop", (r"agent loop has no persisted state",)),
        ),
    ),
    ContractCheck(
        "vibe-health-fix-handoff-contract",
        "agent-playbook/skills/vibe-coding-health-check/SKILL.md",
        (
            InvariantGroup("workflow contracts loaded", (r"../../WORKFLOW-CONTRACTS\.md",)),
            InvariantGroup("fix handoff", (r"vibe-coding-fix",)),
            InvariantGroup("health artifact remains diagnostic", (r"vibe-health-check\.md",)),
        ),
    ),
    ContractCheck(
        "vibe-fix-classification-contract",
        "agent-playbook/skills/vibe-coding-fix/SKILL.md",
        (
            InvariantGroup("workflow contracts loaded", (r"../../WORKFLOW-CONTRACTS\.md",)),
            InvariantGroup("requires source health check", (r"vibe-health-check\.md",)),
            InvariantGroup("safe local cleanup", (r"Safe local cleanup",)),
            InvariantGroup("routed workflow", (r"Routed workflow",)),
            InvariantGroup("user-owned decision", (r"User-owned decision",)),
            InvariantGroup("stop item", (r"Stop item",)),
        ),
    ),
    ContractCheck(
        "vibe-fix-safety-contract",
        "agent-playbook/skills/vibe-coding-fix/SKILL.md",
        (
            InvariantGroup("explicit apply authorization", (r"--apply", r"explicitly asks to\s+fix")),
            InvariantGroup("no commits", (r"Do not commit", r"no `git commit`")),
            InvariantGroup("no pushes", (r"push",)),
            InvariantGroup("release gate verification", (r"scripts/release-gate\.sh --mode all",)),
            InvariantGroup("fix log artifact", (r"vibe-fix-log\.md",)),
        ),
    ),
    ContractCheck(
        "implementation-tournament-contract",
        "agent-playbook/skills/implementation-tournament/SKILL.md",
        (
            InvariantGroup("explicit only", (r"explicitly asks", r"--compete", r"--tournament")),
            InvariantGroup("isolated worktrees", (r"isolated candidate worktrees", r"same base commit")),
            InvariantGroup("objective verification", (r"same checks", r"failing candidate cannot win")),
            InvariantGroup("review angles", (r"Correctness / contract fit", r"Minimality / blast radius", r"Maintainability / readability")),
            InvariantGroup("no winner", (r"No Winner", r"do not apply any candidate patch")),
            InvariantGroup("no commit push", (r"Do not commit or push",)),
        ),
    ),
    ContractCheck(
        "orchestration-spike-boundary-contract",
        ".idea-to-ship/ITS-ROADMAP-020/orchestration-spike.md",
        (
            InvariantGroup("artifact only", (r"artifact-only",)),
            InvariantGroup("read only", (r"read-only",)),
            InvariantGroup("adopt", (r"Adopt",)),
            InvariantGroup("reject", (r"Reject",)),
            InvariantGroup("adapt", (r"Adapt",)),
            InvariantGroup("overlap", (r"Existing Skill Overlap", r"Overlap")),
            InvariantGroup("allowed actions", (r"Allowed Actions",)),
            InvariantGroup("forbidden actions", (r"Forbidden Actions",)),
            InvariantGroup("future gate", (r"Future Decision Gate",)),
            InvariantGroup("no commit", (r"no git commit",)),
            InvariantGroup("no push", (r"no git push",)),
            InvariantGroup("no github mutation", (r"no GitHub mutation",)),
            InvariantGroup("no plugin install", (r"no plugin install",)),
            InvariantGroup("no plugin cache install", (r"no plugin/cache installation",)),
            InvariantGroup("no skill-tree copy", (r"no skill-tree copy",)),
            InvariantGroup("no skill tree copy", (r"no skill tree copy",)),
            InvariantGroup("no deployment mutation", (r"no deployment mutation",)),
            InvariantGroup("no self replication", (r"no self-replication",)),
        ),
    ),
)


WORKTREE_CLEANUP_SCENARIOS: tuple[WorktreeCleanupScenario, ...] = (
    WorktreeCleanupScenario(
        name="default dry-run never removes",
        apply=False,
        confirmed=False,
        pr_status="MERGED",
        expected="report_only",
    ),
    WorktreeCleanupScenario(
        name="apply still needs confirmation",
        apply=True,
        confirmed=False,
        pr_status="MERGED",
        expected="needs_user",
    ),
    WorktreeCleanupScenario(
        name="merged clean confirmed removes normally",
        apply=True,
        confirmed=True,
        pr_status="MERGED",
        expected="remove",
    ),
    WorktreeCleanupScenario(
        name="merged dirty requires confirmed force",
        apply=True,
        confirmed=True,
        pr_status="MERGED",
        has_local_changes=True,
        force=True,
        expected="force_remove",
    ),
    WorktreeCleanupScenario(
        name="closed not merged dirty is never removed",
        apply=True,
        confirmed=True,
        pr_status="CLOSED_NOT_MERGED",
        has_local_changes=True,
        force=True,
        expected="needs_user",
    ),
    WorktreeCleanupScenario(
        name="open pr is kept",
        apply=True,
        confirmed=True,
        pr_status="OPEN",
        expected="keep",
    ),
    WorktreeCleanupScenario(
        name="unknown state is not removed",
        apply=True,
        confirmed=True,
        pr_status="MERGED",
        state_known=False,
        expected="needs_user",
    ),
)


FIX_ISSUE_WORKTREE_SCENARIOS: tuple[FixIssueWorktreeScenario, ...] = (
    FixIssueWorktreeScenario("primary worktree add succeeds", True, False, "continue"),
    FixIssueWorktreeScenario("fallback worktree add succeeds", False, True, "continue"),
    FixIssueWorktreeScenario("both worktree attempts fail", False, False, "terminal_stop"),
)


PR_COMMENT_GATE_SCENARIOS: tuple[PrCommentGateScenario, ...] = (
    PrCommentGateScenario("unconfirmed accepted comments stay analysis-only", False, False, 3, "analysis_only"),
    PrCommentGateScenario("report-only skips implementation", True, True, 3, "report_only"),
    PrCommentGateScenario("confirmed accepted comments may execute", True, False, 2, "executor_allowed"),
    PrCommentGateScenario("no accepted comments has no executor work", True, False, 0, "analysis_only"),
)


FORBIDDEN_CHECKS: tuple[ForbiddenPatternCheck, ...] = (
    ForbiddenPatternCheck(
        "fix-issue-forbidden-bulk-stage",
        "issue-evaluator/skills/fix-issue/SKILL.md",
        (r"git\s+add\s+-A",),
    ),
    ForbiddenPatternCheck(
        "fix-issue-forbidden-current-dir-fallback",
        "issue-evaluator/skills/fix-issue/SKILL.md",
        (r"fall back to working in the current directory",),
    ),
    ForbiddenPatternCheck(
        "clean-worktrees-forbidden-force-default",
        "worktree-cleaner/skills/clean-worktrees/SKILL.md",
        (r"Always use `git worktree remove --force`",),
    ),
    ForbiddenPatternCheck(
        "evaluate-issue-forbidden-inline-round2-prompt",
        "issue-evaluator/skills/evaluate-issue/SKILL.md",
        (r"Adversarial review of issue diagnosis for issue #<number>",),
    ),
    ForbiddenPatternCheck(
        "evaluate-issue-forbidden-inline-round3-prompt",
        "issue-evaluator/skills/evaluate-issue/SKILL.md",
        (r"You are the final synthesis agent",),
    ),
    ForbiddenPatternCheck(
        "evaluate-issue-forbidden-inline-final-report-template",
        "issue-evaluator/skills/evaluate-issue/SKILL.md",
        (r"## Issue Evaluation: <issue-title>",),
    ),
    ForbiddenPatternCheck(
        "tool-review-forbidden-inline-report-template",
        "agent-playbook/skills/tool-review/SKILL.md",
        (r"## Review Rounds[\s\S]{0,300}\| 1 \| BOUNDARIES_NAMES",),
    ),
    ForbiddenPatternCheck(
        "context-audit-forbidden-inline-report-template",
        "agent-playbook/skills/context-audit/SKILL.md",
        (r"# Context Audit[\s\S]{0,120}<repo name>",),
    ),
    ForbiddenPatternCheck(
        "vibe-health-forbidden-inline-report-template",
        "agent-playbook/skills/vibe-coding-health-check/SKILL.md",
        (r"# Vibe Coding Health Check - <repo or target>",),
    ),
)


def decide_worktree_cleanup(scenario: WorktreeCleanupScenario) -> str:
    if not scenario.apply:
        return "report_only"
    if scenario.pr_status == "OPEN":
        return "keep"
    if not scenario.state_known:
        return "needs_user"
    if not scenario.confirmed:
        return "needs_user"

    has_local_risk = scenario.has_local_changes or scenario.has_unpushed_commits
    protected_dirty_statuses = {"CLOSED_NOT_MERGED", "NO_PR", "DETACHED", "NO_UPSTREAM"}
    if has_local_risk and scenario.pr_status in protected_dirty_statuses:
        return "needs_user"
    if has_local_risk:
        if scenario.pr_status == "MERGED" and scenario.force:
            return "force_remove"
        return "needs_user"
    return "remove"


def decide_fix_issue_worktree_setup(scenario: FixIssueWorktreeScenario) -> str:
    if scenario.primary_add_ok or scenario.fallback_add_ok:
        return "continue"
    return "terminal_stop"


def decide_pr_comment_gate(scenario: PrCommentGateScenario) -> str:
    if scenario.report_only:
        return "report_only"
    if not scenario.approved_to_edit or scenario.accepted_count == 0:
        return "analysis_only"
    return "executor_allowed"


ALLOWLISTED_BOUNDED_SKILLS = {
    "agent-playbook:commit-changes",
    "agent-playbook:bootstrap-project-memory",
    "agent-playbook:context-audit",
    "agent-playbook:vibe-coding-health-check",
    "agent-playbook:vibe-coding-fix",
    "agent-playbook:implementation-tournament",
    "agent-playbook:tool-review",
}
BANNED_BROAD_ROUTE_TOKENS = {
    "orchestrate",
    "orchestrator",
    "repo-orchestrator",
    "repo-bootstrap",
    "repo-autopilot",
    "autopilot",
    "bootstrap-agent",
    "agent-orchestrator",
    "bootstrap-orchestrator",
    "repo-enable",
    "repo-enabler",
    "repo-driver",
    "project-bootstrap",
    "project-autopilot",
    "workspace-agent",
    "workspace-orchestrator",
}
BROAD_ROUTE_TOKEN_RE = re.compile(
    r"(?:^|[-_])(?:whole[-_]?repo|repo[-_]?(?:bootstrap|runner|driver|autopilot|orchestrate|orchestrator|enable|enabler)|"
    r"orchestrate|orchestrator|autopilot|agent[-_]?orchestrator|bootstrap[-_]?agent|"
    r"bootstrap[-_]?orchestrator|workspace[-_]?agent|workspace[-_]?orchestrator|"
    r"project[-_]?bootstrap|project[-_]?autopilot)(?:$|[-_])",
    re.IGNORECASE,
)
BROAD_TRIGGER_RE = re.compile(
    r"orchestrat|autopilot|(?:repo|repository)[- ](?:bootstrap|runner|driver|enable|enabler|orchestrator|autopilot)|"
    r"repo bootstrap|repo-bootstrap|bootstrap agent|"
    r"agent orchestrator|repo enable|repo enabler|whole[- ]repo|entire[- ]repository|"
    r"bootstrap this repository|workspace agent|project autopilot|run the repo",
    re.IGNORECASE,
)

GITHUB_WORKFLOW_MUTATION_VERBS = (
    r"write|writes|update|updates|modify|modifies|configure|configures|dispatch|dispatches|"
    r"create|creates|add|adds|set\s+up|sets\s+up|setup|setups|manage|manages|author|authors|"
    r"generate|generates|generated|generating|scaffold|scaffolds|scaffolded|scaffolding|"
    r"maintain|maintains|maintained|maintaining"
)
FORBIDDEN_CAPABILITY_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bgit\s+(?:commit|push|tag|merge|checkout\s+-b)\b", re.IGNORECASE),
    re.compile(
        r"\b(?:commit(?!-)|commits|push(?!-)|pushes|tag(?!-)|tags|merge(?!-)|merges)\b[^\n.!?;]{0,80}"
        r"\b(?:changes|code|commits|diff|files|tags|branches|repo|repository|worktree)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bcommit(?:s|ted|ting)?\b[^\n.!?;]{0,80}\bpush(?:es|ed|ing)?\b|"
        r"\bpush(?:es|ed|ing)?\b[^\n.!?;]{0,80}\bcommit(?:s|ted|ting)?\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bgh\s+(?:pr|issue|api)\b[^\n.]{0,160}"
        r"\b(?:create|comment|merge|review|edit|POST|PATCH|PUT|DELETE)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:open|opens|create|creates|post|posts|comment|comments|merge|merges|edit|edits|submit|submits|file|files|raise|raises|approve|approves|close|closes|label|labels)\b"
        r"[^\n.]{0,80}\b(?:PRs?\b|pull requests?\b|issues?\b|GitHub\b)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:create|creates|open|opens|make|makes)\b[^\n.]{0,80}"
        r"\b(?:commits?|branches?|tags?)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\brequest(?:s)?\s+changes\b[^\n.]{0,80}\b(?:PRs?\b|pull requests?\b|GitHub\b)", re.IGNORECASE),
    re.compile(
        r"\b(?:mutate|mutates|change|changes|edit|edits)\b[^\n.]{0,80}"
        r"\b(?:GitHub|CI|deployment|deployments|settings)\b",
        re.IGNORECASE,
    ),
    re.compile(
        rf"\b(?:{GITHUB_WORKFLOW_MUTATION_VERBS})\b"
        r"[^\n.]{0,80}\b(?:GitHub|GitHub Actions|Actions|CI|workflow|workflows|deployment|deployments|settings)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:GitHub|GitHub Actions|Actions|CI|workflow|workflows|deployment|deployments|settings)\b"
        rf"[^\n.]{{0,80}}\b(?:{GITHUB_WORKFLOW_MUTATION_VERBS})\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:GitHub|GitHub Actions|Actions|CI|workflow|workflows|deployment|deployments)\b"
        r"[^\n.]{0,80}\b(?:creation|addition|update|write|dispatch|configuration|modification|setup|management|authoring|generation|scaffolding|maintenance)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(?:create|creates|open|opens|make|makes)\b[^\n.]{0,80}\bdeployments?\b", re.IGNORECASE),
    re.compile(r"\b(?:GitHub|CI|deployment|deployments)\b[^\n.]{0,80}\bmutation\b", re.IGNORECASE),
    re.compile(
        r"\b(?:plugin|plugins|skill|skills)\b[^\n.]{0,80}"
        r"\b(?:install|installs|copy|copies|sync|syncs)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:install|installs|copy|copies|sync|syncs)\b[^\n.]{0,80}"
        r"\b(?:plugin|plugins|skill|skills)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bcache mutation\b", re.IGNORECASE),
    re.compile(r"\b(?:cp|rsync)\b[^\n.]{0,80}\b(?:skills|plugins)\b", re.IGNORECASE),
    re.compile(r"\bcopy\b[^\n.]{0,80}\bskill tree\b", re.IGNORECASE),
    re.compile(r"\b(?:deploy|deploys|deployed|kubectl apply|terraform apply|gh workflow run)\b", re.IGNORECASE),
    re.compile(
        r"\bself[- ]?replicat|\breplicate\b[^\n.]{0,80}\bskill|"
        r"\binstall\b[^\n.]{0,80}\bitself\b",
        re.IGNORECASE,
    ),
)
NEGATION_PHRASE_RE = re.compile(
    r"\b(?:"
    r"(?:do|does|must|should|may|can)\s+(?:\*\*)?not(?:\*\*)?\s+"
    r"|must\s+never\s+"
    r"|(?:cannot|can't)\s+"
    r"|(?:no|never)\s+"
    r"|(?:forbidden|disallowed)(?::\s*|\s+(?:to\s+)?)"
    r"|(?:is|are)\s+not\s+allowed\s+(?:to\s+)?"
    r")",
    re.IGNORECASE,
)
NEGATED_CAPABILITY_CONNECTOR_RE = re.compile(
    r"^(?:"
    r"\s+|,|:|/|-|\band\b|\bor\b|\bto\b|\bauthorize\b|\bauthorizes\b|"
    r"\bgit\b|\bgh\b|\bgithub\b|\bapi\b|\bworkflow\b|"
    r"\bcommit\b|\bcommits\b|\bpush\b|\bpushes\b|\bpost\b|\bposts\b|"
    r"\bcomment\b|\bcomments\b|\bmerge\b|\bmerges\b|\bedit\b|\bedits\b|"
    r"\bcreate\b|\bcreates\b|\bopen\b|\bopens\b|\bsubmit\b|\bsubmits\b|"
    r"\bfile\b|\bfiles\b|\braise\b|\braises\b|\bapprove\b|\bapproves\b|"
    r"\bclose\b|\bcloses\b|\blabel\b|\blabels\b|\btag\b|\btags\b|"
    r"\bbranch\b|\bbranches\b|\binstall\b|\binstalls\b|\bcopy\b|\bcopies\b|"
    r"\bsync\b|\bsyncs\b|\bdeploy\b|\bdeploys\b|\brequest\b|\brequests\b|"
    r"\bchange\b|\bchanges\b|\bpr\b|\bprs\b|\bpull\b|\brequests\b|"
    r"\bissue\b|\bissues\b|\bplugin\b|\bplugins\b|\bskill\b|\bskills\b|"
    r"\bruntime\b|\binstallations\b|\bexternally\b|\ballow\b|\ballows\b|"
    r"\bpermit\b|\bpermits\b|\bauthorization\b|\bauthorized\b|\bpermission\b|\bpermissions\b"
    r")*$",
    re.IGNORECASE,
)


def capability_match_is_negated(text: str, start: int) -> bool:
    prefix = text[max(0, start - 120):start]
    clause_prefix = re.split(r"[.!?;]", prefix)[-1]
    clause_prefix = re.sub(r"[*`_]+", "", clause_prefix)
    matches = list(NEGATION_PHRASE_RE.finditer(clause_prefix))
    if not matches:
        return False
    connector = clause_prefix[matches[-1].end():]
    return bool(NEGATED_CAPABILITY_CONNECTOR_RE.fullmatch(connector))


def has_unsafe_forbidden_capability(text: str) -> bool:
    for pattern in FORBIDDEN_CAPABILITY_PATTERNS:
        for match in pattern.finditer(text):
            if not capability_match_is_negated(text, match.start()):
                return True
    return False


def has_unbounded_broad_trigger(text: str) -> bool:
    for match in BROAD_TRIGGER_RE.finditer(text):
        prefix = text[max(0, match.start() - 120):match.start()]
        suffix = text[match.end():match.end() + 80]
        clause_start = max(text.rfind(separator, 0, match.start()) for separator in ".!?;\n")
        clause_end_candidates = [
            position for separator in ".!?;\n"
            if (position := text.find(separator, match.end())) != -1
        ]
        clause_end = min(clause_end_candidates) if clause_end_candidates else len(text)
        clause = text[clause_start + 1:clause_end]
        safe_bounded_reference = re.search(
            r"\bwithout\s+turning\b[^\n.]{0,80}\binto\s+(?:an?\s+)?(?:unbounded\s+)?$",
            prefix,
            re.IGNORECASE,
        )
        local_window = text[max(0, match.start() - 80):match.end() + 180]
        safe_audit_reference = (
            re.match(r"[- ]?(?:audit|scan|scanning)\b", suffix, re.IGNORECASE)
            and not has_unsafe_forbidden_capability(clause)
            and not has_unsafe_forbidden_capability(local_window)
        )
        if not safe_bounded_reference and not safe_audit_reference and not capability_match_is_negated(text, match.start()):
            return True
    return False


def normalize_broad_route_token(route: str) -> str:
    normalized = route.strip().strip("`").lower().replace("_", "-")
    return re.sub(r"(?<![a-z0-9])repository(?=$|-)", "repo", normalized)


def has_broad_route_token(route: str) -> bool:
    normalized_route = normalize_broad_route_token(route)
    return normalized_route in BANNED_BROAD_ROUTE_TOKENS or bool(BROAD_ROUTE_TOKEN_RE.search(normalized_route))


def broad_orchestrator_violation_reason(entry: BroadOrchestratorEntry) -> str | None:
    route = normalize_broad_route_token(entry.route_token)
    if route in BANNED_BROAD_ROUTE_TOKENS and entry.entry_id not in ALLOWLISTED_BOUNDED_SKILLS:
        return f"banned-route:{route}"
    if (has_unbounded_broad_trigger(entry.text) or has_broad_route_token(route)) and has_unsafe_forbidden_capability(entry.text):
        return f"broad-mutation:{route or 'no-route'}"
    return None


def evaluate_broad_orchestrator_entry(entry: BroadOrchestratorEntry) -> str:
    return "fail" if broad_orchestrator_violation_reason(entry) else "pass"


def normalize_readme_route_token(cell: str) -> str:
    token = cell.strip().strip("`").strip()
    markdown_link = re.fullmatch(r"\[([^\]]+)\]\([^)]+\)", token)
    if markdown_link:
        token = markdown_link.group(1).strip().strip("`").strip()
    return token


def readme_catalog_entries(path: Path) -> list[BroadOrchestratorEntry]:
    entries: list[BroadOrchestratorEntry] = []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    current_heading = ""
    for line_number, line in enumerate(lines, start=1):
        heading = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*$", line)
        if heading:
            current_heading = heading.group(1)

        table_cells = [
            normalize_readme_route_token(cell)
            for cell in line.strip().strip("|").split("|")
        ] if re.match(r"^\s*\|", line) else []
        table_route = table_cells[0] if table_cells and not re.fullmatch(r"-+", table_cells[0]) else ""
        is_entry = (
            "/skills/" in line
            or "$" in line
            or re.search(r"/([A-Za-z0-9_-]+)\b", line)
            or (table_route and has_broad_route_token(table_route))
            or BROAD_TRIGGER_RE.search(line)
            or has_unsafe_forbidden_capability(line)
            or (current_heading and has_broad_route_token(current_heading))
        )
        if not is_entry:
            continue

        if heading and re.search(r"/([A-Za-z0-9_-]+)\b", line):
            block_lines = [line]
            continuation_index = line_number
            while continuation_index < len(lines):
                next_line = lines[continuation_index]
                if re.match(r"^\s{0,3}#{1,6}\s+", next_line):
                    break
                block_lines.append(next_line)
                continuation_index += 1
        elif re.match(r"^\s*\|", line):
            block_lines = [current_heading, line]
        else:
            block_lines = [current_heading, line]
            continuation_index = line_number
            while continuation_index < len(lines):
                next_line = lines[continuation_index]
                if not next_line.strip():
                    break
                if re.match(r"^\s{0,3}#{1,6}\s+", next_line):
                    break
                if re.match(r"^\s*[-*]\s+", next_line) and continuation_index != line_number:
                    break
                if re.match(r"^\s*\|", next_line):
                    break
                block_lines.append(next_line)
                continuation_index += 1
        block = "\n".join(block_lines)
        route_match = re.search(r"([A-Za-z0-9_-]+)/skills/([A-Za-z0-9_-]+)/SKILL\.md", line)
        command_match = re.search(r"\$([A-Za-z0-9_-]+):([A-Za-z0-9_-]+)", line)
        slash_match = re.search(r"/([A-Za-z0-9_-]+)\b", line)
        if route_match:
            entry_id = f"{route_match.group(1)}:{route_match.group(2)}"
            route_token = route_match.group(2)
        elif command_match:
            entry_id = f"{command_match.group(1)}:{command_match.group(2)}"
            route_token = command_match.group(2)
        elif slash_match:
            entry_id = f"{path.name}:line-{line_number}:{slash_match.group(1)}"
            route_token = slash_match.group(1)
        elif table_route:
            entry_id = f"{path.name}:line-{line_number}:{table_route}"
            route_token = table_route
        else:
            entry_id = f"{path.name}:line-{line_number}"
            route_token = current_heading.lower().replace(" ", "-") if current_heading else ""
        entries.append(BroadOrchestratorEntry(entry_id, route_token, block, f"{path}:line-{line_number}"))
    return entries


def plugin_json_entries(path: Path) -> list[BroadOrchestratorEntry]:
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return [BroadOrchestratorEntry(str(path), "", text, str(path))]

    plugin_name = str(data.get("name") or path.parent.parent.name)
    entries = [
        BroadOrchestratorEntry(
            f"{plugin_name}:plugin-json",
            plugin_name,
            f"{data.get('name', '')}\n{data.get('description', '')}",
            str(path),
        )
    ]
    skill_entries = data.get("skills", [])
    if not isinstance(skill_entries, list):
        skill_entries = []
    for skill in skill_entries:
        if not isinstance(skill, dict):
            continue
        route_token = str(skill.get("name") or skill.get("id") or "")
        entries.append(
            BroadOrchestratorEntry(
                f"{plugin_name}:{route_token}",
                route_token,
                json.dumps(skill, sort_keys=True),
                f"{path}:skill:{route_token}",
            )
        )
    return entries


def marketplace_json_entries(path: Path) -> list[BroadOrchestratorEntry]:
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return [BroadOrchestratorEntry(".claude-plugin:marketplace", "marketplace", text, str(path))]

    entries: list[BroadOrchestratorEntry] = []
    plugins = data.get("plugins", [])
    if not isinstance(plugins, list):
        return entries
    for plugin in plugins:
        if not isinstance(plugin, dict):
            continue
        route_token = str(plugin.get("name") or "")
        entries.append(
            BroadOrchestratorEntry(
                f"marketplace:{route_token}",
                route_token,
                json.dumps(plugin, sort_keys=True),
                f"{path}:plugin:{route_token}",
            )
        )
    return entries


def skill_frontmatter_name(text: str) -> str | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = re.match(r"^\s*name\s*:\s*['\"]?([^'\"#\n]+)", line)
        if match:
            return match.group(1).strip()
    return None


def first_broad_orchestrator_anchor(text: str, route_token: str) -> int:
    normalized_route = normalize_broad_route_token(route_token)
    for line_number, line in enumerate(text.splitlines(), start=1):
        normalized_line = normalize_broad_route_token(line)
        route_on_line = normalized_route and normalized_route in normalized_line and has_broad_route_token(normalized_route)
        if route_on_line or has_unbounded_broad_trigger(line) or has_unsafe_forbidden_capability(line):
            return line_number
    return 1


def markdown_semantic_entries(entry_id: str, route_token: str, text: str, source_path: str) -> list[BroadOrchestratorEntry]:
    document_anchor = first_broad_orchestrator_anchor(text, route_token)
    entries = [BroadOrchestratorEntry(f"{entry_id}:document", route_token, text, f"{source_path}:line-{document_anchor}:document")]
    blocks: list[tuple[int, str]] = []
    current: list[str] = []
    current_start = 1
    for line_number, line in enumerate(text.splitlines(), start=1):
        if re.match(r"^\s{0,3}#{1,6}\s+", line) and current:
            blocks.append((current_start, "\n".join(current)))
            current = [line]
            current_start = line_number
        else:
            if not current:
                current_start = line_number
            current.append(line)
    if current:
        blocks.append((current_start, "\n".join(current)))

    entries.extend(
        BroadOrchestratorEntry(f"{entry_id}:block-{index}", route_token, block, f"{source_path}:line-{line_number}")
        for index, (line_number, block) in enumerate(blocks, start=1)
    )
    return entries


def extract_broad_orchestrator_entries(root: Path) -> list[BroadOrchestratorEntry]:
    entries: list[BroadOrchestratorEntry] = []

    for path in sorted(root.glob("*/skills/*/SKILL.md")):
        relative = path.relative_to(root)
        plugin, skill = relative.parts[0], relative.parts[2]
        text = path.read_text(encoding="utf-8", errors="replace")
        route_tokens = {skill}
        frontmatter_name = skill_frontmatter_name(text)
        if frontmatter_name:
            route_tokens.add(frontmatter_name)
        for route_token in sorted(route_tokens):
            entries.extend(markdown_semantic_entries(f"{plugin}:{route_token}", route_token, text, str(relative)))

    for path in sorted(root.glob("*/skills/*/agents/openai.yaml")):
        relative = path.relative_to(root)
        plugin, skill = relative.parts[0], relative.parts[2]
        text = path.read_text(encoding="utf-8", errors="replace")
        command_match = re.search(r"\$([A-Za-z0-9_-]+):([A-Za-z0-9_-]+)", text)
        route_token = command_match.group(2) if command_match else skill
        entries.append(BroadOrchestratorEntry(f"{plugin}:{skill}:openai", route_token, text, str(relative)))

    readme_paths = sorted(root.glob("*/README.md")) + [root / "README.md"]
    for path in readme_paths:
        if path.is_file():
            entries.extend(readme_catalog_entries(path))

    for path in sorted(root.glob("*/.claude-plugin/plugin.json")):
        entries.extend(plugin_json_entries(path))

    marketplace_path = root / ".claude-plugin" / "marketplace.json"
    if marketplace_path.is_file():
        entries.extend(marketplace_json_entries(marketplace_path))

    return entries


BROAD_ORCHESTRATOR_SCENARIOS: tuple[BroadOrchestratorScenario, ...] = (
    BroadOrchestratorScenario(
        "banned route with git push fails",
        BroadOrchestratorEntry("agent-playbook:repo-autopilot", "repo-autopilot", "run the repo and git push"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "far apart trigger and mutation fails",
        BroadOrchestratorEntry(
            "agent-playbook:whole-repo-runner",
            "whole-repo-runner",
            "whole repo orchestrator\n" + ("safe filler " * 80) + "\ngit push",
        ),
        "fail",
    ),
    BroadOrchestratorScenario(
        "whole repo hyphenated prose with git push fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole-repo helper can git push changes"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "entire repository hyphenated prose with git push fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "entire-repository helper can git push changes"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "whole repo audit with git push fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole-repo audit can git push changes"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "whole repo audit adjacent git push fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole-repo audit. It can git push changes."),
        "fail",
    ),
    BroadOrchestratorScenario(
        "broad route variant without text trigger fails",
        BroadOrchestratorEntry("agent-playbook:whole-repo-runner", "whole-repo-runner", "can git push changes"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "repository bootstrap route variant fails",
        BroadOrchestratorEntry("agent-playbook:repository-bootstrap", "repository-bootstrap", "can git push changes"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "repository driver route variant fails",
        BroadOrchestratorEntry("agent-playbook:repository-driver", "repository-driver", "can git push changes"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "repository runner route variant fails",
        BroadOrchestratorEntry("agent-playbook:repository-runner", "repository-runner", "can git push changes"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "repository orchestrator route variant fails",
        BroadOrchestratorEntry("agent-playbook:repository-orchestrator", "repository-orchestrator", "can git push changes"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "repository autopilot route variant fails",
        BroadOrchestratorEntry("agent-playbook:repository-autopilot", "repository-autopilot", "can git push changes"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "repository enabler route variant fails",
        BroadOrchestratorEntry("agent-playbook:repository-enabler", "repository-enabler", "can git push changes"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "repo enable route variant fails",
        BroadOrchestratorEntry("agent-playbook:repo-enable", "repo-enable", "can install plugins"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "repository enable route variant fails",
        BroadOrchestratorEntry("agent-playbook:repository-enable", "repository-enable", "can install plugins"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "repo orchestrate route variant fails",
        BroadOrchestratorEntry("agent-playbook:repo-orchestrate", "repo-orchestrate", "can git push changes"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "underscore repo enabler route variant fails",
        BroadOrchestratorEntry("agent-playbook:repo_enabler", "repo_enabler", "can git push changes"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "underscore agent orchestrator route variant fails",
        BroadOrchestratorEntry("agent-playbook:agent_orchestrator", "agent_orchestrator", "can git push changes"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "underscore bootstrap orchestrator route variant fails",
        BroadOrchestratorEntry("agent-playbook:bootstrap_orchestrator", "bootstrap_orchestrator", "can git push changes"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "underscore project bootstrap route variant fails",
        BroadOrchestratorEntry("agent-playbook:project_bootstrap", "project_bootstrap", "can git push changes"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "readme slash route with mutation fails",
        BroadOrchestratorEntry("README:line-1:repo-bootstrap", "repo-bootstrap", "### /repo-bootstrap\n\nCan git push changes."),
        "fail",
    ),
    BroadOrchestratorScenario(
        "allowlisted skill with new broad git push fails",
        BroadOrchestratorEntry("agent-playbook:commit-changes", "commit-changes", "whole repo orchestrator may git push"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "synonym route with plugin install fails",
        BroadOrchestratorEntry("agent-playbook:repo-enabler", "repo-enabler", "repo enable workflow can install plugins"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "repository enabler prose with git push fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "repository enabler can git push changes"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "repo enable prose with plugin install fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "repo-enable workflow can install plugins"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "repository enable prose with plugin install fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "repository-enable workflow can install plugins"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "repository bootstrap prose with git push fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "repository bootstrap workflow can git push changes"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "repo driver prose with git push fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "repo driver can git push changes"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "repo runner prose with git push fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "repo runner can git push changes"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "broad trigger install plugins word order fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo helper can install plugins and copy skills"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "marketplace forbidden plugin fails",
        BroadOrchestratorEntry(
            "marketplace:repo-autopilot",
            "repo-autopilot",
            '{"name": "repo-autopilot", "description": "entire repository autopilot can git push"}',
        ),
        "fail",
    ),
    BroadOrchestratorScenario(
        "natural language github write fails",
        BroadOrchestratorEntry(
            "marketplace:repo-reviewer",
            "repo-reviewer",
            "entire repository autopilot opens PRs and comments on issues",
        ),
        "fail",
    ),
    BroadOrchestratorScenario(
        "natural language files issues fails",
        BroadOrchestratorEntry("marketplace:repo-triage", "repo-triage", "whole repo autopilot files issues"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "natural language raises pull requests fails",
        BroadOrchestratorEntry("marketplace:repo-prs", "repo-prs", "entire repository autopilot raises pull requests"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "natural language commit and push changes fails",
        BroadOrchestratorEntry("marketplace:repo-committer", "repo-committer", "whole repo helper can commit and push changes"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "natural language commits code and pushes it fails",
        BroadOrchestratorEntry("marketplace:repo-committer", "repo-committer", "whole repo autopilot commits code and pushes it"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "negated safety boundary language passes",
        BroadOrchestratorEntry(
            "agent-playbook:repo-helper",
            "repo-helper",
            "whole repo orchestration boundary: must not git push or deploy",
        ),
        "pass",
    ),
    BroadOrchestratorScenario(
        "unrelated do not forget git push fails",
        BroadOrchestratorEntry(
            "agent-playbook:repo-helper",
            "repo-helper",
            "whole repo helper. Do not forget to git push changes.",
        ),
        "fail",
    ),
    BroadOrchestratorScenario(
        "unrelated do not ignore errors git push fails",
        BroadOrchestratorEntry(
            "agent-playbook:repo-helper",
            "repo-helper",
            "whole repo helper. Do not ignore errors. It can git push changes.",
        ),
        "fail",
    ),
    BroadOrchestratorScenario(
        "not only git push fails",
        BroadOrchestratorEntry(
            "agent-playbook:repo-helper",
            "repo-helper",
            "whole repo helper not only audits, it can git push changes.",
        ),
        "fail",
    ),
    BroadOrchestratorScenario(
        "without asking git push fails",
        BroadOrchestratorEntry(
            "agent-playbook:repo-helper",
            "repo-helper",
            "whole repo helper without asking can git push changes.",
        ),
        "fail",
    ),
    BroadOrchestratorScenario(
        "do not just audit git push fails",
        BroadOrchestratorEntry(
            "agent-playbook:repo-helper",
            "repo-helper",
            "whole repo helper. Do not just audit, git push changes.",
        ),
        "fail",
    ),
    BroadOrchestratorScenario(
        "do not merely audit git push fails",
        BroadOrchestratorEntry(
            "agent-playbook:repo-helper",
            "repo-helper",
            "whole repo helper. Do not merely audit, git push changes.",
        ),
        "fail",
    ),
    BroadOrchestratorScenario(
        "no tests can git push fails",
        BroadOrchestratorEntry(
            "agent-playbook:repo-helper",
            "repo-helper",
            "whole repo helper, no tests, can git push changes.",
        ),
        "fail",
    ),
    BroadOrchestratorScenario(
        "must not ask can git push fails",
        BroadOrchestratorEntry(
            "agent-playbook:repo-helper",
            "repo-helper",
            "whole repo helper must not ask, can git push changes.",
        ),
        "fail",
    ),
    BroadOrchestratorScenario(
        "natural language creates commits fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo helper creates commits"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "natural language creates branches fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo helper creates branches"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "literal mutate github fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo autopilot can mutate GitHub"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "literal github mutation fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo autopilot allows GitHub mutation"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "literal change github settings fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo autopilot can change GitHub settings"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "literal ci mutation fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo autopilot allows CI mutation"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "literal deployment mutation fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo autopilot allows deployment mutation"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "literal github writes fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo autopilot performs GitHub writes"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "literal updates ci workflows fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo autopilot updates CI workflows"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "literal creates ci workflows fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo autopilot creates CI workflows"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "literal adds github actions workflows fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo autopilot adds GitHub Actions workflows"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "literal sets up github actions workflows fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo autopilot sets up GitHub Actions workflows"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "literal manages ci workflows fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo autopilot manages CI workflows"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "literal generates github actions workflows fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo autopilot generates GitHub Actions workflows"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "literal maintains ci workflows fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo autopilot maintains CI workflows"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "literal scaffolds github workflows fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo autopilot scaffolds GitHub workflows"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "literal github workflow setup fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo autopilot performs GitHub workflow setup"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "literal ci workflow creation fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo autopilot performs CI workflow creation"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "literal github workflow addition fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo autopilot performs GitHub workflow addition"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "literal github workflow creation fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo autopilot performs GitHub workflow creation"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "literal updates deployment settings fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo autopilot updates deployment settings"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "literal modifies deployment settings fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo autopilot modifies deployment settings"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "literal configures deployment settings fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo autopilot configures deployment settings"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "literal dispatches github actions workflows fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo autopilot dispatches GitHub Actions workflows"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "literal creates deployments fails",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo autopilot creates deployments"),
        "fail",
    ),
    BroadOrchestratorScenario(
        "forbidden colon safety boundary passes",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo boundary. Forbidden: git push or deploy."),
        "pass",
    ),
    BroadOrchestratorScenario(
        "markdown bold not commit or push safety boundary passes",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo boundary. Do **not** commit or push."),
        "pass",
    ),
    BroadOrchestratorScenario(
        "markdown bold capability safety boundary passes",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo boundary. Do not **commit** or **push**."),
        "pass",
    ),
    BroadOrchestratorScenario(
        "markdown code capability safety boundary passes",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo boundary. Do not `git push`."),
        "pass",
    ),
    BroadOrchestratorScenario(
        "must not allow git push safety boundary passes",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo boundary. Must not allow git push."),
        "pass",
    ),
    BroadOrchestratorScenario(
        "no authorization git push safety boundary passes",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo boundary. No authorization to git push."),
        "pass",
    ),
    BroadOrchestratorScenario(
        "request changes from user passes",
        BroadOrchestratorEntry("agent-playbook:repo-helper", "repo-helper", "whole repo intake may request changes from the user."),
        "pass",
    ),
    BroadOrchestratorScenario(
        "bounded whole repo audit reference passes",
        BroadOrchestratorEntry(
            "secret-scanner:scan-secrets",
            "scan-secrets",
            'Diff-only scanning asks "is my next commit safe?" For a whole-repo audit, run with --full-file.',
        ),
        "pass",
    ),
    BroadOrchestratorScenario(
        "unchanged allowlisted bounded commit skill passes",
        BroadOrchestratorEntry("agent-playbook:commit-changes", "commit-changes", "create a local commit and optional draft PR"),
        "pass",
    ),
)


def usage() -> None:
    print("Usage: agent-playbook-eval-fixtures.py <repo-root>", file=sys.stderr)


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        print(f"Missing required file: {relative_path}", file=sys.stderr)
        raise SystemExit(2)
    return path.read_text(encoding="utf-8", errors="replace")


def group_matches(text: str, group: InvariantGroup) -> bool:
    return any(
        re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        for pattern in group.patterns
    )


def run_check(root: Path, check: ContractCheck) -> list[str]:
    text = read_text(root, check.relative_path)
    failures: list[str] = []
    for group in check.groups:
        if not group_matches(text, group):
            failures.append(group.name)
    return failures


def run_forbidden_check(root: Path, check: ForbiddenPatternCheck) -> list[str]:
    text = read_text(root, check.relative_path)
    failures: list[str] = []
    for pattern in check.patterns:
        if re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL):
            failures.append(pattern)
    return failures


def validate_openai_yaml(text: str) -> list[str]:
    lines = text.splitlines()
    failures: list[str] = []
    if not lines or lines[0].strip() != "interface:":
        return ["missing top-level interface mapping"]

    fields: dict[str, str] = {}
    for line in lines[1:]:
        if not line.strip():
            continue
        match = re.match(r'^  ([A-Za-z_][A-Za-z0-9_]*)\s*:\s*"(.*)"\s*$', line)
        if not match:
            failures.append(f"malformed line: {line.strip()}")
            continue
        fields[match.group(1)] = match.group(2)

    for field in ("display_name", "short_description", "default_prompt"):
        if not fields.get(field):
            failures.append(f"missing {field}")

    short_description = fields.get("short_description", "")
    if short_description and not 25 <= len(short_description) <= 64:
        failures.append("short_description length outside 25-64")

    default_prompt = fields.get("default_prompt", "")
    if default_prompt and "$" not in default_prompt:
        failures.append("default_prompt missing $skill reference")

    return failures


def run_metadata_checks(root: Path) -> list[tuple[str, str | None]]:
    results: list[tuple[str, str | None]] = []
    metadata_files = sorted(root.glob("*/skills/*/agents/openai.yaml"))
    if not metadata_files:
        return [("openai-yaml-discovery", "no agents/openai.yaml files found")]

    results.append(("openai-yaml-discovery", None))
    for path in metadata_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        failures = validate_openai_yaml(text)
        relative = path.relative_to(root)
        check_id = f"openai-yaml-{relative.parts[0]}-{relative.parts[2]}"
        if failures:
            results.append((check_id, ", ".join(failures)))
        else:
            results.append((check_id, None))
    return results


def run_behavior_scenarios() -> list[tuple[str, str | None]]:
    results: list[tuple[str, str | None]] = []

    for scenario in WORKTREE_CLEANUP_SCENARIOS:
        actual = decide_worktree_cleanup(scenario)
        check_id = f"worktree-cleaner-behavior-{scenario.name.replace(' ', '-')}"
        if actual == scenario.expected:
            results.append((check_id, None))
        else:
            results.append((check_id, f"expected {scenario.expected}, got {actual}"))

    for scenario in FIX_ISSUE_WORKTREE_SCENARIOS:
        actual = decide_fix_issue_worktree_setup(scenario)
        check_id = f"fix-issue-worktree-behavior-{scenario.name.replace(' ', '-')}"
        if actual == scenario.expected:
            results.append((check_id, None))
        else:
            results.append((check_id, f"expected {scenario.expected}, got {actual}"))

    for scenario in PR_COMMENT_GATE_SCENARIOS:
        actual = decide_pr_comment_gate(scenario)
        check_id = f"fix-pr-comments-gate-behavior-{scenario.name.replace(' ', '-')}"
        if actual == scenario.expected:
            results.append((check_id, None))
        else:
            results.append((check_id, f"expected {scenario.expected}, got {actual}"))

    return results


def run_broad_orchestrator_checks(root: Path) -> list[tuple[str, str | None]]:
    results: list[tuple[str, str | None]] = []

    for scenario in BROAD_ORCHESTRATOR_SCENARIOS:
        actual = evaluate_broad_orchestrator_entry(scenario.entry)
        check_id = f"broad-orchestrator-scenario-{scenario.name.replace(' ', '-')}"
        if actual == scenario.expected:
            results.append((check_id, None))
        else:
            results.append((check_id, f"expected {scenario.expected}, got {actual}"))

    violations = [
        (entry, broad_orchestrator_violation_reason(entry))
        for entry in extract_broad_orchestrator_entries(root)
        if broad_orchestrator_violation_reason(entry)
    ]
    if violations:
        evidence = [
            f"{entry.source_ref or entry.entry_id}: {entry.entry_id} [{reason}]"
            for entry, reason in violations
        ]
        results.append(
            (
                "broad-orchestrator-repo-scan",
                "forbidden broad orchestrator entry: " + ", ".join(sorted(set(evidence))),
            )
        )
    else:
        results.append(("broad-orchestrator-repo-scan", None))

    with TemporaryDirectory(prefix="agent-playbook-readme-scan-") as tmp:
        readme = Path(tmp) / "README.md"
        readme.write_text(
            "# Catalog\n\n"
            "| Skill | Purpose |\n"
            "|---|---|\n"
            "| $agent-playbook:repo-helper | whole repo inventory only |\n"
            "| commit helper | may say git push in an unrelated row |\n",
            encoding="utf-8",
        )
        parsed = readme_catalog_entries(readme)
        false_positive = any(evaluate_broad_orchestrator_entry(entry) == "fail" for entry in parsed)
        if not parsed:
            results.append(("broad-orchestrator-readme-table-row-isolation", "fixture README row was not parsed"))
        elif false_positive:
            results.append(("broad-orchestrator-readme-table-row-isolation", "adjacent table rows were combined"))
        else:
            results.append(("broad-orchestrator-readme-table-row-isolation", None))

    with TemporaryDirectory(prefix="agent-playbook-skill-doc-scan-") as tmp:
        root = Path(tmp)
        skill_dir = root / "demo" / "skills" / "repo-helper"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\n"
            "name: repo-helper\n"
            "description: Whole repo helper fixture.\n"
            "---\n\n"
            "# Repo Helper\n\n"
            "This is a whole repo orchestrator.\n\n"
            "## Workflow\n\n"
            "It can git push changes.\n",
            encoding="utf-8",
        )
        violations = [
            entry
            for entry in extract_broad_orchestrator_entries(root)
            if evaluate_broad_orchestrator_entry(entry) == "fail"
        ]
        if violations and all(":line-" in entry.source_ref for entry in violations):
            results.append(("broad-orchestrator-skill-document-cross-section", None))
        elif violations:
            results.append(("broad-orchestrator-skill-document-cross-section", "cross-section violation was not line-anchored"))
        else:
            results.append(("broad-orchestrator-skill-document-cross-section", "cross-section trigger and mutation passed"))

    with TemporaryDirectory(prefix="agent-playbook-frontmatter-scan-") as tmp:
        root = Path(tmp)
        skill_dir = root / "demo" / "skills" / "repo-helper"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\n"
            "name: repo-autopilot\n"
            "description: Banned exposed route fixture.\n"
            "---\n\n"
            "# Repo Helper\n",
            encoding="utf-8",
        )
        violations = [
            entry.entry_id
            for entry in extract_broad_orchestrator_entries(root)
            if evaluate_broad_orchestrator_entry(entry) == "fail"
        ]
        if violations:
            results.append(("broad-orchestrator-frontmatter-route-scan", None))
        else:
            results.append(("broad-orchestrator-frontmatter-route-scan", "frontmatter route token was not scanned"))

    with TemporaryDirectory(prefix="agent-playbook-readme-heading-scan-") as tmp:
        root = Path(tmp)
        readme = root / "README.md"
        readme.write_text(
            "# Catalog\n\n"
            "### /repo-helper\n\n"
            "Whole repo orchestrator can git push changes.\n",
            encoding="utf-8",
        )
        violations = [
            entry.entry_id
            for entry in extract_broad_orchestrator_entries(root)
            if evaluate_broad_orchestrator_entry(entry) == "fail"
        ]
        if violations:
            results.append(("broad-orchestrator-readme-heading-paragraph-scan", None))
        else:
            results.append(("broad-orchestrator-readme-heading-paragraph-scan", "heading paragraph was not scanned"))

    with TemporaryDirectory(prefix="agent-playbook-readme-row-scan-") as tmp:
        root = Path(tmp)
        readme = root / "README.md"
        readme.write_text(
            "# Catalog\n\n"
            "| Skill | Purpose |\n"
            "|---|---|\n"
            "| repo-helper | whole repo orchestrator can git push changes |\n",
            encoding="utf-8",
        )
        violations = [
            entry.entry_id
            for entry in extract_broad_orchestrator_entries(root)
            if evaluate_broad_orchestrator_entry(entry) == "fail"
        ]
        if violations:
            results.append(("broad-orchestrator-readme-plain-row-scan", None))
        else:
            results.append(("broad-orchestrator-readme-plain-row-scan", "plain README row was not scanned"))

    with TemporaryDirectory(prefix="agent-playbook-readme-route-row-") as tmp:
        root = Path(tmp)
        readme = root / "README.md"
        readme.write_text(
            "# Catalog\n\n"
            "| Skill | Purpose |\n"
            "|---|---|\n"
            "| repo-autopilot | inventory only |\n"
            "| repository-bootstrap | can git push changes |\n",
            encoding="utf-8",
        )
        violations = [
            entry.entry_id
            for entry in extract_broad_orchestrator_entries(root)
            if evaluate_broad_orchestrator_entry(entry) == "fail"
        ]
        if any("repo-autopilot" in violation for violation in violations) and any(
            "repository-bootstrap" in violation for violation in violations
        ):
            results.append(("broad-orchestrator-readme-route-column-scan", None))
        else:
            results.append(("broad-orchestrator-readme-route-column-scan", "README first-column route token was not scanned"))

    with TemporaryDirectory(prefix="agent-playbook-readme-link-route-") as tmp:
        root = Path(tmp)
        readme = root / "README.md"
        readme.write_text(
            "# Catalog\n\n"
            "| Skill | Purpose |\n"
            "|---|---|\n"
            "| [repo-autopilot](#repo-autopilot) | inventory only |\n",
            encoding="utf-8",
        )
        violations = [
            entry.entry_id
            for entry in extract_broad_orchestrator_entries(root)
            if evaluate_broad_orchestrator_entry(entry) == "fail"
        ]
        if any("repo-autopilot" in violation for violation in violations):
            results.append(("broad-orchestrator-readme-markdown-link-route-scan", None))
        else:
            results.append(("broad-orchestrator-readme-markdown-link-route-scan", "Markdown link route label was not scanned"))

    with TemporaryDirectory(prefix="agent-playbook-readme-route-only-") as tmp:
        root = Path(tmp)
        readme = root / "README.md"
        banned_route_tokens = (
            "repo-driver",
            "repo-enabler",
            "repo-enable",
            "repository-enable",
            "bootstrap-agent",
            "project-bootstrap",
            "workspace-agent",
        )
        readme.write_text(
            "# Catalog\n\n"
            "| Skill | Purpose |\n"
            "|---|---|\n"
            + "".join(f"| {token} | inventory only |\n" for token in banned_route_tokens),
            encoding="utf-8",
        )
        violations = [
            entry.entry_id
            for entry in extract_broad_orchestrator_entries(root)
            if evaluate_broad_orchestrator_entry(entry) == "fail"
        ]
        missing = [token for token in banned_route_tokens if not any(token in violation for violation in violations)]
        if not missing:
            results.append(("broad-orchestrator-readme-route-only-banned-scan", None))
        else:
            results.append(("broad-orchestrator-readme-route-only-banned-scan", f"route-only token(s) not scanned: {', '.join(missing)}"))

    with TemporaryDirectory(prefix="agent-playbook-readme-negated-scan-") as tmp:
        root = Path(tmp)
        readme = root / "README.md"
        readme.write_text(
            "# Catalog\n\n"
            "### /repo-helper\n\n"
            "Whole repo orchestration boundary: must not git push or deploy.\n",
            encoding="utf-8",
        )
        false_positive = any(
            evaluate_broad_orchestrator_entry(entry) == "fail"
            for entry in extract_broad_orchestrator_entries(root)
        )
        if false_positive:
            results.append(("broad-orchestrator-negated-safety-boundary", "negated boundary was treated as capability"))
        else:
            results.append(("broad-orchestrator-negated-safety-boundary", None))

    with TemporaryDirectory(prefix="agent-playbook-readme-forbidden-colon-") as tmp:
        root = Path(tmp)
        readme = root / "README.md"
        readme.write_text(
            "# Catalog\n\n"
            "### /repo-helper\n\n"
            "Whole repo orchestration boundary. Forbidden: git push or deploy.\n",
            encoding="utf-8",
        )
        false_positive = any(
            evaluate_broad_orchestrator_entry(entry) == "fail"
            for entry in extract_broad_orchestrator_entries(root)
        )
        if false_positive:
            results.append(("broad-orchestrator-forbidden-colon-boundary", "forbidden colon boundary was treated as capability"))
        else:
            results.append(("broad-orchestrator-forbidden-colon-boundary", None))

    return results


def run_all(root: Path, checks: Iterable[ContractCheck]) -> int:
    failures = 0
    print("Agent-playbook contract fixtures")
    for check in checks:
        missing = run_check(root, check)
        if missing:
            failures += 1
            print(f"FAIL {check.check_id}: missing invariant group(s): {', '.join(missing)}")
        else:
            print(f"PASS {check.check_id}: contract fixture coverage present")

    print("Agent-playbook forbidden-pattern fixtures")
    for check in FORBIDDEN_CHECKS:
        present = run_forbidden_check(root, check)
        if present:
            failures += 1
            print(f"FAIL {check.check_id}: forbidden pattern(s) present: {', '.join(present)}")
        else:
            print(f"PASS {check.check_id}: forbidden pattern absent")

    print("Agent-playbook behavior scenario fixtures")
    for check_id, failure in run_behavior_scenarios():
        if failure:
            failures += 1
            print(f"FAIL {check_id}: {failure}")
        else:
            print(f"PASS {check_id}: behavior scenario passed")

    print("Agent-playbook broad-orchestrator fixtures")
    for check_id, failure in run_broad_orchestrator_checks(root):
        if failure:
            failures += 1
            print(f"FAIL {check_id}: {failure}")
        else:
            print(f"PASS {check_id}: broad-orchestrator scenario passed")

    print("Agent-playbook metadata fixtures")
    for check_id, failure in run_metadata_checks(root):
        if failure:
            failures += 1
            print(f"FAIL {check_id}: {failure}")
        else:
            print(f"PASS {check_id}: metadata coverage present")

    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        usage()
        return 2

    root = Path(argv[1]).resolve()
    if not root.is_dir():
        print(f"Repo root is not a directory: {root}", file=sys.stderr)
        return 2

    return run_all(root, CHECKS)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
