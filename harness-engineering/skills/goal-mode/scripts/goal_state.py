#!/usr/bin/env python3
"""Small state helper for the goal-mode skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ALLOWED_STATUS = {"running", "blocked", "complete", "failed"}
SLUG_RE = re.compile(r"^[A-Za-z0-9._-]+$")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def require_slug(slug: str) -> str:
    if not SLUG_RE.match(slug):
        raise SystemExit("slug must contain only letters, digits, dot, underscore, or hyphen")
    return slug


def goal_dir(root: Path, slug: str) -> Path:
    return root / ".harness-engineering" / require_slug(slug) / "goal"


def rel_goal_path(slug: str, name: str) -> str:
    return f".harness-engineering/{slug}/goal/{name}"


def state_file(root: Path, slug: str) -> Path:
    return goal_dir(root, slug) / "state.json"


def read_state(root: Path, slug: str) -> dict[str, Any]:
    path = state_file(root, slug)
    if not path.is_file():
        raise SystemExit(f"goal state not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"state root must be an object: {path}")
    return data


def write_state(root: Path, slug: str, state: dict[str, Any]) -> None:
    directory = goal_dir(root, slug)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "state.json"
    tmp = directory / "state.json.tmp"
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def append_log(root: Path, slug: str, heading: str, lines: list[str]) -> None:
    log_path = goal_dir(root, slug) / "iteration-log.md"
    rendered = [f"\n## {utc_now()} - {heading}"]
    rendered.extend(line for line in lines if line)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(rendered).rstrip() + "\n")


def dedupe(items: list[Any]) -> list[Any]:
    seen: set[str] = set()
    output: list[Any] = []
    for item in items:
        marker = json.dumps(item, sort_keys=True) if isinstance(item, (dict, list)) else str(item)
        if marker in seen:
            continue
        seen.add(marker)
        output.append(item)
    return output


def render_objective(state: dict[str, Any]) -> str:
    def bullets(values: list[str], empty: str) -> str:
        if not values:
            return f"- {empty}"
        return "\n".join(f"- {value}" for value in values)

    return "\n".join(
        [
            f"# Goal Objective - {state['slug']}",
            "",
            f"**Status:** {state['status']}",
            f"**Created:** {state['created_at']}",
            f"**Updated:** {state['updated_at']}",
            "",
            "## Objective",
            state["objective"],
            "",
            "## Success Criteria",
            bullets(state.get("success_criteria", []), "TBD"),
            "",
            "## Non-goals",
            bullets(state.get("non_goals", []), "TBD"),
            "",
            "## Constraints",
            bullets(state.get("constraints", []), "TBD"),
            "",
            "## Current Step",
            state.get("current_step", ""),
            "",
            "## Next Action",
            state.get("next_action", ""),
            "",
        ]
    )


def render_handoff(state: dict[str, Any]) -> str:
    recent_steps = state.get("steps", [])[-5:]
    blockers = state.get("blockers", [])
    verification = state.get("verification", [])[-5:]

    def list_or_empty(values: list[Any], formatter) -> list[str]:
        if not values:
            return ["- None"]
        return [formatter(value) for value in values]

    lines = [
        f"# Goal Handoff - {state['slug']}",
        "",
        f"**Updated:** {state['updated_at']}",
        f"**Status:** {state['status']}",
        "",
        "## Objective",
        state["objective"],
        "",
        "## Current Step",
        state.get("current_step", ""),
        "",
        "## Next Action",
        state.get("next_action", "") or "None",
        "",
        "## Recent Steps",
        *list_or_empty(
            recent_steps,
            lambda item: f"- {item.get('timestamp', '')}: {item.get('step', '')} -> {item.get('result', '')}",
        ),
        "",
        "## Recent Verification",
        *list_or_empty(
            verification,
            lambda item: f"- {item.get('timestamp', '')}: {item.get('evidence', '')}",
        ),
        "",
        "## Blockers",
        *list_or_empty(blockers, lambda item: f"- {item}"),
        "",
        "## Resume Instruction",
        f"Use $goal-mode --resume --slug {state['slug']} to continue. Load state.json, objective.md, this handoff, and only the needed tail of iteration-log.md.",
        "",
    ]
    return "\n".join(lines)


def rewrite_markdown(root: Path, slug: str, state: dict[str, Any]) -> None:
    directory = goal_dir(root, slug)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "objective.md").write_text(render_objective(state), encoding="utf-8")
    (directory / "handoff.md").write_text(render_handoff(state), encoding="utf-8")


def validate_state(state: dict[str, Any], root: Path | None = None) -> list[str]:
    errors: list[str] = []
    required = [
        "schema_version",
        "slug",
        "objective",
        "status",
        "created_at",
        "updated_at",
        "current_step",
        "next_action",
        "steps",
        "verification",
        "blockers",
        "artifacts",
    ]
    for key in required:
        if key not in state:
            errors.append(f"missing key: {key}")
    if state.get("status") not in ALLOWED_STATUS:
        errors.append(f"status must be one of: {', '.join(sorted(ALLOWED_STATUS))}")
    if not isinstance(state.get("steps", []), list):
        errors.append("steps must be a list")
    if not isinstance(state.get("verification", []), list):
        errors.append("verification must be a list")
    if not isinstance(state.get("blockers", []), list):
        errors.append("blockers must be a list")
    if not isinstance(state.get("artifacts", {}), dict):
        errors.append("artifacts must be an object")
    if root is not None and isinstance(state.get("artifacts", {}), dict):
        artifacts = state["artifacts"]
        for key in ("objective", "state", "iteration_log", "handoff"):
            value = artifacts.get(key)
            if not value:
                errors.append(f"missing artifact path: {key}")
            elif not (root / value).is_file():
                errors.append(f"artifact file does not exist: {value}")
    return errors


def cmd_init(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    slug = require_slug(args.slug)
    path = state_file(root, slug)
    if path.exists() and not args.force:
        print(f"Goal already exists: {path}")
        return cmd_status(args)

    now = utc_now()
    state: dict[str, Any] = {
        "schema_version": 1,
        "slug": slug,
        "objective": args.objective,
        "status": "running",
        "created_at": now,
        "updated_at": now,
        "active_phase": "define",
        "current_step": "Define objective, success criteria, non-goals, and constraints",
        "next_action": "Refine the goal contract or start the first verifiable work step",
        "success_criteria": args.success_criterion or [],
        "non_goals": args.non_goal or [],
        "constraints": args.constraint or [],
        "blockers": [],
        "artifacts": {
            "objective": rel_goal_path(slug, "objective.md"),
            "state": rel_goal_path(slug, "state.json"),
            "iteration_log": rel_goal_path(slug, "iteration-log.md"),
            "handoff": rel_goal_path(slug, "handoff.md"),
        },
        "steps": [],
        "verification": [],
    }
    write_state(root, slug, state)
    log_path = goal_dir(root, slug) / "iteration-log.md"
    log_path.write_text(f"# Iteration Log - {slug}\n", encoding="utf-8")
    append_log(root, slug, "initialized", [f"- Objective: {args.objective}"])
    rewrite_markdown(root, slug, state)
    print(f"Initialized goal: {path}")
    return 0


def cmd_record(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    slug = require_slug(args.slug)
    state = read_state(root, slug)
    now = utc_now()

    step_text = args.step or state.get("next_action") or "Unspecified step"
    verifications = args.verification or []
    artifacts = args.artifact or []
    blockers = args.blocker or []
    result = args.result or ""

    entry = {
        "timestamp": now,
        "step": step_text,
        "result": result,
        "verification": verifications,
        "artifacts": artifacts,
        "blockers": blockers,
    }
    state.setdefault("steps", []).append(entry)
    state["current_step"] = step_text
    if args.next_action is not None:
        state["next_action"] = args.next_action
    if args.phase is not None:
        state["active_phase"] = args.phase
    if args.status is not None:
        state["status"] = args.status
    elif blockers:
        state["status"] = "blocked"
    elif state.get("status") == "blocked" and not blockers:
        state["status"] = "running"

    existing_blockers = [] if args.clear_blockers else state.get("blockers", [])
    state["blockers"] = dedupe([*existing_blockers, *blockers])
    for evidence in verifications:
        state.setdefault("verification", []).append(
            {"timestamp": now, "step": step_text, "evidence": evidence}
        )
    for artifact in artifacts:
        state.setdefault("artifacts", {})[Path(artifact).name] = artifact
    state["updated_at"] = now

    write_state(root, slug, state)
    append_log(
        root,
        slug,
        "recorded step",
        [
            f"- Step: {step_text}",
            f"- Result: {result}" if result else "",
            *[f"- Verification: {item}" for item in verifications],
            *[f"- Artifact: {item}" for item in artifacts],
            *[f"- Blocker: {item}" for item in blockers],
            f"- Next action: {state.get('next_action', '')}",
        ],
    )
    rewrite_markdown(root, slug, state)
    print(f"Recorded goal step: {state_file(root, slug)}")
    return 0


def cmd_complete(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    slug = require_slug(args.slug)
    state = read_state(root, slug)
    now = utc_now()
    state["status"] = "complete"
    state["current_step"] = "Complete"
    state["next_action"] = ""
    state["blockers"] = []
    state["updated_at"] = now
    for evidence in args.verification or []:
        state.setdefault("verification", []).append(
            {"timestamp": now, "step": "Complete", "evidence": evidence}
        )
    state.setdefault("steps", []).append(
        {
            "timestamp": now,
            "step": "Complete",
            "result": args.summary,
            "verification": args.verification or [],
            "artifacts": [],
            "blockers": [],
        }
    )
    write_state(root, slug, state)
    append_log(
        root,
        slug,
        "completed",
        [
            f"- Summary: {args.summary}",
            *[f"- Verification: {item}" for item in args.verification or []],
        ],
    )
    rewrite_markdown(root, slug, state)
    print(f"Completed goal: {state_file(root, slug)}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    slug = require_slug(args.slug)
    state = read_state(root, slug)
    errors = validate_state(state, root)
    last_verification = state.get("verification", [])[-1:] or []
    blockers = state.get("blockers", [])
    print(f"Goal: {slug}")
    print(f"Status: {state.get('status', '')}")
    print(f"Objective: {state.get('objective', '')}")
    print(f"Current step: {state.get('current_step', '')}")
    print(f"Next action: {state.get('next_action', '') or 'None'}")
    print(f"Blockers: {', '.join(blockers) if blockers else 'None'}")
    if last_verification:
        print(f"Latest verification: {last_verification[0].get('evidence', '')}")
    print(f"Handoff: {rel_goal_path(slug, 'handoff.md')}")
    if errors:
        print("Validation: failed")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Validation: passed")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    slug = require_slug(args.slug)
    state = read_state(root, slug)
    errors = validate_state(state, root)
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Goal state validates")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repository root; default: current directory")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="create a new goal state")
    init.add_argument("--slug", default="current")
    init.add_argument("--objective", required=True)
    init.add_argument("--success-criterion", action="append")
    init.add_argument("--non-goal", action="append")
    init.add_argument("--constraint", action="append")
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=cmd_init)

    record = subparsers.add_parser("record", help="append a goal step and update state")
    record.add_argument("--slug", default="current")
    record.add_argument("--step")
    record.add_argument("--result")
    record.add_argument("--verification", action="append")
    record.add_argument("--artifact", action="append")
    record.add_argument("--blocker", action="append")
    record.add_argument("--clear-blockers", action="store_true")
    record.add_argument("--next-action")
    record.add_argument("--phase")
    record.add_argument("--status", choices=sorted(ALLOWED_STATUS))
    record.set_defaults(func=cmd_record)

    complete = subparsers.add_parser("complete", help="mark a goal complete")
    complete.add_argument("--slug", default="current")
    complete.add_argument("--summary", required=True)
    complete.add_argument("--verification", action="append")
    complete.set_defaults(func=cmd_complete)

    status = subparsers.add_parser("status", help="print a compact state summary")
    status.add_argument("--slug", default="current")
    status.set_defaults(func=cmd_status)

    validate = subparsers.add_parser("validate", help="validate state shape")
    validate.add_argument("--slug", default="current")
    validate.set_defaults(func=cmd_validate)

    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
