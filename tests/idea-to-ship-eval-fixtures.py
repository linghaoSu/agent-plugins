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


require(
    "idea-to-ship/skills/grill/SKILL.md",
    r"Ask exactly one unresolved",
    r"Offer 2–4 real\s+options",
    r"Discover facts locally",
    r"Do not answer for the user",
    r"--with-docs",
    r"hard to reverse.*surprising without.*real tradeoff",
)
if len(read("idea-to-ship/skills/grill/SKILL.md").splitlines()) > 80:
    FAILURES.append("grill exceeds 80 lines")

require(
    "idea-to-ship/skills/test/SKILL.md",
    r"--mode gate\|full\|backfill",
    r"public seams",
    r"tautolog",
    r"tracer-bullet",
    r"Never edit production code",
)
require(
    "idea-to-ship/skills/review/SKILL.md",
    r"--target design\|code",
    r"design-review\.md",
    r"code-review\.md",
    r"\*\*Spec:\*\*",
    r"\*\*Standards:\*\*",
)
require(
    "idea-to-ship/skills/roadmap/SKILL.md",
    r"--commercial",
    r"commercialization\.md",
    r"cheapest validation",
)
require(
    "issue-evaluator/skills/evaluate-issue/SKILL.md",
    r"red-capable",
    r"3–5 ranked, falsifiable hypotheses",
    r"Do not produce a certain root cause",
)
require(
    "issue-evaluator/skills/fix-issue/SKILL.md",
    r"Require a tight red-capable reproduction",
    r"original\s+unminimized reproduction",
    r"Remove tagged instrumentation",
)

removed = (
    "idea-to-ship/skills/commercialize/SKILL.md",
    "idea-to-ship/skills/tdd/SKILL.md",
    "idea-to-ship/skills/review-design/SKILL.md",
    "idea-to-ship/skills/review-code/SKILL.md",
    "issue-evaluator/skills/update-code-style/SKILL.md",
)
for path in removed:
    if (ROOT / path).exists():
        FAILURES.append(f"removed skill still exists: {path}")

for path in (
    "idea-to-ship/WORKFLOW-CONTRACTS.md",
    "idea-to-ship/skills/review/SKILL.md",
    "issue-evaluator/WORKFLOW-CONTRACTS.md",
):
    forbid(path, r"\bOpus\b", r"\bSonnet\b", r"\bHaiku\b", r"codex-rescue", r"subagent_type")

skills = list(ROOT.glob("*/skills/*/SKILL.md"))
if len(skills) != 27:
    FAILURES.append(f"expected 27 skills, found {len(skills)}")
if any(len(path.read_text(encoding="utf-8").splitlines()) > 250 for path in skills):
    FAILURES.append("a SKILL.md exceeds 250 lines")
if sum(len(path.read_text(encoding="utf-8").splitlines()) for path in skills) > 4600:
    FAILURES.append("total SKILL.md lines exceed 4600")
if sum(len(path.read_text(encoding="utf-8").splitlines()) <= 150 for path in skills) < 22:
    FAILURES.append("fewer than 80% of skills are at most 150 lines")

if FAILURES:
    for failure in FAILURES:
        print(f"FAIL {failure}")
    raise SystemExit(1)
print("PASS idea-to-ship consolidated workflow fixtures")
