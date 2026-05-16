#!/usr/bin/env python3
"""Deterministic fixtures for scripts/skill-topology-scan.py."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


def usage() -> None:
    print("Usage: skill-topology-scan-fixtures.py <repo-root>", file=sys.stderr)


def run_command(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, check=False, capture_output=True, text=True)


def skill_text(name: str, body: str = "") -> str:
    return (
        "---\n"
        f"name: {name}\n"
        f"description: Fixture skill {name} for topology scan.\n"
        "---\n"
        "\n"
        f"# {name.title()}\n"
        "\n"
        f"{body}"
    )


def write_skill(root: Path, slug: str, body: str = "") -> Path:
    path = root / "plugin" / "skills" / slug / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(skill_text(slug, body), encoding="utf-8")
    return path


def run_scan(repo_root: Path, scanner: Path) -> subprocess.CompletedProcess[str]:
    return run_command(["python3", str(scanner), str(repo_root)], repo_root)


def assert_contains(output: str, needle: str, scenario: str) -> None:
    if needle not in output:
        raise AssertionError(f"{scenario}: missing {needle!r}\noutput:\n{output}")


def assert_not_contains(output: str, needle: str, scenario: str) -> None:
    if needle in output:
        raise AssertionError(f"{scenario}: unexpected {needle!r}\noutput:\n{output}")


def scenario_topology_report(scanner: Path) -> None:
    with TemporaryDirectory(prefix="skill-topology-") as tmp:
        root = Path(tmp)
        write_skill(
            root,
            "parent",
            (
                "Use `$plugin:leaf` for focused work.\n"
                "Broken related skill: `$plugin:missing`.\n"
                "Broken removed plugin skill: `$missing-plugin:ghost`.\n"
                "Path reference: plugin/skills/spoke-one/SKILL.md.\n"
                "Broken path reference: plugin/skills/ghost/SKILL.md.\n"
                "Broken removed plugin path: missing-plugin/skills/ghost/SKILL.md.\n"
            ),
        )
        write_skill(root, "leaf")
        write_skill(
            root,
            "hub",
            (
                "Related skills: $plugin:parent, $plugin:leaf, "
                "plugin/skills/spoke-two/SKILL.md.\n"
            ),
        )
        write_skill(root, "spoke-one")
        write_skill(root, "spoke-two")
        write_skill(root, "orphan", "The default prompt may mention `$plugin:orphan` without creating a graph edge.\n")

        (root / "README.md").write_text(
            "# Fixture Catalog\n\n"
            "| Skill | Purpose |\n"
            "|---|---|\n"
            "| [parent](plugin/skills/parent/SKILL.md) | Parent skill. |\n"
            "| [leaf](plugin/skills/leaf/SKILL.md) | Leaf skill. |\n",
            encoding="utf-8",
        )

        result = run_scan(root, scanner)
        if result.returncode != 0:
            raise AssertionError(
                f"topology scan expected exit 0, got {result.returncode}\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )

        output = result.stdout
        assert_contains(output, "# Skill Topology Report", "report heading")
        assert_contains(output, "Total plugins: 1", "summary plugin count")
        assert_contains(output, "Total skills: 6", "summary skill count")
        assert_contains(output, "Broken references: 4", "summary broken ref count")
        assert_contains(output, "## Skill Inventory", "inventory section")
        assert_contains(
            output,
            "| `plugin:parent` | parent | parent | `plugin/skills/parent/SKILL.md` | 2 | 1 |",
            "parent inventory row",
        )
        assert_contains(
            output,
            "| `plugin:leaf` | leaf | leaf | `plugin/skills/leaf/SKILL.md` | 0 | 2 |",
            "leaf inventory row",
        )
        assert_contains(output, "## Skill Tree", "skill tree section")
        assert_contains(output, "- `plugin`", "plugin tree row")
        assert_contains(output, "  - `parent` (parent) - `plugin/skills/parent/SKILL.md`", "parent tree row")
        assert_contains(output, "  - `orphan` (leaf) - `plugin/skills/orphan/SKILL.md`", "orphan tree row")

        assert_contains(output, "## Broken References", "broken refs section")
        assert_contains(
            output,
            "| `plugin:parent` | `plugin/skills/parent/SKILL.md` | `plugin:missing` | `$plugin:missing` |",
            "broken plugin-qualified ref",
        )
        assert_contains(
            output,
            "| `plugin:parent` | `plugin/skills/parent/SKILL.md` | `plugin:ghost` | `plugin/skills/ghost/SKILL.md` |",
            "broken path ref",
        )
        assert_contains(
            output,
            "| `plugin:parent` | `plugin/skills/parent/SKILL.md` | `missing-plugin:ghost` | `$missing-plugin:ghost` |",
            "broken unknown plugin-qualified ref",
        )
        assert_contains(
            output,
            "| `plugin:parent` | `plugin/skills/parent/SKILL.md` | `missing-plugin:ghost` | `missing-plugin/skills/ghost/SKILL.md` |",
            "broken unknown plugin path ref",
        )

        assert_contains(output, "## Orphan Skills", "orphan section")
        assert_contains(output, "| `plugin:orphan` | `plugin/skills/orphan/SKILL.md` |", "orphan row")
        assert_not_contains(output, "| `plugin:leaf` | `plugin/skills/leaf/SKILL.md` |", "linked leaf is not orphan")

        assert_contains(output, "## Hub Skills", "hub section")
        assert_contains(output, "| `plugin:hub` | 3 |", "hub row")

        assert_contains(output, "## README Coverage Gaps", "readme coverage section")
        assert_contains(output, "| `plugin:hub` | `plugin/skills/hub/SKILL.md` |", "readme missing hub row")
        assert_contains(output, "| `plugin:orphan` | `plugin/skills/orphan/SKILL.md` |", "readme missing orphan row")


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        usage()
        return 2

    repo_root = Path(argv[0]).resolve()
    scanner = repo_root / "scripts" / "skill-topology-scan.py"
    scenario_topology_report(scanner)
    print("skill topology scan fixtures passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
