#!/usr/bin/env python3
"""Advisory hygiene checks for skill definitions.

This script is intentionally conservative: findings are release-gate advisory
signals, not blockers. It focuses on issues that make skill routing noisy or
cause recently-added skills to miss UI metadata.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


MAX_DESCRIPTION_CHARS = 320


@dataclass(frozen=True)
class Finding:
    check_id: str
    path: str
    message: str

    def render(self) -> str:
        return f"{self.check_id}: {self.path}: {self.message}"


def run_git(args: list[str], root: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout


def iter_all_skill_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.glob("*/skills/*/SKILL.md")
        if path.is_file()
    )


def changed_skill_files(root: Path, mode: str) -> list[Path]:
    if mode == "all":
        return iter_all_skill_files(root)

    diff_args = ["diff", "--name-only", "--diff-filter=ACMRT"]
    if mode == "staged":
        diff_args.append("--cached")
    else:
        diff_args.append("HEAD")
    diff_args.extend(["--", "*/skills/*/SKILL.md"])

    files = {
        root / line
        for line in run_git(diff_args, root).splitlines()
        if line.strip()
    }

    if mode == "working":
        untracked = run_git(
            ["ls-files", "--others", "--exclude-standard", "--", "*/skills/*/SKILL.md"],
            root,
        )
        files.update(root / line for line in untracked.splitlines() if line.strip())

    return sorted(path for path in files if path.is_file())


def added_skill_files(root: Path, mode: str) -> list[Path]:
    if mode == "staged":
        output = run_git(
            ["diff", "--cached", "--name-status", "--diff-filter=A", "--", "*/skills/*/SKILL.md"],
            root,
        )
    else:
        output = run_git(
            ["diff", "--name-status", "--diff-filter=A", "HEAD", "--", "*/skills/*/SKILL.md"],
            root,
        )

    files: set[Path] = set()
    for line in output.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            files.add(root / parts[-1])

    if mode in {"working", "all"}:
        untracked = run_git(
            ["ls-files", "--others", "--exclude-standard", "--", "*/skills/*/SKILL.md"],
            root,
        )
        files.update(root / line for line in untracked.splitlines() if line.strip())

    return sorted(path for path in files if path.is_file())


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def read_skill_text(root: Path, path: Path, mode: str) -> str:
    if mode == "staged":
        relative = str(path.relative_to(root))
        return run_git(["show", f":{relative}"], root)
    return read_text(path)


def metadata_exists(root: Path, path: Path, mode: str) -> bool:
    if mode == "staged":
        relative = str(path.relative_to(root))
        result = subprocess.run(
            ["git", "cat-file", "-e", f":{relative}"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    return path.is_file()


def extract_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[1:index])
    return ""


def frontmatter_value(frontmatter: str, key: str) -> str:
    match = re.search(r"^\s*" + re.escape(key) + r"\s*:\s*(.*)$", frontmatter, re.MULTILINE)
    return match.group(1).strip().strip("\"'") if match else ""


def extract_section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.find(marker)
    if start == -1:
        return ""
    next_heading = re.search(r"^##\s+", text[start + len(marker):], flags=re.MULTILINE)
    if not next_heading:
        return text[start:]
    return text[start:start + len(marker) + next_heading.start()]


def check_description_lengths(root: Path, skill_files: list[Path], mode: str) -> list[Finding]:
    findings: list[Finding] = []
    for path in skill_files:
        text = read_skill_text(root, path, mode)
        description = frontmatter_value(extract_frontmatter(text), "description")
        if len(description) > MAX_DESCRIPTION_CHARS:
            findings.append(
                Finding(
                    "long-description",
                    str(path.relative_to(root)),
                    f"description is {len(description)} chars; keep routing text <= {MAX_DESCRIPTION_CHARS}",
                )
            )
    return findings


def check_shared_contract_references(root: Path, skill_files: list[Path], mode: str) -> list[Finding]:
    findings: list[Finding] = []
    for path in skill_files:
        text = read_skill_text(root, path, mode)
        relative = str(path.relative_to(root))

        routing_section = extract_section(text, "Runtime-Aware Agent Routing")
        if routing_section:
            lines = [line for line in routing_section.splitlines() if line.strip()]
            if len(lines) > 5 and "WORKFLOW-CONTRACTS.md" not in routing_section:
                findings.append(
                    Finding(
                        "inline-runtime-routing",
                        relative,
                        "Runtime-Aware Agent Routing section is long but does not cite a shared WORKFLOW-CONTRACTS.md",
                    )
                )

        if (
            "MARKETPLACE_PATH=" in text
            and "Reviewer Preference" in text
            and "WORKFLOW-CONTRACTS.md" not in text
        ):
            findings.append(
                Finding(
                    "inline-code-style-lifecycle",
                    relative,
                    "inline code-style-guide lifecycle should cite issue-evaluator/WORKFLOW-CONTRACTS.md",
                )
            )
    return findings


def check_added_skill_metadata(root: Path, mode: str) -> list[Finding]:
    findings: list[Finding] = []
    for skill_path in added_skill_files(root, mode):
        metadata_path = skill_path.parent / "agents" / "openai.yaml"
        if not metadata_exists(root, metadata_path, mode):
            findings.append(
                Finding(
                    "missing-openai-metadata",
                    str(skill_path.relative_to(root)),
                    "new skill has no sibling agents/openai.yaml metadata",
                )
            )
    return findings


def run(root: Path, mode: str) -> list[Finding]:
    skill_files = changed_skill_files(root, mode)
    findings: list[Finding] = []
    findings.extend(check_description_lengths(root, skill_files, mode))
    findings.extend(check_shared_contract_references(root, skill_files, mode))
    findings.extend(check_added_skill_metadata(root, mode))
    return findings


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("staged", "working", "all"), default="all")
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"Repo root is not a directory: {root}", file=sys.stderr)
        return 2

    try:
        findings = run(root, args.mode)
    except Exception as exc:  # noqa: BLE001 - command-line diagnostic
        print(f"skill hygiene check failed: {exc}", file=sys.stderr)
        return 2

    if findings:
        for finding in findings:
            print(finding.render())
        return 1

    print("Skill hygiene check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
