#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(sys.argv[1]).resolve()
FAILURES: list[str] = []


def read(path: str) -> str:
    target = ROOT / path
    if not target.is_file():
        FAILURES.append(f"missing file: {path}")
        return ""
    return target.read_text(encoding="utf-8")


def require(path: str, *patterns: str) -> None:
    text = read(path)
    for pattern in patterns:
        if not re.search(pattern, text, re.MULTILINE | re.DOTALL):
            FAILURES.append(f"{path}: missing /{pattern}/")


def forbid(path: str, *patterns: str) -> None:
    text = read(path)
    for pattern in patterns:
        if re.search(pattern, text, re.MULTILINE | re.DOTALL):
            FAILURES.append(f"{path}: forbidden /{pattern}/")


schema = (
    r"role: coordinator \| executor \| reviewer \| arbiter",
    r"capability: routine \| reasoning \| critical",
    r"independent_context: true \| false",
    r"parallelizable: true \| false",
)
for contract in (
    "agent-playbook/WORKFLOW-CONTRACTS.md",
    "idea-to-ship/WORKFLOW-CONTRACTS.md",
    "issue-evaluator/WORKFLOW-CONTRACTS.md",
):
    require(contract, *schema, r"degraded")
    forbid(contract, r"\bOpus\b", r"\bSonnet\b", r"\bHaiku\b", r"codex-rescue", r"subagent_type")

require(
    "antifragile/skills/antifragile-audit/SKILL.md",
    r"--scope system\|agent",
    r"System scope",
    r"Agent scope",
    r"write no artifact",
)
require(
    "harness-engineering/skills/harness/SKILL.md",
    r"--mode design\|audit\|resilience\|contract",
    r"harness-design\.md",
    r"harness-audit\.md",
    r"resilience-plan\.md",
    r"sprint-contract\.md",
)
require(
    "agent-playbook/skills/commit-changes/SKILL.md",
    r"does not authorize a\s+push or PR",
    r"Preserve unrelated user changes",
    r"Do not add tool",
)
require(
    "agent-playbook/skills/implementation-tournament/SKILL.md",
    r"explicitly requests",
    r"identical objective verification",
    r"adopt.*merge.*reject-all",
)

removed_paths = (
    "agent-playbook/skills/workflow-router/SKILL.md",
    "agent-playbook/skills/vibe-coding-health-check/SKILL.md",
    "agent-playbook/skills/vibe-coding-fix/SKILL.md",
    "antifragile/skills/antifragile-agent/SKILL.md",
    "antifragile/skills/antifragile-system/SKILL.md",
    "harness-engineering/skills/harness-design/SKILL.md",
    "harness-engineering/skills/harness-audit/SKILL.md",
    "harness-engineering/skills/resilience-plan/SKILL.md",
    "harness-engineering/skills/sprint-contract/SKILL.md",
)
for path in removed_paths:
    if (ROOT / path).exists():
        FAILURES.append(f"removed skill still exists: {path}")

if FAILURES:
    for failure in FAILURES:
        print(f"FAIL {failure}")
    raise SystemExit(1)
print("PASS agent-playbook consolidated contract fixtures")
