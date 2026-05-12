#!/usr/bin/env python3
"""Offline contract fixtures for critical idea-to-ship skill workflows."""

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
    skill_path: str
    groups: tuple[InvariantGroup, ...]


CHECKS: tuple[ContractCheck, ...] = (
    ContractCheck(
        "brainstorm-mandatory-readme-contract",
        "idea-to-ship/README.md",
        (
            InvariantGroup("mandatory brainstorm", (r"mandatory brainstorm", r"do not skip `/brainstorm`")),
            InvariantGroup("downstream stop", (r"requirements\.md` is missing.{0,160}downstream skills stop",)),
            InvariantGroup("roadmap boundary", (r"Roadmaps can sequence work.{0,180}do not replace",)),
        ),
    ),
    ContractCheck(
        "brainstorm-mandatory-skill-contract",
        "idea-to-ship/skills/brainstorm/SKILL.md",
        (
            InvariantGroup("mandatory first stage", (r"mandatory first stage",)),
            InvariantGroup("downstream skills stop", (r"Downstream skills.{0,160}must stop",)),
            InvariantGroup("roadmap does not replace", (r"roadmap.{0,80}does not replace",)),
        ),
    ),
    ContractCheck(
        "architect-requires-brainstorm-contract",
        "idea-to-ship/skills/architect/SKILL.md",
        (
            InvariantGroup("requires requirements", (r"Require `requirements\.md`",)),
            InvariantGroup("run brainstorm when missing", (r"/brainstorm --slug <slug>",)),
            InvariantGroup("thin requirements return to brainstorm", (r"thin.{0,160}/brainstorm --slug <slug>",)),
        ),
    ),
    ContractCheck(
        "test-requires-brainstorm-contract",
        "idea-to-ship/skills/test/SKILL.md",
        (
            InvariantGroup("requires requirements", (r"Require `requirements\.md`",)),
            InvariantGroup("run brainstorm when missing", (r"/brainstorm --slug <slug>",)),
            InvariantGroup("no diff substitute", (r"not substitutes for brainstormed requirements", r"not.*substitute.*requirements")),
        ),
    ),
    ContractCheck(
        "review-code-requires-brainstorm-contract",
        "idea-to-ship/skills/review-code/SKILL.md",
        (
            InvariantGroup("requires requirements", (r"Require `requirements\.md`",)),
            InvariantGroup("run brainstorm when missing", (r"/brainstorm --slug <slug>",)),
            InvariantGroup("required context", (r"Requirements \(required context\)",)),
        ),
    ),
    ContractCheck(
        "roadmap-does-not-replace-brainstorm-contract",
        "idea-to-ship/skills/roadmap/SKILL.md",
        (
            InvariantGroup("roadmap boundary", (r"Roadmap does not replace `/brainstorm`",)),
            InvariantGroup("slug mode requirements", (r"In slug mode.{0,180}requirements\.md",)),
            InvariantGroup("portfolio next action", (r"portfolio mode.{0,260}/brainstorm --slug <slug>",)),
        ),
    ),
    ContractCheck(
        "roadmap-first-run-contract",
        "idea-to-ship/skills/roadmap/SKILL.md",
        (
            InvariantGroup(
                "first-run candidate brief target",
                (r"first run.{0,240}candidate brief.{0,240}write_target",),
            ),
        ),
    ),
    ContractCheck(
        "roadmap-rerun-preservation-contract",
        "idea-to-ship/skills/roadmap/SKILL.md",
        (
            InvariantGroup("rerun or refresh", (r"\brerun\b", r"\brefresh\b")),
            InvariantGroup(
                "human content preservation",
                (r"human content", r"human-owned content", r"human edits"),
            ),
            InvariantGroup(
                "marker merge or draft fallback",
                (r"generated markers", r"roadmap\.draft\.md", r"\bdraft\.md\b"),
            ),
        ),
    ),
    ContractCheck(
        "roadmap-final-without-approval-contract",
        "idea-to-ship/skills/roadmap/SKILL.md",
        (
            InvariantGroup("final mode", (r"--final",)),
            InvariantGroup("priority approval", (r"priority approval",)),
            InvariantGroup(
                "blocked final lanes",
                (r"final .*lanes are not\s+written", r"without .*approval", r"ask .*approval"),
            ),
        ),
    ),
    ContractCheck(
        "test-story-traceability-contract",
        "idea-to-ship/skills/test/SKILL.md",
        (
            InvariantGroup("user stories", (r"user stories",)),
            InvariantGroup("acceptance criteria", (r"acceptance criteria",)),
            InvariantGroup("scenario matrix", (r"scenario matrix",)),
            InvariantGroup("test matrix", (r"test matrix",)),
            InvariantGroup("test layer split", (r"unit\s*/\s*integration\s*/\s*e2e",)),
        ),
    ),
    ContractCheck(
        "test-negative-scenarios-contract",
        "idea-to-ship/skills/test/SKILL.md",
        (
            InvariantGroup("happy path", (r"happy path",)),
            InvariantGroup("edge or corner cases", (r"edge/corner", r"corner / boundary", r"edge cases")),
            InvariantGroup(
                "invalid or abnormal input",
                (r"invalid / abnormal input", r"invalid-input", r"malformed input"),
            ),
            InvariantGroup("failure modes", (r"failure modes", r"failure-mode")),
        ),
    ),
    ContractCheck(
        "review-code-missing-test-plan-contract",
        "idea-to-ship/skills/review-code/SKILL.md",
        (
            InvariantGroup("missing test plan", (r"test-plan\.md`? is absent", r"test-plan\.md`? if absent")),
            InvariantGroup("observable behavior change", (r"diff changes observable behavior", r"behavior-changing")),
            InvariantGroup("verification gap", (r"verification gap",)),
            InvariantGroup("warning severity", (r"\bwarning\b",)),
        ),
    ),
    ContractCheck(
        "review-code-runtime-aware-routing-contract",
        "idea-to-ship/skills/review-code/SKILL.md",
        (
            InvariantGroup("runtime-aware routing", (r"runtime-aware",)),
            InvariantGroup("non-Claude runtime path", (r"non-claude",)),
            InvariantGroup("fallback path", (r"\bfallback\b",)),
            InvariantGroup("fallback reason recorded", (r"fallback reason", r"state the fallback", r"note the fallback")),
        ),
    ),
)


def usage() -> None:
    print("Usage: idea-to-ship-eval-fixtures.py <repo-root>", file=sys.stderr)


def read_skill(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        print(f"Missing skill file: {relative_path}", file=sys.stderr)
        raise SystemExit(2)
    return path.read_text(encoding="utf-8", errors="replace")


def group_matches(text: str, group: InvariantGroup) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL) for pattern in group.patterns)


def run_check(root: Path, check: ContractCheck) -> list[str]:
    text = read_skill(root, check.skill_path)
    failures: list[str] = []
    for group in check.groups:
        if not group_matches(text, group):
            failures.append(group.name)
    return failures


def run_all(root: Path, checks: Iterable[ContractCheck]) -> int:
    failures = 0
    print("Idea-to-ship contract fixtures")
    for check in checks:
        missing = run_check(root, check)
        if missing:
            failures += 1
            print(f"FAIL {check.check_id}: missing invariant group(s): {', '.join(missing)}")
        else:
            print(f"PASS {check.check_id}: contract fixture coverage present")
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
