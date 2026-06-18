#!/usr/bin/env python3
"""Offline behavior fixtures for the idea-to-ship roadmap exporter."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


GENERATED_START = "<!-- idea-to-ship:roadmap generated:start -->"
GENERATED_END = "<!-- idea-to-ship:roadmap generated:end -->"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def run_export(root: Path, source: Path, output_dir: Path, generated_at: str) -> subprocess.CompletedProcess[str]:
    mapping = source.with_name("mapping.json")
    write_json(
        mapping,
        {
            "provider": "linear",
            "scope_type": "portfolio",
            "scope_id": "portfolio",
            "target": {"team": "roadmap-team"},
        },
    )
    return subprocess.run(
        [
            sys.executable,
            str(root / "idea-to-ship" / "scripts" / "roadmap_export.py"),
            "--source",
            str(source),
            "--provider",
            "linear",
            "--scope",
            "portfolio",
            "--scope-id",
            "portfolio",
            "--output-dir",
            str(output_dir),
            "--mapping-file",
            str(mapping),
            "--generated-at",
            generated_at,
        ],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def valid_roadmap() -> str:
    return f"""---
goal: Ship roadmap export
horizon: 2026-Q3
generated_at: 2026-06-17 00:00
repo_head: abc123
dirty_worktree: no
mode: portfolio
source_scope: local
---

# Roadmap - Ship roadmap export

{GENERATED_START}

## Now

### ITS-ROADMAP-023 - Export roadmap to PM issues
**Status:** Planned
**Work Type:** Feature
**Evidence Class:** Explicit
**Confidence:** High
**Source Anchors:** .idea-to-ship/ITS-ROADMAP-023/requirements.md:1
**Why Now / Why Next / Why Later:** Why Now: users need reviewable import artifacts.
**Owner:** Unassigned
**Decision Owner:** None
**Release Gate:** entry criteria; exit criteria; evidence required; no-go conditions
**Evidence Required:** roadmap export fixture
**Dependencies:** None
**Risk:** medium - parser drift can drop fields

## Candidate Backlog

### ITS-ROADMAP-999 - Unapproved candidate
**Status:** Candidate
**Work Type:** Feature
**Evidence Class:** Explicit
**Confidence:** High
**Source Anchors:** .idea-to-ship/roadmap.md:1
**Why Now / Why Next / Why Later:** Why Later: not approved for external export.
**Owner:** Unassigned
**Decision Owner:** None
**Release Gate:** not ready
**Evidence Required:** approval
**Dependencies:** None
**Risk:** low - should remain blocked

{GENERATED_END}
"""


def missing_required_field_roadmap() -> str:
    return f"""---
goal: Broken roadmap export
mode: portfolio
---

# Roadmap - Broken

{GENERATED_START}

## Now

### ITS-ROADMAP-024 - Missing gate
**Status:** Planned
**Work Type:** Feature
**Evidence Class:** Explicit
**Confidence:** High
**Source Anchors:** .idea-to-ship/ITS-ROADMAP-023/requirements.md:1
**Why Now / Why Next / Why Later:** Why Now: prove hard failure.
**Owner:** Unassigned
**Decision Owner:** None
**Evidence Required:** failure fixture
**Dependencies:** None
**Risk:** medium - invalid exports must halt

{GENERATED_END}
"""


def check_happy_path(root: Path) -> tuple[str, str | None]:
    with TemporaryDirectory(prefix="roadmap-export-happy-") as temp:
        temp_root = Path(temp)
        source = temp_root / "roadmap.md"
        output_dir = temp_root / "exports"
        write_text(source, valid_roadmap())

        first = run_export(root, source, output_dir, "2026-06-17T00:00:00Z")
        if first.returncode != 0:
            return ("roadmap-export-happy-path", first.stdout + first.stderr)

        records = read_jsonl(output_dir / "issues.jsonl")
        if len(records) != 2:
            return ("roadmap-export-happy-path", f"expected 2 JSONL records, got {len(records)}")

        overview, child = records
        if overview.get("role") != "overview" or child.get("role") != "child":
            return ("roadmap-export-happy-path", "overview/child record order is wrong")

        overview_fields = overview.get("overview_fields")
        if not isinstance(overview_fields, dict):
            return ("roadmap-export-happy-path", "missing overview_fields")
        if overview_fields.get("exported_item_count") != 1:
            return ("roadmap-export-happy-path", "overview item count should exclude blocked candidates")
        if overview_fields.get("provider_target") != "linear team roadmap-team":
            return ("roadmap-export-happy-path", "missing provider target summary")

        relation = child.get("relation")
        if not isinstance(relation, dict) or relation.get("overview_id") != overview.get("roadmap_id"):
            return ("roadmap-export-happy-path", "child is not linked to overview")

        roadmap_fields = child.get("roadmap_fields")
        required = {
            "status",
            "work_type",
            "evidence_class",
            "confidence",
            "source_anchors",
            "rationale",
            "release_gate",
            "evidence_required",
            "dependencies",
            "risk",
            "owner",
            "decision_owner",
        }
        if not isinstance(roadmap_fields, dict) or not required.issubset(roadmap_fields):
            return ("roadmap-export-happy-path", "child roadmap_fields do not preserve required evidence")

        manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
        if manifest.get("blocked", {}).get("ITS-ROADMAP-999", {}).get("reason") != "candidate-not-approved":
            return ("roadmap-export-happy-path", "unapproved candidate was not recorded as blocked")

        second_output = temp_root / "exports-second"
        second = run_export(root, source, second_output, "2026-06-18T00:00:00Z")
        if second.returncode != 0:
            return ("roadmap-export-happy-path", second.stdout + second.stderr)
        second_records = read_jsonl(second_output / "issues.jsonl")
        first_hashes = [record.get("content_hash") for record in records]
        second_hashes = [record.get("content_hash") for record in second_records]
        if first_hashes != second_hashes:
            return ("roadmap-export-happy-path", "generated_at-only changes should not alter content hashes")

        for required_file in ("roadmap-export.md", "issues.jsonl", "manifest.json"):
            if not (output_dir / required_file).is_file():
                return ("roadmap-export-happy-path", f"missing {required_file}")

        return ("roadmap-export-happy-path", None)


def check_missing_required_field(root: Path) -> tuple[str, str | None]:
    with TemporaryDirectory(prefix="roadmap-export-invalid-") as temp:
        temp_root = Path(temp)
        source = temp_root / "roadmap.md"
        output_dir = temp_root / "exports"
        write_text(source, missing_required_field_roadmap())

        result = run_export(root, source, output_dir, "2026-06-17T00:00:00Z")
        if result.returncode != 1:
            return ("roadmap-export-missing-required-field", f"expected exit 1, got {result.returncode}")
        combined = result.stdout + result.stderr
        if "Release Gate" not in combined or "Retry:" not in combined:
            return ("roadmap-export-missing-required-field", "missing field and retry guidance not reported")
        if (output_dir / "issues.jsonl").exists() or (output_dir / "roadmap-export.md").exists():
            return ("roadmap-export-missing-required-field", "failed export wrote final artifacts")
        return ("roadmap-export-missing-required-field", None)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: idea-to-ship-roadmap-export-fixtures.py <repo-root>", file=sys.stderr)
        return 2

    root = Path(argv[1]).resolve()
    failures = 0
    print("Idea-to-ship roadmap export fixtures")
    for check in (check_happy_path, check_missing_required_field):
        check_id, failure = check(root)
        if failure:
            failures += 1
            print(f"FAIL {check_id}: {failure}")
        else:
            print(f"PASS {check_id}: roadmap export behavior covered")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
