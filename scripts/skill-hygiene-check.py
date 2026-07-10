#!/usr/bin/env python3
"""Advisory hygiene checks for skill definitions.

This script is intentionally conservative: findings are release-gate advisory
signals, not blockers. It focuses on issues that make skill routing noisy or
cause recently-added skills to miss UI metadata.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Literal, Optional


MAX_DESCRIPTION_CHARS = 240
MAX_SKILL_LINES = 250
MODERATE_SKILL_LINES = 150
FULL_CONTRACT_MARKERS = (
    "## Output, Token, And Error Contract",
    "status: success | needs_user | terminal | degraded",
    "truncated: true | false",
)
OUTPUT_CONTRACT_MAX_MARKER_SPAN_LINES = 40
MAX_CANDIDATE_LINES = 80
MIN_REPEATED_LITERAL_CHARS = 300
MIN_REPEATED_BLOCK_CHARS = 600
MIN_REPEATED_BLOCK_LINES = 8
MIN_TEMPLATE_STRUCTURE_ANCHORS = 5
MIN_TEMPLATE_LITERAL_CHARS = 160
REPEATED_BLOCK_SIMILARITY = 0.92
MAX_FUZZY_CANDIDATE_CHARS = 8_000
MAX_FUZZY_COMPARISONS_PER_FILE = 2_000
MAX_FUZZY_COMPARE_CHARS_PER_FILE = 500_000
MAX_FUZZY_PAIR_COST_PER_COMPARISON = 4_000_000
MAX_FUZZY_PAIR_COST_TOTAL = 20_000_000
MAX_FUZZY_COMPARISONS_TOTAL = 10_000
MAX_FUZZY_COMPARE_CHARS_TOTAL = 2_000_000
PROMPT_PLACEHOLDER_RATIO = 0.35
TEMPLATE_PLACEHOLDER_RATIO = 0.70
PLACEHOLDER_RE = re.compile(r"<[^>\n]+>|\{[^}\n]+\}|\b[A-Z][A-Z0-9_]{3,}\b")
STRUCTURE_PLACEHOLDER_RE = re.compile(r"<[^>\n]+>|\{[^}\n]+\}|\b[A-Z][A-Z0-9_]*_[A-Z0-9_]*\b")
PLACEHOLDER_LABEL_RE = re.compile(r"^\s*(?:<([^>\n:]+)>|\{([^}\n:]+)\})\s*:")
LINE_NUMBER_PREFIX_RE = re.compile(r"^\s*\d{1,5}\s*(?:[:|]\s*|\s{2,})")
FENCE_RE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})(.*)$")
HEADING_RE = re.compile(r"^[ \t]{0,3}(#{1,6})\s+(.+?)\s*$")
YAML_KEY_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_-]*)\s*:")
NUMBERED_LABEL_RE = re.compile(r"^\s*\d+\.\s*([^:]{3,60}):")
OUTPUT_WRAPPER_HEADING_RE = re.compile(
    r"^\s*#{1,6}\s+"
    r"(Final Report|Issues Raised|Review Rounds|Residual|Output|Handoff|Summary)\b",
    re.IGNORECASE,
)
INTERNAL_HEADING_TITLES = {
    "requirements",
    "architecture",
    "issue details",
    "final report",
    "review rounds",
    "output",
    "handoff",
    "output, token, and error contract",
}
PROMPT_TRIGGER_RE = re.compile(
    r"(use this prompt|run this prompt|adversarial .*review|for each issue|"
    r"if you find no|assigned angle|read-only|you are|your job)",
    re.IGNORECASE,
)
TEMPLATE_TRIGGER_RE = re.compile(
    r"(final report|report template|output template|write the following report|"
    r"issues raised|residual open issues)",
    re.IGNORECASE,
)
PROMPT_ROLE_SCORE_PATTERNS = (
    "you are",
    "your job",
    "assigned angle",
    "read-only",
    "do not edit",
    "do not modify",
    "reviewer",
    "agent",
    "sub-agent",
)
PROMPT_PHRASE_SCORE_PATTERNS = (
    "use this prompt",
    "run this prompt",
    "for each issue",
    "if you find no",
    "respond with exactly",
)
PROMPT_INPUT_SCORE_PATTERNS = (
    "## requirements",
    "## architecture",
    "## issue details",
    "<full content",
    "<angle>",
)
TEMPLATE_SKELETON_PATTERNS = (
    "status:",
    "outputs_written:",
    "| severity |",
    "| round |",
    "| check |",
)
STRUCTURE_YAML_KEYS = {
    "status",
    "outputs_written",
    "next_action",
    "truncated",
    "reviewed_with",
    "evidence_summary",
    "severity",
    "file",
    "issue",
    "resolution",
    "evidence",
}
SKILL_AUTHORING_BASELINE = Path("scripts/skill-authoring-baseline.txt")
USAGE_SECTION_TITLES = {"workflow", "when to use", "usage", "steps", "arguments", "examples"}
QUALIFIED_SKILL_REF_RE = re.compile(r"(?<![A-Za-z0-9_/-])(\$?)([A-Za-z0-9_-]+):([A-Za-z0-9_-]+)\b")
PATH_SKILL_REF_RE = re.compile(r"(?<![A-Za-z0-9_./-])([A-Za-z0-9_-]+)/skills/([A-Za-z0-9_-]+)/SKILL\.md\b")
COMMAND_FENCE_LANGUAGES = {"bash", "sh", "zsh", "shell", "console", "terminal"}
COMMAND_START_RE = re.compile(r"^\s*(?:\$+\s*)?(git|rm|python3?|bash|npm|pnpm|yarn|uv|make|scripts/|\./)\b")
COMMAND_PLACEHOLDER_RE = re.compile(r"<[^>\n]+>|\{[^}\n]+\}|\b[A-Z][A-Z0-9_]*_[A-Z0-9_]*\b")
HEREDOC_RE = re.compile(r"<<-?['\"]?[A-Za-z_][A-Za-z0-9_-]*['\"]?")
UNSAFE_COMMAND_RE = re.compile(
    r"(&&|\|\||;|\brm\s+-rf\b|\bgit\s+reset\s+--hard\b|\bgit\s+clean\s+-fd\b|"
    r"\bgit\s+checkout\s+--(?:\s|$)|\bcurl\b[^\n|]*\|\s*(?:sh|bash)\b)",
    re.IGNORECASE,
)
COMMAND_SAFETY_RE = re.compile(
    r"\b(approval|confirm|dry-run|non-mutating|read-only|explicit authorization|review before running)\b",
    re.IGNORECASE,
)
PLACEHOLDER_EXPLANATION_RE = re.compile(r"\b(replace|set|export|placeholder)\b", re.IGNORECASE)


@dataclass(frozen=True)
class Finding:
    check_id: str
    path: str
    message: str

    def render(self) -> str:
        return f"{self.check_id}: {self.path}: {self.message}"


@dataclass(frozen=True)
class BlockCandidate:
    source_path: str
    start_line: int
    end_line: int
    heading: str
    family: Literal["prompt", "template"]
    normalized_text: str
    literal_text: str
    placeholder_ratio: float
    stable_anchors: tuple[str, ...]
    fingerprint: str
    output_contract_masked: bool
    exact_only: bool = False


@dataclass(frozen=True)
class CandidateClassification:
    family: Literal["prompt", "template"]
    exact_only: bool = False


@dataclass(frozen=True)
class RepetitionMatch:
    family: Literal["prompt", "template"]
    match_type: Literal["same-file-exact", "cross-file-exact", "same-file-fuzzy"]
    candidate: BlockCandidate
    matched: BlockCandidate
    duplicate_count: int = 1


@dataclass(frozen=True)
class ScanLimit:
    path: str
    family: Literal["prompt", "template"]
    comparisons: int
    compared_chars: int
    pair_cost: int
    total_comparisons: int
    total_compared_chars: int
    total_pair_cost: int
    reason: str


ExactCandidateKey = tuple[Literal["prompt", "template"], str, str, Optional[tuple[str, ...]]]


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

    if mode == "staged":
        return sorted(files)

    if mode == "working":
        untracked = run_git(
            ["ls-files", "--others", "--exclude-standard", "--", "*/skills/*/SKILL.md"],
            root,
        )
        files.update(root / line for line in untracked.splitlines() if line.strip())

    return sorted(path for path in files if path.is_file())


def reference_skill_files(root: Path, mode: str) -> list[Path]:
    if mode == "staged":
        output = run_git(["ls-files", "--", "*/skills/*/SKILL.md"], root)
        return sorted(root / line for line in output.splitlines() if line.strip())
    return iter_all_skill_files(root)


def dirty_skill_files(root: Path) -> list[Path]:
    output = run_git(
        ["diff", "--name-only", "--diff-filter=ACMRT", "HEAD", "--", "*/skills/*/SKILL.md"],
        root,
    )
    return sorted(root / line for line in output.splitlines() if line.strip())


def untracked_skill_files(root: Path) -> list[Path]:
    output = run_git(["ls-files", "--others", "--exclude-standard", "--", "*/skills/*/SKILL.md"], root)
    return sorted(root / line for line in output.splitlines() if line.strip())


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

    if mode == "staged":
        return sorted(files)

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


def read_index_text(root: Path, relative: str) -> str | None:
    result = subprocess.run(
        ["git", "show", f":{relative}"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def read_baseline_text(root: Path, mode: str) -> str:
    relative = SKILL_AUTHORING_BASELINE.as_posix()
    if mode == "staged":
        return read_index_text(root, relative) or ""
    path = root / SKILL_AUTHORING_BASELINE
    return read_text(path) if path.is_file() else ""


def parse_authoring_baseline(root: Path, mode: str) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in read_baseline_text(root, mode).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        path, separator, digest = line.partition("\t")
        if separator and path and digest:
            entries[path] = digest.strip()
    return entries


def skill_text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def authoring_target_skill_files(root: Path, mode: str) -> list[Path]:
    if mode in {"staged", "working"}:
        return changed_skill_files(root, mode)

    baseline = parse_authoring_baseline(root, mode)
    dirty_paths = {path.resolve() for path in dirty_skill_files(root)}
    untracked_paths = {path.resolve() for path in untracked_skill_files(root)}
    targets: set[Path] = set()

    for path in iter_all_skill_files(root):
        relative = path.relative_to(root).as_posix()
        digest = skill_text_hash(read_text(path))
        resolved = path.resolve()
        if (
            baseline.get(relative) != digest
            or resolved in dirty_paths
            or resolved in untracked_paths
        ):
            targets.add(path)

    targets.update(path for path in untracked_paths if path.is_file())
    return sorted(targets)


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


def fence_parts(line: str) -> tuple[str, str] | None:
    match = FENCE_RE.match(line)
    if not match:
        return None
    return match.group(1), match.group(2)


def fence_marker(line: str) -> str | None:
    parts = fence_parts(line)
    return parts[0] if parts else None


def is_closing_fence(line: str, active_fence: str) -> bool:
    parts = fence_parts(line)
    if not parts:
        return False
    marker, rest = parts
    return marker[0] == active_fence[0] and len(marker) >= len(active_fence) and not rest.strip()


def is_indented_code_line(line: str) -> bool:
    return line.startswith("    ") or line.startswith("\t")


def strip_html_comment_spans(line: str, in_comment: bool = False) -> tuple[str, bool]:
    pieces: list[str] = []
    search_from = 0
    current = in_comment
    while True:
        if current:
            end = line.find("-->", search_from)
            if end == -1:
                return "".join(pieces), True
            current = False
            search_from = end + 3
            continue

        start = line.find("<!--", search_from)
        if start == -1:
            pieces.append(line[search_from:])
            return "".join(pieces), False
        pieces.append(line[search_from:start])
        end = line.find("-->", start + 4)
        if end == -1:
            return "".join(pieces), True
        search_from = end + 3


def strip_invisible_markdown_blocks(text: str) -> str:
    lines = []
    active_fence: str | None = None
    in_comment = False
    for line in text.splitlines():
        marker = fence_marker(line)
        if active_fence:
            if marker and is_closing_fence(line, active_fence):
                active_fence = None
            continue
        if in_comment:
            visible_line, in_comment = strip_html_comment_spans(line, True)
            if in_comment or visible_line.strip():
                lines.append(visible_line)
            continue
        if marker:
            active_fence = marker
            continue
        if is_indented_code_line(line):
            continue
        visible_line, in_comment = strip_html_comment_spans(line, False)
        if in_comment or visible_line.strip():
            lines.append(visible_line)
    return "\n".join(lines)


def extract_markdown_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    target = normalize_anchor(heading)
    active_fence: str | None = None
    in_comment = False
    start_index: int | None = None
    start_level: int | None = None

    for index, line in enumerate(lines):
        marker = fence_marker(line)
        if active_fence:
            if marker and is_closing_fence(line, active_fence):
                active_fence = None
            continue
        if marker:
            active_fence = marker
            continue
        if is_indented_code_line(line):
            continue
        visible_line, in_comment = strip_html_comment_spans(line, in_comment)
        if in_comment and not visible_line.strip():
            continue
        match = HEADING_RE.match(visible_line)
        if not match:
            continue
        level = len(match.group(1))
        title = normalize_anchor(match.group(2))
        if start_index is None:
            if title == target and level == 2:
                start_index = index
                start_level = level
            continue
        if start_level is not None and level <= start_level:
            return "\n".join(lines[start_index:index])

    if start_index is None:
        return ""
    return "\n".join(lines[start_index:])


def strip_fenced_blocks(text: str) -> str:
    return strip_invisible_markdown_blocks(text)


def has_hygiene_exception(text: str, check_id: str) -> bool:
    section = extract_markdown_section(text, "Hygiene Exception")
    if not section:
        return False
    section = strip_fenced_blocks(section)
    pattern = re.compile(r"^[ \t]*" + re.escape(check_id) + r"[ \t]*:[ \t]*(\S.+)$", re.MULTILINE)
    return bool(pattern.search(section))


def visible_heading_titles(text: str) -> list[str]:
    titles: list[str] = []
    for line in strip_fenced_blocks(text).splitlines():
        heading = HEADING_RE.match(line)
        if heading:
            titles.append(normalize_anchor(heading.group(2)))
    return titles


def skill_id_for_path(root: Path, path: Path) -> str | None:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return None
    if len(parts) != 4 or parts[1] != "skills" or parts[3] != "SKILL.md":
        return None
    return f"{parts[0]}:{parts[2]}"


def known_skill_ids(root: Path, mode: str) -> set[str]:
    ids: set[str] = set()
    for path in reference_skill_files(root, mode):
        skill_id = skill_id_for_path(root, path)
        if skill_id:
            ids.add(skill_id)
    return ids


def extract_skill_references(text: str) -> list[str]:
    refs: list[str] = []
    seen: set[str] = set()
    for match in QUALIFIED_SKILL_REF_RE.finditer(text):
        plugin = match.group(2)
        target_id = f"{plugin}:{match.group(3)}"
        if target_id not in seen:
            refs.append(target_id)
            seen.add(target_id)
    for match in PATH_SKILL_REF_RE.finditer(text):
        target_id = f"{match.group(1)}:{match.group(2)}"
        if target_id not in seen:
            refs.append(target_id)
            seen.add(target_id)
    return refs


@dataclass(frozen=True)
class CommandBlock:
    start_line: int
    end_line: int
    text: str
    context: str


def command_blocks(text: str) -> list[CommandBlock]:
    lines = text.splitlines()
    blocks: list[CommandBlock] = []
    active_fence: str | None = None
    start_index = 0
    active_is_command = False
    content: list[str] = []
    for index, line in enumerate(lines):
        marker = fence_marker(line)
        if active_fence:
            if marker and is_closing_fence(line, active_fence):
                if active_is_command:
                    context_start = max(0, start_index - 5)
                    context = "\n".join(lines[context_start:start_index])
                    blocks.append(CommandBlock(start_index + 1, index + 1, "\n".join(content), context))
                active_fence = None
                active_is_command = False
                content = []
                continue
            content.append(line)
            continue
        parts = fence_parts(line)
        if not parts:
            continue
        active_fence = parts[0]
        start_index = index
        info = parts[1].strip().split()
        language = info[0].lower() if info else ""
        active_is_command = language in COMMAND_FENCE_LANGUAGES
        content = []
        if not active_is_command and not language:
            following = next((candidate for candidate in lines[index + 1:] if candidate.strip()), "")
            active_is_command = bool(COMMAND_START_RE.match(following))
    return blocks


def command_has_safety_language(block: CommandBlock) -> bool:
    return bool(COMMAND_SAFETY_RE.search(f"{block.context}\n{block.text}"))


def command_has_placeholder_explanation(block: CommandBlock) -> bool:
    return bool(PLACEHOLDER_EXPLANATION_RE.search(block.context))

def collapse_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def remove_fence_delimiters(text: str) -> str:
    lines: list[str] = []
    active_fence: str | None = None
    for line in text.splitlines():
        marker = fence_marker(line)
        if active_fence:
            if marker and is_closing_fence(line, active_fence):
                active_fence = None
                continue
            lines.append(line)
            continue
        if marker:
            active_fence = marker
            continue
        lines.append(line)
    return "\n".join(lines)


def strip_line_number_prefix(line: str) -> str:
    return LINE_NUMBER_PREFIX_RE.sub("", line)


def strip_line_number_prefixes(text: str) -> str:
    return "\n".join(strip_line_number_prefix(line) for line in text.splitlines())


def normalize_candidate_text(text: str) -> str:
    text = strip_line_number_prefixes(remove_fence_delimiters(text))
    normalized_lines = []
    for line in text.splitlines():
        heading = HEADING_RE.match(line)
        if heading:
            line = heading.group(2)
        normalized_lines.append(line)
    normalized = PLACEHOLDER_RE.sub(" <placeholder> ", "\n".join(normalized_lines))
    normalized = normalized.lower()
    return collapse_whitespace(normalized)


def literal_candidate_text(text: str) -> str:
    text = strip_line_number_prefixes(remove_fence_delimiters(text))
    return collapse_whitespace(PLACEHOLDER_RE.sub(" ", text).lower())


def placeholder_ratio(text: str) -> float:
    text = remove_fence_delimiters(text)
    normalized_before_replacement = collapse_whitespace(text.lower())
    placeholder_chars = sum(len(match.group(0)) for match in PLACEHOLDER_RE.finditer(text))
    return placeholder_chars / max(1, len(normalized_before_replacement))


def normalize_anchor(anchor: str) -> str:
    return collapse_whitespace(anchor.strip().strip("<>{}").lower())


def stable_anchors(text: str) -> tuple[str, ...]:
    anchors: list[str] = []
    seen: set[str] = set()
    for line in strip_line_number_prefixes(remove_fence_delimiters(text)).splitlines():
        heading = HEADING_RE.match(line)
        if heading:
            anchor = normalize_anchor(heading.group(2))
            if anchor and anchor not in seen:
                anchors.append(anchor)
                seen.add(anchor)

        yaml_key = YAML_KEY_RE.match(line)
        if yaml_key:
            anchor = normalize_anchor(yaml_key.group(1))
            if anchor and anchor not in seen:
                anchors.append(anchor)
                seen.add(anchor)

        placeholder_label = PLACEHOLDER_LABEL_RE.match(line)
        if placeholder_label:
            anchor = normalize_anchor(placeholder_label.group(1) or placeholder_label.group(2) or "")
            if anchor and anchor not in seen:
                anchors.append(anchor)
                seen.add(anchor)

        numbered_label = NUMBERED_LABEL_RE.match(line)
        if numbered_label:
            anchor = normalize_anchor(numbered_label.group(1))
            if anchor and anchor not in seen:
                anchors.append(anchor)
                seen.add(anchor)

        if "|" in line:
            cells = [normalize_anchor(cell) for cell in line.strip().strip("|").split("|")]
            for cell in cells:
                if not cell or set(cell) <= {"-"} or cell in seen:
                    continue
                anchors.append(cell)
                seen.add(cell)
    return tuple(anchors)


def split_instruction_and_output(text: str) -> tuple[str, str]:
    lines = text.splitlines()
    stripped_lines = [strip_line_number_prefix(line) for line in lines]
    for index, line in enumerate(stripped_lines):
        lower = line.lower()
        if OUTPUT_WRAPPER_HEADING_RE.match(line):
            return "\n".join(lines[:index]), "\n".join(lines[index:])
        if "|" in line and any(cell in lower for cell in ("severity", "round", "check")):
            return "\n".join(lines[:index]), "\n".join(lines[index:])
        if YAML_KEY_RE.match(line) and any(
            lower.lstrip().startswith(prefix)
            for prefix in ("status:", "outputs_written:", "next_action:", "truncated:")
        ):
            return "\n".join(lines[:index]), "\n".join(lines[index:])
    return text, ""


def count_pattern_hits(text: str, patterns: tuple[str, ...]) -> int:
    lower = text.lower()
    return sum(1 for pattern in patterns if pattern in lower)


def prompt_score(instruction_prefix: str, full_text: str) -> int:
    score = count_pattern_hits(instruction_prefix, PROMPT_ROLE_SCORE_PATTERNS) * 2
    score += count_pattern_hits(full_text, PROMPT_PHRASE_SCORE_PATTERNS) * 2
    score += count_pattern_hits(instruction_prefix, PROMPT_INPUT_SCORE_PATTERNS)
    score += imperative_prompt_score(instruction_prefix)
    return score


def template_score(output_suffix: str, full_text: str) -> int:
    template_source = output_suffix if output_suffix else full_text
    score = 0
    for line in template_source.splitlines():
        stripped = strip_line_number_prefix(line)
        if OUTPUT_WRAPPER_HEADING_RE.match(stripped):
            score += 2
        if any(pattern in stripped.lower() for pattern in TEMPLATE_SKELETON_PATTERNS):
            score += 1
        elif PLACEHOLDER_LABEL_RE.match(stripped):
            score += 1
        else:
            yaml_key = YAML_KEY_RE.match(stripped)
            if yaml_key and normalize_anchor(yaml_key.group(1)) in STRUCTURE_YAML_KEYS:
                score += 1
    return score


def imperative_prompt_score(text: str) -> int:
    score = 0
    for line in text.splitlines():
        if re.match(r"^\s*(review|inspect|report|verify|avoid|name|do|use|check)\b", line, re.IGNORECASE):
            score += 1
            if score == 4:
                return score
    return score


def is_output_contract_heading(line: str) -> bool:
    heading = HEADING_RE.match(strip_line_number_prefix(line))
    return bool(heading and normalize_anchor(heading.group(2)) == "output, token, and error contract")


def output_contract_spans(text: str) -> list[tuple[int, int]]:
    lines = text.splitlines()
    scan_lines = [""] * len(lines)
    owner_markers: dict[tuple[str, int], list[tuple[int, str]]] = {}
    fence_markers: dict[int, str] = {}
    section_levels: dict[int, int] = {0: 0}
    active_fence: str | None = None
    fence_start = -1
    in_comment = False
    section_start = 0

    for index, line in enumerate(lines):
        if active_fence:
            scan_lines[index] = line
            marker = fence_marker(line)
            if marker and is_closing_fence(line, active_fence):
                active_fence = None
                fence_start = -1
                continue

            owner = ("fence", fence_start)
            for contract_marker in FULL_CONTRACT_MARKERS:
                if contract_marker in line:
                    owner_markers.setdefault(owner, []).append((index, contract_marker))
            continue

        visible_line, in_comment = strip_html_comment_spans(line, in_comment)
        scan_lines[index] = visible_line
        if in_comment and not visible_line.strip():
            continue

        marker = fence_marker(visible_line)
        if marker:
            active_fence = marker
            fence_start = index
            fence_markers[fence_start] = marker
            continue

        heading = HEADING_RE.match(strip_line_number_prefix(visible_line))
        if heading:
            section_start = index
            section_levels[section_start] = len(heading.group(1))

        owner = ("section", section_start)
        for contract_marker in FULL_CONTRACT_MARKERS:
            if contract_marker in visible_line:
                owner_markers.setdefault(owner, []).append((index, contract_marker))

    spans: list[tuple[int, int]] = []
    for (owner_type, owner_start), marker_entries in sorted(owner_markers.items(), key=lambda item: item[0]):
        marker_kinds = {marker for _, marker in marker_entries}
        marker_lines = [line_number for line_number, _ in marker_entries]
        if len(marker_kinds) < 2:
            continue
        first_marker = min(marker_lines)
        if max(marker_lines) - first_marker > OUTPUT_CONTRACT_MAX_MARKER_SPAN_LINES:
            continue

        start = first_marker
        start_heading_level = section_levels.get(owner_start) if owner_type == "section" else None
        if owner_type == "section":
            for index in range(first_marker, owner_start - 1, -1):
                if is_output_contract_heading(scan_lines[index]):
                    start = index
                    heading = HEADING_RE.match(strip_line_number_prefix(scan_lines[index]))
                    start_heading_level = len(heading.group(1))
                    break
        else:
            for index in range(first_marker, owner_start, -1):
                if is_output_contract_heading(scan_lines[index]):
                    start = index
                    break

        limit = min(len(lines) - 1, first_marker + OUTPUT_CONTRACT_MAX_MARKER_SPAN_LINES)
        end = limit
        active_span_fence = fence_markers.get(owner_start) if owner_type == "fence" else None
        for index in range(first_marker + 1, limit + 1):
            if active_span_fence and is_closing_fence(lines[index], active_span_fence):
                end = index
                break
            if not active_span_fence and FENCE_RE.match(scan_lines[index]):
                end = index
                break
            heading = HEADING_RE.match(strip_line_number_prefix(scan_lines[index]))
            if heading and index != start:
                heading_level = len(heading.group(1))
                if start_heading_level is None or heading_level <= start_heading_level:
                    end = index - 1
                    break

        spans.append((start, end))

    return spans


def mask_output_contract_spans(text: str) -> tuple[str, bool]:
    spans = output_contract_spans(text)
    if not spans:
        return text, False

    lines = text.splitlines()
    masked_indexes: set[int] = set()
    for start, end in spans:
        masked_indexes.update(range(start, end + 1))

    kept_lines = [
        line
        for index, line in enumerate(lines)
        if index not in masked_indexes
    ]
    return "\n".join(kept_lines), True


def classify_candidate(text: str) -> CandidateClassification | None:
    instruction_prefix, output_suffix = split_instruction_and_output(text)
    normalized = normalize_candidate_text(text)
    literal = literal_candidate_text(text)
    literal_prefix = literal_candidate_text(instruction_prefix)
    ratio = placeholder_ratio(text)
    anchors = stable_anchors(text)
    nonblank_lines = sum(1 for line in text.splitlines() if line.strip())

    prompt_points = prompt_score(instruction_prefix, text)
    template_points = template_score(output_suffix, text)

    if (
        prompt_points >= 4
        and prompt_points >= template_points
        and len(literal_prefix) >= MIN_REPEATED_LITERAL_CHARS
        and (len(normalized) >= MIN_REPEATED_BLOCK_CHARS or nonblank_lines >= MIN_REPEATED_BLOCK_LINES)
        and ratio <= PROMPT_PLACEHOLDER_RATIO
    ):
        return CandidateClassification("prompt")

    structurally_anchored_template = (
        template_points >= 4
        and template_points > prompt_points
        and len(anchors) >= MIN_TEMPLATE_STRUCTURE_ANCHORS
        and len(literal) >= MIN_TEMPLATE_LITERAL_CHARS
    )
    if structurally_anchored_template:
        if ratio <= TEMPLATE_PLACEHOLDER_RATIO:
            return CandidateClassification("template")
        return CandidateClassification("template", exact_only=True)

    return None


def heading_title(line: str) -> str:
    heading = HEADING_RE.match(strip_line_number_prefix(line))
    return normalize_anchor(heading.group(2)) if heading else ""


def ranges_overlap(first_start: int, first_end: int, second_start: int, second_end: int) -> bool:
    return first_start <= second_end and second_start <= first_end


def candidate_from_text(path: Path, root: Path, text: str, start_line: int, end_line: int) -> BlockCandidate | None:
    evidence_text, output_contract_masked = mask_output_contract_spans(text)
    classification = classify_candidate(evidence_text)
    if not classification:
        return None

    normalized = normalize_candidate_text(evidence_text)
    literal = literal_candidate_text(evidence_text)
    first_heading = next((heading_title(line) for line in evidence_text.splitlines() if heading_title(line)), "")
    heading = first_heading or collapse_whitespace(text.splitlines()[0])[:60]
    return BlockCandidate(
        source_path=str(path.relative_to(root)),
        start_line=start_line,
        end_line=end_line,
        heading=heading,
        family=classification.family,
        normalized_text=normalized,
        literal_text=literal,
        placeholder_ratio=placeholder_ratio(evidence_text),
        stable_anchors=stable_anchors(evidence_text),
        fingerprint=hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16],
        output_contract_masked=output_contract_masked,
        exact_only=classification.exact_only,
    )


def fenced_ranges(lines: list[str]) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    start: int | None = None
    active_fence: str | None = None
    for index, line in enumerate(lines):
        marker = fence_marker(line)
        if not marker:
            continue
        if active_fence is None:
            active_fence = marker
            start = index
        elif is_closing_fence(line, active_fence):
            ranges.append((start, index))
            active_fence = None
            start = None
    return ranges


def internal_heading_has_candidate_structure(lines: list[str], heading_index: int) -> bool:
    lookahead = [
        strip_line_number_prefix(line)
        for line in lines[heading_index + 1:heading_index + 6]
    ]
    lookahead_text = "\n".join(lookahead)

    if STRUCTURE_PLACEHOLDER_RE.search(lookahead_text):
        return True
    if re.search(r"(for each issue|if you find no|respond with exactly)", lookahead_text, re.IGNORECASE):
        return True

    for line in lookahead:
        if "|" in line and line.count("|") >= 2:
            return True
        yaml_key = YAML_KEY_RE.match(line)
        if yaml_key and normalize_anchor(yaml_key.group(1)) in STRUCTURE_YAML_KEYS:
            return True
        if PLACEHOLDER_LABEL_RE.match(line):
            return True
    return False


def is_template_start(lines: list[str], index: int) -> bool:
    stripped = strip_line_number_prefix(lines[index])
    if OUTPUT_WRAPPER_HEADING_RE.match(stripped):
        return internal_heading_has_candidate_structure(lines, index)
    return bool(TEMPLATE_TRIGGER_RE.search(stripped))


def non_fenced_end(lines: list[str], start: int) -> int:
    limit = min(len(lines), start + MAX_CANDIDATE_LINES)
    for index in range(start + 1, limit):
        line = lines[index]
        if FENCE_RE.match(line) or line.strip() == "---":
            return index
        heading = HEADING_RE.match(strip_line_number_prefix(line))
        if heading:
            title = heading_title(line)
            if title in INTERNAL_HEADING_TITLES and internal_heading_has_candidate_structure(lines, index):
                continue
            return index
    return limit


def extract_block_candidates(root: Path, path: Path, text: str) -> list[BlockCandidate]:
    lines = text.splitlines()
    candidates: list[BlockCandidate] = []
    occupied_ranges: list[tuple[int, int]] = []

    for start, end in fenced_ranges(lines):
        candidate = candidate_from_text(path, root, "\n".join(lines[start:end + 1]), start + 1, end + 1)
        if candidate:
            candidates.append(candidate)
            occupied_ranges.append((start, end))

    for index, line in enumerate(lines):
        stripped = strip_line_number_prefix(line)
        if not (PROMPT_TRIGGER_RE.search(stripped) or is_template_start(lines, index)):
            continue
        end = non_fenced_end(lines, index)
        if end <= index:
            continue
        if any(ranges_overlap(index, end - 1, used_start, used_end) for used_start, used_end in occupied_ranges):
            continue
        candidate = candidate_from_text(path, root, "\n".join(lines[index:end]), index + 1, end)
        if candidate:
            candidates.append(candidate)
            occupied_ranges.append((index, end - 1))

    return sorted(candidates, key=lambda item: (item.source_path, item.start_line, item.end_line, item.family))


def dump_repetition_candidates(root: Path, mode: str) -> list[str]:
    lines: list[str] = []
    for path in changed_skill_files(root, mode):
        text = read_skill_text(root, path, mode)
        for candidate in extract_block_candidates(root, path, text):
            anchors = ",".join(candidate.stable_anchors)
            lines.append(
                "\t".join(
                    (
                        "candidate",
                        f"path={candidate.source_path}",
                        f"family={candidate.family}",
                        f"start_line={candidate.start_line}",
                        f"end_line={candidate.end_line}",
                        f"normalized_chars={len(candidate.normalized_text)}",
                        f"literal_chars={len(candidate.literal_text)}",
                        f"placeholder_ratio={candidate.placeholder_ratio:.3f}",
                        f"stable_anchors={anchors}",
                        f"fingerprint={candidate.fingerprint}",
                        f"output_contract_masked={str(candidate.output_contract_masked).lower()}",
                        f"exact_only={str(candidate.exact_only).lower()}",
                    )
                )
            )
    return lines


def collect_block_candidates(root: Path, paths: list[Path], mode: str) -> dict[str, list[BlockCandidate]]:
    candidates: dict[str, list[BlockCandidate]] = {}
    for path in paths:
        text = read_skill_text(root, path, mode)
        relative = str(path.relative_to(root))
        candidates[relative] = extract_block_candidates(root, path, text)
    return candidates


def collect_reference_block_candidates(
    root: Path,
    paths: list[Path],
    mode: str,
    target_map: dict[str, list[BlockCandidate]],
) -> dict[str, list[BlockCandidate]]:
    candidates: dict[str, list[BlockCandidate]] = {}
    remaining_paths: list[Path] = []
    for path in paths:
        relative = str(path.relative_to(root))
        if relative in target_map:
            candidates[relative] = target_map[relative]
        else:
            remaining_paths.append(path)

    candidates.update(collect_block_candidates(root, remaining_paths, mode))
    return candidates


def candidates_do_not_overlap(first: BlockCandidate, second: BlockCandidate) -> bool:
    if first.source_path != second.source_path:
        return True
    return not ranges_overlap(first.start_line, first.end_line, second.start_line, second.end_line)


def exact_candidate_key(candidate: BlockCandidate) -> ExactCandidateKey:
    anchors = candidate.stable_anchors if candidate.exact_only else None
    return candidate.family, candidate.fingerprint, candidate.normalized_text, anchors


def exact_candidate_match(first: BlockCandidate, second: BlockCandidate) -> bool:
    if (first.exact_only or second.exact_only) and first.stable_anchors != second.stable_anchors:
        return False
    return (
        first.family == second.family
        and first.fingerprint == second.fingerprint
        and first.normalized_text == second.normalized_text
        and candidates_do_not_overlap(first, second)
    )


def plausible_fuzzy_pair(first: BlockCandidate, second: BlockCandidate) -> bool:
    if first.family != second.family:
        return False
    if not candidates_do_not_overlap(first, second):
        return False
    first_len = len(first.normalized_text)
    second_len = len(second.normalized_text)
    if not first_len or not second_len:
        return False
    ratio = min(first_len, second_len) / max(first_len, second_len)
    return 0.80 <= ratio <= 1.25


def candidate_token_prefix(candidate: BlockCandidate) -> tuple[str, ...]:
    tokens = re.findall(r"[a-z0-9]+", candidate.literal_text)
    return tuple(tokens[:6])


def fuzzy_same_file_matches(
    target_map: dict[str, list[BlockCandidate]],
    enabled_families: set[Literal["prompt", "template"]],
) -> tuple[list[RepetitionMatch], list[ScanLimit], dict[str, dict[str, int]]]:
    matches: list[RepetitionMatch] = []
    limits: list[ScanLimit] = []
    family_totals = {
        family: {"comparisons": 0, "compared_chars": 0, "pair_cost": 0}
        for family in enabled_families
    }

    for path in sorted(target_map):
        for family in sorted(enabled_families):
            candidates = [
                candidate
                for candidate in target_map[path]
                if candidate.family == family and not candidate.exact_only
            ]
            if len(candidates) < 2:
                continue

            comparisons = 0
            compared_chars = 0
            pair_cost_total = 0
            limited_reason = ""

            for first_index, first in enumerate(candidates):
                for second in candidates[first_index + 1:]:
                    if not plausible_fuzzy_pair(first, second):
                        continue
                    if first.normalized_text == second.normalized_text:
                        continue
                    if candidate_token_prefix(first) != candidate_token_prefix(second):
                        continue

                    totals = family_totals[family]
                    pair_chars = len(first.normalized_text) + len(second.normalized_text)
                    pair_cost = len(first.normalized_text) * len(second.normalized_text)
                    if (
                        len(first.normalized_text) > MAX_FUZZY_CANDIDATE_CHARS
                        or len(second.normalized_text) > MAX_FUZZY_CANDIDATE_CHARS
                    ):
                        pair_cost_total += pair_cost
                        limited_reason = "candidate_chars"
                        break
                    if pair_cost > MAX_FUZZY_PAIR_COST_PER_COMPARISON:
                        pair_cost_total += pair_cost
                        limited_reason = "pair_cost"
                        break
                    if comparisons + 1 > MAX_FUZZY_COMPARISONS_PER_FILE:
                        pair_cost_total += pair_cost
                        limited_reason = "comparisons"
                        break
                    if compared_chars + pair_chars > MAX_FUZZY_COMPARE_CHARS_PER_FILE:
                        pair_cost_total += pair_cost
                        limited_reason = "compared_chars"
                        break
                    if totals["comparisons"] + 1 > MAX_FUZZY_COMPARISONS_TOTAL:
                        pair_cost_total += pair_cost
                        limited_reason = "total_comparisons"
                        break
                    if totals["compared_chars"] + pair_chars > MAX_FUZZY_COMPARE_CHARS_TOTAL:
                        pair_cost_total += pair_cost
                        limited_reason = "total_compared_chars"
                        break
                    if totals["pair_cost"] + pair_cost > MAX_FUZZY_PAIR_COST_TOTAL:
                        pair_cost_total += pair_cost
                        limited_reason = "total_pair_cost"
                        break

                    comparisons += 1
                    compared_chars += pair_chars
                    pair_cost_total += pair_cost
                    totals["comparisons"] += 1
                    totals["compared_chars"] += pair_chars
                    totals["pair_cost"] += pair_cost
                    similarity = SequenceMatcher(
                        None,
                        first.normalized_text,
                        second.normalized_text,
                        autojunk=False,
                    ).ratio()
                    if similarity >= REPEATED_BLOCK_SIMILARITY:
                        matches.append(RepetitionMatch(family, "same-file-fuzzy", first, second))
                if limited_reason:
                    break

            if limited_reason:
                limits.append(
                    ScanLimit(
                        path,
                        family,
                        comparisons,
                        compared_chars,
                        pair_cost_total,
                        family_totals[family]["comparisons"],
                        family_totals[family]["compared_chars"],
                        family_totals[family]["pair_cost"],
                        limited_reason,
                    )
                )

    return matches, limits, family_totals


def repetition_matches(
    root: Path,
    mode: str,
    fuzzy_families: set[Literal["prompt", "template"]] | None = None,
) -> tuple[
    list[RepetitionMatch],
    dict[str, int],
    list[ScanLimit],
    dict[str, dict[str, int]],
    dict[str, dict[str, int]],
]:
    if fuzzy_families is None:
        fuzzy_families = {"prompt", "template"}
    target_paths = changed_skill_files(root, mode)
    reference_paths = reference_skill_files(root, mode)
    target_map = collect_block_candidates(root, target_paths, mode)
    reference_map = collect_reference_block_candidates(root, reference_paths, mode, target_map)
    all_reference_candidates = [
        candidate
        for candidates in reference_map.values()
        for candidate in candidates
    ]
    candidate_counts = {
        "prompt": sum(1 for candidate in all_reference_candidates if candidate.family == "prompt"),
        "template": sum(1 for candidate in all_reference_candidates if candidate.family == "template"),
    }

    matches: list[RepetitionMatch] = []
    seen: set[tuple[str, int, int, str, int, int, str]] = set()
    exact_reference_groups: dict[ExactCandidateKey, list[BlockCandidate]] = {}
    for candidate in all_reference_candidates:
        exact_reference_groups.setdefault(exact_candidate_key(candidate), []).append(candidate)
    for group in exact_reference_groups.values():
        group.sort(key=lambda item: (item.source_path, item.start_line, item.end_line))

    canonical_exact_paths: dict[ExactCandidateKey, str] = {}
    for key, group in exact_reference_groups.items():
        candidate = group[0]
        canonical = canonical_exact_paths.get(key)
        if canonical is None or candidate.source_path < canonical:
            canonical_exact_paths[key] = candidate.source_path
    exact_index_metrics = {
        "prompt": {"group_count": 0, "max_group_size": 0},
        "template": {"group_count": 0, "max_group_size": 0},
    }
    for group in exact_reference_groups.values():
        family = group[0].family
        exact_index_metrics[family]["group_count"] += 1
        exact_index_metrics[family]["max_group_size"] = max(
            exact_index_metrics[family]["max_group_size"],
            len(group),
        )

    for target_candidates in target_map.values():
        for index, candidate in enumerate(target_candidates):
            for matched in target_candidates[index + 1:]:
                if not exact_candidate_match(candidate, matched):
                    continue
                key = (
                    candidate.source_path,
                    candidate.start_line,
                    candidate.end_line,
                    matched.source_path,
                    matched.start_line,
                    matched.end_line,
                    "same-file-exact",
                )
                if key in seen:
                    continue
                seen.add(key)
                matches.append(RepetitionMatch(candidate.family, "same-file-exact", candidate, matched))

            exact_key = exact_candidate_key(candidate)
            if mode == "all" and canonical_exact_paths.get(exact_key) == candidate.source_path:
                continue
            exact_group = exact_reference_groups.get(exact_key, [])
            other_matches = [
                matched
                for matched in exact_group
                if matched.source_path != candidate.source_path
                and exact_candidate_match(candidate, matched)
            ]
            if not other_matches:
                continue
            matched = other_matches[0]
            key = (
                candidate.source_path,
                candidate.start_line,
                candidate.end_line,
                matched.source_path,
                matched.start_line,
                matched.end_line,
                "cross-file-exact",
            )
            if key in seen:
                continue
            seen.add(key)
            matches.append(
                RepetitionMatch(
                    candidate.family,
                    "cross-file-exact",
                    candidate,
                    matched,
                    len(other_matches),
                )
            )

    fuzzy_matches, limits, family_totals = fuzzy_same_file_matches(target_map, fuzzy_families)
    matches.extend(fuzzy_matches)

    return sorted(
        matches,
        key=lambda match: (
            match.candidate.source_path,
            match.candidate.start_line,
            match.matched.source_path,
            match.matched.start_line,
            match.family,
            match.match_type,
        ),
    ), candidate_counts, limits, family_totals, exact_index_metrics


def dry_run_repetition_baseline(root: Path, mode: str) -> list[str]:
    matches, candidate_counts, limits, family_totals, exact_index_metrics = repetition_matches(root, mode)
    lines: list[str] = []
    exact_match_counts = {"prompt": 0, "template": 0}
    fuzzy_match_counts = {"prompt": 0, "template": 0}
    for match in matches:
        if match.match_type.endswith("exact"):
            exact_match_counts[match.family] += 1
        else:
            fuzzy_match_counts[match.family] += 1
        masked = match.candidate.output_contract_masked or match.matched.output_contract_masked
        lines.append(
            "\t".join(
                (
                    "match",
                    f"path={match.candidate.source_path}",
                    f"family={match.family}",
                    f"start_line={match.candidate.start_line}",
                    f"end_line={match.candidate.end_line}",
                    f"fingerprint={match.candidate.fingerprint}",
                    f"matched_path={match.matched.source_path}",
                    f"matched_start_line={match.matched.start_line}",
                    f"matched_end_line={match.matched.end_line}",
                    f"match_type={match.match_type}",
                    f"duplicate_count={match.duplicate_count}",
                    f"output_contract_masked={str(masked).lower()}",
                )
            )
        )

    limited_families = {limit.family for limit in limits}
    for family in ("prompt", "template"):
        lines.append(
            "\t".join(
                (
                    "summary",
                    f"family={family}",
                    f"candidate_count={candidate_counts[family]}",
                    f"exact_match_count={exact_match_counts[family]}",
                    f"fuzzy_match_count={fuzzy_match_counts[family]}",
                    f"limited={str(family in limited_families).lower()}",
                    f"exact_index_group_count={exact_index_metrics[family]['group_count']}",
                    f"exact_index_max_group_size={exact_index_metrics[family]['max_group_size']}",
                    f"total_comparisons={family_totals.get(family, {}).get('comparisons', 0)}",
                    f"total_compared_chars={family_totals.get(family, {}).get('compared_chars', 0)}",
                    f"total_pair_cost={family_totals.get(family, {}).get('pair_cost', 0)}",
                )
            )
        )
    return lines


def valid_scan_limit_exception(text: str) -> bool:
    section = extract_markdown_section(text, "Hygiene Exception")
    if not section:
        return False
    section = strip_fenced_blocks(section)
    evidence_pattern = re.compile(r"^[ \t]*(reviewed-with|cap-evidence)[ \t]*:[ \t]*(\S.+)$", re.MULTILINE)
    has_valid_evidence = any(
        "--dry-run-repetition-baseline" in match.group(2)
        or "tests/skill-hygiene-check-fixtures.sh" in match.group(2)
        or "tests/skill-hygiene-release-gate-fixtures.sh" in match.group(2)
        for match in evidence_pattern.finditer(section)
    )
    return (
        has_hygiene_exception(text, "repetition-scan-limited")
        and has_valid_evidence
    )


def check_repetition_scan_limits(root: Path, limits: list[ScanLimit], mode: str) -> list[Finding]:
    findings: list[Finding] = []
    by_path: dict[str, list[ScanLimit]] = {}
    for limit in limits:
        by_path.setdefault(limit.path, []).append(limit)

    for path, path_limits in sorted(by_path.items()):
        text = read_skill_text(root, root / path, mode)
        if valid_scan_limit_exception(text):
            continue
        families = ",".join(sorted({limit.family for limit in path_limits}))
        comparisons = sum(limit.comparisons for limit in path_limits)
        compared_chars = sum(limit.compared_chars for limit in path_limits)
        pair_cost = sum(limit.pair_cost for limit in path_limits)
        total_comparisons = max(limit.total_comparisons for limit in path_limits)
        total_compared_chars = max(limit.total_compared_chars for limit in path_limits)
        total_pair_cost = max(limit.total_pair_cost for limit in path_limits)
        reasons = ",".join(sorted({limit.reason for limit in path_limits}))
        findings.append(
            Finding(
                "repetition-scan-limited",
                path,
                (
                    f"families={families} comparisons={comparisons} "
                    f"compared_chars={compared_chars} pair_cost={pair_cost} "
                    f"total_comparisons={total_comparisons} "
                    f"total_compared_chars={total_compared_chars} total_pair_cost={total_pair_cost} "
                    f"reasons={reasons}; exact matching ran, but fuzzy near-duplicate "
                    "coverage was bounded"
                ),
            )
        )
    return findings


def repeated_inline_findings_from_matches(
    matches: list[RepetitionMatch],
    enabled_families: set[Literal["prompt", "template"]],
) -> list[Finding]:
    grouped: dict[tuple[str, Literal["prompt", "template"]], list[RepetitionMatch]] = {}
    for match in matches:
        if match.family not in enabled_families:
            continue
        grouped.setdefault((match.candidate.source_path, match.family), []).append(match)

    findings: list[Finding] = []
    for (path, family), path_matches in sorted(grouped.items()):
        first = path_matches[0]
        if family == "prompt":
            check_id = "repeated-inline-prompt"
            recommendation = "extract reusable prompt text to a prompt artifact or cite a shared contract"
        else:
            check_id = "repeated-inline-template"
            recommendation = "extract reusable template text to a template artifact or cite a shared contract"
        findings.append(
            Finding(
                check_id,
                path,
                (
                    f"duplicate_count={sum(match.duplicate_count for match in path_matches)} first_span="
                    f"{first.candidate.start_line}-{first.candidate.end_line} match_type={first.match_type} matches "
                    f"{first.matched.source_path}:{first.matched.start_line}-{first.matched.end_line}; "
                    f"{recommendation}"
                ),
            )
        )
    return findings


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


def check_skill_size(root: Path, skill_files: list[Path], mode: str) -> list[Finding]:
    findings: list[Finding] = []
    for path in skill_files:
        text = read_skill_text(root, path, mode)
        line_count = len(text.splitlines())
        if line_count > MAX_SKILL_LINES:
            findings.append(
                Finding(
                    "oversized-skill",
                    str(path.relative_to(root)),
                    f"skill is {line_count} lines; move long prompts/templates out of SKILL.md",
                )
            )
        elif line_count > MODERATE_SKILL_LINES and not has_hygiene_exception(text, "moderate-skill-bloat"):
            findings.append(
                Finding(
                    "moderate-skill-bloat",
                    str(path.relative_to(root)),
                    (
                        f"skill is {line_count} lines; above moderate threshold "
                        f"{MODERATE_SKILL_LINES}; extract reusable prompts/templates "
                        "or cite shared contracts, or document why the skill remains self-contained"
                    ),
                )
            )
    return findings


def check_inline_output_contract_blocks(root: Path, skill_files: list[Path], mode: str) -> list[Finding]:
    findings: list[Finding] = []
    for path in skill_files:
        text = read_skill_text(root, path, mode)
        markers = [marker for marker in FULL_CONTRACT_MARKERS if marker in text]
        if len(markers) >= 2:
            findings.append(
                Finding(
                    "inline-output-contract",
                    str(path.relative_to(root)),
                    "move repeated output/token/error contract fields to WORKFLOW-CONTRACTS.md and cite them",
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


def check_authoring_standards(root: Path, skill_files: list[Path], mode: str) -> list[Finding]:
    findings: list[Finding] = []
    known_ids = known_skill_ids(root, mode)

    for path in skill_files:
        text = read_skill_text(root, path, mode)
        relative = path.relative_to(root).as_posix()
        titles = visible_heading_titles(text)
        visible_text = strip_fenced_blocks(text)

        if not any(title in USAGE_SECTION_TITLES for title in titles) and not has_hygiene_exception(text, "missing-actionable-usage"):
            findings.append(
                Finding(
                    "missing-actionable-usage",
                    relative,
                    "skill lacks a visible usage/workflow/steps/arguments/examples section",
                )
            )

        related_section = extract_markdown_section(text, "Related Skills")
        if related_section:
            related_visible = strip_fenced_blocks(related_section)
            refs = extract_skill_references(related_visible)
            broken_refs = [ref for ref in refs if ref not in known_ids]
            for ref in broken_refs:
                if not has_hygiene_exception(text, "broken-related-skill"):
                    findings.append(
                        Finding(
                            "broken-related-skill",
                            relative,
                            f"Related Skills references unknown local skill {ref}",
                        )
                    )

            # Related Skills is optional. Validate references when authors use
            # the section without forcing every focused skill to advertise a
            # second workflow.

        for block in command_blocks(text):
            has_unsafe = bool(UNSAFE_COMMAND_RE.search(block.text) or HEREDOC_RE.search(block.text))
            if (
                has_unsafe
                and not command_has_safety_language(block)
                and not has_hygiene_exception(text, "unsafe-command-example")
            ):
                findings.append(
                    Finding(
                        "unsafe-command-example",
                        relative,
                        f"command block lines {block.start_line}-{block.end_line} contains chained, heredoc, or destructive commands without nearby safety language",
                    )
                )
                break

        for block in command_blocks(text):
            if (
                COMMAND_PLACEHOLDER_RE.search(block.text)
                and not command_has_placeholder_explanation(block)
                and not has_hygiene_exception(text, "unexplained-command-placeholder")
            ):
                findings.append(
                    Finding(
                        "unexplained-command-placeholder",
                        relative,
                        f"command block lines {block.start_line}-{block.end_line} contains placeholder tokens without nearby explanation",
                    )
                )
                break

    return findings


def run(root: Path, mode: str) -> list[Finding]:
    skill_files = changed_skill_files(root, mode)
    findings: list[Finding] = []
    findings.extend(check_description_lengths(root, skill_files, mode))
    findings.extend(check_shared_contract_references(root, skill_files, mode))
    findings.extend(check_skill_size(root, skill_files, mode))
    findings.extend(check_inline_output_contract_blocks(root, skill_files, mode))
    matches, _, limits, _, _ = repetition_matches(root, mode)
    findings.extend(repeated_inline_findings_from_matches(matches, {"prompt", "template"}))
    findings.extend(check_repetition_scan_limits(root, limits, mode))
    findings.extend(check_added_skill_metadata(root, mode))
    findings.extend(check_authoring_standards(root, authoring_target_skill_files(root, mode), mode))
    return findings


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("staged", "working", "all"), default="all")
    parser.add_argument("--dump-repetition-candidates", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--dry-run-repetition-baseline", action="store_true")
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"Repo root is not a directory: {root}", file=sys.stderr)
        return 2

    try:
        if args.dump_repetition_candidates:
            for line in dump_repetition_candidates(root, args.mode):
                print(line)
            return 0
        if args.dry_run_repetition_baseline:
            for line in dry_run_repetition_baseline(root, args.mode):
                print(line)
            return 0

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
