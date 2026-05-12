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


CHECKS: tuple[ContractCheck, ...] = (
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
