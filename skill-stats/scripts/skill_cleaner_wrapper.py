#!/usr/bin/env python3
"""Guarded report adapter for the external skill-cleaner analyzer."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
from pathlib import Path
from typing import Any

KNOWN_SECTIONS = (
    "Skill Budget",
    "Description candidates",
    "Duplicates",
    "Unused candidates",
    "Root summary",
)
ARCHIVE_SEGMENTS = {
    "archive",
    "archives",
    "backup",
    "backups",
    "dropbox",
    ".trash",
    "old",
    "historical",
}
STDOUT_CAP = 256 * 1024
STDERR_CAP = 32 * 1024
EVIDENCE_TTL_SECONDS = 2 * 60 * 60


def int_env(name: str, default: int) -> int:
    try:
        return max(1, int(os.environ.get(name, str(default))))
    except ValueError:
        return default


LOG_DISCOVERY_MATCH_CAP_PER_BASE = int_env("SKILL_STATS_CLEANER_LOG_DISCOVERY_MATCH_CAP", 1000)
LOG_DISCOVERY_ENTRY_CAP_PER_BASE = int_env("SKILL_STATS_CLEANER_LOG_DISCOVERY_ENTRY_CAP", 5000)


class NeedsUser(Exception):
    pass


def emit(payload: dict[str, Any]) -> int:
    print(json.dumps(payload, sort_keys=True))
    return 0


def status_payload(mode: str, status: str, message: str) -> dict[str, Any]:
    error_type = "needs_user" if status == "needs_user" else "terminal"
    return {
        "status": status,
        "mode": mode,
        "inputs_resolved": {},
        "errors": [{"type": error_type, "message": message}],
        "outputs_written": [],
        "skipped": [],
        "truncated": False,
        "next_action": "Review the error and rerun with the corrected bundle, hash, root, or config input.",
    }


def display_path(path: Path, home: Path, explicit_labels: dict[Path, str] | None = None) -> str:
    resolved = path.resolve()
    labels = explicit_labels or {}
    for root, label in sorted(labels.items(), key=lambda item: len(str(item[0])), reverse=True):
        try:
            suffix = resolved.relative_to(root)
        except ValueError:
            continue
        return label if str(suffix) == "." else f"{label}/{suffix.as_posix()}"
    try:
        suffix = resolved.relative_to(home)
    except ValueError:
        return str(resolved)
    return "~" if str(suffix) == "." else f"~/{suffix.as_posix()}"


def redact_text(text: str, home: Path, explicit_labels: dict[Path, str]) -> str:
    redacted = text.replace(str(home), "~")
    for root, label in sorted(explicit_labels.items(), key=lambda item: len(str(item[0])), reverse=True):
        redacted = redacted.replace(str(root), label)
    redacted = re.sub(r"-----BEGIN [^-]+PRIVATE KEY-----.*?-----END [^-]+PRIVATE KEY-----", "[REDACTED_PRIVATE_KEY]", redacted, flags=re.S)
    redacted = re.sub(r"\b[A-Fa-f0-9]{40,}\b", "[REDACTED_HEX]", redacted)
    redacted = re.sub(r"\b[A-Za-z0-9+/]{48,}={0,2}\b", "[REDACTED_OPAQUE]", redacted)
    return redacted


def base_report(status: str, args: argparse.Namespace, home: Path) -> dict[str, Any]:
    return {
        "status": status,
        "mode": "skill-cleaner-report",
        "inputs": {
            "analyzer": {"display_path": ""},
            "months": args.months,
            "scan_roots": [],
            "log_sources": [],
            "skipped_logs": [],
            "deep_logs": bool(args.deep_logs),
            "no_logs": bool(args.no_logs),
        },
        "inputs_resolved": {},
        "sections": [],
        "display_findings": [],
        "skipped": [],
        "errors": [],
        "outputs_written": [],
        "truncated": False,
    }


def resolve_analyzer(raw_path: str | None) -> Path:
    if not raw_path:
        raise NeedsUser("Provide --analyzer or set SKILL_STATS_CLEANER_ANALYZER.")

    root = Path(raw_path).expanduser().resolve()
    if root.is_file() and root.name == "skill-cleaner.ts" and root.parent.name == "scripts":
        script = root
    elif root.is_dir() and (root / "skills" / "skill-cleaner" / "scripts" / "skill-cleaner.ts").is_file():
        script = root / "skills" / "skill-cleaner" / "scripts" / "skill-cleaner.ts"
    elif root.is_dir() and (root / "scripts" / "skill-cleaner.ts").is_file():
        script = root / "scripts" / "skill-cleaner.ts"
    else:
        raise NeedsUser("Analyzer must be a skill-cleaner.ts script, skill directory, or agent-scripts checkout.")

    text = script.read_text(encoding="utf-8", errors="replace")
    matched_labels = sum(1 for label in KNOWN_SECTIONS if label in text)
    if "skill-cleaner" not in text or matched_labels < 2:
        raise NeedsUser("Analyzer identity check failed for skill-cleaner.ts.")
    return script


def git_root(cwd: Path) -> Path:
    result = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=cwd, check=False, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        return Path(result.stdout.strip()).resolve()
    return cwd.resolve()


def append_root(
    roots: list[dict[str, Any]],
    seen: set[Path],
    path: Path,
    source: str,
    explicit: bool,
    home: Path,
    labels: dict[Path, str],
) -> Path | None:
    if not path.exists():
        return None
    resolved = path.resolve()
    if resolved in seen:
        return None
    seen.add(resolved)
    roots.append(
        {
            "display_path": display_path(resolved, home, labels),
            "source": source,
            "explicit": explicit,
        }
    )
    return resolved


def resolve_scan_roots(args: argparse.Namespace, repo_root: Path, home: Path) -> tuple[list[dict[str, Any]], list[Path], list[Path], dict[Path, str]]:
    roots: list[dict[str, Any]] = []
    scan_paths: list[Path] = []
    explicit_paths: list[Path] = []
    labels: dict[Path, str] = {}
    seen: set[Path] = set()
    appended = append_root(roots, seen, repo_root, "repo", False, home, labels)
    if appended:
        scan_paths.append(appended)

    for plugin_dir in sorted(repo_root.glob("*/skills")):
        owner = plugin_dir.parent
        if any(plugin_dir.glob("*/SKILL.md")):
            appended = append_root(roots, seen, owner, "repo_plugin", False, home, labels)
            if appended:
                scan_paths.append(appended)

    codex_home = Path(os.environ.get("CODEX_HOME", home / ".codex")).expanduser()
    for path, source in (
        (codex_home / "skills", "codex_home"),
        (codex_home / "plugins" / "cache", "codex_plugin_cache"),
    ):
        appended = append_root(roots, seen, path, source, False, home, labels)
        if appended:
            scan_paths.append(appended)

    for raw in args.root:
        resolved = Path(raw).expanduser().resolve()
        try:
            suffix = resolved.relative_to(home)
            label = "~" if str(suffix) == "." else f"~/{suffix.as_posix()}"
        except ValueError:
            label = str(resolved)
        labels[resolved] = label
        explicit_paths.append(resolved)
        appended = append_root(roots, seen, resolved, "explicit_user_root", True, home, labels)
        if appended:
            scan_paths.append(appended)
        if len(roots) >= 20:
            break

    return roots, scan_paths, explicit_paths, labels


def has_archive_segment(path: Path) -> bool:
    return any(part.lower() in ARCHIVE_SEGMENTS for part in path.parts)


def recent(path: Path) -> bool:
    return time.time() - path.stat().st_mtime <= 90 * 24 * 60 * 60


def add_log_candidate(
    entries: list[dict[str, Any]],
    skipped: list[dict[str, Any]],
    seen: set[Path],
    path: Path,
    source: str,
    home: Path,
    labels: dict[Path, str],
    deep_logs: bool,
) -> None:
    if not path.is_file():
        return
    resolved = path.resolve()
    if resolved in seen:
        return
    seen.add(resolved)
    if has_archive_segment(resolved) and not deep_logs:
        skipped.append(
            {
                "source": source,
                "display_path": display_path(resolved, home, labels),
                "reason": "archive_or_deep_not_requested",
            }
        )
        return
    try:
        size = resolved.stat().st_size
    except OSError:
        skipped.append({"source": source, "display_path": display_path(resolved, home, labels), "reason": "unreadable"})
        return
    if not recent(resolved):
        skipped.append({"source": source, "display_path": display_path(resolved, home, labels), "reason": "older_than_90d"})
        return
    if size > 2 * 1024 * 1024:
        skipped.append({"source": source, "display_path": display_path(resolved, home, labels), "reason": "file_too_large"})
        return
    entries.append(
        {
            "display_path": display_path(resolved, home, labels),
            "source": source,
            "explicit": False,
            "_mtime": resolved.stat().st_mtime,
            "_size": size,
        }
    )


def capped_log_files(
    base: Path,
    source: str,
    skipped: list[dict[str, Any]],
    home: Path,
    labels: dict[Path, str],
):
    stack = [base]
    visited = 0
    matched = 0
    while stack:
        current = stack.pop()
        try:
            entries = os.scandir(current)
        except OSError:
            skipped.append({"source": source, "display_path": display_path(current, home, labels), "reason": "unreadable"})
            continue
        with entries:
            for entry in entries:
                visited += 1
                if visited > LOG_DISCOVERY_ENTRY_CAP_PER_BASE:
                    skipped.append(
                        {
                            "source": source,
                            "display_path": display_path(base, home, labels),
                            "reason": "source_scan_cap",
                        }
                    )
                    return
                path = Path(entry.path)
                try:
                    if entry.is_dir(follow_symlinks=False):
                        stack.append(path)
                        continue
                    if not entry.is_file(follow_symlinks=False):
                        continue
                except OSError:
                    skipped.append({"source": source, "display_path": display_path(path, home, labels), "reason": "unreadable"})
                    continue
                if path.suffix.lower() not in (".jsonl", ".log", ".txt"):
                    continue
                if matched >= LOG_DISCOVERY_MATCH_CAP_PER_BASE:
                    skipped.append(
                        {
                            "source": source,
                            "display_path": display_path(base, home, labels),
                            "reason": "source_scan_cap",
                        }
                    )
                    return
                matched += 1
                yield path


def log_cap_reasons(skipped: list[dict[str, Any]]) -> set[str]:
    cap_reasons = {"source_file_cap", "total_log_cap", "source_scan_cap", "file_too_large"}
    return {str(entry.get("reason")) for entry in skipped if entry.get("reason") in cap_reasons}


def finalize_log_sources(entries: list[dict[str, Any]], skipped: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    total_bytes = 0
    sources = sorted({entry["source"] for entry in entries})
    for source in sources:
        source_entries = [entry for entry in entries if entry["source"] == source]
        source_entries.sort(key=lambda entry: (-float(entry["_mtime"]), entry["display_path"]))
        for index, entry in enumerate(source_entries):
            if index >= 20:
                skipped.append(
                    {
                        "source": source,
                        "display_path": entry["display_path"],
                        "reason": "source_file_cap",
                    }
                )
                continue
            if total_bytes + int(entry["_size"]) > 20 * 1024 * 1024:
                skipped.append(
                    {
                        "source": source,
                        "display_path": entry["display_path"],
                        "reason": "total_log_cap",
                    }
                )
                continue
            total_bytes += int(entry["_size"])
            selected.append({key: value for key, value in entry.items() if not key.startswith("_")})
    return selected


def resolve_logs(args: argparse.Namespace, home: Path, labels: dict[Path, str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if args.no_logs:
        return [], []

    entries: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    seen: set[Path] = set()

    claude = home / ".claude"
    add_log_candidate(entries, skipped, seen, claude / "skill-stats.jsonl", "claude_recent", home, labels, args.deep_logs)
    for base in (claude / "projects", claude / "logs", claude):
        if base.exists():
            for path in capped_log_files(base, "claude_recent", skipped, home, labels):
                if base == claude and not has_archive_segment(path):
                    continue
                add_log_candidate(entries, skipped, seen, path, "claude_recent", home, labels, args.deep_logs)

    codex_home = Path(os.environ.get("CODEX_HOME", home / ".codex")).expanduser()
    for dirname in ("sessions", "logs", "history"):
        base = codex_home / dirname
        if base.exists():
            for path in capped_log_files(base, "codex_recent", skipped, home, labels):
                add_log_candidate(entries, skipped, seen, path, "codex_recent", home, labels, args.deep_logs)

    openclaw_home = Path(os.environ.get("OPENCLAW_HOME", home / ".openclaw")).expanduser()
    if openclaw_home.exists():
        for dirname in ("sessions", "logs", "history"):
            base = openclaw_home / dirname
            if base.exists():
                for path in capped_log_files(base, "openclaw_recent", skipped, home, labels):
                    add_log_candidate(entries, skipped, seen, path, "openclaw_recent", home, labels, args.deep_logs)

    return finalize_log_sources(entries, skipped), skipped


def run_analyzer(script: Path, args: argparse.Namespace, scan_roots: list[Path]) -> tuple[str, str, bool, bool]:
    node = shutil.which("node")
    if not node:
        raise NeedsUser("node is required to run the external skill-cleaner analyzer.")
    command = [
        node,
        "--experimental-strip-types",
        str(script),
        "--months",
        str(args.months),
    ]
    optional_flags = (
        ("--max-log-mb", args.max_log_mb),
        ("--context-tokens", args.context_tokens),
        ("--budget-percent", args.budget_percent),
    )
    for flag, value in optional_flags:
        if value is not None:
            command.extend([flag, str(value)])
    for root in scan_roots:
        command.extend(["--root", str(root)])
    if args.deep_logs:
        command.append("--deep-logs")
    if args.no_logs:
        command.append("--no-logs")

    with tempfile.TemporaryFile() as stdout_file, tempfile.TemporaryFile() as stderr_file:
        result = subprocess.run(command, check=False, stdout=stdout_file, stderr=stderr_file, timeout=90)
        stdout_file.seek(0, os.SEEK_END)
        stderr_file.seek(0, os.SEEK_END)
        stdout_size = stdout_file.tell()
        stderr_size = stderr_file.tell()
        stdout_truncated = stdout_size > STDOUT_CAP
        stderr_truncated = stderr_size > STDERR_CAP
        stdout_file.seek(0)
        stderr_file.seek(0)
        stdout = stdout_file.read(STDOUT_CAP).decode("utf-8", errors="replace")
        stderr = stderr_file.read(STDERR_CAP).decode("utf-8", errors="replace")
    if result.returncode != 0:
        stderr = stderr or f"analyzer exited {result.returncode}"
    return stdout, stderr, stdout_truncated or stderr_truncated, result.returncode == 0


def parse_sections(stdout: str, home: Path, labels: dict[Path, str]) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in stdout.splitlines():
        heading = line.strip().lstrip("#").strip()
        stripped = line.strip()
        if stripped.startswith("#"):
            if heading in KNOWN_SECTIONS:
                current = {"name": heading, "lines": [], "truncated": False}
                sections.append(current)
            else:
                current = None
            continue
        if current is not None and line.strip():
            if len(current["lines"]) < 20:
                current["lines"].append(redact_text(line.strip(), home, labels))
            else:
                current["truncated"] = True
    return sections


def raw_section_text(stdout: str, section_name: str) -> str:
    lines: list[str] = []
    current: str | None = None
    for line in stdout.splitlines():
        heading = line.strip().lstrip("#").strip()
        stripped = line.strip()
        if stripped.startswith("#"):
            current = heading if heading in KNOWN_SECTIONS else None
            continue
        if current == section_name:
            lines.append(line)
    return "\n".join(lines)


def unknown_markdown_headings(stdout: str) -> list[str]:
    headings: list[str] = []
    for line in stdout.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        heading = stripped.lstrip("#").strip()
        if heading and heading not in KNOWN_SECTIONS:
            headings.append(heading)
    return headings


def frontmatter_description(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise NeedsUser("SKILL.md missing YAML frontmatter")
    end = None
    for index, line in enumerate(lines[1:], 1):
        if line == "---":
            end = index
            break
    if end is None:
        raise NeedsUser("SKILL.md frontmatter is not closed")
    descriptions = [line[len("description: ") :] for line in lines[1:end] if line.startswith("description: ")]
    if len(descriptions) != 1:
        raise NeedsUser("SKILL.md must have exactly one simple description field")
    return descriptions[0]


def frontmatter_name(path: Path) -> str:
    skill_path = path / "SKILL.md" if path.is_dir() else path
    text = skill_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return path.parent.name if skill_path.name == "SKILL.md" else path.name
    for line in lines[1:]:
        if line == "---":
            break
        if line.startswith("name: "):
            return line[len("name: ") :].strip() or path.name
    return path.parent.name if skill_path.name == "SKILL.md" else path.name


def valid_single_line(value: str) -> bool:
    if not value or "\n" in value or "\r" in value or any(ord(char) < 32 for char in value):
        return False
    if value != value.strip():
        return False
    if value[0] in "-?:!&*#{}[],|>@`\"'%":
        return False
    return ": " not in value and " #" not in value


def config_disable_candidates(target: Path, kept: Path, order: int, args: argparse.Namespace) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    value = frontmatter_name(target)
    for config_index, raw_config in enumerate(args.config, 1):
        config = Path(raw_config).expanduser().resolve()
        try:
            data = load_json_file(config)
            target_list = resolve_pointer(data, "/disabledSkills")
        except (NeedsUser, OSError):
            continue
        if not isinstance(target_list, list) or value in target_list:
            continue
        candidates.append(
            {
                "action_id": f"action:disable:{order:03d}:{config_index:02d}",
                "action": "disable_json_config_entry",
                "canonical_target_path": str(config),
                "display_target_path": str(config),
                "payload": {
                    "json_pointer": "/disabledSkills",
                    "value": value,
                    "kept_copy": str(kept),
                    "duplicate_target_path": str(target),
                    "duplicate_skill_name": value,
                    "prior_value_present": False,
                    "prior_list_values_hash": sha256_id(target_list),
                    "rollback_snapshot_hash": file_sha256(config),
                },
                "required_authorization": "explicit_config",
                "preconditions": ["json_pointer_list", "value_absent_before"],
                "rollback": "restore JSON file from captured rollback snapshot",
            }
        )
    return candidates


def duplicate_findings(
    stdout: str,
    home: Path,
    labels: dict[Path, str],
    args: argparse.Namespace,
    scan_roots: list[Path],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    evidence_findings: list[dict[str, Any]] = []
    display_findings: list[dict[str, Any]] = []
    order = 1
    pattern = re.compile(r"duplicate:\s+(?P<target>.*?)\s+kept:\s+(?P<kept>.*?)\s+confidence:\s+(?P<confidence>\w+)")
    for line in stdout.splitlines():
        match = pattern.search(line)
        if not match:
            continue
        target = Path(match.group("target")).expanduser().resolve()
        kept = Path(match.group("kept")).expanduser().resolve()
        confidence = match.group("confidence").lower()
        finding_id = f"finding:duplicate:{order:03d}"
        action_id = f"action:delete:{order:03d}"
        action_candidates: list[dict[str, Any]] = []
        manual_only = True
        target_valid = False
        try:
            require_skill_target(target)
            target_valid = is_under(target, scan_roots)
        except NeedsUser:
            target_valid = False
        if target_valid and kept.is_file() and kept.name == "SKILL.md" and target != kept and target not in kept.parents and is_under(kept, scan_roots):
            manual_only = False
            action_candidates.append(
                {
                    "action_id": action_id,
                    "action": "delete_path",
                    "canonical_target_path": str(target),
                    "display_target_path": display_path(target, home, labels),
                    "payload": {"kept_copy": str(kept), "untracked_policy": "tracked_only"},
                    "required_authorization": "mutation_root",
                    "preconditions": ["kept_copy_exists", "target_is_skill", "tracked_only_clean"],
                    "rollback": "restore from git or named backup",
                }
            )
            action_candidates.extend(config_disable_candidates(target, kept, order, args))
        evidence_findings.append(
            {
                "finding_id": finding_id,
                "finding_type": "duplicate",
                "source_section": "Duplicates",
                "source_excerpt": redact_text(line.strip(), home, labels),
                "evidence_order": order,
                "confidence": confidence,
                "manual_only": manual_only,
                "canonical_target_path": str(target),
                "display_target_path": display_path(target, home, labels),
                "action_candidates": action_candidates,
            }
        )
        display_findings.append(
            {
                "finding_id": finding_id,
                "finding_type": "duplicate",
                "display_target_path": display_path(target, home, labels),
                "confidence": confidence,
                "manual_only": manual_only,
                "action_candidates": [
                    {
                        "action_id": candidate["action_id"],
                        "action": candidate["action"],
                        "display_target_path": display_path(Path(candidate["canonical_target_path"]), home, labels),
                        "rationale": "near-copy duplicate reported by analyzer",
                    }
                    for candidate in action_candidates
                ],
            }
        )
        order += 1
    return evidence_findings, display_findings


def description_findings(
    stdout: str,
    home: Path,
    labels: dict[Path, str],
    scan_roots: list[Path],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    evidence_findings: list[dict[str, Any]] = []
    display_findings: list[dict[str, Any]] = []
    pattern = re.compile(
        r"description:\s+(?P<target>.*?)\s+old:\s+(?P<old>.*?)\s+new:\s+(?P<new>.*?)\s+confidence:\s+(?P<confidence>\w+)"
    )
    order = 1
    for line in stdout.splitlines():
        match = pattern.search(line)
        if not match:
            continue
        target = Path(match.group("target")).expanduser().resolve()
        old_description = match.group("old").strip()
        new_description = match.group("new").strip()
        confidence = match.group("confidence").lower()
        finding_id = f"finding:description:{order:03d}"
        action_id = f"action:description:{order:03d}"
        action_candidates: list[dict[str, Any]] = []
        manual_only = True
        try:
            if is_under(target, scan_roots):
                validate_description(target, old_description)
            if is_under(target, scan_roots) and valid_single_line(new_description):
                manual_only = False
                action_candidates.append(
                    {
                        "action_id": action_id,
                        "action": "edit_skill_description",
                        "canonical_target_path": str(target),
                        "display_target_path": display_path(target, home, labels),
                        "payload": {"old_description": old_description, "new_description": new_description},
                        "required_authorization": "mutation_root",
                        "preconditions": ["old_description_matches", "single_line_frontmatter_description"],
                        "rollback": "restore old_description",
                    }
                )
        except NeedsUser:
            pass
        evidence_findings.append(
            {
                "finding_id": finding_id,
                "finding_type": "description_candidate",
                "source_section": "Description candidates",
                "source_excerpt": redact_text(line.strip(), home, labels),
                "evidence_order": 1000 + order,
                "confidence": confidence,
                "manual_only": manual_only,
                "canonical_target_path": str(target),
                "display_target_path": display_path(target, home, labels),
                "action_candidates": action_candidates,
            }
        )
        display_findings.append(
            {
                "finding_id": finding_id,
                "finding_type": "description_candidate",
                "display_target_path": display_path(target, home, labels),
                "confidence": confidence,
                "manual_only": manual_only,
                "action_candidates": [
                    {
                        "action_id": candidate["action_id"],
                        "action": candidate["action"],
                        "display_target_path": display_path(Path(candidate["canonical_target_path"]), home, labels),
                        "rationale": "description budget candidate reported by analyzer",
                    }
                    for candidate in action_candidates
                ],
            }
        )
        order += 1
    return evidence_findings, display_findings


def secure_output_dir(raw_dir: str | None, prefix: str) -> Path:
    if not raw_dir:
        base = Path(os.environ.get("TMPDIR", "/tmp")).expanduser()
        try:
            return Path(tempfile.mkdtemp(prefix=prefix, dir=str(base))).resolve()
        except OSError as exc:
            raise NeedsUser(f"cannot create private output directory under {base}: {exc}") from exc
    path = Path(raw_dir).expanduser()
    if path.exists() and path.is_symlink():
        raise NeedsUser(f"output directory must not be a symlink: {path}")
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise NeedsUser(f"cannot create output directory: {path}: {exc}") from exc
    if path.is_symlink():
        raise NeedsUser(f"output directory must not be a symlink: {path}")
    try:
        path.chmod(0o700)
    except OSError as exc:
        raise NeedsUser(f"cannot protect output directory: {path}: {exc}") from exc
    return path.resolve()


def write_private_json(path: Path, data: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(path, flags, 0o600)
    except OSError as exc:
        raise NeedsUser(f"cannot write private JSON bundle: {path}: {exc}") from exc
    with os.fdopen(fd, "wb") as handle:
        handle.write(data)


def write_evidence(args: argparse.Namespace, report: dict[str, Any], findings: list[dict[str, Any]], script: Path, repo_root: Path) -> Path:
    digest_input = json.dumps(
        {
            "created": time.time_ns(),
            "script": str(script),
            "findings": findings,
        },
        sort_keys=True,
    ).encode("utf-8")
    report_id = "report:" + hashlib.sha256(digest_input).hexdigest()[:16]
    evidence_dir = secure_output_dir(args.evidence_dir, "skill-stats-cleaner-evidence-")
    evidence_path = evidence_dir / f"{report_id.removeprefix('report:')}.json"
    evidence = {
        "report_id": report_id,
        "findings": findings,
        "display_findings": report["display_findings"],
        "analyzer_path_hash": "sha256:" + hashlib.sha256(str(script).encode("utf-8")).hexdigest(),
        "analyzer_identity": {"display_path": report["inputs"]["analyzer"]["display_path"]},
        "inputs": report["inputs"],
        "wrapper_version": 1,
        "repo_root": str(repo_root),
        "created_at": int(time.time()),
        "expires_at": int(time.time()) + EVIDENCE_TTL_SECONDS,
    }
    data = json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode("utf-8")
    write_private_json(evidence_path, data)
    report["report_id"] = report_id
    report["evidence_bundle"] = {
        "path": str(evidence_path),
        "display_path": str(evidence_path),
        "sha256": hashlib.sha256(data).hexdigest(),
    }
    report["outputs_written"] = [str(evidence_path)]
    return evidence_path


def command_report(args: argparse.Namespace) -> int:
    cwd = Path.cwd().resolve()
    home = Path(os.environ.get("HOME", "~")).expanduser().resolve()
    report = base_report("success", args, home)
    raw_analyzer = args.analyzer or os.environ.get("SKILL_STATS_CLEANER_ANALYZER")

    try:
        script = resolve_analyzer(raw_analyzer)
    except NeedsUser as exc:
        report["status"] = "needs_user"
        report["errors"].append({"type": "needs_user", "message": str(exc)})
        report["next_action"] = "Provide --analyzer or set SKILL_STATS_CLEANER_ANALYZER to skill-cleaner.ts."
        return emit(report)

    repo_root = git_root(cwd)
    scan_roots, scan_paths, _explicit_roots, labels = resolve_scan_roots(args, repo_root, home)
    report["inputs"]["analyzer"] = {"display_path": display_path(script, home, labels)}
    report["inputs"]["scan_roots"] = scan_roots
    log_sources, skipped_logs = resolve_logs(args, home, labels)
    report["inputs"]["log_sources"] = log_sources
    report["inputs"]["skipped_logs"] = skipped_logs
    report["inputs_resolved"] = report["inputs"]

    try:
        stdout, stderr, truncated, analyzer_ok = run_analyzer(script, args, scan_paths)
    except NeedsUser as exc:
        report["status"] = "needs_user"
        report["errors"].append({"type": "needs_user", "message": str(exc)})
        report["next_action"] = "Install node or rerun after fixing analyzer setup."
        return emit(report)
    except subprocess.TimeoutExpired:
        stdout = ""
        stderr = "analyzer timed out"
        truncated = False
        analyzer_ok = False

    capped_log_reasons = log_cap_reasons(skipped_logs)
    log_cap_hit = bool(capped_log_reasons)
    report["truncated"] = bool(truncated or log_cap_hit)
    sections = parse_sections(stdout, home, labels)
    log_scope_limited = bool(log_sources) and not args.no_logs
    unknown_headings = unknown_markdown_headings(stdout)
    if sections and analyzer_ok and not truncated and not log_cap_hit and not unknown_headings and not log_scope_limited:
        duplicate_evidence, duplicate_display = duplicate_findings(raw_section_text(stdout, "Duplicates"), home, labels, args, scan_paths)
        description_evidence, description_display = description_findings(raw_section_text(stdout, "Description candidates"), home, labels, scan_paths)
        findings = [*duplicate_evidence, *description_evidence]
        display_findings = [*duplicate_display, *description_display]
    else:
        findings, display_findings = [], []
    report["display_findings"] = display_findings
    if sections:
        report["sections"] = sections
    else:
        report["status"] = "degraded"
        report["sections"] = [
            {
                "name": "Raw analyzer excerpt",
                "lines": [redact_text(line, home, labels) for line in stdout.splitlines()[:20]],
                "truncated": bool(truncated),
            }
        ]
        report["errors"].append({"type": "degraded", "message": "known analyzer sections were not found"})

    if not analyzer_ok:
        report["status"] = "degraded"
        report["errors"].append({"type": "degraded", "message": redact_text(stderr, home, labels)})
    elif truncated:
        report["status"] = "degraded"
        report["errors"].append({"type": "degraded", "message": "analyzer output was truncated"})
    elif log_cap_hit:
        report["status"] = "degraded"
        report["skipped"].append("log discovery was capped; cleanup action ids suppressed")
        report["errors"].append({"type": "degraded", "message": f"log discovery was capped: {', '.join(sorted(capped_log_reasons))}"})
    elif unknown_headings:
        report["status"] = "degraded"
        safe_headings = [redact_text(heading[:80], home, labels) for heading in unknown_headings[:5]]
        report["errors"].append({"type": "degraded", "message": f"unknown analyzer headings: {', '.join(safe_headings)}"})
    elif log_scope_limited:
        report["status"] = "degraded"
        report["skipped"].append("log source forwarding unsupported by external analyzer wrapper; rerun with --no-logs for cleanup action ids")
        report["errors"].append({"type": "degraded", "message": "explicit bounded log sources were recorded but not forwarded to the analyzer"})

    try:
        write_evidence(args, report, findings, script, repo_root)
    except NeedsUser as exc:
        report["status"] = "needs_user"
        report["errors"].append({"type": "needs_user", "message": str(exc)})
        report["outputs_written"] = []
    report["inputs_resolved"] = report["inputs"]
    if "next_action" not in report:
        report["next_action"] = "Select action_id values only after reviewing the redacted report."
    return emit(report)


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise NeedsUser(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def load_json_file(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)
    except OSError as exc:
        raise NeedsUser(f"cannot read JSON: {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise NeedsUser(f"invalid JSON: {path}: {exc}") from exc


def int_field(data: dict[str, Any], key: str, default: int | None = None) -> int:
    value = data.get(key, default)
    if value is None:
        raise NeedsUser(f"missing integer field: {key}")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise NeedsUser(f"invalid integer field: {key}") from exc


def canonical_bytes(data: Any) -> bytes:
    def normalize(value: Any) -> Any:
        if isinstance(value, str):
            return unicodedata.normalize("NFC", value)
        if isinstance(value, list):
            return [normalize(item) for item in value]
        if isinstance(value, dict):
            return {normalize(str(key)): normalize(item) for key, item in value.items()}
        return value

    return json.dumps(normalize(data), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_id(data: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(data)).hexdigest()


def file_sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def current_home() -> Path:
    return Path(os.environ.get("HOME", "~")).expanduser().resolve()


def resolved_paths(values: list[str]) -> list[Path]:
    seen: set[Path] = set()
    paths: list[Path] = []
    for value in values:
        path = Path(value).expanduser().resolve()
        if path not in seen:
            seen.add(path)
            paths.append(path)
    return sorted(paths, key=str)


def has_skill_leaf(root: Path) -> bool:
    if root.is_file() and root.name == "SKILL.md":
        return True
    if root.is_dir() and (root / "SKILL.md").is_file():
        return True
    if root.is_dir() and any(root.glob("*/SKILL.md")):
        return True
    if root.is_dir() and any(root.glob("skills/*/SKILL.md")):
        return True
    return False


def validate_mutation_roots(values: list[str], repo_root: Path, home: Path) -> list[Path]:
    paths = resolved_paths(values)
    for path in paths:
        if not path.exists() or not path.is_dir():
            raise NeedsUser(f"authorized root is not an existing directory: {path}")
        if path == Path(path.anchor):
            raise NeedsUser(f"authorized root is too broad: {path}")
        if path == home:
            raise NeedsUser(f"authorized root must not be the whole home directory: {path}")
        if path == repo_root:
            raise NeedsUser(f"authorized root must not be the whole repo root: {path}")
        if path in repo_root.parents:
            raise NeedsUser(f"authorized root is a broad ancestor of the repo: {path}")
        if not has_skill_leaf(path):
            raise NeedsUser(f"authorized root does not contain skill leaves: {path}")
    return paths


def auth_digest(roots: list[Path], configs: list[Path]) -> str:
    return sha256_id({"roots": [str(path) for path in roots], "configs": [str(path) for path in configs]})


def is_under(path: Path, roots: list[Path]) -> bool:
    resolved = path.resolve()
    for root in roots:
        try:
            resolved.relative_to(root.resolve())
            return True
        except ValueError:
            continue
    return False


def is_same_or_under(path: Path, root: Path) -> bool:
    resolved = path.resolve()
    candidate = root.resolve()
    return resolved == candidate or candidate in resolved.parents


def require_skill_target(path: Path) -> None:
    if path.is_dir() and (path / "SKILL.md").is_file():
        return
    if path.is_file() and path.name == "SKILL.md":
        return
    raise NeedsUser(f"target is not a skill directory or SKILL.md: {path}")


def pointer_parts(pointer: str) -> list[str]:
    if not pointer.startswith("/"):
        raise NeedsUser(f"unsupported JSON pointer: {pointer}")
    return [part.replace("~1", "/").replace("~0", "~") for part in pointer.lstrip("/").split("/") if part]


def resolve_pointer(data: Any, pointer: str) -> Any:
    current = data
    for part in pointer_parts(pointer):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            raise NeedsUser(f"JSON pointer does not resolve: {pointer}")
    return current


def set_pointer_value(data: Any, pointer: str, value: Any) -> None:
    parts = pointer_parts(pointer)
    if not parts:
        raise NeedsUser("cannot set whole JSON document")
    current = data
    for part in parts[:-1]:
        current = current[part]
    current[parts[-1]] = value


def read_evidence(path: Path, repo_root: Path) -> tuple[dict[str, Any], str]:
    if not path.is_file():
        raise NeedsUser(f"evidence bundle not found: {path}")
    digest = file_sha256(path)
    evidence = load_json_file(path)
    if not isinstance(evidence, dict):
        raise NeedsUser("evidence bundle must be a JSON object")
    if "expires_at" not in evidence:
        raise NeedsUser("evidence bundle missing expires_at")
    if int_field(evidence, "expires_at") < int(time.time()):
        raise NeedsUser("evidence bundle expired")
    if not evidence.get("repo_root"):
        raise NeedsUser("evidence bundle missing repo_root")
    if Path(str(evidence["repo_root"])).resolve() != repo_root:
        raise NeedsUser("evidence bundle repo root does not match current repo")
    if evidence.get("wrapper_version") != 1:
        raise NeedsUser("evidence bundle wrapper version is unsupported")
    if not evidence.get("report_id"):
        raise NeedsUser("evidence bundle missing report_id")
    if not isinstance(evidence.get("findings", []), list):
        raise NeedsUser("evidence bundle findings must be a list")
    return evidence, digest


def action_candidates(evidence: dict[str, Any]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for finding in evidence.get("findings", []):
        if not isinstance(finding, dict):
            raise NeedsUser("evidence finding must be an object")
        if not isinstance(finding.get("action_candidates", []), list):
            raise NeedsUser("evidence action_candidates must be a list")
        for candidate in finding.get("action_candidates", []):
            if not isinstance(candidate, dict):
                raise NeedsUser("evidence action candidate must be an object")
            pairs.append((finding, candidate))
    return pairs


def validate_description(path: Path, old_description: str) -> None:
    if not path.is_file() or path.name != "SKILL.md":
        raise NeedsUser(f"description target is not SKILL.md: {path}")
    if not valid_single_line(old_description):
        raise NeedsUser("old_description must be a single line")
    text = path.read_text(encoding="utf-8")
    if frontmatter_description(text) != old_description:
        raise NeedsUser(f"old_description does not match: {path}")


def validate_config_action(
    path: Path,
    pointer: str,
    value: str,
    prior_hash: str | None,
    rollback_snapshot_hash: str | None,
) -> list[Any]:
    if path.suffix.lower() != ".json":
        raise NeedsUser(f"config target is not JSON: {path}")
    if rollback_snapshot_hash and file_sha256(path) != rollback_snapshot_hash:
        raise NeedsUser("config file hash changed since report")
    data = load_json_file(path)
    target = resolve_pointer(data, pointer)
    if not isinstance(target, list):
        raise NeedsUser(f"JSON pointer does not resolve to a list: {pointer}")
    if not isinstance(value, str) or not value:
        raise NeedsUser("config value must be a non-empty string")
    if value in target:
        raise NeedsUser("config value already present; refusing config drift")
    if prior_hash and sha256_id(target) != prior_hash:
        raise NeedsUser("config list hash changed since report")
    return target


def plan_action(
    plan_id: str,
    finding: dict[str, Any],
    candidate: dict[str, Any],
    roots: list[Path],
    configs: list[Path],
    home: Path,
    labels: dict[Path, str],
) -> dict[str, Any]:
    if finding.get("manual_only"):
        raise NeedsUser(f"selected action is attached to manual-only finding: {candidate.get('action_id')}")
    action = candidate.get("action")
    payload = candidate.get("payload") or {}
    path = Path(str(candidate.get("canonical_target_path") or finding.get("canonical_target_path"))).resolve()
    base = {
        "id": plan_id,
        "action": action,
        "source_finding_id": finding.get("finding_id"),
        "source_action_id": candidate.get("action_id"),
        "path": str(path),
        "display_path": display_path(path, home, labels),
        "rationale": redact_text(str(finding.get("source_excerpt", "")), home, labels),
        "rollback": candidate.get("rollback", ""),
    }
    if not base["source_finding_id"] or not base["source_action_id"]:
        raise NeedsUser("selected action missing source ids")

    if action == "delete_path":
        if not is_under(path, roots):
            raise NeedsUser(f"delete target outside authorized roots: {path}")
        require_skill_target(path)
        kept = Path(str(payload.get("kept_copy", ""))).resolve()
        if not kept.is_file() or kept.name != "SKILL.md":
            raise NeedsUser(f"kept copy is not a SKILL.md: {kept}")
        if kept == path or (path.is_dir() and is_same_or_under(kept, path)):
            raise NeedsUser("kept copy must be outside the delete target")
        if not is_under(kept, roots):
            raise NeedsUser(f"kept copy outside authorized roots: {kept}")
        policy = str(payload.get("untracked_policy", "tracked_only"))
        if policy not in ("tracked_only", "disposable_confirmed"):
            raise NeedsUser(f"unsupported untracked_policy: {policy}")
        if policy == "disposable_confirmed" and not payload.get("disposable_rationale"):
            raise NeedsUser("disposable_confirmed delete missing disposable_rationale")
        base.update(
            {
                "kept_copy": str(kept),
                "untracked_policy": policy,
                "disposable_rationale": payload.get("disposable_rationale", ""),
            }
        )
        return base

    if action == "edit_skill_description":
        if not is_under(path, roots):
            raise NeedsUser(f"description target outside authorized roots: {path}")
        if not path.is_file() or path.name != "SKILL.md":
            raise NeedsUser(f"description target is not SKILL.md: {path}")
        old_description = str(payload.get("old_description", ""))
        new_description = str(payload.get("new_description", ""))
        if not old_description or not new_description:
            raise NeedsUser("description action missing old/new description")
        validate_description(path, old_description)
        if not valid_single_line(new_description):
            raise NeedsUser("new_description must be a safe single-line frontmatter scalar")
        base.update({"old_description": old_description, "new_description": new_description})
        return base

    if action == "disable_json_config_entry":
        if path not in configs:
            raise NeedsUser(f"config target was not explicitly authorized: {path}")
        pointer = str(payload.get("json_pointer", ""))
        value = str(payload.get("value", ""))
        duplicate_target = Path(str(payload.get("duplicate_target_path", ""))).resolve()
        duplicate_skill_name = str(payload.get("duplicate_skill_name", ""))
        if not duplicate_skill_name:
            raise NeedsUser("config action missing duplicate_skill_name")
        if not is_under(duplicate_target, roots):
            raise NeedsUser(f"config duplicate target outside authorized roots: {duplicate_target}")
        require_skill_target(duplicate_target)
        actual_skill_name = frontmatter_name(duplicate_target)
        if actual_skill_name != duplicate_skill_name:
            raise NeedsUser("config duplicate target skill name changed since report")
        if value != duplicate_skill_name and not value.endswith(f":{duplicate_skill_name}"):
            raise NeedsUser("config value does not match duplicate skill name")
        kept = Path(str(payload.get("kept_copy", ""))).resolve() if payload.get("kept_copy") else None
        if kept is not None:
            if not kept.is_file() or kept.name != "SKILL.md":
                raise NeedsUser(f"kept copy is not a SKILL.md: {kept}")
            if not is_under(kept, roots):
                raise NeedsUser(f"kept copy outside authorized roots: {kept}")
        if payload.get("prior_value_present") is not False:
            raise NeedsUser("config action does not prove prior_value_present false")
        if not payload.get("rollback_snapshot_hash"):
            raise NeedsUser("config action missing rollback snapshot hash")
        validate_config_action(path, pointer, value, payload.get("prior_list_values_hash"), payload.get("rollback_snapshot_hash"))
        base.update(
            {
                "json_pointer": pointer,
                "value": value,
                "prior_value_present": False,
                "prior_list_values_hash": payload.get("prior_list_values_hash"),
                "rollback_snapshot_hash": payload.get("rollback_snapshot_hash"),
                "kept_copy": str(kept) if kept is not None else "",
                "duplicate_target_path": str(duplicate_target),
                "duplicate_skill_name": duplicate_skill_name,
            }
        )
        return base

    raise NeedsUser(f"unsupported action: {action}")


def canonical_plan_from_evidence(
    evidence: dict[str, Any],
    selected_action_ids: list[str],
    roots: list[Path],
    configs: list[Path],
    home: Path,
) -> dict[str, Any]:
    selected = list(dict.fromkeys(selected_action_ids))
    if not selected:
        raise NeedsUser("at least one --action-id is required")
    candidates = {candidate.get("action_id"): (finding, candidate) for finding, candidate in action_candidates(evidence)}
    missing = [action_id for action_id in selected if action_id not in candidates]
    if missing:
        raise NeedsUser(f"selected action id not found in evidence bundle: {', '.join(missing)}")

    labels = {root: display_path(root, home) for root in roots}
    ordered = sorted((candidates[action_id] for action_id in selected), key=lambda pair: (pair[0].get("evidence_order", 999999), pair[1].get("action_id", "")))
    actions = [
        plan_action(f"A{index:03d}", finding, candidate, roots, configs, home, labels)
        for index, (finding, candidate) in enumerate(ordered, 1)
    ]
    preflight_apply_actions(actions, roots, configs)
    canonical_plan = {
        "version": 1,
        "created_from": "skill-cleaner-report",
        "source_report_id": evidence["report_id"],
        "allowed_apply_roots": [{"path": str(root), "source": "explicit_user_root", "explicit": True} for root in roots],
        "authorized_config_targets": [{"path": str(config), "source": "explicit_config", "explicit": True} for config in configs],
        "actions": actions,
    }
    return canonical_plan


def build_plan(args: argparse.Namespace, evidence: dict[str, Any], evidence_digest: str, evidence_path: Path, repo_root: Path) -> dict[str, Any]:
    selected = list(dict.fromkeys(args.action_id))
    home = current_home()
    roots = validate_mutation_roots(args.root, repo_root, home)
    configs = resolved_paths(args.config)
    canonical_plan = canonical_plan_from_evidence(evidence, selected, roots, configs, home)
    plan_id = sha256_id(canonical_plan)
    labels = {root: display_path(root, home) for root in roots}
    def display_action(action: dict[str, Any]) -> dict[str, Any]:
        row = {
            "id": action["id"],
            "action": action["action"],
            "display_path": display_path(Path(action["path"]), home, labels),
            "rationale": action.get("rationale", ""),
            "rollback": action.get("rollback", ""),
        }
        if action["action"] == "delete_path":
            row.update(
                {
                    "kept_copy": display_path(Path(action["kept_copy"]), home, labels),
                    "untracked_policy": action.get("untracked_policy", ""),
                    "disposable_rationale": action.get("disposable_rationale", ""),
                }
            )
        elif action["action"] == "edit_skill_description":
            row.update(
                {
                    "old_description": action.get("old_description", ""),
                    "new_description": action.get("new_description", ""),
                }
            )
        elif action["action"] == "disable_json_config_entry":
            row.update(
                {
                    "json_pointer": action.get("json_pointer", ""),
                    "value": action.get("value", ""),
                    "duplicate_target": display_path(Path(action["duplicate_target_path"]), home, labels),
                    "duplicate_skill_name": action.get("duplicate_skill_name", ""),
                    "kept_copy": display_path(Path(action["kept_copy"]), home, labels) if action.get("kept_copy") else "",
                }
            )
        return row

    display_plan = {
        "plan_id": plan_id,
        "source_report_id": evidence["report_id"],
        "actions": [display_action(action) for action in canonical_plan["actions"]],
    }
    return {
        "plan_id": plan_id,
        "canonical_plan": canonical_plan,
        "display_plan": display_plan,
        "source_report_id": evidence["report_id"],
        "evidence_bundle_path": str(evidence_path),
        "evidence_digest": evidence_digest,
        "selected_action_ids": selected,
        "authorization_inputs_digest": auth_digest(roots, configs),
        "wrapper_version": 1,
        "repo_root": str(repo_root),
        "created_at": int(time.time()),
    }


def write_plan_bundle(args: argparse.Namespace, bundle: dict[str, Any]) -> Path:
    plan_dir = secure_output_dir(args.plan_dir, "skill-stats-cleaner-plans-")
    plan_path = plan_dir / f"{bundle['plan_id'].removeprefix('sha256:')}.json"
    data = canonical_bytes(bundle)
    write_private_json(plan_path, data)
    return plan_path


def command_preflight(args: argparse.Namespace) -> int:
    repo_root = git_root(Path.cwd())
    try:
        evidence_path = Path(args.evidence_bundle).expanduser().resolve()
        evidence, evidence_digest = read_evidence(evidence_path, repo_root)
        bundle = build_plan(args, evidence, evidence_digest, evidence_path, repo_root)
        plan_path = write_plan_bundle(args, bundle)
    except NeedsUser as exc:
        return emit(status_payload("skill-cleaner-plan", "needs_user", str(exc)))

    return emit(
        {
            "status": "success",
            "mode": "skill-cleaner-plan",
            "plan_id": bundle["plan_id"],
            "plan_bundle": {"path": str(plan_path), "display_path": str(plan_path)},
            "display_plan": bundle["display_plan"],
            "inputs_resolved": {
                "evidence_bundle": str(evidence_path),
                "selected_action_ids": bundle["selected_action_ids"],
                "roots": [entry["path"] for entry in bundle["canonical_plan"]["allowed_apply_roots"]],
                "configs": [entry["path"] for entry in bundle["canonical_plan"]["authorized_config_targets"]],
            },
            "outputs_written": [str(plan_path)],
            "skipped": [],
            "errors": [],
            "truncated": False,
            "next_action": "Request current-session /plan approval for this exact plan_id before apply.",
        }
    )


def read_plan_bundle(path: Path, repo_root: Path) -> dict[str, Any]:
    if not path.is_file():
        raise NeedsUser(f"plan bundle not found: {path}")
    bundle = load_json_file(path)
    if not isinstance(bundle, dict):
        raise NeedsUser("plan bundle must be a JSON object")
    try:
        if Path(str(bundle.get("repo_root", ""))).resolve() != repo_root:
            raise NeedsUser("plan bundle repo root does not match current repo")
    except OSError as exc:
        raise NeedsUser("plan bundle repo root is invalid") from exc
    if int_field(bundle, "created_at", 0) + EVIDENCE_TTL_SECONDS < int(time.time()):
        raise NeedsUser("plan bundle expired")
    if bundle.get("wrapper_version") != 1:
        raise NeedsUser("plan bundle wrapper version is unsupported")
    canonical_plan = bundle.get("canonical_plan")
    if not isinstance(canonical_plan, dict):
        raise NeedsUser("plan bundle canonical_plan must be an object")
    if sha256_id(canonical_plan) != bundle.get("plan_id"):
        raise NeedsUser("plan bundle hash does not match canonical plan")
    if not bundle.get("evidence_bundle_path") or not bundle.get("evidence_digest"):
        raise NeedsUser("plan bundle missing evidence provenance")
    return bundle


def git_root_for_path(path: Path) -> Path | None:
    cwd = path if path.is_dir() else path.parent
    result = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=cwd, check=False, capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return Path(result.stdout.strip()).resolve()


def git_relative(git_root_path: Path, path: Path) -> str:
    return path.resolve().relative_to(git_root_path).as_posix()


def require_tracked_clean_delete_target(path: Path) -> None:
    git_root_path = git_root_for_path(path)
    if git_root_path is None:
        raise NeedsUser(f"tracked_only delete target is not inside a git worktree: {path}")
    rel = git_relative(git_root_path, path)
    tracked = subprocess.run(["git", "ls-files", "--", rel], cwd=git_root_path, check=False, capture_output=True, text=True)
    if tracked.returncode != 0 or not tracked.stdout.strip():
        raise NeedsUser(f"tracked_only delete target has no tracked files: {path}")
    status = subprocess.run(
        ["git", "status", "--porcelain=v1", "--ignored", "--untracked-files=all", "--", rel],
        cwd=git_root_path,
        check=False,
        capture_output=True,
        text=True,
    )
    if status.returncode != 0:
        raise NeedsUser(f"could not inspect git state for delete target: {path}")
    if status.stdout.strip():
        first = status.stdout.splitlines()[0]
        raise NeedsUser(f"tracked_only delete target has dirty, untracked, or ignored content: {first}")


def require_delete_policy(action: dict[str, Any], path: Path) -> None:
    policy = action.get("untracked_policy", "tracked_only")
    if policy == "tracked_only":
        require_tracked_clean_delete_target(path)
        return
    if policy == "disposable_confirmed" and action.get("disposable_rationale"):
        return
    raise NeedsUser(f"unsupported or incomplete untracked_policy: {policy}")


def paths_overlap(first: Path, second: Path) -> bool:
    a = first.resolve()
    b = second.resolve()
    return a == b or a in b.parents or b in a.parents


def preflight_apply_actions(actions: list[dict[str, Any]], roots: list[Path], configs: list[Path]) -> None:
    seen_action_ids: set[str] = set()
    seen_paths: set[str] = set()
    filesystem_targets: list[Path] = []
    seen_config_ops: set[tuple[str, str, str]] = set()
    for action in actions:
        action_id = str(action.get("id", ""))
        if not action_id or action_id in seen_action_ids:
            raise NeedsUser(f"duplicate or missing plan action id: {action_id}")
        seen_action_ids.add(action_id)
        path = Path(action["path"]).resolve()
        key = str(path)
        if key in seen_paths:
            raise NeedsUser(f"duplicate target path: {path}")
        seen_paths.add(key)
        for existing in filesystem_targets:
            if paths_overlap(path, existing):
                raise NeedsUser(f"overlapping filesystem actions: {existing} and {path}")
        filesystem_targets.append(path)
        if action["action"] == "delete_path":
            if not is_under(path, roots):
                raise NeedsUser(f"delete target outside authorized roots: {path}")
            require_skill_target(path)
            kept = Path(action["kept_copy"]).resolve()
            if not kept.is_file() or kept.name != "SKILL.md":
                raise NeedsUser(f"kept copy missing: {kept}")
            if kept == path or (path.is_dir() and is_same_or_under(kept, path)):
                raise NeedsUser("kept copy must be outside the delete target")
            if not is_under(kept, roots):
                raise NeedsUser(f"kept copy outside authorized roots: {kept}")
            require_delete_policy(action, path)
        elif action["action"] == "edit_skill_description":
            if not is_under(path, roots):
                raise NeedsUser(f"description target outside authorized roots: {path}")
            validate_description(path, action["old_description"])
        elif action["action"] == "disable_json_config_entry":
            if path not in configs:
                raise NeedsUser(f"config target was not explicitly authorized: {path}")
            duplicate_target = Path(str(action.get("duplicate_target_path", ""))).resolve()
            duplicate_skill_name = str(action.get("duplicate_skill_name", ""))
            if not duplicate_skill_name:
                raise NeedsUser("config action missing duplicate_skill_name")
            if not is_under(duplicate_target, roots):
                raise NeedsUser(f"config duplicate target outside authorized roots: {duplicate_target}")
            require_skill_target(duplicate_target)
            actual_skill_name = frontmatter_name(duplicate_target)
            if actual_skill_name != duplicate_skill_name:
                raise NeedsUser("config duplicate target skill name changed since report")
            if action["value"] != duplicate_skill_name and not action["value"].endswith(f":{duplicate_skill_name}"):
                raise NeedsUser("config value does not match duplicate skill name")
            kept = Path(str(action.get("kept_copy", ""))).resolve() if action.get("kept_copy") else None
            if kept is not None:
                if not kept.is_file() or kept.name != "SKILL.md":
                    raise NeedsUser(f"kept copy missing: {kept}")
                if not is_under(kept, roots):
                    raise NeedsUser(f"kept copy outside authorized roots: {kept}")
            op = (str(path), action["json_pointer"], action["value"])
            if op in seen_config_ops:
                raise NeedsUser(f"duplicate config disable operation: {op}")
            seen_config_ops.add(op)
            validate_config_action(
                path,
                action["json_pointer"],
                action["value"],
                action.get("prior_list_values_hash"),
                action.get("rollback_snapshot_hash"),
            )
        else:
            raise NeedsUser(f"unsupported action: {action['action']}")


def replace_description(path: Path, old_description: str, new_description: str) -> None:
    if not valid_single_line(new_description):
        raise NeedsUser("new_description must be a single line")
    text = path.read_text(encoding="utf-8")
    frontmatter_description(text)
    lines = text.splitlines(keepends=True)
    end = None
    for index, line in enumerate(lines[1:], 1):
        if line.rstrip("\n") == "---":
            end = index
            break
    if end is None:
        raise NeedsUser("SKILL.md frontmatter is not closed")
    for index in range(1, end):
        line = lines[index]
        newline = "\n" if line.endswith("\n") else ""
        if line.rstrip("\n").startswith("description: "):
            if line.rstrip("\n") != f"description: {old_description}":
                raise NeedsUser(f"old_description does not match: {path}")
            lines[index] = f"description: {new_description}{newline}"
            atomic_write_text(path, "".join(lines))
            return
    raise NeedsUser(f"old_description does not match: {path}")


def append_config_value(path: Path, pointer: str, value: str) -> None:
    parts = pointer_parts(pointer)
    if parts != ["disabledSkills"]:
        raise NeedsUser(f"config text append supports only /disabledSkills: {pointer}")
    text = path.read_text(encoding="utf-8")
    data = load_json_file(path)
    target = resolve_pointer(data, pointer)
    if value in target:
        raise NeedsUser("config value already present")
    start, end = top_level_json_array_span(text, "disabledSkills")
    updated_array = append_json_string_to_array_text(text[start:end], value)
    atomic_write_text(path, f"{text[:start]}{updated_array}{text[end:]}")


def skip_json_ws(text: str, index: int) -> int:
    while index < len(text) and text[index] in " \t\r\n":
        index += 1
    return index


def top_level_json_array_span(text: str, key: str) -> tuple[int, int]:
    decoder = json.JSONDecoder(object_pairs_hook=reject_duplicate_keys)
    index = skip_json_ws(text, 0)
    if index >= len(text) or text[index] != "{":
        raise NeedsUser("config JSON must be an object")
    index += 1
    while True:
        index = skip_json_ws(text, index)
        if index >= len(text):
            raise NeedsUser(f"config JSON key not found: {key}")
        if text[index] == "}":
            raise NeedsUser(f"config JSON key not found: {key}")
        if text[index] != '"':
            raise NeedsUser("config JSON object has unsupported formatting")
        found_key, key_end = decoder.raw_decode(text, index)
        if not isinstance(found_key, str):
            raise NeedsUser("config JSON object key must be a string")
        colon = skip_json_ws(text, key_end)
        if colon >= len(text) or text[colon] != ":":
            raise NeedsUser("config JSON object key missing colon")
        value_start = skip_json_ws(text, colon + 1)
        decoded_value, value_end = decoder.raw_decode(text, value_start)
        if found_key == key:
            if not isinstance(decoded_value, list) or value_start >= len(text) or text[value_start] != "[":
                raise NeedsUser(f"config JSON key is not an array: {key}")
            return value_start, value_end
        index = skip_json_ws(text, value_end)
        if index < len(text) and text[index] == ",":
            index += 1
            continue
        if index < len(text) and text[index] == "}":
            raise NeedsUser(f"config JSON key not found: {key}")
        raise NeedsUser("config JSON object has unsupported separator")


def json_line_indent(line: str) -> str:
    return line[: len(line) - len(line.lstrip(" \t"))]


def append_json_string_to_array_text(array_text: str, value: str) -> str:
    parsed = json.loads(array_text)
    if not isinstance(parsed, list):
        raise NeedsUser("config JSON target is not an array")
    encoded = json.dumps(value, ensure_ascii=False)
    close = array_text.rfind("]")
    if close < 0:
        raise NeedsUser("config JSON array is not closed")
    if not parsed:
        open_index = array_text.find("[")
        if "\n" not in array_text:
            return f"{array_text[:open_index + 1]}{encoded}{array_text[close:]}"
        close_line = array_text[:close].splitlines()[-1] if array_text[:close].splitlines() else ""
        close_indent = json_line_indent(close_line)
        return f"{array_text[:open_index + 1]}\n{close_indent}  {encoded}\n{close_indent}{array_text[close:]}"
    before_close = array_text[:close]
    if "\n" not in array_text:
        return f"{before_close.rstrip()}, {encoded}{array_text[close:]}"
    value_indent = ""
    for line in reversed(before_close.splitlines()):
        stripped = line.strip()
        if stripped and stripped != "[":
            value_indent = json_line_indent(line)
            break
    if not value_indent:
        close_line = array_text[:close].splitlines()[-1] if array_text[:close].splitlines() else ""
        value_indent = f"{json_line_indent(close_line)}  "
    return f"{before_close.rstrip()},\n{value_indent}{encoded}\n{array_text[close:]}"


def atomic_write_text(path: Path, text: str) -> None:
    mode = path.stat().st_mode & 0o7777
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    tmp_path = Path(tmp_name)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_path, path)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def command_apply(args: argparse.Namespace) -> int:
    repo_root = git_root(Path.cwd())
    if not args.plan_bundle:
        return emit(status_payload("skill-cleaner-apply", "needs_user", "--plan-bundle is required"))
    if not args.approved_plan_sha:
        return emit(status_payload("skill-cleaner-apply", "needs_user", "--approved-plan-sha is required"))
    plan_path = Path(args.plan_bundle).expanduser().resolve()
    try:
        bundle = read_plan_bundle(plan_path, repo_root)
        if args.approved_plan_sha != bundle["plan_id"]:
            raise NeedsUser("approved plan hash does not match plan bundle")
        roots = validate_mutation_roots(args.root, repo_root, current_home())
        configs = resolved_paths(args.config)
        if auth_digest(roots, configs) != bundle.get("authorization_inputs_digest"):
            raise NeedsUser("authorization inputs changed since preflight")
        evidence_path = Path(str(bundle["evidence_bundle_path"])).expanduser().resolve()
        evidence, evidence_digest = read_evidence(evidence_path, repo_root)
        if evidence_digest != bundle.get("evidence_digest"):
            raise NeedsUser("evidence bundle digest changed since preflight")
        expected_plan = canonical_plan_from_evidence(evidence, list(bundle.get("selected_action_ids", [])), roots, configs, current_home())
        if expected_plan != bundle["canonical_plan"]:
            raise NeedsUser("plan actions do not match evidence bundle")
        planned_roots = resolved_paths([entry["path"] for entry in bundle["canonical_plan"].get("allowed_apply_roots", [])])
        planned_configs = resolved_paths([entry["path"] for entry in bundle["canonical_plan"].get("authorized_config_targets", [])])
        if planned_roots != roots or planned_configs != configs:
            raise NeedsUser("plan authorization targets do not match current inputs")
        actions = bundle["canonical_plan"]["actions"]
        preflight_apply_actions(actions, roots, configs)
    except NeedsUser as exc:
        return emit(status_payload("skill-cleaner-apply", "needs_user", str(exc)))

    rollback: list[tuple[str, Path, Path | bytes, str | None]] = []
    touched: list[str] = []
    try:
        for action in actions:
            path = Path(action["path"]).resolve()
            if action["action"] == "delete_path":
                backup = Path(tempfile.mkdtemp(prefix="skill-cleaner-delete-")) / path.name
                if path.is_dir():
                    shutil.copytree(path, backup, symlinks=True)
                    rollback.append(("delete_path", path, backup, None))
                    shutil.rmtree(path)
                else:
                    shutil.copy2(path, backup)
                    rollback.append(("delete_path", path, backup, None))
                    path.unlink()
                touched.append(str(path))
            elif action["action"] == "edit_skill_description":
                before = path.read_bytes()
                rollback.append(("write_bytes", path, before, None))
                replace_description(path, action["old_description"], action["new_description"])
                touched.append(str(path))
            elif action["action"] == "disable_json_config_entry":
                before = path.read_bytes()
                rollback.append(("write_bytes", path, before, action.get("rollback_snapshot_hash")))
                append_config_value(path, action["json_pointer"], action["value"])
                touched.append(str(path))

        for action in actions:
            path = Path(action["path"]).resolve()
            if action["action"] == "delete_path" and path.exists():
                raise NeedsUser(f"delete postcondition failed: {path}")
            if action["action"] == "edit_skill_description":
                text = path.read_text(encoding="utf-8")
                if f"description: {action['new_description']}" not in text:
                    raise NeedsUser(f"description postcondition failed: {path}")
            if action["action"] == "disable_json_config_entry":
                data = load_json_file(path)
                if action["value"] not in resolve_pointer(data, action["json_pointer"]):
                    raise NeedsUser(f"config postcondition failed: {path}")
    except Exception as exc:
        residual: list[str] = []
        for kind, path, snapshot, expected_hash in reversed(rollback):
            if kind == "delete_path":
                if path.exists():
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                backup = snapshot
                if isinstance(backup, Path):
                    if backup.is_dir():
                        shutil.copytree(backup, path, symlinks=True)
                    else:
                        path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(backup, path)
                    shutil.rmtree(backup.parent, ignore_errors=True)
            elif kind == "write_bytes" and isinstance(snapshot, bytes):
                path.write_bytes(snapshot)
                if expected_hash and file_sha256(path) != expected_hash:
                    residual.append(str(path))
        message = f"apply failed and rollback was attempted: {exc}"
        if residual:
            message = f"{message}; rollback hash mismatch: {', '.join(residual)}"
        return emit(status_payload("skill-cleaner-apply", "needs_user", message))

    try:
        plan_path.unlink()
        touched.append(str(plan_path))
    except FileNotFoundError:
        pass
    for kind, _path, snapshot, _expected_hash in rollback:
        if kind == "delete_path" and isinstance(snapshot, Path):
            shutil.rmtree(snapshot.parent, ignore_errors=True)
    return emit(
        {
            "status": "success",
            "mode": "skill-cleaner-apply",
            "inputs_resolved": {
                "plan_bundle": str(plan_path),
                "approved_plan_sha": args.approved_plan_sha,
                "roots": [str(root) for root in roots],
                "configs": [str(config) for config in configs],
            },
            "outputs_written": touched,
            "skipped": [],
            "errors": [],
            "truncated": False,
            "next_action": "Review touched paths before committing with the owning commit workflow.",
        }
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    report = subparsers.add_parser("report")
    report.add_argument("--analyzer")
    report.add_argument("--months", type=int, default=3)
    report.add_argument("--max-log-mb", type=int)
    report.add_argument("--context-tokens", type=int)
    report.add_argument("--budget-percent", type=int)
    report.add_argument("--root", action="append", default=[])
    report.add_argument("--deep-logs", action="store_true")
    report.add_argument("--no-logs", action="store_true")
    report.add_argument("--config", action="append", default=[])
    report.add_argument("--evidence-dir")
    preflight = subparsers.add_parser("preflight-plan")
    preflight.add_argument("--evidence-bundle", required=True)
    preflight.add_argument("--action-id", action="append", default=[])
    preflight.add_argument("--root", action="append", default=[])
    preflight.add_argument("--config", action="append", default=[])
    preflight.add_argument("--plan-dir")
    apply = subparsers.add_parser("apply")
    apply.add_argument("--plan-bundle")
    apply.add_argument("--approved-plan-sha")
    apply.add_argument("--root", action="append", default=[])
    apply.add_argument("--config", action="append", default=[])
    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "report":
        return command_report(args)
    if args.command == "preflight-plan":
        return command_preflight(args)
    if args.command == "apply":
        return command_apply(args)
    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
