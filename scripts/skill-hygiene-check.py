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
from pathlib import Path
from typing import Literal


MAX_DESCRIPTION_CHARS = 320
MAX_SKILL_LINES = 750
FULL_CONTRACT_MARKERS = (
    "## Output, Token, And Error Contract",
    "status: success | needs_user | terminal | degraded",
    "truncated: true | false",
)
MAX_CANDIDATE_LINES = 80
MIN_REPEATED_LITERAL_CHARS = 300
MIN_REPEATED_BLOCK_CHARS = 600
MIN_REPEATED_BLOCK_LINES = 8
MIN_TEMPLATE_STRUCTURE_ANCHORS = 5
MIN_TEMPLATE_LITERAL_CHARS = 160
PROMPT_PLACEHOLDER_RATIO = 0.35
TEMPLATE_PLACEHOLDER_RATIO = 0.70
PLACEHOLDER_RE = re.compile(r"<[^>\n]+>|\{[^}\n]+\}|\b[A-Z][A-Z0-9_]{3,}\b")
STRUCTURE_PLACEHOLDER_RE = re.compile(r"<[^>\n]+>|\{[^}\n]+\}|\b[A-Z][A-Z0-9_]*_[A-Z0-9_]*\b")
PLACEHOLDER_LABEL_RE = re.compile(r"^\s*(?:<([^>\n:]+)>|\{([^}\n:]+)\})\s*:")
LINE_NUMBER_PREFIX_RE = re.compile(r"^\s*\d{1,5}\s*(?:[:|]\s*|\s{2,})")
FENCE_RE = re.compile(r"^\s*```")
HEADING_RE = re.compile(r"^\s*(#{1,6})\s+(.+?)\s*$")
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


def collapse_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def remove_fence_delimiters(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not FENCE_RE.match(line))


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


def has_output_contract_span(text: str) -> bool:
    return sum(1 for marker in FULL_CONTRACT_MARKERS if marker in text) >= 2


def classify_candidate(text: str) -> Literal["prompt", "template"] | None:
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
        return "prompt"

    if (
        template_points >= 4
        and template_points > prompt_points
        and len(anchors) >= MIN_TEMPLATE_STRUCTURE_ANCHORS
        and len(literal) >= MIN_TEMPLATE_LITERAL_CHARS
        and ratio <= TEMPLATE_PLACEHOLDER_RATIO
    ):
        return "template"

    return None


def heading_title(line: str) -> str:
    heading = HEADING_RE.match(strip_line_number_prefix(line))
    return normalize_anchor(heading.group(2)) if heading else ""


def ranges_overlap(first_start: int, first_end: int, second_start: int, second_end: int) -> bool:
    return first_start <= second_end and second_start <= first_end


def candidate_from_text(path: Path, root: Path, text: str, start_line: int, end_line: int) -> BlockCandidate | None:
    family = classify_candidate(text)
    if not family:
        return None

    normalized = normalize_candidate_text(text)
    literal = literal_candidate_text(text)
    first_heading = next((heading_title(line) for line in text.splitlines() if heading_title(line)), "")
    heading = first_heading or collapse_whitespace(text.splitlines()[0])[:60]
    return BlockCandidate(
        source_path=str(path.relative_to(root)),
        start_line=start_line,
        end_line=end_line,
        heading=heading,
        family=family,
        normalized_text=normalized,
        literal_text=literal,
        placeholder_ratio=placeholder_ratio(text),
        stable_anchors=stable_anchors(text),
        fingerprint=hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16],
        output_contract_masked=has_output_contract_span(text),
    )


def fenced_ranges(lines: list[str]) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    start: int | None = None
    for index, line in enumerate(lines):
        if not FENCE_RE.match(line):
            continue
        if start is None:
            start = index
        else:
            ranges.append((start, index))
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
                    )
                )
            )
    return lines


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


def run(root: Path, mode: str) -> list[Finding]:
    skill_files = changed_skill_files(root, mode)
    findings: list[Finding] = []
    findings.extend(check_description_lengths(root, skill_files, mode))
    findings.extend(check_shared_contract_references(root, skill_files, mode))
    findings.extend(check_skill_size(root, skill_files, mode))
    findings.extend(check_inline_output_contract_blocks(root, skill_files, mode))
    findings.extend(check_added_skill_metadata(root, mode))
    return findings


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("staged", "working", "all"), default="all")
    parser.add_argument("--dump-repetition-candidates", action="store_true", help=argparse.SUPPRESS)
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
