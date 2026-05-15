#!/usr/bin/env python3
"""Offline contract fixtures for critical agent-playbook workflows."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
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
