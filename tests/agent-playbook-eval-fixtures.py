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
            InvariantGroup("truncation contract", (r"Token budget", r"truncated: true")),
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
        ),
    ),
    ContractCheck(
        "high-risk-token-budget-contract",
        "issue-evaluator/skills/review-pr/SKILL.md",
        (
            InvariantGroup("token budget", (r"Token budget",)),
            InvariantGroup("truncated marker", (r"truncated:\s*true",)),
            InvariantGroup("next action", (r"next_action",)),
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
            InvariantGroup("token budget", (r"Token budget", r"truncated: true")),
        ),
    ),
    ContractCheck(
        "antifragile-readonly-budget-contract",
        "antifragile/skills/antifragile-agent/SKILL.md",
        (
            InvariantGroup("read only", (r"read-only",)),
            InvariantGroup("stdout only", (r"stdout", r"outputs_written: \[\]")),
            InvariantGroup("token budget", (r"Token budget", r"truncated: true")),
            InvariantGroup("typed errors", (r"retryable \| terminal \| needs_user \| degraded",)),
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
