#!/usr/bin/env python3
"""Read-only skill topology report for the local plugin marketplace."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


QUALIFIED_REF_RE = re.compile(r"(?<![A-Za-z0-9_/-])(\$?)([A-Za-z0-9_-]+):([A-Za-z0-9_-]+)\b")
PATH_REF_RE = re.compile(r"(?<![A-Za-z0-9_./-])([A-Za-z0-9_-]+)/skills/([A-Za-z0-9_-]+)/SKILL\.md\b")
FRONTMATTER_VALUE_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)$")


@dataclass(frozen=True)
class Skill:
    skill_id: str
    plugin: str
    slug: str
    path: str
    name: str
    description: str


@dataclass(frozen=True)
class Reference:
    source_id: str
    target_id: str
    evidence: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def extract_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    closing_index: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = index
            break
    if closing_index is None:
        return {}

    values: dict[str, str] = {}
    for line in lines[1:closing_index]:
        match = FRONTMATTER_VALUE_RE.match(line)
        if not match:
            continue
        values[match.group(1)] = match.group(2).strip().strip("\"'")
    return values


def discover_skills(root: Path) -> list[Skill]:
    skills: list[Skill] = []
    for path in sorted(root.glob("*/skills/*/SKILL.md")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        parts = path.relative_to(root).parts
        if len(parts) != 4:
            continue
        plugin, _, slug, _ = parts
        frontmatter = extract_frontmatter(read_text(path))
        skills.append(
            Skill(
                skill_id=f"{plugin}:{slug}",
                plugin=plugin,
                slug=slug,
                path=relative,
                name=frontmatter.get("name") or slug,
                description=frontmatter.get("description") or "",
            )
        )
    return skills


def extract_references(root: Path, skill: Skill, known_plugins: set[str]) -> list[Reference]:
    text = read_text(root / skill.path)
    refs: list[Reference] = []
    seen: set[tuple[str, str]] = set()

    for match in QUALIFIED_REF_RE.finditer(text):
        explicit = match.group(1) == "$"
        plugin = match.group(2)
        if not explicit and plugin not in known_plugins:
            continue
        target_id = f"{plugin}:{match.group(3)}"
        evidence = match.group(0)
        key = (target_id, evidence)
        if key in seen:
            continue
        seen.add(key)
        refs.append(Reference(skill.skill_id, target_id, evidence))

    for match in PATH_REF_RE.finditer(text):
        plugin = match.group(1)
        target_id = f"{plugin}:{match.group(2)}"
        evidence = match.group(0)
        key = (target_id, evidence)
        if key in seen:
            continue
        seen.add(key)
        refs.append(Reference(skill.skill_id, target_id, evidence))

    return sorted(refs, key=lambda item: (item.target_id, item.evidence))


def readme_catalog_paths(root: Path) -> set[str]:
    readme = root / "README.md"
    if not readme.is_file():
        return set()
    return {
        f"{match.group(1)}/skills/{match.group(2)}/SKILL.md"
        for match in PATH_REF_RE.finditer(read_text(readme))
    }


def md(value: str) -> str:
    return f"`{value}`"


def render_table_empty(columns: int) -> str:
    return "| _none_ |" + " |" * (columns - 1)


def render_report(root: Path, skills: list[Skill], hub_threshold: int) -> str:
    by_id = {skill.skill_id: skill for skill in skills}
    known_plugins = {skill.plugin for skill in skills}
    references = [
        ref
        for skill in skills
        for ref in extract_references(root, skill, known_plugins)
    ]
    valid_refs = [ref for ref in references if ref.target_id in by_id and ref.target_id != ref.source_id]
    broken_refs = [ref for ref in references if ref.target_id not in by_id]

    outbound: dict[str, set[str]] = {skill.skill_id: set() for skill in skills}
    inbound: dict[str, set[str]] = {skill.skill_id: set() for skill in skills}
    mentioned_targets: dict[str, set[str]] = {skill.skill_id: set() for skill in skills}
    for ref in references:
        if ref.target_id == ref.source_id:
            continue
        mentioned_targets.setdefault(ref.source_id, set()).add(ref.target_id)
    for ref in valid_refs:
        outbound[ref.source_id].add(ref.target_id)
        inbound[ref.target_id].add(ref.source_id)

    roles = {
        skill.skill_id: "parent" if mentioned_targets.get(skill.skill_id) else "leaf"
        for skill in skills
    }
    orphans = [
        skill
        for skill in skills
        if not outbound[skill.skill_id]
        and not inbound[skill.skill_id]
        and not mentioned_targets.get(skill.skill_id)
    ]
    hubs = [
        (skill, len(outbound[skill.skill_id] | inbound[skill.skill_id]))
        for skill in skills
    ]
    hubs = [
        (skill, degree)
        for skill, degree in hubs
        if degree >= hub_threshold
    ]
    hubs.sort(key=lambda item: (-item[1], item[0].skill_id))

    catalog_paths = readme_catalog_paths(root)
    readme_gaps = [skill for skill in skills if skill.path not in catalog_paths]

    lines: list[str] = [
        "# Skill Topology Report",
        "",
        f"Total plugins: {len(known_plugins)}",
        f"Total skills: {len(skills)}",
        f"Broken references: {len(broken_refs)}",
        f"Orphan skills: {len(orphans)}",
        f"Hub skills (degree >= {hub_threshold}): {len(hubs)}",
        f"README coverage gaps: {len(readme_gaps)}",
        "",
        "## Skill Inventory",
        "",
        "| Skill | Name | Role | Path | Outbound | Inbound |",
        "|---|---|---|---|---:|---:|",
    ]
    if skills:
        for skill in skills:
            lines.append(
                "| "
                f"{md(skill.skill_id)} | {skill.name} | {roles[skill.skill_id]} | {md(skill.path)} | "
                f"{len(outbound[skill.skill_id])} | {len(inbound[skill.skill_id])} |"
            )
    else:
        lines.append(render_table_empty(6))

    lines.extend(["", "## Skill Tree", ""])
    if skills:
        for plugin in sorted(known_plugins):
            lines.append(f"- {md(plugin)}")
            for skill in [item for item in skills if item.plugin == plugin]:
                lines.append(f"  - {md(skill.slug)} ({roles[skill.skill_id]}) - {md(skill.path)}")
    else:
        lines.append("- _none_")

    lines.extend([
        "",
        "## Broken References",
        "",
        "| Source | Source Path | Target | Evidence |",
        "|---|---|---|---|",
    ])
    if broken_refs:
        for ref in sorted(broken_refs, key=lambda item: (item.source_id, item.target_id, item.evidence)):
            source_path = by_id[ref.source_id].path
            lines.append(
                f"| {md(ref.source_id)} | {md(source_path)} | "
                f"{md(ref.target_id)} | {md(ref.evidence)} |"
            )
    else:
        lines.append(render_table_empty(4))

    lines.extend([
        "",
        "## Orphan Skills",
        "",
        "| Skill | Path |",
        "|---|---|",
    ])
    if orphans:
        for skill in orphans:
            lines.append(f"| {md(skill.skill_id)} | {md(skill.path)} |")
    else:
        lines.append(render_table_empty(2))

    lines.extend([
        "",
        "## Hub Skills",
        "",
        "| Skill | Degree | Outbound | Inbound |",
        "|---|---:|---:|---:|",
    ])
    if hubs:
        for skill, degree in hubs:
            lines.append(
                f"| {md(skill.skill_id)} | {degree} | "
                f"{len(outbound[skill.skill_id])} | {len(inbound[skill.skill_id])} |"
            )
    else:
        lines.append(render_table_empty(4))

    lines.extend([
        "",
        "## README Coverage Gaps",
        "",
        "| Skill | Path |",
        "|---|---|",
    ])
    if readme_gaps:
        for skill in readme_gaps:
            lines.append(f"| {md(skill.skill_id)} | {md(skill.path)} |")
    else:
        lines.append(render_table_empty(2))

    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hub-threshold", type=int, default=3)
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"Repo root is not a directory: {root}", file=sys.stderr)
        return 2
    if args.hub_threshold < 1:
        print("--hub-threshold must be >= 1", file=sys.stderr)
        return 2

    skills = discover_skills(root)
    print(render_report(root, skills, args.hub_threshold), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
