#!/usr/bin/env python3
"""Offline contract fixtures for critical idea-to-ship skill workflows."""

from __future__ import annotations

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
    skill_path: str
    groups: tuple[InvariantGroup, ...]


GENERATED_START = "<!-- idea-to-ship:roadmap generated:start -->"
GENERATED_END = "<!-- idea-to-ship:roadmap generated:end -->"
ROADMAP_LANE_FIELDS = (
    "**Status:**",
    "**Work Type:**",
    "**Evidence Class:**",
    "**Confidence:**",
    "**Source Anchors:**",
    "**Why Now / Why Next / Why Later:**",
    "**Owner:**",
    "**Decision Owner:**",
    "**Release Gate:**",
    "**Evidence Required:**",
    "**Dependencies:**",
    "**Risk:**",
)
REQUIREMENTS_CORE_HEADINGS = (
    "## Problem",
    "## Functional Requirements",
    "## Success Criteria",
    "## Open Questions",
)
ARCHITECTURE_CORE_HEADINGS = (
    "## Summary",
    "## Codebase Context",
    "## Alternatives Considered",
    "## Recommendation",
    "## Chosen Design",
    "## Staged Implementation Plan",
)


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
        "brainstorm-rerun-preservation-contract",
        "idea-to-ship/skills/brainstorm/SKILL.md",
        (
            InvariantGroup("requirements ownership", (r"Requirements Ownership",)),
            InvariantGroup("stable requirement ids", (r"stable requirement IDs",)),
            InvariantGroup("requirement id examples", (r"FR-\*", r"FR-1")),
            InvariantGroup(
                "human content preservation",
                (r"human notes", r"manual exclusions", r"human edits"),
            ),
            InvariantGroup("draft fallback", (r"requirements\.draft\.md",)),
            InvariantGroup("replacement approval", (r"explicit approval",)),
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
        "architect-rerun-preservation-contract",
        "idea-to-ship/skills/architect/SKILL.md",
        (
            InvariantGroup("architecture ownership", (r"Architecture Ownership",)),
            InvariantGroup("option identity preservation", (r"option names",)),
            InvariantGroup("stage identity preservation", (r"stage names",)),
            InvariantGroup("decision history preservation", (r"decision history",)),
            InvariantGroup(
                "human content preservation",
                (r"human notes", r"unresolved risks", r"human edits"),
            ),
            InvariantGroup("draft fallback", (r"architecture\.draft\.md",)),
            InvariantGroup("replacement approval", (r"explicit approval",)),
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
            InvariantGroup(
                "delegation authorization",
                (r"policy authorizes delegation", r"authorizes delegation"),
            ),
            InvariantGroup("host permission", (r"host permits sub-agents",)),
            InvariantGroup("capacity fallback", (r"at capacity", r"capacity fallback")),
            InvariantGroup("fallback path", (r"\bfallback\b",)),
            InvariantGroup("fallback reason recorded", (r"fallback reason", r"state the fallback", r"note the fallback")),
        ),
    ),
)


def has_valid_generated_markers(text: str) -> bool:
    start = text.find(GENERATED_START)
    end = text.find(GENERATED_END)
    if start == -1 or end == -1:
        return False
    if start >= end:
        return False
    return text.count(GENERATED_START) == 1 and text.count(GENERATED_END) == 1


def has_required_headings(text: str, headings: tuple[str, ...]) -> bool:
    return all(heading in text for heading in headings)


def resolve_structured_artifact_write_target(
    artifact_path: Path, draft_name: str, required_headings: tuple[str, ...]
) -> Path:
    if not artifact_path.exists():
        return artifact_path

    text = artifact_path.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        return artifact_path
    if has_required_headings(text, required_headings):
        return artifact_path
    return artifact_path.with_name(draft_name)


def resolve_roadmap_write_target(roadmap_path: Path) -> Path:
    if not roadmap_path.exists():
        return roadmap_path

    text = roadmap_path.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        return roadmap_path
    if has_valid_generated_markers(text):
        return roadmap_path
    return roadmap_path.with_name("roadmap.draft.md")


def roadmap_lane_items_are_structured(text: str) -> bool:
    matches = list(re.finditer(r"^### ITS-[^\n]+", text, flags=re.MULTILINE))
    if not matches:
        return False

    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[match.start():end]
        if not all(field in block for field in ROADMAP_LANE_FIELDS):
            return False
    return True


def test_plan_has_traceability_sections(text: str) -> bool:
    required_headings = (
        "## User Stories",
        "## Acceptance Criteria",
        "## Scenario Matrix",
        "## Test Matrix",
        "### Unit",
        "### Integration",
        "## Results",
    )
    return all(heading in text for heading in required_headings)


def run_artifact_fixtures(root: Path) -> list[tuple[str, str | None]]:
    results: list[tuple[str, str | None]] = []

    roadmap_path = root / ".idea-to-ship" / "roadmap.md"
    roadmap_text = read_skill(root, ".idea-to-ship/roadmap.md")
    if has_valid_generated_markers(roadmap_text):
        results.append(("roadmap-generated-marker-artifact", None))
    else:
        results.append(
            ("roadmap-generated-marker-artifact", "invalid or missing generated marker pair")
        )

    if roadmap_lane_items_are_structured(roadmap_text):
        results.append(("roadmap-lane-schema-artifact", None))
    else:
        results.append(
            ("roadmap-lane-schema-artifact", "lane item missing required template fields")
        )

    if has_valid_generated_markers(roadmap_text):
        expected_target = roadmap_path
    else:
        expected_target = roadmap_path.with_name("roadmap.draft.md")
    actual_target = resolve_roadmap_write_target(roadmap_path)
    if actual_target == expected_target:
        results.append(("roadmap-write-target-artifact", None))
    else:
        results.append(
            (
                "roadmap-write-target-artifact",
                f"expected {expected_target.name}, got {actual_target.name}",
            )
        )

    with TemporaryDirectory(prefix="idea-to-ship-artifacts-") as tmp:
        temp_root = Path(tmp)
        artifact_dir = temp_root / ".idea-to-ship"
        artifact_dir.mkdir()
        human_only = artifact_dir / "roadmap.md"
        human_only.write_text("# Human Roadmap\n\nManual planning notes.\n", encoding="utf-8")
        draft_target = resolve_roadmap_write_target(human_only)
        if draft_target.name == "roadmap.draft.md":
            results.append(("roadmap-draft-fallback-artifact", None))
        else:
            results.append(
                (
                    "roadmap-draft-fallback-artifact",
                    f"expected roadmap.draft.md, got {draft_target.name}",
                )
            )

        generated = artifact_dir / "generated.md"
        generated.write_text(
            "# Roadmap\n\nHuman note.\n\n"
            f"{GENERATED_START}\n\n## Now\n\nagent content\n\n{GENERATED_END}\n",
            encoding="utf-8",
        )
        generated_target = resolve_roadmap_write_target(generated)
        if generated_target == generated:
            results.append(("roadmap-marker-preservation-artifact", None))
        else:
            results.append(
                (
                    "roadmap-marker-preservation-artifact",
                    f"expected generated.md, got {generated_target.name}",
                )
            )

        malformed_requirements = artifact_dir / "requirements.md"
        malformed_requirements.write_text(
            "# Human Requirements\n\nManual product notes.\n", encoding="utf-8"
        )
        requirements_target = resolve_structured_artifact_write_target(
            malformed_requirements,
            "requirements.draft.md",
            REQUIREMENTS_CORE_HEADINGS,
        )
        if requirements_target.name == "requirements.draft.md":
            results.append(("requirements-draft-fallback-artifact", None))
        else:
            results.append(
                (
                    "requirements-draft-fallback-artifact",
                    f"expected requirements.draft.md, got {requirements_target.name}",
                )
            )

        malformed_architecture = artifact_dir / "architecture.md"
        malformed_architecture.write_text(
            "# Human Architecture\n\nManual design notes.\n", encoding="utf-8"
        )
        architecture_target = resolve_structured_artifact_write_target(
            malformed_architecture,
            "architecture.draft.md",
            ARCHITECTURE_CORE_HEADINGS,
        )
        if architecture_target.name == "architecture.draft.md":
            results.append(("architecture-draft-fallback-artifact", None))
        else:
            results.append(
                (
                    "architecture-draft-fallback-artifact",
                    f"expected architecture.draft.md, got {architecture_target.name}",
                )
            )

    requirements_path = root / ".idea-to-ship" / "ITS-ROADMAP-006" / "requirements.md"
    requirements_text = read_skill(
        root, ".idea-to-ship/ITS-ROADMAP-006/requirements.md"
    )
    requirements_target = resolve_structured_artifact_write_target(
        requirements_path,
        "requirements.draft.md",
        REQUIREMENTS_CORE_HEADINGS,
    )
    if (
        has_required_headings(requirements_text, REQUIREMENTS_CORE_HEADINGS)
        and requirements_target == requirements_path
    ):
        results.append(("requirements-structured-artifact", None))
    else:
        results.append(
            (
                "requirements-structured-artifact",
                "missing core headings or unsafe write target",
            )
        )

    architecture_path = root / ".idea-to-ship" / "ITS-ROADMAP-006" / "architecture.md"
    architecture_text = read_skill(
        root, ".idea-to-ship/ITS-ROADMAP-006/architecture.md"
    )
    architecture_target = resolve_structured_artifact_write_target(
        architecture_path,
        "architecture.draft.md",
        ARCHITECTURE_CORE_HEADINGS,
    )
    if (
        has_required_headings(architecture_text, ARCHITECTURE_CORE_HEADINGS)
        and architecture_target == architecture_path
    ):
        results.append(("architecture-structured-artifact", None))
    else:
        results.append(
            (
                "architecture-structured-artifact",
                "missing core headings or unsafe write target",
            )
        )

    test_plan_text = read_skill(root, ".idea-to-ship/ITS-ROADMAP-006/test-plan.md")
    if test_plan_has_traceability_sections(test_plan_text):
        results.append(("test-plan-traceability-artifact", None))
    else:
        results.append(
            ("test-plan-traceability-artifact", "missing required traceability sections")
        )

    return results


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
    print("Idea-to-ship artifact fixtures")
    for check_id, failure in run_artifact_fixtures(root):
        if failure:
            failures += 1
            print(f"FAIL {check_id}: {failure}")
        else:
            print(f"PASS {check_id}: artifact safety coverage present")
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
