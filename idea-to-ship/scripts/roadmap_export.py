#!/usr/bin/env python3
"""Export idea-to-ship roadmap items to local PM-tool issue artifacts."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
ROADMAP_GENERATED_START = "<!-- idea-to-ship:roadmap generated:start -->"
ROADMAP_GENERATED_END = "<!-- idea-to-ship:roadmap generated:end -->"
EXPORT_GENERATED_START = "<!-- idea-to-ship:roadmap-export generated:start -->"
EXPORT_GENERATED_END = "<!-- idea-to-ship:roadmap-export generated:end -->"

REQUIRED_FIELDS = (
    "Status",
    "Work Type",
    "Evidence Class",
    "Confidence",
    "Source Anchors",
    "Why Now / Why Next / Why Later",
    "Owner",
    "Decision Owner",
    "Release Gate",
    "Evidence Required",
    "Dependencies",
    "Risk",
)

FIELD_TO_KEY = {
    "Status": "status",
    "Work Type": "work_type",
    "Evidence Class": "evidence_class",
    "Confidence": "confidence",
    "Source Anchors": "source_anchors",
    "Why Now / Why Next / Why Later": "rationale",
    "Owner": "owner",
    "Decision Owner": "decision_owner",
    "Release Gate": "release_gate",
    "Evidence Required": "evidence_required",
    "Dependencies": "dependencies",
    "Risk": "risk",
}

EXECUTABLE_SECTIONS = {"Now", "Next", "Later", "Milestones"}
NON_EXECUTABLE_SECTION_KEYWORDS = (
    "Candidate Backlog",
    "Candidate Work",
    "Unverified Signals",
    "Conflicts",
    "Rejected / Not Roadmap-Relevant",
)


class ExportError(Exception):
    def __init__(self, message: str, retry: str, code: int = 1) -> None:
        super().__init__(message)
        self.message = message
        self.retry = retry
        self.code = code


@dataclass(frozen=True)
class RoadmapItem:
    item_id: str
    title: str
    section: str
    fields: dict[str, str]
    anchors: list[str]
    block: str
    source_line: int


@dataclass(frozen=True)
class BlockedItem:
    item_id: str
    title: str
    reason: str


def normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(normalize_text(text).encode("utf-8")).hexdigest()


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_json(payload: Any) -> str:
    return sha256_text(canonical_json(payload))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export idea-to-ship roadmap issue artifacts")
    parser.add_argument("--source", required=True)
    parser.add_argument("--provider", required=True, choices=("linear", "gitlab"))
    parser.add_argument("--scope", required=True, choices=("portfolio", "slug"))
    parser.add_argument("--scope-id")
    parser.add_argument("--output-dir")
    parser.add_argument("--include-approved-candidates", action="store_true")
    parser.add_argument("--mapping-file")
    parser.add_argument("--manifest")
    parser.add_argument("--csv", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--generated-at")
    parser.add_argument("--max-items", type=int, default=200)
    parser.add_argument("--max-output-bytes", type=int, default=5_000_000)
    parser.add_argument("--formats", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    if args.formats:
        formats = {item.strip() for item in args.formats.split(",") if item.strip()}
        if not {"markdown", "jsonl"}.issubset(formats):
            raise ExportError(
                "--formats cannot disable required Markdown or JSONL output",
                "Remove --formats or include both markdown and jsonl. Use --csv for additive CSV output.",
                code=2,
            )
        if "csv" in formats:
            args.csv = True

    if args.max_items <= 0:
        raise ExportError("--max-items must be positive", "Pass a positive --max-items value.", code=2)
    if args.max_output_bytes <= 0:
        raise ExportError(
            "--max-output-bytes must be positive",
            "Pass a positive --max-output-bytes value.",
            code=2,
        )
    return args


def generated_at_value(value: str | None) -> str:
    if value:
        return value
    source_date_epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if source_date_epoch:
        timestamp = int(source_date_epoch)
        return dt.datetime.fromtimestamp(timestamp, tz=dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return dt.datetime.now(tz=dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def infer_scope_id(scope_type: str, source: Path, explicit: str | None) -> str:
    if explicit:
        return explicit
    if scope_type == "portfolio":
        return "portfolio"
    parts = source.parts
    if ".idea-to-ship" in parts:
        index = parts.index(".idea-to-ship")
        if index + 1 < len(parts):
            return parts[index + 1]
    raise ExportError(
        "Missing --scope-id for slug roadmap source",
        "Pass --scope-id <slug> or use a source under .idea-to-ship/<slug>/.",
        code=2,
    )


def default_output_dir(source: Path, provider: str, scope_type: str, scope_id: str) -> Path:
    if scope_type == "portfolio":
        return Path(".idea-to-ship") / "exports" / provider
    return source.parent / "exports" / provider if source.name == "roadmap.md" else Path(".idea-to-ship") / scope_id / "exports" / provider


def load_mapping(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    mapping_path = Path(path)
    try:
        return json.loads(mapping_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ExportError(
            f"Mapping file not found: {mapping_path}",
            "Fix --mapping-file or rerun without a mapping file.",
            code=2,
        ) from exc
    except json.JSONDecodeError as exc:
        raise ExportError(
            f"Mapping file is not valid JSON: {mapping_path}: {exc}",
            "Fix the mapping JSON before rerunning.",
            code=2,
        ) from exc


def provider_required_target(provider: str) -> str:
    return "team" if provider == "linear" else "project_path"


def validate_mapping(provider: str, scope_type: str, scope_id: str, mapping: dict[str, Any]) -> dict[str, Any]:
    if mapping.get("provider", provider) != provider:
        raise ExportError(
            "Mapping provider does not match --provider",
            "Use a mapping file for the selected provider or change --provider.",
        )
    if mapping.get("scope_type", scope_type) != scope_type or mapping.get("scope_id", scope_id) != scope_id:
        raise ExportError(
            "Mapping scope does not match export scope",
            "Use a mapping file with matching scope_type and scope_id.",
        )
    target = mapping.get("target") or {}
    if not isinstance(target, dict):
        raise ExportError("Mapping target must be an object", "Fix target in the mapping file.")
    required = provider_required_target(provider)
    if not target.get(required):
        raise ExportError(
            f"Missing required provider target mapping: {required}",
            f"Add target.{required} to the mapping file before rerunning.",
        )
    return target


def provider_target_summary(provider: str, target: dict[str, Any]) -> str:
    if provider == "linear":
        return f"linear team {target.get('team')}"
    return f"gitlab project {target.get('project_path')}"


def generated_section(text: str) -> tuple[str, int]:
    start = text.find(ROADMAP_GENERATED_START)
    end = text.find(ROADMAP_GENERATED_END)
    if start == -1 or end == -1 or start >= end:
        return text, 1
    prefix = text[: start + len(ROADMAP_GENERATED_START)]
    line_offset = prefix.count("\n") + 1
    return text[start + len(ROADMAP_GENERATED_START) : end], line_offset


def parse_goal(text: str) -> str:
    for line in normalize_text(text).splitlines():
        if line.startswith("goal:"):
            return line.split(":", 1)[1].strip()
    for line in normalize_text(text).splitlines():
        if line.startswith("# Roadmap - "):
            return line.removeprefix("# Roadmap - ").strip()
    return "Roadmap export"


def parse_field_lines(block: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in normalize_text(block).splitlines():
        match = re.match(r"^\*\*(.+?):\*\*\s*(.*)$", line)
        if match:
            fields[match.group(1).strip()] = match.group(2).strip()
    return fields


def split_anchors(raw: str) -> list[str]:
    value = raw.strip()
    if not value or value.lower() in {"none", "unknown"}:
        return []
    return [part.strip() for part in re.split(r"\s*,\s*|\s+;\s+", value) if part.strip()]


def parse_items(source_text: str) -> list[RoadmapItem]:
    text, line_offset = generated_section(source_text)
    lines = normalize_text(text).splitlines()
    items: list[RoadmapItem] = []
    current_section = ""
    current_start: int | None = None
    current_heading = ""
    current_lines: list[str] = []
    current_line_number = 1

    def flush() -> None:
        nonlocal current_start, current_heading, current_lines, current_line_number
        if current_start is None:
            return
        match = re.match(r"^###\s+(ITS-[A-Z0-9-]+)\s+-\s+(.+?)\s*$", current_heading)
        if match:
            block = "\n".join(current_lines).strip() + "\n"
            fields = parse_field_lines(block)
            anchors = split_anchors(fields.get("Source Anchors", ""))
            items.append(
                RoadmapItem(
                    item_id=match.group(1),
                    title=match.group(2).strip(),
                    section=current_section,
                    fields=fields,
                    anchors=anchors,
                    block=block,
                    source_line=line_offset + current_line_number - 1,
                )
            )
        current_start = None
        current_heading = ""
        current_lines = []

    for index, line in enumerate(lines, start=1):
        if line.startswith("## ") and not line.startswith("### "):
            flush()
            current_section = line.removeprefix("## ").strip()
            continue
        if line.startswith("### "):
            flush()
            current_start = index
            current_line_number = index
            current_heading = line
            current_lines = [line]
            continue
        if current_start is not None:
            current_lines.append(line)
    flush()
    return items


def blocked_reason(item: RoadmapItem, include_approved_candidates: bool) -> str | None:
    confidence = item.fields.get("Confidence", "").strip().lower()
    evidence_class = item.fields.get("Evidence Class", "").strip().lower()
    if not item.anchors:
        return "missing-source-anchors"
    if confidence == "low":
        return "weak-confidence"
    if confidence == "unknown":
        return "unknown-confidence"
    if evidence_class == "inferred":
        return "inferred-only"

    if item.section in EXECUTABLE_SECTIONS:
        return None
    if any(keyword.lower() in item.section.lower() for keyword in NON_EXECUTABLE_SECTION_KEYWORDS):
        if (
            include_approved_candidates
            and item.fields.get("External Export", "").strip().lower() == "approved"
        ):
            return None
        return "candidate-not-approved"
    return "non-executable-section"


def validate_required_fields(items: list[RoadmapItem]) -> None:
    for item in items:
        missing = [field for field in REQUIRED_FIELDS if not item.fields.get(field)]
        if missing:
            raise ExportError(
                f"Missing required fields for {item.item_id}: {', '.join(missing)}",
                f"Add {', '.join(missing)} to roadmap item {item.item_id} before rerunning.",
            )


def roadmap_fields(item: RoadmapItem) -> dict[str, Any]:
    mapped: dict[str, Any] = {}
    for field in REQUIRED_FIELDS:
        key = FIELD_TO_KEY[field]
        mapped[key] = item.anchors if key == "source_anchors" else item.fields.get(field)
    return mapped


def canonical_body(body: str, generated_at: str) -> str:
    return normalize_text(body).replace(generated_at, "<generated_at>")


def record_content_hash(record: dict[str, Any], generated_at: str) -> str:
    overview_fields = record.get("overview_fields")
    if isinstance(overview_fields, dict):
        overview_fields = {key: value for key, value in overview_fields.items() if key != "generated_at"}
    payload = {
        "provider": record["provider"],
        "scope_type": record["scope_type"],
        "scope_id": record["scope_id"],
        "role": record["role"],
        "roadmap_id": record["roadmap_id"],
        "title": record["title"],
        "body_markdown": canonical_body(str(record["body_markdown"]), generated_at),
        "overview_fields": overview_fields,
        "roadmap_fields": record["roadmap_fields"],
        "provider_fields": record["provider_fields"],
        "relation": record["relation"],
    }
    return sha256_json(payload)


def build_overview_body(goal: str, scope_type: str, scope_id: str, provider: str, target_summary: str, item_count: int, blocked_count: int, source: Path, generated_at: str) -> str:
    return "\n".join(
        [
            f"# Roadmap export - {goal}",
            "",
            f"- Scope: {scope_type}:{scope_id}",
            f"- Provider: {provider}",
            f"- Provider target: {target_summary}",
            f"- Exported items: {item_count}",
            f"- Blocked items: {blocked_count}",
            f"- Generated at: {generated_at}",
            f"- Source: {source}",
            "",
        ]
    )


def build_child_body(item: RoadmapItem) -> str:
    fields = roadmap_fields(item)
    return "\n".join(
        [
            f"# [{item.item_id}] {item.title}",
            "",
            f"- Status: {fields['status']}",
            f"- Work Type: {fields['work_type']}",
            f"- Evidence Class: {fields['evidence_class']}",
            f"- Confidence: {fields['confidence']}",
            f"- Source Anchors: {', '.join(fields['source_anchors'])}",
            f"- Rationale: {fields['rationale']}",
            f"- Release Gate: {fields['release_gate']}",
            f"- Evidence Required: {fields['evidence_required']}",
            f"- Dependencies: {fields['dependencies']}",
            f"- Risk: {fields['risk']}",
            f"- Owner: {fields['owner']}",
            f"- Decision Owner: {fields['decision_owner']}",
            "",
        ]
    )


def build_records(
    source: Path,
    source_text: str,
    provider: str,
    scope_type: str,
    scope_id: str,
    target: dict[str, Any],
    mapping_hash: str,
    provider_target_hash: str,
    generated_at: str,
    executable: list[RoadmapItem],
    blocked: list[BlockedItem],
) -> list[dict[str, Any]]:
    source_hash = sha256_text(source_text)
    overview_id = f"overview:{scope_type}:{scope_id}"
    goal = parse_goal(source_text)
    target_summary = provider_target_summary(provider, target)
    overview_body = build_overview_body(
        goal,
        scope_type,
        scope_id,
        provider,
        target_summary,
        len(executable),
        len(blocked),
        source,
        generated_at,
    )
    overview: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "provider": provider,
        "scope_type": scope_type,
        "scope_id": scope_id,
        "role": "overview",
        "roadmap_id": overview_id,
        "title": f"Roadmap export - {goal}",
        "body_markdown": overview_body,
        "overview_fields": {
            "goal": goal,
            "scope_type": scope_type,
            "scope_id": scope_id,
            "exported_item_count": len(executable),
            "blocked_item_count": len(blocked),
            "provider_target": target_summary,
            "generated_at": generated_at,
            "source_path": str(source),
        },
        "roadmap_fields": {
            "status": None,
            "work_type": None,
            "evidence_class": None,
            "confidence": None,
            "source_anchors": [],
            "rationale": "portfolio overview" if scope_type == "portfolio" else "slug overview",
            "release_gate": None,
            "evidence_required": None,
            "dependencies": None,
            "risk": None,
            "owner": "Unassigned",
            "decision_owner": "None",
        },
        "provider_fields": {
            "target": target,
            "labels": ["roadmap", "idea-to-ship"],
            "assignee": None,
        },
        "source": {"path": str(source), "content_hash": source_hash, "anchors": []},
        "provider_target": provider_target_hash,
        "mapping_hash": mapping_hash,
        "relation": None,
        "content_hash": "",
        "status": "new",
        "action": "create",
    }
    overview["content_hash"] = record_content_hash(overview, generated_at)
    records = [overview]

    for item in executable:
        body = build_child_body(item)
        record: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "generated_at": generated_at,
            "provider": provider,
            "scope_type": scope_type,
            "scope_id": scope_id,
            "role": "child",
            "roadmap_id": item.item_id,
            "title": f"[{item.item_id}] {item.title}",
            "body_markdown": body,
            "overview_fields": None,
            "roadmap_fields": roadmap_fields(item),
            "provider_fields": {
                "target": target,
                "labels": ["roadmap", f"type::{item.fields.get('Work Type', '').lower()}"],
                "assignee": None,
            },
            "source": {"path": str(source), "content_hash": source_hash, "anchors": item.anchors},
            "provider_target": provider_target_hash,
            "mapping_hash": mapping_hash,
            "relation": {"overview_id": overview_id, "kind": "child-of-overview"},
            "content_hash": "",
            "status": "new",
            "action": "create",
        }
        record["content_hash"] = record_content_hash(record, generated_at)
        records.append(record)
    return records


def render_jsonl(records: list[dict[str, Any]]) -> str:
    return "\n".join(canonical_json(record) for record in records) + "\n"


def render_markdown(records: list[dict[str, Any]], blocked: list[BlockedItem]) -> str:
    overview = records[0]
    lines = [
        "# Roadmap Export",
        "",
        EXPORT_GENERATED_START,
        "",
        str(overview["body_markdown"]).rstrip(),
        "",
        "## Child Items",
        "",
    ]
    for record in records[1:]:
        lines.extend(
            [
                f"### {record['roadmap_id']} - {record['title']}",
                f"- Status: {record['status']}",
                f"- Action: {record['action']}",
                f"- Relation: child-of {record['relation']['overview_id']}",
                "",
                str(record["body_markdown"]).rstrip(),
                "",
            ]
        )
    lines.extend(["## Blocked Items", ""])
    if blocked:
        for item in blocked:
            lines.append(f"- {item.item_id} - {item.title}: {item.reason}")
    else:
        lines.append("- None")
    lines.extend(["", EXPORT_GENERATED_END, ""])
    return "\n".join(lines)


def render_manifest(
    records: list[dict[str, Any]],
    blocked: list[BlockedItem],
    source: Path,
    source_text: str,
    provider: str,
    scope_type: str,
    scope_id: str,
    target: dict[str, Any],
    provider_target_hash: str,
    mapping_hash: str,
    generated_at: str,
) -> str:
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "scope_type": scope_type,
        "scope_id": scope_id,
        "source": {"path": str(source), "content_hash": sha256_text(source_text)},
        "provider": provider,
        "provider_target": provider_target_hash,
        "mapping_hash": mapping_hash,
        "target": target,
        "overview": {
            "roadmap_id": records[0]["roadmap_id"],
            "content_hash": records[0]["content_hash"],
            "remote_refs": [],
            "status": records[0]["status"],
            "action": records[0]["action"],
        },
        "items": {
            record["roadmap_id"]: {
                "role": "child",
                "content_hash": record["content_hash"],
                "remote_refs": [],
                "status": record["status"],
                "action": record["action"],
            }
            for record in records[1:]
        },
        "blocked": {item.item_id: {"reason": item.reason} for item in blocked},
        "conflicts": {"duplicate_remote_refs": []},
    }
    return json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_csv(records: list[dict[str, Any]]) -> str:
    from io import StringIO

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=("role", "roadmap_id", "title", "status", "action"))
    writer.writeheader()
    for record in records:
        writer.writerow(
            {
                "role": record["role"],
                "roadmap_id": record["roadmap_id"],
                "title": record["title"],
                "status": record["status"],
                "action": record["action"],
            }
        )
    return output.getvalue()


def classify_items(items: list[RoadmapItem], include_approved_candidates: bool) -> tuple[list[RoadmapItem], list[BlockedItem]]:
    seen: dict[str, RoadmapItem] = {}
    for item in items:
        if item.item_id in seen:
            raise ExportError(
                f"Duplicate roadmap ID: {item.item_id}",
                f"Make roadmap IDs unique before rerunning: {item.item_id}.",
            )
        seen[item.item_id] = item

    executable: list[RoadmapItem] = []
    blocked: list[BlockedItem] = []
    for item in items:
        reason = blocked_reason(item, include_approved_candidates)
        if reason:
            blocked.append(BlockedItem(item.item_id, item.title, reason))
        else:
            executable.append(item)
    return executable, blocked


def validate_output_budget(rendered: dict[str, str], max_output_bytes: int) -> None:
    total = sum(len(value.encode("utf-8")) for value in rendered.values())
    if total > max_output_bytes:
        raise ExportError(
            f"Rendered output exceeds --max-output-bytes ({total} > {max_output_bytes})",
            "Narrow the export scope or rerun with a larger explicit --max-output-bytes value.",
        )


def write_outputs(output_dir: Path, rendered: dict[str, str], dry_run: bool) -> None:
    if dry_run:
        return
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, content in rendered.items():
        (output_dir / name).write_text(content, encoding="utf-8", newline="\n")


def run(argv: list[str]) -> int:
    args = parse_args(argv)
    source = Path(args.source)
    if not source.is_file():
        raise ExportError(
            f"Source roadmap not found: {source}",
            "Fix --source to point at an existing roadmap file.",
            code=2,
        )

    scope_type = args.scope
    scope_id = infer_scope_id(scope_type, source, args.scope_id)
    output_dir = Path(args.output_dir) if args.output_dir else default_output_dir(source, args.provider, scope_type, scope_id)
    generated_at = generated_at_value(args.generated_at)
    source_text = normalize_text(source.read_text(encoding="utf-8"))
    mapping = load_mapping(args.mapping_file)
    target = validate_mapping(args.provider, scope_type, scope_id, mapping)
    target_identity = {
        "provider": args.provider,
        "scope_type": scope_type,
        "scope_id": scope_id,
        "target": target,
    }
    provider_target_hash = sha256_json(target_identity)
    mapping_hash = sha256_json(
        {
            "provider": args.provider,
            "scope_type": scope_type,
            "scope_id": scope_id,
            "source_path": str(source),
            "target": target,
            "assignees": mapping.get("assignees", {}),
            "labels": mapping.get("labels", {}),
            "relation_mode": "child-of-overview",
        }
    )

    items = parse_items(source_text)
    if len(items) > args.max_items:
        raise ExportError(
            f"Parsed item count exceeds --max-items ({len(items)} > {args.max_items})",
            "Narrow the export scope or rerun with a larger explicit --max-items value.",
        )
    executable, blocked = classify_items(items, args.include_approved_candidates)
    validate_required_fields(executable)

    records = build_records(
        source=source,
        source_text=source_text,
        provider=args.provider,
        scope_type=scope_type,
        scope_id=scope_id,
        target=target,
        mapping_hash=mapping_hash,
        provider_target_hash=provider_target_hash,
        generated_at=generated_at,
        executable=executable,
        blocked=blocked,
    )
    rendered = {
        "roadmap-export.md": render_markdown(records, blocked),
        "issues.jsonl": render_jsonl(records),
        "manifest.json": render_manifest(
            records,
            blocked,
            source,
            source_text,
            args.provider,
            scope_type,
            scope_id,
            target,
            provider_target_hash,
            mapping_hash,
            generated_at,
        ),
    }
    if args.csv:
        rendered["issues.csv"] = render_csv(records)
    validate_output_budget(rendered, args.max_output_bytes)
    write_outputs(output_dir, rendered, args.dry_run)

    action = "Validated" if args.dry_run else "Exported"
    print(f"{action} {len(records) - 1} child item(s), {len(blocked)} blocked item(s) for {args.provider}.")
    return 0


def main(argv: list[str]) -> int:
    try:
        return run(argv)
    except ExportError as exc:
        stream = sys.stderr if exc.code else sys.stdout
        print(exc.message, file=stream)
        print(f"Retry: {exc.retry}", file=stream)
        return exc.code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
