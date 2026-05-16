#!/usr/bin/env python3
"""Deterministic fixtures for scripts/skill-hygiene-check.py."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

SINGLE_SKILL_FIXTURE_RELATED_NOTE = "No other local related skills in this fixture repo."


@dataclass(frozen=True)
class CheckerResult:
    code: int
    stdout: str
    stderr: str


def usage() -> None:
    print("Usage: skill-hygiene-check-fixtures.py <repo-root>", file=sys.stderr)


def run_command(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, check=False, capture_output=True, text=True)


def require_ok(args: list[str], cwd: Path) -> None:
    result = run_command(args, cwd)
    if result.returncode != 0:
        raise AssertionError(
            f"command failed: {' '.join(args)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


def init_repo(root: Path) -> None:
    require_ok(["git", "init", "-q"], root)
    require_ok(["git", "config", "user.email", "fixtures@example.com"], root)
    require_ok(["git", "config", "user.name", "Skill Hygiene Fixtures"], root)


def commit_all(root: Path, message: str = "fixture baseline") -> None:
    write_authoring_baseline(root)
    require_ok(["git", "add", "."], root)
    require_ok(["git", "commit", "-q", "-m", message], root)


def write_authoring_baseline(root: Path) -> None:
    baseline_path = root / "scripts" / "skill-authoring-baseline.txt"
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for skill_path in sorted(root.glob("*/skills/*/SKILL.md")):
        relative = skill_path.relative_to(root).as_posix()
        digest = hashlib.sha256(skill_path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
        rows.append(f"{relative}\t{digest}")
    baseline_path.write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")


def skill_text(description: str = "Short routing description.", body: str = "") -> str:
    return (
        "---\n"
        "name: demo\n"
        f"description: {description}\n"
        "---\n"
        "\n"
        "# Demo Skill\n"
        "\n"
        f"{body}"
    )


def weak_skill_text(description: str = "Short routing description.", body: str = "") -> str:
    return skill_text(description, body)


def authoring_compliant_body(related: str = "$plugin:demo") -> str:
    return (
        "## Usage\n"
        "Use this skill when a fixture needs an authoring-compliant example.\n\n"
        "## Workflow\n"
        "Track progress with a checklist and update status after each step.\n\n"
        "```mermaid\n"
        "flowchart TD\n"
        "    Start --> Check\n"
        "    Check --> Done\n"
        "```\n\n"
        "## Related Skills\n"
        f"- {related}\n"
        "- No other local related skills in this fixture repo.\n\n"
        "## Examples\n"
        "Set the PATH_VALUE placeholder before running the command.\n\n"
        "```bash\n"
        "python3 scripts/example.py PATH_VALUE\n"
        "```\n"
    )


def authoring_compliant_skill_text(
    description: str = "Short routing description.",
    related: str = "$plugin:demo",
    body_suffix: str = "",
) -> str:
    return skill_text(description, authoring_compliant_body(related) + body_suffix)


def weak_authoring_body() -> str:
    return (
        "## Notes\n"
        "This stage routes to another process but gives no task tracking.\n\n"
        "```bash\n"
        "python3 scripts/run.py <TARGET> && rm -rf build\n"
        "cat <<'PY' > /tmp/generated.py\n"
        "print('unsafe heredoc')\n"
        "PY\n"
        "```\n"
        "\n"
        "## Related Skills\n"
        "- $plugin:missing\n"
    )


def usage_only_skill_text(related_lines: str) -> str:
    return skill_text(
        body=(
            "## Usage\n"
            "Use this fixture skill when testing related-skill validation.\n\n"
            "## Related Skills\n"
            f"{related_lines.rstrip()}\n"
        )
    )


AUTHORING_FINDING_IDS = {
    "broken-related-skill",
    "missing-actionable-usage",
    "missing-related-skills",
    "missing-task-tracking",
    "missing-workflow-diagram",
    "unexplained-command-placeholder",
    "unsafe-command-example",
}


def skill_text_with_total_lines(total_lines: int, body_prefix: str = "") -> str:
    text = skill_text(body=body_prefix)
    current_lines = len(text.splitlines())
    if current_lines > total_lines:
        raise AssertionError(f"base skill text already has {current_lines} lines, above requested {total_lines}")
    filler = "\n".join(f"Filler line {index}" for index in range(total_lines - current_lines))
    body = body_prefix
    if body and filler:
        body = f"{body.rstrip()}\n{filler}"
    elif filler:
        body = filler
    return skill_text(body=body)


def write_skill(root: Path, relative_path: str, text: str) -> Path:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def write_metadata(root: Path, skill_relative_path: str) -> None:
    skill_path = root / skill_relative_path
    metadata_path = skill_path.parent / "agents" / "openai.yaml"
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(
        'interface:\n'
        '  display_name: "Demo"\n'
        '  short_description: "Fixture metadata for demo skill"\n'
        '  default_prompt: "$demo"\n',
        encoding="utf-8",
    )


def run_checker(repo_root: Path, checker: Path, mode: str) -> CheckerResult:
    result = run_command(["python3", str(checker), "--mode", mode, str(repo_root)], repo_root)
    return CheckerResult(result.returncode, result.stdout, result.stderr)


def run_candidate_inventory(repo_root: Path, checker: Path, mode: str) -> CheckerResult:
    result = run_command(
        ["python3", str(checker), "--mode", mode, "--dump-repetition-candidates", str(repo_root)],
        repo_root,
    )
    return CheckerResult(result.returncode, result.stdout, result.stderr)


def run_repetition_baseline(repo_root: Path, checker: Path, mode: str) -> CheckerResult:
    result = run_command(
        ["python3", str(checker), "--mode", mode, "--dry-run-repetition-baseline", str(repo_root)],
        repo_root,
    )
    return CheckerResult(result.returncode, result.stdout, result.stderr)


def finding_ids(output: str) -> set[str]:
    ids: set[str] = set()
    for line in output.splitlines():
        if ": " not in line:
            continue
        ids.add(line.split(":", 1)[0])
    return ids


def assert_findings(result: CheckerResult, expected_ids: set[str], scenario: str) -> None:
    actual_ids = finding_ids(result.stdout)
    if result.code != 1 or actual_ids != expected_ids:
        raise AssertionError(
            f"{scenario}: expected exit 1 with IDs {sorted(expected_ids)}, "
            f"got exit {result.code} with IDs {sorted(actual_ids)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


def assert_pass(result: CheckerResult, scenario: str) -> None:
    if result.code != 0:
        raise AssertionError(
            f"{scenario}: expected exit 0, got {result.code}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


def parse_candidate_inventory(result: CheckerResult, scenario: str) -> list[dict[str, str]]:
    if result.code != 0:
        raise AssertionError(
            f"{scenario}: expected candidate inventory exit 0, got {result.code}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )

    records: list[dict[str, str]] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if not parts or parts[0] != "candidate":
            raise AssertionError(f"{scenario}: unexpected inventory line: {line}")
        record: dict[str, str] = {}
        for part in parts[1:]:
            key, separator, value = part.partition("=")
            if not separator:
                raise AssertionError(f"{scenario}: malformed inventory field: {part}")
            record[key] = value
        records.append(record)
    return records


def parse_baseline_records(result: CheckerResult, scenario: str) -> list[dict[str, str]]:
    if result.code != 0:
        raise AssertionError(
            f"{scenario}: expected repetition baseline exit 0, got {result.code}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )

    records: list[dict[str, str]] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if parts[0] not in {"match", "summary"}:
            raise AssertionError(f"{scenario}: unexpected baseline line: {line}")
        record = {"record_type": parts[0]}
        for part in parts[1:]:
            key, separator, value = part.partition("=")
            if not separator:
                raise AssertionError(f"{scenario}: malformed baseline field: {part}")
            record[key] = value
        records.append(record)
    return records


def candidate_by_path(records: list[dict[str, str]], path: str, scenario: str) -> dict[str, str]:
    matches = [record for record in records if record.get("path") == path]
    if len(matches) != 1:
        raise AssertionError(
            f"{scenario}: expected one candidate for {path}, got {len(matches)}: {records}"
        )
    return matches[0]


def reject_candidate_path(records: list[dict[str, str]], path: str, scenario: str) -> None:
    matches = [record for record in records if record.get("path") == path]
    if matches:
        raise AssertionError(f"{scenario}: expected no candidate for {path}, got {matches}")


def line_number(text: str, needle: str) -> int:
    for index, line in enumerate(text.splitlines(), start=1):
        if needle in line:
            return index
    raise AssertionError(f"missing line containing: {needle}")


def scenario_existing_checks_all(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-all-") as tmp:
        root = Path(tmp)
        init_repo(root)
        long_description = "x" * 321
        write_skill(root, "plugin/skills/long/SKILL.md", skill_text(long_description))
        write_metadata(root, "plugin/skills/long/SKILL.md")
        write_skill(
            root,
            "plugin/skills/contract/SKILL.md",
            skill_text(
                body=(
                    "## Output, Token, And Error Contract\n"
                    "status: success | needs_user | terminal | degraded\n"
                    "truncated: true | false\n"
                )
            ),
        )
        write_metadata(root, "plugin/skills/contract/SKILL.md")
        write_skill(
            root,
            "plugin/skills/oversized/SKILL.md",
            skill_text(body="\n".join(f"line {index}" for index in range(760))),
        )
        write_metadata(root, "plugin/skills/oversized/SKILL.md")
        commit_all(root)

        result = run_checker(root, checker, "all")
        assert_findings(
            result,
            {"long-description", "inline-output-contract", "oversized-skill"},
            "existing checks in all mode",
        )


def scenario_all_mode_ignores_committed_legacy_metadata(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-all-legacy-") as tmp:
        root = Path(tmp)
        init_repo(root)
        write_skill(root, "plugin/skills/legacy/SKILL.md", skill_text())
        commit_all(root)

        result = run_checker(root, checker, "all")
        assert_pass(result, "all mode ignores committed legacy metadata")


def scenario_added_skill_metadata_working(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-working-added-") as tmp:
        root = Path(tmp)
        init_repo(root)
        write_skill(root, "plugin/skills/base/SKILL.md", skill_text())
        write_metadata(root, "plugin/skills/base/SKILL.md")
        commit_all(root)
        write_skill(root, "plugin/skills/new/SKILL.md", authoring_compliant_skill_text(related="$plugin:base"))

        result = run_checker(root, checker, "working")
        assert_findings(result, {"missing-openai-metadata"}, "working added skill metadata")


def scenario_staged_deleted_modified_skill(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-staged-deleted-") as tmp:
        root = Path(tmp)
        init_repo(root)
        skill_path = "plugin/skills/demo/SKILL.md"
        write_skill(root, skill_path, skill_text())
        write_metadata(root, skill_path)
        commit_all(root)

        write_skill(root, skill_path, authoring_compliant_skill_text("x" * 321))
        require_ok(["git", "add", skill_path], root)
        (root / skill_path).unlink()

        result = run_checker(root, checker, "staged")
        assert_findings(result, {"long-description"}, "staged deleted modified skill")


def scenario_staged_deleted_added_skill_metadata(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-staged-added-deleted-") as tmp:
        root = Path(tmp)
        init_repo(root)
        write_skill(root, "plugin/skills/base/SKILL.md", skill_text())
        write_metadata(root, "plugin/skills/base/SKILL.md")
        commit_all(root)

        skill_path = "plugin/skills/new/SKILL.md"
        write_skill(root, skill_path, authoring_compliant_skill_text(related="$plugin:base"))
        require_ok(["git", "add", skill_path], root)
        (root / skill_path).unlink()

        result = run_checker(root, checker, "staged")
        assert_findings(
            result,
            {"missing-openai-metadata"},
            "staged deleted added skill metadata",
        )


def scenario_staged_reads_index_not_worktree(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-staged-index-") as tmp:
        root = Path(tmp)
        init_repo(root)
        skill_path = "plugin/skills/demo/SKILL.md"
        write_skill(root, skill_path, skill_text())
        write_metadata(root, skill_path)
        commit_all(root)

        write_skill(root, skill_path, authoring_compliant_skill_text("Safe staged description."))
        require_ok(["git", "add", skill_path], root)
        write_skill(root, skill_path, skill_text("x" * 321))

        result = run_checker(root, checker, "staged")
        assert_pass(result, "staged reads index not dirty worktree")


def scenario_candidate_inventory_classifies_prompt_and_template(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-candidates-") as tmp:
        root = Path(tmp)
        init_repo(root)
        prompt_body = (
            "Use this prompt when assigning an adversarial reviewer.\n"
            "You are an independent reviewer. Your job is to inspect the changed skill file, "
            "name every concrete bug, and avoid style-only feedback.\n"
            "Assigned angle: correctness and security.\n"
            "READ-ONLY: Do not edit files, do not modify git state, and do not infer missing facts.\n"
            "For each issue, report severity, path, line, concrete problem, and concrete fix.\n"
            "If you find no material issue, respond with exactly LGTM.\n"
            "Review the requirements, architecture, test plan, and implementation log before deciding.\n"
            "Return only evidence-backed findings and keep speculative concerns out of the report.\n"
        )
        template_body = (
            "## Final Report\n"
            "| Severity | File | Issue | Resolution |\n"
            "|---|---|---|---|\n"
            "| <severity> | <file> | <issue> | <resolution> |\n"
            "\n"
            "status: <success-or-failure>\n"
            "outputs_written: <artifact paths>\n"
            "next_action: <command>\n"
            "truncated: <true-or-false>\n"
            "reviewed_with: <command evidence>\n"
            "evidence_summary: record the command or artifact that proves each reported outcome and the exact reviewer-visible status used for handoff.\n"
        )
        write_skill(root, "plugin/skills/prompt/SKILL.md", skill_text(body=prompt_body))
        write_metadata(root, "plugin/skills/prompt/SKILL.md")
        write_skill(root, "plugin/skills/template/SKILL.md", skill_text(body=template_body))
        write_metadata(root, "plugin/skills/template/SKILL.md")
        commit_all(root)

        normal_result = run_checker(root, checker, "all")
        assert_pass(normal_result, "candidate inventory normal mode stays clean")

        records = parse_candidate_inventory(
            run_candidate_inventory(root, checker, "all"),
            "candidate inventory classifies prompt and template",
        )
        prompt = candidate_by_path(
            records,
            "plugin/skills/prompt/SKILL.md",
            "candidate inventory prompt record",
        )
        template = candidate_by_path(
            records,
            "plugin/skills/template/SKILL.md",
            "candidate inventory template record",
        )

        if prompt.get("family") != "prompt":
            raise AssertionError(f"expected prompt family, got {prompt}")
        if int(prompt.get("normalized_chars", "0")) < 600:
            raise AssertionError(f"expected prompt normalized length evidence, got {prompt}")
        if int(prompt.get("literal_chars", "0")) < 300:
            raise AssertionError(f"expected prompt literal length evidence, got {prompt}")
        if float(prompt.get("placeholder_ratio", "1")) >= 0.35:
            raise AssertionError(f"expected prompt placeholder ratio below cap, got {prompt}")
        if len(prompt.get("fingerprint", "")) < 12:
            raise AssertionError(f"expected prompt fingerprint evidence, got {prompt}")

        if template.get("family") != "template":
            raise AssertionError(f"expected template family, got {template}")
        anchors = template.get("stable_anchors", "")
        for expected_anchor in ("final report", "severity", "status", "outputs_written"):
            if expected_anchor not in anchors:
                raise AssertionError(f"missing template anchor {expected_anchor}: {template}")
        if template.get("output_contract_masked") != "false":
            raise AssertionError(f"expected no output-contract mask in stage 3, got {template}")


def scenario_candidate_inventory_ignores_ordinary_sections(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-candidate-negative-") as tmp:
        root = Path(tmp)
        init_repo(root)
        ordinary_body = (
            "## Requirements\n"
            "This section describes ordinary usage constraints for maintainers.\n"
            "\n"
            "## Architecture\n"
            "This section names local files and explains why the skill stays small.\n"
            "\n"
            "## Final Report\n"
            "This section references an external template without embedding one.\n"
        )
        write_skill(root, "plugin/skills/ordinary/SKILL.md", skill_text(body=ordinary_body))
        write_metadata(root, "plugin/skills/ordinary/SKILL.md")
        commit_all(root)

        normal_result = run_checker(root, checker, "all")
        assert_pass(normal_result, "ordinary section normal mode stays clean")

        records = parse_candidate_inventory(
            run_candidate_inventory(root, checker, "all"),
            "candidate inventory ordinary section negative",
        )
        if records:
            raise AssertionError(f"ordinary sections should not create candidates: {records}")


def scenario_candidate_inventory_spans_internal_headings(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-candidate-span-") as tmp:
        root = Path(tmp)
        init_repo(root)
        body = (
            "Use this prompt for an adversarial implementation reviewer.\n"
            "You are a skeptical reviewer. Your job is to verify code against the stage contract.\n"
            "Assigned angle: traceability and failure modes.\n"
            "READ-ONLY: Do not edit files or change git state.\n"
            "Return only evidence-backed findings and keep speculative concerns out of the report.\n"
            "\n"
            "## Requirements\n"
            "<full requirements content goes here>\n"
            "\n"
            "## Architecture\n"
            "<full architecture content goes here>\n"
            "\n"
            "## Final Report\n"
            "For each issue, report severity, path, line, problem, and fix.\n"
            "If you find no material issue, respond with exactly LGTM.\n"
            "Use the implementation log and test plan as evidence before returning.\n"
        )
        write_skill(root, "plugin/skills/span/SKILL.md", skill_text(body=body))
        write_metadata(root, "plugin/skills/span/SKILL.md")
        commit_all(root)

        records = parse_candidate_inventory(
            run_candidate_inventory(root, checker, "all"),
            "candidate inventory internal heading span",
        )
        record = candidate_by_path(
            records,
            "plugin/skills/span/SKILL.md",
            "candidate inventory internal heading span record",
        )
        start_line = int(record.get("start_line", "0"))
        end_line = int(record.get("end_line", "0"))
        expected_start = line_number(skill_text(body=body), "Use this prompt")
        expected_end_floor = line_number(skill_text(body=body), "respond with exactly LGTM")

        if record.get("family") != "prompt":
            raise AssertionError(f"expected internal-heading sample to classify as prompt: {record}")
        if start_line != expected_start:
            raise AssertionError(f"expected candidate to start at trigger line {expected_start}: {record}")
        if end_line < expected_end_floor:
            raise AssertionError(f"expected candidate to include internal final report section: {record}")


def scenario_candidate_inventory_respects_fence_marker_type(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-candidate-fence-marker-") as tmp:
        root = Path(tmp)
        init_repo(root)
        body = (
            "~~~text\n"
            f"{duplicate_prompt_text()}\n"
            "```example fence marker inside a tilde block\n"
            "This line must stay inside the tilde fenced candidate.\n"
            "~~~\n"
        )
        text = skill_text(body=body)
        path = "plugin/skills/mixed-fence/SKILL.md"
        write_skill(root, path, text)
        write_metadata(root, path)
        commit_all(root)

        records = parse_candidate_inventory(
            run_candidate_inventory(root, checker, "all"),
            "candidate inventory respects fence marker type",
        )
        record = candidate_by_path(records, path, "mixed fence marker candidate")
        if int(record["end_line"]) != len(text.splitlines()):
            raise AssertionError(f"tilde fence candidate ended before closing tilde fence: {record}")


def scenario_candidate_inventory_classifier_boundaries(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-candidate-boundary-") as tmp:
        root = Path(tmp)
        init_repo(root)
        structured_prompt_body = (
            "Use this prompt when assigning an adversarial reviewer.\n"
            "You are an independent reviewer. Your job is to inspect the changed skill file, "
            "name every concrete bug, and avoid style-only feedback.\n"
            "Assigned angle: correctness and security.\n"
            "READ-ONLY: Do not edit files, do not modify git state, and do not infer missing facts.\n"
            "For each issue, report severity, path, line, concrete problem, and concrete fix.\n"
            "If you find no material issue, respond with exactly LGTM.\n"
            "Review the requirements, architecture, test plan, and implementation log before deciding.\n"
            "Return only evidence-backed findings and keep speculative concerns out of the report.\n"
            "\n"
            "## Final Report\n"
            "| Severity | File | Issue | Resolution |\n"
            "|---|---|---|---|\n"
            "| <severity> | <file> | <issue> | <resolution> |\n"
        )
        template_body = (
            "## Final Report\n"
            "| Severity | File | Issue | Resolution |\n"
            "|---|---|---|---|\n"
            "| <severity> | <file> | <issue> | <resolution> |\n"
            "\n"
            "status: <success-or-failure>\n"
            "outputs_written: <artifact paths>\n"
            "next_action: <command>\n"
            "truncated: <true-or-false>\n"
            "reviewed_with: <command evidence>\n"
            "evidence_summary: record the command or artifact that proves each reported outcome.\n"
        )
        template_with_input_sections_body = (
            "## Final Report\n"
            "## Requirements\n"
            "<requirements summary goes here>\n"
            "## Architecture\n"
            "<architecture summary goes here>\n"
            "status: <success-or-failure>\n"
            "outputs_written: <artifact paths>\n"
            "next_action: <command>\n"
            "truncated: <true-or-false>\n"
            "reviewed_with: <command evidence>\n"
            "evidence_summary: record the command or artifact that proves each reported outcome.\n"
        )
        placeholder_label_template_body = (
            "## Final Report\n"
            "<severity>: record whether the issue is critical, warning, or nit.\n"
            "<file>: record the changed file path.\n"
            "<issue>: record the concrete issue.\n"
            "<resolution>: record the concrete resolution.\n"
            "<evidence>: record the command or artifact that proves the outcome.\n"
        )
        output_wrapper_body = (
            "## Output\n"
            "status: <success-or-failure>\n"
            "outputs_written: <artifact paths>\n"
            "next_action: <command>\n"
            "truncated: <true-or-false>\n"
            "reviewed_with: <command evidence>\n"
            "evidence_summary: record the command or artifact that proves each reported outcome and the exact reviewer-visible status used for handoff.\n"
        )
        ordinary_labeled_report_body = (
            "## Final Report\n"
            "Scope: ordinary maintainer prose, not a reusable output wrapper.\n"
            "Owner: skill maintainers.\n"
            "Risk: low because this section only documents a local decision.\n"
            "Decision: keep the external template reference.\n"
            "Evidence: maintainer notes in the surrounding prose.\n"
        )
        below_threshold_body = (
            "Use this prompt.\n"
            "You are a reviewer.\n"
            "If you find no issue, respond with exactly LGTM.\n"
        )
        placeholder_heavy_body = (
            "Use this prompt when assigning an adversarial reviewer.\n"
            "You are <ROLE_NAME_WITH_LONG_PLACEHOLDER_TEXT> and your job is <JOB_DETAILS_WITH_LONG_PLACEHOLDER_TEXT>.\n"
            "Assigned angle: <ANGLE_WITH_LONG_PLACEHOLDER_TEXT>.\n"
            "READ-ONLY: Do not edit <PATH_WITH_LONG_PLACEHOLDER_TEXT> or modify <STATE_WITH_LONG_PLACEHOLDER_TEXT>.\n"
            "For each issue, report <SEVERITY_PLACEHOLDER>, <FILE_PLACEHOLDER>, <LINE_PLACEHOLDER>, "
            "and <CONCRETE_FIX_PLACEHOLDER>.\n"
            "If you find no material issue, respond with exactly <LGTM_PLACEHOLDER>.\n"
            "Review <REQUIREMENTS_PLACEHOLDER>, <ARCHITECTURE_PLACEHOLDER>, and <TEST_PLAN_PLACEHOLDER>.\n"
            "Return only <EVIDENCE_BACKED_FINDINGS_PLACEHOLDER> and omit <SPECULATION_PLACEHOLDER>.\n"
        )
        single_signal_body = (
            "For each issue, compare the supplied material with the expected result.\n"
            "Neutral context line one provides enough text to exceed the length threshold without adding prompt signals.\n"
            "Neutral context line two provides enough text to exceed the length threshold without adding prompt signals.\n"
            "Neutral context line three provides enough text to exceed the length threshold without adding prompt signals.\n"
            "Neutral context line four provides enough text to exceed the length threshold without adding prompt signals.\n"
            "Neutral context line five provides enough text to exceed the length threshold without adding prompt signals.\n"
            "Neutral context line six provides enough text to exceed the length threshold without adding prompt signals.\n"
            "Neutral context line seven provides enough text to exceed the length threshold without adding prompt signals.\n"
        )

        write_skill(root, "plugin/skills/prompt-output/SKILL.md", skill_text(body=structured_prompt_body))
        write_metadata(root, "plugin/skills/prompt-output/SKILL.md")
        write_skill(root, "plugin/skills/template-only/SKILL.md", skill_text(body=template_body))
        write_metadata(root, "plugin/skills/template-only/SKILL.md")
        write_skill(
            root,
            "plugin/skills/template-input-sections/SKILL.md",
            skill_text(body=template_with_input_sections_body),
        )
        write_metadata(root, "plugin/skills/template-input-sections/SKILL.md")
        write_skill(
            root,
            "plugin/skills/placeholder-label-template/SKILL.md",
            skill_text(body=placeholder_label_template_body),
        )
        write_metadata(root, "plugin/skills/placeholder-label-template/SKILL.md")
        write_skill(root, "plugin/skills/output-wrapper/SKILL.md", skill_text(body=output_wrapper_body))
        write_metadata(root, "plugin/skills/output-wrapper/SKILL.md")
        write_skill(
            root,
            "plugin/skills/ordinary-labeled-report/SKILL.md",
            skill_text(body=ordinary_labeled_report_body),
        )
        write_metadata(root, "plugin/skills/ordinary-labeled-report/SKILL.md")
        write_skill(root, "plugin/skills/below-threshold/SKILL.md", skill_text(body=below_threshold_body))
        write_metadata(root, "plugin/skills/below-threshold/SKILL.md")
        write_skill(root, "plugin/skills/placeholder-heavy/SKILL.md", skill_text(body=placeholder_heavy_body))
        write_metadata(root, "plugin/skills/placeholder-heavy/SKILL.md")
        write_skill(root, "plugin/skills/single-signal/SKILL.md", skill_text(body=single_signal_body))
        write_metadata(root, "plugin/skills/single-signal/SKILL.md")
        commit_all(root)

        records = parse_candidate_inventory(
            run_candidate_inventory(root, checker, "all"),
            "candidate inventory classifier boundaries",
        )
        prompt_output = candidate_by_path(
            records,
            "plugin/skills/prompt-output/SKILL.md",
            "prompt with structured output stays prompt",
        )
        template_only = candidate_by_path(
            records,
            "plugin/skills/template-only/SKILL.md",
            "template-dominant output stays template",
        )
        template_input_sections = candidate_by_path(
            records,
            "plugin/skills/template-input-sections/SKILL.md",
            "output-only template with input sections stays template",
        )
        placeholder_label_template = candidate_by_path(
            records,
            "plugin/skills/placeholder-label-template/SKILL.md",
            "placeholder-label template stays template",
        )
        output_wrapper = candidate_by_path(
            records,
            "plugin/skills/output-wrapper/SKILL.md",
            "output wrapper heading starts template candidate",
        )

        if prompt_output.get("family") != "prompt":
            raise AssertionError(f"prompt with structured output should stay prompt: {prompt_output}")
        if template_only.get("family") != "template":
            raise AssertionError(f"template-dominant output should stay template: {template_only}")
        if template_input_sections.get("family") != "template":
            raise AssertionError(f"output-only template with input sections should stay template: {template_input_sections}")
        if placeholder_label_template.get("family") != "template":
            raise AssertionError(f"placeholder-label template should stay template: {placeholder_label_template}")
        if "severity" not in placeholder_label_template.get("stable_anchors", ""):
            raise AssertionError(f"placeholder labels should become stable anchors: {placeholder_label_template}")
        if output_wrapper.get("family") != "template":
            raise AssertionError(f"output wrapper heading should start a template candidate: {output_wrapper}")
        reject_candidate_path(
            records,
            "plugin/skills/below-threshold/SKILL.md",
            "below-threshold prompt should not become a candidate",
        )
        reject_candidate_path(
            records,
            "plugin/skills/placeholder-heavy/SKILL.md",
            "placeholder-heavy prompt should not become a candidate",
        )
        reject_candidate_path(
            records,
            "plugin/skills/single-signal/SKILL.md",
            "single prompt signal should not reach classifier threshold",
        )
        reject_candidate_path(
            records,
            "plugin/skills/ordinary-labeled-report/SKILL.md",
            "ordinary labeled final report prose should not become a template",
        )


def scenario_candidate_inventory_stops_before_plain_internal_heading(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-candidate-plain-heading-") as tmp:
        root = Path(tmp)
        init_repo(root)
        body = (
            "Use this prompt when assigning an adversarial reviewer.\n"
            "You are an independent reviewer. Your job is to inspect the changed skill file, "
            "name every concrete bug, and avoid style-only feedback.\n"
            "Assigned angle: correctness and security.\n"
            "READ-ONLY: Do not edit files, do not modify git state, and do not infer missing facts.\n"
            "For each issue, report severity, path, line, concrete problem, and concrete fix.\n"
            "If you find no material issue, respond with exactly LGTM.\n"
            "Review the requirements, architecture, test plan, and implementation log before deciding.\n"
            "Return only evidence-backed findings and keep speculative concerns out of the report.\n"
            "\n"
            "## Requirements\n"
            "Scope: ordinary maintainer prose with a label that should not be treated as YAML skeleton.\n"
            "This ordinary prose explains project constraints and should not be absorbed into the prompt candidate.\n"
            "It has no placeholders, tables, YAML skeleton, or model-output instructions.\n"
        )
        write_skill(root, "plugin/skills/plain-heading/SKILL.md", skill_text(body=body))
        write_metadata(root, "plugin/skills/plain-heading/SKILL.md")
        commit_all(root)

        records = parse_candidate_inventory(
            run_candidate_inventory(root, checker, "all"),
            "candidate inventory plain internal heading boundary",
        )
        record = candidate_by_path(
            records,
            "plugin/skills/plain-heading/SKILL.md",
            "candidate inventory plain internal heading boundary record",
        )
        requirements_line = line_number(skill_text(body=body), "## Requirements")
        end_line = int(record.get("end_line", "0"))

        if end_line >= requirements_line:
            raise AssertionError(f"ordinary internal heading should not be absorbed: {record}")


def scenario_candidate_inventory_strips_line_numbers_for_fingerprints(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-candidate-line-numbers-") as tmp:
        root = Path(tmp)
        init_repo(root)
        plain_body = (
            "Use this prompt when assigning an adversarial reviewer.\n"
            "You are an independent reviewer. Your job is to inspect the changed skill file, "
            "name every concrete bug, and avoid style-only feedback.\n"
            "Assigned angle: correctness and security.\n"
            "READ-ONLY: Do not edit files, do not modify git state, and do not infer missing facts.\n"
            "For each issue, report severity, path, line, concrete problem, and concrete fix.\n"
            "If you find no material issue, respond with exactly LGTM.\n"
            "Review the requirements, architecture, test plan, and implementation log before deciding.\n"
            "Return only evidence-backed findings and keep speculative concerns out of the report.\n"
        )
        numbered_body = "\n".join(
            f"{100 + index}: {line}"
            for index, line in enumerate(plain_body.splitlines(), start=1)
        )
        write_skill(root, "plugin/skills/plain/SKILL.md", skill_text(body=plain_body))
        write_metadata(root, "plugin/skills/plain/SKILL.md")
        write_skill(root, "plugin/skills/numbered/SKILL.md", skill_text(body=numbered_body))
        write_metadata(root, "plugin/skills/numbered/SKILL.md")
        commit_all(root)

        records = parse_candidate_inventory(
            run_candidate_inventory(root, checker, "all"),
            "candidate inventory strips line numbers for fingerprints",
        )
        plain = candidate_by_path(records, "plugin/skills/plain/SKILL.md", "plain fingerprint record")
        numbered = candidate_by_path(records, "plugin/skills/numbered/SKILL.md", "numbered fingerprint record")

        if plain.get("fingerprint") != numbered.get("fingerprint"):
            raise AssertionError(f"line-numbered and plain candidates should fingerprint equally: {records}")


def scenario_candidate_inventory_normalizes_uppercase_placeholders(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-candidate-uppercase-placeholders-") as tmp:
        root = Path(tmp)
        init_repo(root)
        source_body = (
            "Use this prompt when assigning an adversarial reviewer.\n"
            "You are an independent reviewer. Your job is to inspect SOURCE_PATH, "
            "name every concrete bug, and avoid style-only feedback.\n"
            "Assigned angle: correctness and security.\n"
            "READ-ONLY: Do not edit files, do not modify git state, and do not infer missing facts.\n"
            "For each issue, report severity, path, line, concrete problem, and concrete fix.\n"
            "If you find no material issue, respond with exactly LGTM.\n"
            "Review the requirements, architecture, test plan, and implementation log before deciding.\n"
            "Return only evidence-backed findings and keep speculative concerns out of the report.\n"
        )
        target_body = source_body.replace("SOURCE_PATH", "TARGET_PATH")
        write_skill(root, "plugin/skills/source-placeholder/SKILL.md", skill_text(body=source_body))
        write_metadata(root, "plugin/skills/source-placeholder/SKILL.md")
        write_skill(root, "plugin/skills/target-placeholder/SKILL.md", skill_text(body=target_body))
        write_metadata(root, "plugin/skills/target-placeholder/SKILL.md")
        commit_all(root)

        records = parse_candidate_inventory(
            run_candidate_inventory(root, checker, "all"),
            "candidate inventory normalizes uppercase placeholders",
        )
        source = candidate_by_path(
            records,
            "plugin/skills/source-placeholder/SKILL.md",
            "source uppercase placeholder record",
        )
        target = candidate_by_path(
            records,
            "plugin/skills/target-placeholder/SKILL.md",
            "target uppercase placeholder record",
        )

        if source.get("fingerprint") != target.get("fingerprint"):
            raise AssertionError(f"uppercase placeholder names should fingerprint equally: {records}")


def duplicate_prompt_text() -> str:
    return (
        "Use this prompt when assigning an adversarial reviewer.\n"
        "You are an independent reviewer. Your job is to inspect the changed skill file, "
        "name every concrete bug, and avoid style-only feedback.\n"
        "Assigned angle: correctness and security.\n"
        "READ-ONLY: Do not edit files, do not modify git state, and do not infer missing facts.\n"
        "For each issue, report severity, path, line, concrete problem, and concrete fix.\n"
        "If you find no material issue, respond with exactly LGTM.\n"
        "Review the requirements, architecture, test plan, and implementation log before deciding.\n"
        "Return only evidence-backed findings and keep speculative concerns out of the report.\n"
    )


def duplicate_template_text() -> str:
    return (
        "## Final Report\n"
        "| Severity | File | Issue | Resolution |\n"
        "|---|---|---|---|\n"
        "| <severity> | <file> | <issue> | <resolution> |\n"
        "\n"
        "status: <success-or-failure>\n"
        "outputs_written: <artifact paths>\n"
        "next_action: <command>\n"
        "truncated: <true-or-false>\n"
        "reviewed_with: <command evidence>\n"
        "evidence_summary: record the command or artifact that proves each reported outcome and the exact reviewer-visible status used for handoff.\n"
    )


def placeholder_heavy_template_text() -> str:
    return (
        "## Final Report\n"
        "| Severity | File | Issue | Resolution | Evidence |\n"
        "|---|---|---|---|---|\n"
        "| <severity_level_placeholder_value_for_reviewer_output> | "
        "<repository_relative_file_path_placeholder_value> | "
        "<issue_description_placeholder_value_for_material_regression> | "
        "<resolution_placeholder_value_for_required_fix> | "
        "<evidence_placeholder_value_for_verification_command> |\n"
        "| <severity_level_placeholder_value_for_reviewer_output> | "
        "<repository_relative_file_path_placeholder_value> | "
        "<issue_description_placeholder_value_for_material_regression> | "
        "<resolution_placeholder_value_for_required_fix> | "
        "<evidence_placeholder_value_for_verification_command> |\n"
        "status: <status_placeholder_value>\n"
        "outputs_written: <outputs_written_placeholder_value>\n"
        "next_action: <next_action_placeholder_value>\n"
        "truncated: <truncation_state_placeholder_value>\n"
        "reviewed_with: <review_command_placeholder_value>\n"
        "evidence_summary: <evidence_summary_placeholder_value>\n"
    )


def near_duplicate_template_text() -> str:
    return duplicate_template_text().replace(
        "reviewer-visible status used for handoff",
        "reviewer-visible status used for final handoff",
    )


def long_template_text(label: str) -> str:
    rows = "\n".join(
        (
            f"| warning | file-{index}.md | issue {label} {index} compares requirements, architecture, "
            "implementation log, test plan, release-gate output, and reviewer evidence for concrete regressions | "
            f"resolution {index} records the exact fix and owner | evidence {index} names the command and artifact |"
        )
        for index in range(28)
    )
    return (
        "## Final Report\n"
        "| Severity | File | Issue | Resolution | Evidence |\n"
        "|---|---|---|---|---|\n"
        f"{rows}\n"
        "status: <success-or-failure>\n"
        "outputs_written: <artifact paths>\n"
        "next_action: <command>\n"
        "truncated: <true-or-false>\n"
        "reviewed_with: <command evidence>\n"
        "evidence_summary: record the command or artifact that proves each reported outcome and the exact reviewer-visible status used for handoff.\n"
    )


def budget_template_text(label: str) -> str:
    rows = "\n".join(
        (
            f"| warning | file-{index}.md | issue {label} {index} compares requirements, architecture, "
            "implementation log, test plan, release-gate output, and reviewer evidence | "
            f"resolution {index} records the exact fix and owner |"
        )
        for index in range(8)
    )
    return (
        "## Final Report\n"
        "| Severity | File | Issue | Resolution |\n"
        "|---|---|---|---|\n"
        f"{rows}\n"
        "status: <success-or-failure>\n"
        "outputs_written: <artifact paths>\n"
        "next_action: <command>\n"
        "truncated: <true-or-false>\n"
        "reviewed_with: <command evidence>\n"
        "evidence_summary: record the command or artifact that proves each reported outcome.\n"
    )


def near_duplicate_prompt_text() -> str:
    return duplicate_prompt_text().replace(
        "Assigned angle: correctness and security.",
        "Assigned angle: correctness, reliability, and security.",
    )


def long_prompt_text(label: str) -> str:
    repeated_lines = "\n".join(
        (
            f"Review evidence bundle {label} section {index}: "
            "compare requirements, architecture, implementation log, test plan, and release-gate output; "
            "report only concrete issues with severity, path, line, problem, and fix."
        )
        for index in range(18)
    )
    return (
        "Use this prompt when assigning an adversarial reviewer.\n"
        "You are an independent reviewer. Your job is to inspect the changed skill file, "
        "name every concrete bug, and avoid style-only feedback.\n"
        "Assigned angle: correctness and security.\n"
        "READ-ONLY: Do not edit files, do not modify git state, and do not infer missing facts.\n"
        "For each issue, report severity, path, line, concrete problem, and concrete fix.\n"
        "If you find no material issue, respond with exactly LGTM.\n"
        f"{repeated_lines}\n"
        "Return only evidence-backed findings and keep speculative concerns out of the report.\n"
    )


def budget_prompt_text(label: str) -> str:
    repeated_lines = "\n".join(
        (
            f"Review budget bundle {label} section {index}: compare requirements, architecture, "
            "implementation log, test plan, release-gate output, and reviewer evidence."
        )
        for index in range(6)
    )
    return (
        "Use this prompt when assigning an adversarial reviewer.\n"
        "You are an independent reviewer. Your job is to inspect the changed skill file, "
        "name every concrete bug, and avoid style-only feedback.\n"
        "Assigned angle: correctness and security.\n"
        "READ-ONLY: Do not edit files, do not modify git state, and do not infer missing facts.\n"
        "For each issue, report severity, path, line, concrete problem, and concrete fix.\n"
        f"{repeated_lines}\n"
        "If you find no material issue, respond with exactly LGTM.\n"
        "Return only evidence-backed findings and keep speculative concerns out of the report.\n"
    )


def output_contract_block() -> str:
    return (
        "## Output, Token, And Error Contract\n"
        "status: success | needs_user | terminal | degraded\n"
        "inputs_resolved: <resolved inputs>\n"
        "outputs_written: <paths>\n"
        "next_action: <command>\n"
        "truncated: true | false\n"
    )


def valid_output_contract_prompt() -> str:
    return (
        f"{duplicate_prompt_text()}\n"
        "## Output, Token, And Error Contract\n"
        "status: success | needs_user | terminal | degraded\n"
        "inputs_resolved: <resolved inputs>\n"
        "outputs_written: <paths>\n"
        "next_action: <command>\n"
        "truncated: true | false\n"
    )


def scan_limit_line_values(output: str, path: str) -> dict[str, str]:
    prefix = f"repetition-scan-limited: {path}: "
    for line in output.splitlines():
        if not line.startswith(prefix):
            continue
        values: dict[str, str] = {}
        for part in line[len(prefix):].split():
            key, separator, value = part.partition("=")
            if separator:
                values[key] = value.rstrip(";")
        return values
    raise AssertionError(f"missing repetition-scan-limited line for {path}:\n{output}")


def summary_by_family(records: list[dict[str, str]], family: str) -> dict[str, str]:
    matches = [
        record for record in records
        if record.get("record_type") == "summary" and record.get("family") == family
    ]
    if len(matches) != 1:
        raise AssertionError(f"expected one summary for {family}, got {matches}")
    return matches[0]


def scenario_repetition_baseline_reports_exact_matches(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-baseline-exact-") as tmp:
        root = Path(tmp)
        init_repo(root)
        prompt = duplicate_prompt_text()
        template = duplicate_template_text()
        write_skill(
            root,
            "plugin/skills/prompt-copy/SKILL.md",
            skill_text(body=f"{prompt}\n## Separator\n\n{prompt}"),
        )
        write_metadata(root, "plugin/skills/prompt-copy/SKILL.md")
        write_skill(root, "plugin/skills/template-source/SKILL.md", skill_text(body=template))
        write_metadata(root, "plugin/skills/template-source/SKILL.md")
        write_skill(root, "plugin/skills/template-target/SKILL.md", skill_text(body=template))
        write_metadata(root, "plugin/skills/template-target/SKILL.md")
        commit_all(root)

        records = parse_baseline_records(
            run_repetition_baseline(root, checker, "all"),
            "repetition baseline reports exact matches",
        )
        matches = [record for record in records if record["record_type"] == "match"]
        summaries = [record for record in records if record["record_type"] == "summary"]
        prompt_matches = [record for record in matches if record.get("family") == "prompt"]
        template_matches = [record for record in matches if record.get("family") == "template"]

        if not any(record.get("match_type") == "same-file-exact" for record in prompt_matches):
            raise AssertionError(f"expected same-file prompt exact match: {records}")
        if not any(record.get("match_type") == "cross-file-exact" for record in template_matches):
            raise AssertionError(f"expected cross-file template exact match: {records}")
        for record in matches:
            for key in ("path", "start_line", "end_line", "fingerprint", "matched_path", "matched_start_line", "matched_end_line"):
                if not record.get(key):
                    raise AssertionError(f"baseline match missing {key}: {record}")
        if not any(record.get("family") == "prompt" for record in summaries):
            raise AssertionError(f"expected prompt summary record: {records}")
        if not any(record.get("family") == "template" for record in summaries):
            raise AssertionError(f"expected template summary record: {records}")


def scenario_repetition_baseline_reports_exact_index_metrics(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-baseline-exact-index-") as tmp:
        root = Path(tmp)
        init_repo(root)
        prompt = duplicate_prompt_text()
        for index in range(12):
            write_skill(
                root,
                f"plugin/skills/exact-index-{index:02d}/SKILL.md",
                skill_text(body=prompt),
            )
            write_metadata(root, f"plugin/skills/exact-index-{index:02d}/SKILL.md")
        commit_all(root)

        records = parse_baseline_records(
            run_repetition_baseline(root, checker, "all"),
            "exact index baseline metrics",
        )
        prompt_summary = summary_by_family(records, "prompt")
        candidate_count = int(prompt_summary.get("candidate_count", "0"))
        exact_match_count = int(prompt_summary.get("exact_match_count", "0"))
        group_count = int(prompt_summary.get("exact_index_group_count", "0"))
        max_group_size = int(prompt_summary.get("exact_index_max_group_size", "0"))
        if candidate_count < 12:
            raise AssertionError(f"expected prompt candidates in scaled exact fixture: {prompt_summary}")
        if exact_match_count != candidate_count - 1:
            raise AssertionError(f"expected one representative match per non-canonical duplicate: {prompt_summary}")
        if group_count != 1:
            raise AssertionError(f"expected grouped exact index to collapse duplicates: {prompt_summary}")
        if max_group_size != candidate_count:
            raise AssertionError(f"expected one exact index bucket containing all prompts: {prompt_summary}")
        matches = [record for record in records if record["record_type"] == "match"]
        if not all(int(record.get("duplicate_count", "0")) == candidate_count - 1 for record in matches):
            raise AssertionError(f"expected representative matches to carry duplicate count: {matches}")


def scenario_output_contract_masking_avoids_contract_only_matches(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-contract-mask-") as tmp:
        root = Path(tmp)
        init_repo(root)
        contract = output_contract_block()
        prompt_with_contract = (
            f"{duplicate_prompt_text()}\n"
            f"{contract}"
        )
        fenced_prompt_with_contract = (
            "```markdown\n"
            f"{duplicate_prompt_text()}\n"
            f"{contract}"
            "```\n"
        )
        heading_prompt_with_contract_fields = (
            "## Use this prompt when assigning a reviewer\n"
            f"{duplicate_prompt_text()}"
            "status: success | needs_user | terminal | degraded\n"
            "truncated: true | false\n"
        )
        prompt_lines = duplicate_prompt_text().splitlines()
        commented_contract_prompt = "\n".join(
            [
                prompt_lines[0],
                "<!--",
                contract.rstrip(),
                "-->",
                *prompt_lines[1:],
            ]
        ) + "\n"
        tilde_contract_wrapper = (
            "~~~markdown\n"
            f"{contract}"
            "```example marker inside a tilde fenced contract\n"
            "contract-only text after an inner backtick marker must remain masked.\n"
            "~~~\n"
        )
        write_skill(
            root,
            "plugin/skills/contract-only/SKILL.md",
            skill_text(body=f"```yaml\n{contract}```\n\n```yaml\n{contract}```\n"),
        )
        write_metadata(root, "plugin/skills/contract-only/SKILL.md")
        write_skill(
            root,
            "plugin/skills/tilde-contract-wrapper/SKILL.md",
            skill_text(body=f"{tilde_contract_wrapper}\n## Separator\n\n{tilde_contract_wrapper}"),
        )
        write_metadata(root, "plugin/skills/tilde-contract-wrapper/SKILL.md")
        write_skill(
            root,
            "plugin/skills/prompt-with-contract/SKILL.md",
            skill_text(body=f"{prompt_with_contract}\n## Separator\n\n{prompt_with_contract}"),
        )
        write_metadata(root, "plugin/skills/prompt-with-contract/SKILL.md")
        write_skill(
            root,
            "plugin/skills/fenced-prompt-with-contract/SKILL.md",
            skill_text(body=f"{fenced_prompt_with_contract}\n## Separator\n\n{fenced_prompt_with_contract}"),
        )
        write_metadata(root, "plugin/skills/fenced-prompt-with-contract/SKILL.md")
        write_skill(
            root,
            "plugin/skills/heading-prompt-with-contract-fields/SKILL.md",
            skill_text(body=f"{heading_prompt_with_contract_fields}\n## Separator\n\n{heading_prompt_with_contract_fields}"),
        )
        write_metadata(root, "plugin/skills/heading-prompt-with-contract-fields/SKILL.md")
        write_skill(
            root,
            "plugin/skills/commented-contract-prompt/SKILL.md",
            skill_text(body=f"{commented_contract_prompt}\n## Separator\n\n{commented_contract_prompt}"),
        )
        write_metadata(root, "plugin/skills/commented-contract-prompt/SKILL.md")
        commit_all(root)

        normal_result = run_checker(root, checker, "all")
        assert_findings(
            normal_result,
            {"inline-output-contract", "repeated-inline-prompt"},
            "contract-only normal mode keeps output-contract finding and prompt duplicate",
        )

        records = parse_baseline_records(
            run_repetition_baseline(root, checker, "all"),
            "output contract masking avoids contract-only matches",
        )
        matches = [record for record in records if record["record_type"] == "match"]
        if any(record.get("path") == "plugin/skills/contract-only/SKILL.md" for record in matches):
            raise AssertionError(f"contract-only duplicate should not produce repetition baseline match: {records}")
        if any(record.get("path") == "plugin/skills/tilde-contract-wrapper/SKILL.md" for record in matches):
            raise AssertionError(f"tilde fenced contract wrapper should mask through closing tilde fence: {records}")
        prompt_matches = [
            record
            for record in matches
            if record.get("path") == "plugin/skills/prompt-with-contract/SKILL.md"
            and record.get("family") == "prompt"
        ]
        fenced_prompt_matches = [
            record
            for record in matches
            if record.get("path") == "plugin/skills/fenced-prompt-with-contract/SKILL.md"
            and record.get("family") == "prompt"
        ]
        commented_prompt_matches = [
            record
            for record in matches
            if record.get("path") == "plugin/skills/commented-contract-prompt/SKILL.md"
            and record.get("family") == "prompt"
        ]
        heading_prompt_matches = [
            record
            for record in matches
            if record.get("path") == "plugin/skills/heading-prompt-with-contract-fields/SKILL.md"
            and record.get("family") == "prompt"
        ]
        if not prompt_matches:
            raise AssertionError(f"prompt duplicate with masked contract should still match: {records}")
        if not all(record.get("output_contract_masked") == "true" for record in prompt_matches):
            raise AssertionError(f"expected output_contract_masked evidence on prompt matches: {prompt_matches}")
        if not fenced_prompt_matches:
            raise AssertionError(f"fenced prompt duplicate with contract subspan should still match: {records}")
        if not all(record.get("output_contract_masked") == "true" for record in fenced_prompt_matches):
            raise AssertionError(f"expected fenced contract subspan masking evidence: {fenced_prompt_matches}")
        if not commented_prompt_matches:
            raise AssertionError(f"HTML-commented contract markers should not hide prompt duplicate: {records}")
        if any(record.get("output_contract_masked") == "true" for record in commented_prompt_matches):
            raise AssertionError(f"HTML-commented contract markers should not create mask evidence: {commented_prompt_matches}")
        if not heading_prompt_matches:
            raise AssertionError(f"heading prompt with contract fields should keep prompt body visible: {records}")
        if not all(record.get("output_contract_masked") == "true" for record in heading_prompt_matches):
            raise AssertionError(f"heading prompt contract fields should mask only field subspan: {heading_prompt_matches}")


def scenario_output_contract_markers_in_unrelated_sections_do_not_mask(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-contract-unrelated-") as tmp:
        root = Path(tmp)
        init_repo(root)
        unrelated = (
            f"{duplicate_prompt_text()}\n"
            "## Output, Token, And Error Contract\n"
            "\n"
            "## Separate Status Section\n"
            "status: success | needs_user | terminal | degraded\n"
            "\n"
            "## Separate Truncation Section\n"
            "truncated: true | false\n"
        )
        valid = valid_output_contract_prompt()
        write_skill(
            root,
            "plugin/skills/unrelated-contract-markers/SKILL.md",
            skill_text(body=f"{unrelated}\n## Separator\n\n{unrelated}"),
        )
        write_metadata(root, "plugin/skills/unrelated-contract-markers/SKILL.md")
        write_skill(
            root,
            "plugin/skills/owned-contract-markers/SKILL.md",
            skill_text(body=f"{valid}\n## Separator\n\n{valid}"),
        )
        write_metadata(root, "plugin/skills/owned-contract-markers/SKILL.md")
        commit_all(root)

        records = parse_baseline_records(
            run_repetition_baseline(root, checker, "all"),
            "unrelated output-contract markers do not mask",
        )
        matches = [record for record in records if record["record_type"] == "match"]
        unrelated_matches = [
            record
            for record in matches
            if record.get("path") == "plugin/skills/unrelated-contract-markers/SKILL.md"
        ]
        owned_matches = [
            record
            for record in matches
            if record.get("path") == "plugin/skills/owned-contract-markers/SKILL.md"
        ]
        if not unrelated_matches:
            raise AssertionError(f"expected unrelated-marker prompt duplicate to remain visible: {records}")
        if any(record.get("output_contract_masked") == "true" for record in unrelated_matches):
            raise AssertionError(f"unrelated section markers must not create owned mask: {unrelated_matches}")
        if not owned_matches or not all(record.get("output_contract_masked") == "true" for record in owned_matches):
            raise AssertionError(f"same-section output contract should be masked: {owned_matches}")


def scenario_repeated_inline_prompt_exact_findings(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-prompt-exact-") as tmp:
        root = Path(tmp)
        init_repo(root)
        prompt = duplicate_prompt_text()
        write_skill(
            root,
            "plugin/skills/same-file/SKILL.md",
            skill_text(body=f"{prompt}\n## Separator\n\n{prompt}"),
        )
        write_metadata(root, "plugin/skills/same-file/SKILL.md")
        commit_all(root)

        result = run_checker(root, checker, "all")
        assert_findings(result, {"repeated-inline-prompt"}, "same-file repeated prompt exact finding")
        line = result.stdout.strip()
        for token in ("duplicate_count=1", "extract reusable prompt", "prompt artifact", "shared contract"):
            if token not in line:
                raise AssertionError(f"repeated prompt message missing {token}: {line}")
        if "repeated-inline-template" in result.stdout:
            raise AssertionError(f"prompt duplicate must not emit template ID:\n{result.stdout}")


def scenario_repeated_inline_prompt_cross_file_working_targets(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-prompt-cross-") as tmp:
        root = Path(tmp)
        init_repo(root)
        prompt = duplicate_prompt_text()
        write_skill(root, "plugin/skills/a-source/SKILL.md", skill_text(body=prompt))
        write_metadata(root, "plugin/skills/a-source/SKILL.md")
        write_skill(root, "plugin/skills/z-source/SKILL.md", skill_text(body=prompt.replace("correctness", "traceability")))
        write_metadata(root, "plugin/skills/z-source/SKILL.md")
        commit_all(root)

        write_skill(
            root,
            "plugin/skills/z-target/SKILL.md",
            skill_text(body=f"{authoring_compliant_body(related='$plugin:a-source')}\n{prompt}"),
        )
        write_metadata(root, "plugin/skills/z-target/SKILL.md")
        write_skill(
            root,
            "plugin/skills/a-target/SKILL.md",
            skill_text(body=f"{authoring_compliant_body(related='$plugin:z-source')}\n{prompt.replace('correctness', 'traceability')}"),
        )
        write_metadata(root, "plugin/skills/a-target/SKILL.md")

        result = run_checker(root, checker, "working")
        assert_findings(result, {"repeated-inline-prompt"}, "working cross-file repeated prompt targets")
        for target in ("plugin/skills/z-target/SKILL.md", "plugin/skills/a-target/SKILL.md"):
            if target not in result.stdout:
                raise AssertionError(f"expected repeated prompt finding for target {target}:\n{result.stdout}")
        for line in result.stdout.splitlines():
            if line.startswith("repeated-inline-prompt: plugin/skills/a-source/SKILL.md"):
                raise AssertionError(f"working mode should not emit source path findings:\n{result.stdout}")
            if line.startswith("repeated-inline-prompt: plugin/skills/z-source/SKILL.md"):
                raise AssertionError(f"working mode should not emit source path findings:\n{result.stdout}")


def scenario_repeated_inline_prompt_fuzzy_same_file(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-prompt-fuzzy-") as tmp:
        root = Path(tmp)
        init_repo(root)
        prompt = duplicate_prompt_text()
        near_prompt = near_duplicate_prompt_text()
        write_skill(
            root,
            "plugin/skills/fuzzy/SKILL.md",
            skill_text(body=f"{prompt}\n## Separator\n\n{near_prompt}"),
        )
        write_metadata(root, "plugin/skills/fuzzy/SKILL.md")
        commit_all(root)

        result = run_checker(root, checker, "all")
        assert_findings(result, {"repeated-inline-prompt"}, "same-file fuzzy repeated prompt finding")
        if "same-file-fuzzy" not in result.stdout:
            raise AssertionError(f"expected fuzzy match evidence in repeated prompt finding:\n{result.stdout}")

        baseline = parse_baseline_records(
            run_repetition_baseline(root, checker, "all"),
            "fuzzy prompt baseline records",
        )
        if not any(record.get("match_type") == "same-file-fuzzy" for record in baseline):
            raise AssertionError(f"dry-run baseline should report fuzzy prompt match: {baseline}")


def scenario_repetition_scan_limited_prompt_budget_and_exception(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-scan-limited-") as tmp:
        root = Path(tmp)
        init_repo(root)
        exact_prompt = duplicate_prompt_text()
        limited_body = (
            f"{long_prompt_text('alpha')}\n## Near Duplicate\n\n{long_prompt_text('beta')}\n"
            f"## Exact Duplicate\n\n{exact_prompt}\n## Exact Duplicate Copy\n\n{exact_prompt}"
        )
        excepted_body = (
            "## Hygiene Exception\n"
            "repetition-scan-limited: accepted pair-cost cap for intentionally long local audit prompts.\n"
            "reviewed-with: python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .\n\n"
            f"{long_prompt_text('gamma')}\n## Near Duplicate\n\n{long_prompt_text('delta')}\n"
            f"## Exact Duplicate\n\n{exact_prompt}\n## Exact Duplicate Copy\n\n{exact_prompt}"
        )
        fenced_exception_body = (
            "```markdown\n"
            "## Hygiene Exception\n"
            "repetition-scan-limited: fenced examples must not suppress real findings.\n"
            "reviewed-with: python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .\n"
            "```\n\n"
            f"{long_prompt_text('epsilon')}\n## Near Duplicate\n\n{long_prompt_text('zeta')}\n"
        )
        same_marker_info_fence_exception_body = (
            "```markdown\n"
            "```example\n"
            "## Hygiene Exception\n"
            "repetition-scan-limited: same-marker info-string fences must not close the outer fence.\n"
            "reviewed-with: python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .\n"
            "```\n\n"
            f"{long_prompt_text('same-marker-alpha')}\n## Near Duplicate\n\n{long_prompt_text('same-marker-beta')}\n"
        )
        tilde_fenced_exception_body = (
            "~~~markdown\n"
            "## Hygiene Exception\n"
            "repetition-scan-limited: tilde-fenced examples must not suppress real findings.\n"
            "reviewed-with: python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .\n"
            "~~~\n\n"
            f"{long_prompt_text('eta')}\n## Near Duplicate\n\n{long_prompt_text('theta')}\n"
        )
        indented_exception_body = (
            "    ## Hygiene Exception\n"
            "    repetition-scan-limited: indented examples must not suppress real findings.\n"
            "    reviewed-with: python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .\n\n"
            f"{long_prompt_text('iota')}\n## Near Duplicate\n\n{long_prompt_text('kappa')}\n"
        )
        inline_hidden_reason_body = (
            "## Hygiene Exception\n"
            "repetition-scan-limited: <!-- hidden reason must not suppress -->\n"
            "reviewed-with: python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .\n\n"
            f"{long_prompt_text('rho')}\n## Near Duplicate\n\n{long_prompt_text('sigma')}\n"
        )
        inline_hidden_evidence_body = (
            "## Hygiene Exception\n"
            "repetition-scan-limited: visible reason.\n"
            "reviewed-with: <!-- hidden evidence must not suppress -->\n\n"
            f"{long_prompt_text('tau')}\n## Near Duplicate\n\n{long_prompt_text('upsilon')}\n"
        )
        weak_evidence_exception_body = (
            "## Hygiene Exception\n"
            "repetition-scan-limited: visible reason without a real dry-run evidence command.\n"
            "reviewed-with: ok\n\n"
            f"{long_prompt_text('weak-evidence-alpha')}\n## Near Duplicate\n\n{long_prompt_text('weak-evidence-beta')}\n"
        )
        fence_comment_then_valid_body = (
            "```text\n"
            "<!-- this fenced comment marker must not hide the visible exception below\n"
            "```\n\n"
            "## Hygiene Exception\n"
            "repetition-scan-limited: accepted pair-cost cap after fenced comment marker.\n"
            "reviewed-with: python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .\n\n"
            f"{long_prompt_text('phi')}\n## Near Duplicate\n\n{long_prompt_text('chi')}\n"
        )
        fenced_inside_section_body = (
            "## Hygiene Exception\n"
            "~~~text\n"
            "repetition-scan-limited: fenced examples inside a real section must not suppress.\n"
            "reviewed-with: python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .\n"
            "~~~\n\n"
            f"{long_prompt_text('lambda')}\n## Near Duplicate\n\n{long_prompt_text('mu')}\n"
        )
        indented_inside_section_body = (
            "## Hygiene Exception\n"
            "    repetition-scan-limited: indented examples inside a real section must not suppress.\n"
            "    reviewed-with: python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .\n\n"
            f"{long_prompt_text('nu')}\n## Near Duplicate\n\n{long_prompt_text('xi')}\n"
        )
        html_comment_exception_body = (
            "<!--\n"
            "## Hygiene Exception\n"
            "repetition-scan-limited: hidden comments must not suppress real findings.\n"
            "reviewed-with: python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .\n"
            "-->\n\n"
            f"{long_prompt_text('omicron')}\n## Near Duplicate\n\n{long_prompt_text('pi')}\n"
        )
        lone_body = long_prompt_text("lone")
        write_skill(root, "plugin/skills/limited/SKILL.md", skill_text(body=limited_body))
        write_metadata(root, "plugin/skills/limited/SKILL.md")
        write_skill(root, "plugin/skills/excepted/SKILL.md", skill_text(body=excepted_body))
        write_metadata(root, "plugin/skills/excepted/SKILL.md")
        write_skill(root, "plugin/skills/fenced-exception/SKILL.md", skill_text(body=fenced_exception_body))
        write_metadata(root, "plugin/skills/fenced-exception/SKILL.md")
        write_skill(
            root,
            "plugin/skills/same-marker-info-fence-exception/SKILL.md",
            skill_text(body=same_marker_info_fence_exception_body),
        )
        write_metadata(root, "plugin/skills/same-marker-info-fence-exception/SKILL.md")
        write_skill(root, "plugin/skills/tilde-fenced-exception/SKILL.md", skill_text(body=tilde_fenced_exception_body))
        write_metadata(root, "plugin/skills/tilde-fenced-exception/SKILL.md")
        write_skill(root, "plugin/skills/indented-exception/SKILL.md", skill_text(body=indented_exception_body))
        write_metadata(root, "plugin/skills/indented-exception/SKILL.md")
        write_skill(root, "plugin/skills/inline-hidden-reason/SKILL.md", skill_text(body=inline_hidden_reason_body))
        write_metadata(root, "plugin/skills/inline-hidden-reason/SKILL.md")
        write_skill(root, "plugin/skills/inline-hidden-evidence/SKILL.md", skill_text(body=inline_hidden_evidence_body))
        write_metadata(root, "plugin/skills/inline-hidden-evidence/SKILL.md")
        write_skill(root, "plugin/skills/weak-evidence-exception/SKILL.md", skill_text(body=weak_evidence_exception_body))
        write_metadata(root, "plugin/skills/weak-evidence-exception/SKILL.md")
        write_skill(root, "plugin/skills/fence-comment-valid/SKILL.md", skill_text(body=fence_comment_then_valid_body))
        write_metadata(root, "plugin/skills/fence-comment-valid/SKILL.md")
        write_skill(root, "plugin/skills/fenced-inside-section/SKILL.md", skill_text(body=fenced_inside_section_body))
        write_metadata(root, "plugin/skills/fenced-inside-section/SKILL.md")
        write_skill(root, "plugin/skills/indented-inside-section/SKILL.md", skill_text(body=indented_inside_section_body))
        write_metadata(root, "plugin/skills/indented-inside-section/SKILL.md")
        write_skill(root, "plugin/skills/html-comment-exception/SKILL.md", skill_text(body=html_comment_exception_body))
        write_metadata(root, "plugin/skills/html-comment-exception/SKILL.md")
        write_skill(root, "plugin/skills/lone/SKILL.md", skill_text(body=lone_body))
        write_metadata(root, "plugin/skills/lone/SKILL.md")
        commit_all(root)

        result = run_checker(root, checker, "all")
        actual_ids = finding_ids(result.stdout)
        expected_ids = {"repeated-inline-prompt", "repetition-scan-limited"}
        if result.code != 1 or actual_ids != expected_ids:
            raise AssertionError(
                f"scan-limit fixture expected IDs {sorted(expected_ids)}, "
                f"got exit {result.code} IDs {sorted(actual_ids)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
        if "repetition-scan-limited: plugin/skills/limited/SKILL.md" not in result.stdout:
            raise AssertionError(f"expected scan-limit finding for limited skill:\n{result.stdout}")
        for path in (
            "plugin/skills/fenced-exception/SKILL.md",
            "plugin/skills/same-marker-info-fence-exception/SKILL.md",
            "plugin/skills/tilde-fenced-exception/SKILL.md",
            "plugin/skills/indented-exception/SKILL.md",
            "plugin/skills/inline-hidden-reason/SKILL.md",
            "plugin/skills/inline-hidden-evidence/SKILL.md",
            "plugin/skills/weak-evidence-exception/SKILL.md",
            "plugin/skills/fenced-inside-section/SKILL.md",
            "plugin/skills/indented-inside-section/SKILL.md",
            "plugin/skills/html-comment-exception/SKILL.md",
        ):
            if f"repetition-scan-limited: {path}" not in result.stdout:
                raise AssertionError(f"code-block scan-limit exception should not suppress {path}:\n{result.stdout}")
        if "repetition-scan-limited: plugin/skills/excepted/SKILL.md" in result.stdout:
            raise AssertionError(f"valid scan-limit exception should suppress only scan-limit finding:\n{result.stdout}")
        if "repetition-scan-limited: plugin/skills/fence-comment-valid/SKILL.md" in result.stdout:
            raise AssertionError(f"visible scan-limit exception after fenced comment marker should suppress finding:\n{result.stdout}")
        if "plugin/skills/lone/SKILL.md" in result.stdout:
            raise AssertionError(f"lone large candidate must not emit scan-limit finding:\n{result.stdout}")
        for token in ("families=prompt", "pair_cost", "comparisons"):
            if token not in result.stdout:
                raise AssertionError(f"scan-limit message missing {token}:\n{result.stdout}")
        for path in (
            "plugin/skills/limited/SKILL.md",
            "plugin/skills/fenced-exception/SKILL.md",
            "plugin/skills/same-marker-info-fence-exception/SKILL.md",
            "plugin/skills/tilde-fenced-exception/SKILL.md",
            "plugin/skills/indented-exception/SKILL.md",
            "plugin/skills/inline-hidden-reason/SKILL.md",
            "plugin/skills/inline-hidden-evidence/SKILL.md",
            "plugin/skills/weak-evidence-exception/SKILL.md",
            "plugin/skills/fenced-inside-section/SKILL.md",
            "plugin/skills/indented-inside-section/SKILL.md",
            "plugin/skills/html-comment-exception/SKILL.md",
        ):
            values = scan_limit_line_values(result.stdout, path)
            if int(values.get("pair_cost", "0")) <= 0:
                raise AssertionError(f"scan-limit pair-cost evidence must be nonzero for {path}:\n{result.stdout}")


def scenario_repetition_scan_limited_whole_run_budget_is_family_scoped(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-total-budget-") as tmp:
        root = Path(tmp)
        init_repo(root)
        for index in range(35):
            first = budget_prompt_text(f"alpha-{index}")
            second = budget_prompt_text(f"beta-{index}")
            write_skill(
                root,
                f"plugin/skills/prompt-budget-{index:02d}/SKILL.md",
                skill_text(body=f"{first}\n## Near Duplicate\n\n{second}"),
            )
            write_metadata(root, f"plugin/skills/prompt-budget-{index:02d}/SKILL.md")

        template = duplicate_template_text()
        near_template = near_duplicate_template_text()
        write_skill(
            root,
            "plugin/skills/template-after-prompt-budget/SKILL.md",
            skill_text(body=f"{template}\n## Separator\n\n{near_template}"),
        )
        write_metadata(root, "plugin/skills/template-after-prompt-budget/SKILL.md")

        for index in range(35):
            first = budget_template_text(f"alpha-{index}")
            second = budget_template_text(f"beta-{index}")
            write_skill(
                root,
                f"plugin/skills/template-budget-{index:02d}/SKILL.md",
                skill_text(body=f"{first}\n## Near Duplicate\n\n{second}"),
            )
            write_metadata(root, f"plugin/skills/template-budget-{index:02d}/SKILL.md")
        commit_all(root)

        result = run_checker(root, checker, "all")
        actual_ids = finding_ids(result.stdout)
        expected_ids = {"repeated-inline-prompt", "repeated-inline-template", "repetition-scan-limited"}
        if result.code != 1 or actual_ids != expected_ids:
            raise AssertionError(
                f"whole-run budget fixture expected IDs {sorted(expected_ids)}, "
                f"got exit {result.code} IDs {sorted(actual_ids)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
        if "reasons=total_pair_cost" not in result.stdout:
            raise AssertionError(f"expected whole-run pair-cost limit evidence:\n{result.stdout}")
        prompt_limit_path = ""
        for line in result.stdout.splitlines():
            if (
                line.startswith("repetition-scan-limited: plugin/skills/prompt-budget-")
                and "families=prompt" in line
                and "reasons=total_pair_cost" in line
            ):
                prompt_limit_path = line.removeprefix("repetition-scan-limited: ").split(": ", 1)[0]
                break
        if not prompt_limit_path:
            raise AssertionError(f"expected prompt-family whole-run pair-cost limit evidence:\n{result.stdout}")
        values = scan_limit_line_values(result.stdout, prompt_limit_path)
        total_comparisons = int(values.get("total_comparisons", "0"))
        total_compared_chars = int(values.get("total_compared_chars", "0"))
        total_pair_cost = int(values.get("total_pair_cost", "0"))
        if not (0 < total_comparisons <= 10_000):
            raise AssertionError(f"total comparisons outside budget: {values}\n{result.stdout}")
        if not (0 < total_compared_chars <= 2_000_000):
            raise AssertionError(f"total compared chars outside budget: {values}\n{result.stdout}")
        if not (0 < total_pair_cost <= 20_000_000):
            raise AssertionError(f"total pair cost outside budget: {values}\n{result.stdout}")
        if "repeated-inline-template: plugin/skills/template-after-prompt-budget/SKILL.md" not in result.stdout:
            raise AssertionError(f"prompt budget exhaustion should not starve template fuzzy checks:\n{result.stdout}")
        template_limit_path = ""
        for line in result.stdout.splitlines():
            if (
                line.startswith("repetition-scan-limited: plugin/skills/template-budget-")
                and "families=template" in line
                and "reasons=total_pair_cost" in line
            ):
                template_limit_path = line.removeprefix("repetition-scan-limited: ").split(": ", 1)[0]
                break
        if not template_limit_path:
            raise AssertionError(f"expected template-family whole-run pair-cost limit evidence:\n{result.stdout}")
        template_values = scan_limit_line_values(result.stdout, template_limit_path)
        for key, cap in (
            ("total_comparisons", 10_000),
            ("total_compared_chars", 2_000_000),
            ("total_pair_cost", 20_000_000),
        ):
            value = int(template_values.get(key, "0"))
            if not (0 < value <= cap):
                raise AssertionError(f"template total {key} outside budget: {template_values}\n{result.stdout}")

        baseline = parse_baseline_records(
            run_repetition_baseline(root, checker, "all"),
            "whole-run budget baseline metrics",
        )
        prompt_summary = summary_by_family(baseline, "prompt")
        template_summary = summary_by_family(baseline, "template")
        for key, cap in (
            ("total_comparisons", 10_000),
            ("total_compared_chars", 2_000_000),
            ("total_pair_cost", 20_000_000),
        ):
            prompt_value = int(prompt_summary.get(key, "0"))
            template_value = int(template_summary.get(key, "0"))
            if not (0 < prompt_value <= cap):
                raise AssertionError(f"prompt baseline {key} outside cap {cap}: {prompt_summary}")
            if not (0 < template_value <= cap):
                raise AssertionError(f"template baseline {key} outside cap {cap}: {template_summary}")


def scenario_repeated_inline_template_exact_findings(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-template-exact-") as tmp:
        root = Path(tmp)
        init_repo(root)
        template = duplicate_template_text()
        write_skill(
            root,
            "plugin/skills/template-same/SKILL.md",
            skill_text(body=f"{template}\n## Separator\n\n{template}"),
        )
        write_metadata(root, "plugin/skills/template-same/SKILL.md")
        write_skill(root, "plugin/skills/template-source/SKILL.md", skill_text(body=template))
        write_metadata(root, "plugin/skills/template-source/SKILL.md")
        commit_all(root)

        all_result = run_checker(root, checker, "all")
        assert_findings(all_result, {"repeated-inline-template"}, "all-mode same-file exact template finding")
        if not any(
            line.startswith("repeated-inline-template: plugin/skills/template-same/SKILL.md")
            and "same-file-exact" in line
            for line in all_result.stdout.splitlines()
        ):
            raise AssertionError(f"expected same-file exact template finding for template-same:\n{all_result.stdout}")

        write_skill(
            root,
            "plugin/skills/template-target/SKILL.md",
            skill_text(body=f"{authoring_compliant_body(related='$plugin:template-source')}\n{template}"),
        )
        write_metadata(root, "plugin/skills/template-target/SKILL.md")

        result = run_checker(root, checker, "working")
        assert_findings(result, {"repeated-inline-template"}, "exact repeated template findings")
        if not any(
            line.startswith("repeated-inline-template: plugin/skills/template-target/SKILL.md")
            for line in result.stdout.splitlines()
        ):
            raise AssertionError(f"expected working repeated template finding for template-target:\n{result.stdout}")
        if "extract reusable template" not in result.stdout or "template artifact" not in result.stdout:
            raise AssertionError(f"expected template extraction guidance:\n{result.stdout}")
        if "repeated-inline-prompt" in result.stdout:
            raise AssertionError(f"template duplicate must not emit prompt ID:\n{result.stdout}")


def scenario_repeated_inline_template_placeholder_heavy_exact_only(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-template-placeholder-heavy-") as tmp:
        root = Path(tmp)
        init_repo(root)
        template = placeholder_heavy_template_text()
        write_skill(
            root,
            "plugin/skills/template-placeholder-heavy/SKILL.md",
            skill_text(body=f"{template}\n## Separator\n\n{template}"),
        )
        write_metadata(root, "plugin/skills/template-placeholder-heavy/SKILL.md")
        commit_all(root)

        inventory = parse_candidate_inventory(
            run_candidate_inventory(root, checker, "all"),
            "placeholder-heavy template exact-only inventory",
        )
        records = [
            record
            for record in inventory
            if record.get("path") == "plugin/skills/template-placeholder-heavy/SKILL.md"
        ]
        if len(records) != 2:
            raise AssertionError(f"expected two placeholder-heavy template candidates: {inventory}")
        if not all(record.get("family") == "template" for record in records):
            raise AssertionError(f"placeholder-heavy candidates must remain templates: {records}")
        if not all(record.get("exact_only") == "true" for record in records):
            raise AssertionError(f"placeholder-heavy candidates must be exact-only: {records}")
        if not all(float(record.get("placeholder_ratio", "0")) > 0.70 for record in records):
            raise AssertionError(f"fixture did not exceed placeholder ratio cap: {records}")

        result = run_checker(root, checker, "all")
        assert_findings(result, {"repeated-inline-template"}, "placeholder-heavy exact template finding")
        if "same-file-exact" not in result.stdout:
            raise AssertionError(f"placeholder-heavy template should match by exact fingerprint:\n{result.stdout}")
        if "same-file-fuzzy" in result.stdout:
            raise AssertionError(f"placeholder-heavy template must not use fuzzy matching:\n{result.stdout}")


def scenario_repeated_inline_template_placeholder_heavy_cross_file_requires_same_anchors(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-template-placeholder-heavy-cross-") as tmp:
        root = Path(tmp)
        init_repo(root)
        source_template = placeholder_heavy_template_text()
        target_template = source_template.replace(
            "issue_description_placeholder_value_for_material_regression",
            "risk_summary_placeholder_value_for_material_regression",
        )
        write_skill(root, "plugin/skills/template-source/SKILL.md", skill_text(body=source_template))
        write_metadata(root, "plugin/skills/template-source/SKILL.md")
        commit_all(root)

        write_skill(
            root,
            "plugin/skills/template-target/SKILL.md",
            skill_text(body=f"{authoring_compliant_body(related='$plugin:template-source')}\n{target_template}"),
        )
        write_metadata(root, "plugin/skills/template-target/SKILL.md")

        inventory = parse_candidate_inventory(
            run_candidate_inventory(root, checker, "all"),
            "placeholder-heavy cross-file exact-only inventory",
        )
        source = candidate_by_path(
            inventory,
            "plugin/skills/template-source/SKILL.md",
            "placeholder-heavy source inventory",
        )
        target = candidate_by_path(
            inventory,
            "plugin/skills/template-target/SKILL.md",
            "placeholder-heavy target inventory",
        )
        if source.get("fingerprint") != target.get("fingerprint"):
            raise AssertionError(f"fixture should share normalized fingerprint: {inventory}")
        if source.get("stable_anchors") == target.get("stable_anchors"):
            raise AssertionError(f"fixture should differ by stable anchors: {inventory}")
        if source.get("exact_only") != "true" or target.get("exact_only") != "true":
            raise AssertionError(f"both placeholder-heavy templates should be exact-only: {inventory}")

        result = run_checker(root, checker, "working")
        assert_pass(result, "placeholder-heavy cross-file exact-only requires matching stable anchors")


def scenario_repeated_inline_template_placeholder_heavy_all_mode_canonical_by_anchors(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-template-placeholder-heavy-all-") as tmp:
        root = Path(tmp)
        init_repo(root)
        anchor_a = placeholder_heavy_template_text()
        anchor_b = anchor_a.replace(
            "issue_description_placeholder_value_for_material_regression",
            "risk_summary_placeholder_value_for_material_regression",
        )
        write_skill(root, "plugin/skills/a-anchor-a/SKILL.md", skill_text(body=anchor_a))
        write_metadata(root, "plugin/skills/a-anchor-a/SKILL.md")
        write_skill(root, "plugin/skills/b-anchor-b/SKILL.md", skill_text(body=anchor_b))
        write_metadata(root, "plugin/skills/b-anchor-b/SKILL.md")
        write_skill(root, "plugin/skills/c-anchor-b-copy/SKILL.md", skill_text(body=anchor_b))
        write_metadata(root, "plugin/skills/c-anchor-b-copy/SKILL.md")
        commit_all(root)

        result = run_checker(root, checker, "all")
        assert_findings(result, {"repeated-inline-template"}, "placeholder-heavy all-mode canonical per anchor group")
        lines = result.stdout.splitlines()
        if not any(line.startswith("repeated-inline-template: plugin/skills/c-anchor-b-copy/SKILL.md") for line in lines):
            raise AssertionError(f"expected only non-canonical copy in anchor-b subgroup to warn:\n{result.stdout}")
        for path in ("plugin/skills/a-anchor-a/SKILL.md", "plugin/skills/b-anchor-b/SKILL.md"):
            if any(line.startswith(f"repeated-inline-template: {path}") for line in lines):
                raise AssertionError(f"anchor subgroup canonical path should not warn for {path}:\n{result.stdout}")


def scenario_repeated_inline_template_fuzzy_same_file(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-template-fuzzy-") as tmp:
        root = Path(tmp)
        init_repo(root)
        template = duplicate_template_text()
        near_template = near_duplicate_template_text()
        write_skill(
            root,
            "plugin/skills/template-fuzzy/SKILL.md",
            skill_text(body=f"{template}\n## Separator\n\n{near_template}"),
        )
        write_metadata(root, "plugin/skills/template-fuzzy/SKILL.md")
        commit_all(root)

        result = run_checker(root, checker, "all")
        assert_findings(result, {"repeated-inline-template"}, "same-file fuzzy repeated template finding")
        if "same-file-fuzzy" not in result.stdout:
            raise AssertionError(f"expected fuzzy match evidence in repeated template finding:\n{result.stdout}")

        baseline = parse_baseline_records(
            run_repetition_baseline(root, checker, "all"),
            "fuzzy template baseline records",
        )
        if not any(record.get("match_type") == "same-file-fuzzy" and record.get("family") == "template" for record in baseline):
            raise AssertionError(f"dry-run baseline should report fuzzy template match: {baseline}")


def scenario_repetition_scan_limited_template_budget_and_exception(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-template-scan-limited-") as tmp:
        root = Path(tmp)
        init_repo(root)
        exact_template = duplicate_template_text()
        limited_body = (
            f"{long_template_text('alpha')}\n## Near Duplicate\n\n{long_template_text('beta')}\n"
            f"## Exact Duplicate\n\n{exact_template}\n## Exact Duplicate Copy\n\n{exact_template}"
        )
        excepted_body = (
            "## Hygiene Exception\n"
            "repetition-scan-limited: accepted pair-cost cap for intentionally long local report templates.\n"
            "cap-evidence: python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .\n\n"
            f"{long_template_text('gamma')}\n## Near Duplicate\n\n{long_template_text('delta')}\n"
            f"## Exact Duplicate\n\n{exact_template}\n## Exact Duplicate Copy\n\n{exact_template}"
        )
        lone_body = long_template_text("lone")
        write_skill(root, "plugin/skills/template-limited/SKILL.md", skill_text(body=limited_body))
        write_metadata(root, "plugin/skills/template-limited/SKILL.md")
        write_skill(root, "plugin/skills/template-excepted/SKILL.md", skill_text(body=excepted_body))
        write_metadata(root, "plugin/skills/template-excepted/SKILL.md")
        write_skill(root, "plugin/skills/template-lone/SKILL.md", skill_text(body=lone_body))
        write_metadata(root, "plugin/skills/template-lone/SKILL.md")
        commit_all(root)

        result = run_checker(root, checker, "all")
        actual_ids = finding_ids(result.stdout)
        expected_ids = {"repeated-inline-template", "repetition-scan-limited"}
        if result.code != 1 or actual_ids != expected_ids:
            raise AssertionError(
                f"template scan-limit fixture expected IDs {sorted(expected_ids)}, "
                f"got exit {result.code} IDs {sorted(actual_ids)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
        if "repetition-scan-limited: plugin/skills/template-limited/SKILL.md" not in result.stdout:
            raise AssertionError(f"expected scan-limit finding for limited template skill:\n{result.stdout}")
        if "repetition-scan-limited: plugin/skills/template-excepted/SKILL.md" in result.stdout:
            raise AssertionError(f"valid scan-limit exception should suppress template scan-limit finding:\n{result.stdout}")
        if "plugin/skills/template-lone/SKILL.md" in result.stdout:
            raise AssertionError(f"lone large template candidate must not emit scan-limit finding:\n{result.stdout}")
        for token in ("families=template", "pair_cost", "comparisons"):
            if token not in result.stdout:
                raise AssertionError(f"template scan-limit message missing {token}:\n{result.stdout}")
        values = scan_limit_line_values(result.stdout, "plugin/skills/template-limited/SKILL.md")
        if int(values.get("pair_cost", "0")) <= 0:
            raise AssertionError(f"template scan-limit pair-cost evidence must be nonzero:\n{result.stdout}")


def scenario_repetition_scan_limited_aggregates_prompt_and_template(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-scan-limited-aggregate-") as tmp:
        root = Path(tmp)
        init_repo(root)
        body = (
            f"{long_prompt_text('alpha')}\n## Near Duplicate Prompt\n\n{long_prompt_text('beta')}\n"
            f"## Template Alpha\n\n{long_template_text('alpha')}\n"
            f"## Near Duplicate Template\n\n{long_template_text('beta')}\n"
        )
        path = "plugin/skills/aggregate-limited/SKILL.md"
        write_skill(root, path, skill_text(body=body))
        write_metadata(root, path)
        commit_all(root)

        result = run_checker(root, checker, "all")
        assert_findings(result, {"repetition-scan-limited"}, "aggregated prompt/template scan-limit finding")
        lines = [
            line for line in result.stdout.splitlines()
            if line.startswith(f"repetition-scan-limited: {path}:")
        ]
        if len(lines) != 1:
            raise AssertionError(f"expected one aggregated scan-limit finding for {path}:\n{result.stdout}")
        line = lines[0]
        if "families=prompt,template" not in line:
            raise AssertionError(f"expected prompt/template family aggregation: {line}")
        values = scan_limit_line_values(result.stdout, path)
        if int(values.get("pair_cost", "0")) <= 0:
            raise AssertionError(f"aggregated scan-limit pair-cost evidence must be nonzero:\n{result.stdout}")


def scenario_moderate_skill_bloat_positive_and_exceptions(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-moderate-bloat-") as tmp:
        root = Path(tmp)
        init_repo(root)
        write_skill(root, "plugin/skills/moderate/SKILL.md", skill_text_with_total_lines(401))
        write_metadata(root, "plugin/skills/moderate/SKILL.md")
        write_skill(
            root,
            "plugin/skills/excepted/SKILL.md",
            skill_text_with_total_lines(
                401,
                body_prefix=(
                    "## Hygiene Exception\n"
                    "moderate-skill-bloat: intentionally self-contained because the skill has a compact local checklist.\n"
                ),
            ),
        )
        write_metadata(root, "plugin/skills/excepted/SKILL.md")
        write_skill(
            root,
            "plugin/skills/empty-exception/SKILL.md",
            skill_text_with_total_lines(
                401,
                body_prefix=(
                    "## Hygiene Exception\n"
                    "moderate-skill-bloat:\n"
                ),
            ),
        )
        write_metadata(root, "plugin/skills/empty-exception/SKILL.md")
        write_skill(
            root,
            "plugin/skills/fenced-exception/SKILL.md",
            skill_text_with_total_lines(
                401,
                body_prefix=(
                    "```markdown\n"
                    "## Hygiene Exception\n"
                    "moderate-skill-bloat: fenced examples must not suppress real findings.\n"
                    "```\n"
                ),
            ),
        )
        write_metadata(root, "plugin/skills/fenced-exception/SKILL.md")
        write_skill(
            root,
            "plugin/skills/tilde-fenced-exception/SKILL.md",
            skill_text_with_total_lines(
                401,
                body_prefix=(
                    "~~~markdown\n"
                    "## Hygiene Exception\n"
                    "moderate-skill-bloat: tilde-fenced examples must not suppress real findings.\n"
                    "~~~\n"
                ),
            ),
        )
        write_metadata(root, "plugin/skills/tilde-fenced-exception/SKILL.md")
        write_skill(
            root,
            "plugin/skills/indented-exception/SKILL.md",
            skill_text_with_total_lines(
                401,
                body_prefix=(
                    "    ## Hygiene Exception\n"
                    "    moderate-skill-bloat: indented examples must not suppress real findings.\n"
                ),
            ),
        )
        write_metadata(root, "plugin/skills/indented-exception/SKILL.md")
        write_skill(
            root,
            "plugin/skills/inline-hidden-reason/SKILL.md",
            skill_text_with_total_lines(
                401,
                body_prefix=(
                    "## Hygiene Exception\n"
                    "moderate-skill-bloat: <!-- hidden reason must not suppress -->\n"
                ),
            ),
        )
        write_metadata(root, "plugin/skills/inline-hidden-reason/SKILL.md")
        write_skill(
            root,
            "plugin/skills/fence-comment-valid/SKILL.md",
            skill_text_with_total_lines(
                401,
                body_prefix=(
                    "```text\n"
                    "<!-- this fenced comment marker must not hide the visible exception below\n"
                    "```\n\n"
                    "## Hygiene Exception\n"
                    "moderate-skill-bloat: visible exception remains valid after fenced comment marker.\n"
                ),
            ),
        )
        write_metadata(root, "plugin/skills/fence-comment-valid/SKILL.md")
        write_skill(
            root,
            "plugin/skills/html-comment-exception/SKILL.md",
            skill_text_with_total_lines(
                401,
                body_prefix=(
                    "<!--\n"
                    "## Hygiene Exception\n"
                    "moderate-skill-bloat: hidden comments must not suppress real findings.\n"
                    "-->\n"
                ),
            ),
        )
        write_metadata(root, "plugin/skills/html-comment-exception/SKILL.md")
        write_skill(
            root,
            "plugin/skills/nested-exception/SKILL.md",
            skill_text_with_total_lines(
                401,
                body_prefix=(
                    "### Hygiene Exception\n"
                    "moderate-skill-bloat: nested headings must not suppress real findings.\n"
                ),
            ),
        )
        write_metadata(root, "plugin/skills/nested-exception/SKILL.md")
        write_skill(
            root,
            "plugin/skills/fenced-inside-section/SKILL.md",
            skill_text_with_total_lines(
                401,
                body_prefix=(
                    "## Hygiene Exception\n"
                    "```text\n"
                    "moderate-skill-bloat: fenced examples inside a real section must not suppress.\n"
                    "```\n"
                ),
            ),
        )
        write_metadata(root, "plugin/skills/fenced-inside-section/SKILL.md")
        write_skill(
            root,
            "plugin/skills/tilde-fenced-inside-section/SKILL.md",
            skill_text_with_total_lines(
                401,
                body_prefix=(
                    "## Hygiene Exception\n"
                    "~~~text\n"
                    "moderate-skill-bloat: tilde-fenced examples inside a real section must not suppress.\n"
                    "~~~\n"
                ),
            ),
        )
        write_metadata(root, "plugin/skills/tilde-fenced-inside-section/SKILL.md")
        write_skill(
            root,
            "plugin/skills/indented-inside-section/SKILL.md",
            skill_text_with_total_lines(
                401,
                body_prefix=(
                    "## Hygiene Exception\n"
                    "    moderate-skill-bloat: indented examples inside a real section must not suppress.\n"
                ),
            ),
        )
        write_metadata(root, "plugin/skills/indented-inside-section/SKILL.md")
        write_skill(
            root,
            "plugin/skills/unrelated-exception/SKILL.md",
            skill_text_with_total_lines(
                401,
                body_prefix=(
                    "## Hygiene Exception\n"
                    "repetition-scan-limited: this unrelated exception must not suppress moderate bloat.\n"
                ),
            ),
        )
        write_metadata(root, "plugin/skills/unrelated-exception/SKILL.md")
        write_skill(
            root,
            "plugin/skills/oversized-with-exception/SKILL.md",
            skill_text_with_total_lines(
                751,
                body_prefix=(
                    "## Hygiene Exception\n"
                    "moderate-skill-bloat: intentionally self-contained, but oversized must still fire.\n"
                ),
            ),
        )
        write_metadata(root, "plugin/skills/oversized-with-exception/SKILL.md")
        commit_all(root)

        result = run_checker(root, checker, "all")
        actual_ids = finding_ids(result.stdout)
        expected_ids = {"moderate-skill-bloat", "oversized-skill"}
        if result.code != 1 or actual_ids != expected_ids:
            raise AssertionError(
                f"moderate bloat fixture expected IDs {sorted(expected_ids)}, "
                f"got exit {result.code} IDs {sorted(actual_ids)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
        moderate_lines = [
            line for line in result.stdout.splitlines()
            if line.startswith("moderate-skill-bloat:")
        ]
        if len(moderate_lines) != 12:
            raise AssertionError(f"expected twelve unsuppressed moderate findings, got {moderate_lines}")
        for line in moderate_lines:
            for token in ("401", "400", "extract", "prompts/templates", "shared contracts"):
                if token not in line:
                    raise AssertionError(f"moderate bloat message missing {token}: {line}")
        if "plugin/skills/excepted/SKILL.md" in result.stdout:
            raise AssertionError(f"valid moderate-bloat exception should suppress finding:\n{result.stdout}")
        if "plugin/skills/fence-comment-valid/SKILL.md" in result.stdout:
            raise AssertionError(f"visible moderate-bloat exception after fenced comment marker should suppress finding:\n{result.stdout}")
        if "oversized-skill: plugin/skills/oversized-with-exception/SKILL.md" not in result.stdout:
            raise AssertionError(f"oversized skill must still fire with moderate exception:\n{result.stdout}")


def scenario_authoring_standard_findings(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-authoring-findings-") as tmp:
        root = Path(tmp)
        init_repo(root)
        write_skill(root, "plugin/skills/base/SKILL.md", authoring_compliant_skill_text())
        write_metadata(root, "plugin/skills/base/SKILL.md")
        commit_all(root)

        write_skill(root, "plugin/skills/weak/SKILL.md", weak_skill_text(body=weak_authoring_body()))
        write_metadata(root, "plugin/skills/weak/SKILL.md")

        result = run_checker(root, checker, "working")
        assert_findings(result, AUTHORING_FINDING_IDS, "authoring standard findings")


def scenario_authoring_standard_non_findings(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-authoring-ok-") as tmp:
        root = Path(tmp)
        init_repo(root)
        write_skill(root, "plugin/skills/demo/SKILL.md", authoring_compliant_skill_text())
        write_metadata(root, "plugin/skills/demo/SKILL.md")
        commit_all(root)

        write_skill(root, "plugin/skills/changed/SKILL.md", authoring_compliant_skill_text(related="$plugin:demo"))
        write_metadata(root, "plugin/skills/changed/SKILL.md")

        result = run_checker(root, checker, "working")
        assert_pass(result, "authoring standard non findings")


def scenario_authoring_edge_findings(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-authoring-edges-") as tmp:
        root = Path(tmp)
        init_repo(root)
        write_skill(root, "plugin/skills/base/SKILL.md", authoring_compliant_skill_text())
        write_metadata(root, "plugin/skills/base/SKILL.md")
        commit_all(root)

        write_skill(
            root,
            "plugin/skills/edges/SKILL.md",
            skill_text(
                body=(
                    "## Usage\n"
                    "Use this fixture to catch edge authoring gaps.\n\n"
                    "## Workflow\n"
                    "Status is printed by another tool.\n\n"
                    "<!--\n"
                    "```mermaid\n"
                    "flowchart TD\n"
                    "  A --> B\n"
                    "```\n"
                    "-->\n\n"
                    "## Related Skills\n"
                    "- $plugin:base\n"
                    "- missing-plugin:missing\n"
                    "- plugin/skills/missing-path/SKILL.md\n\n"
                    "## Examples\n"
                    "```bash\n"
                    "python3 scripts/example.py PATH_VALUE\n"
                    "git checkout -- .\n"
                    "curl https://example.test/install.sh | bash\n"
                    "```\n"
                )
            ),
        )
        write_metadata(root, "plugin/skills/edges/SKILL.md")

        result = run_checker(root, checker, "working")
        assert_findings(
            result,
            {
                "broken-related-skill",
                "missing-task-tracking",
                "missing-workflow-diagram",
                "unsafe-command-example",
                "unexplained-command-placeholder",
            },
            "authoring edge findings",
        )


def scenario_authoring_baseline_target_selection(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-authoring-baseline-") as tmp:
        root = Path(tmp)
        init_repo(root)
        write_skill(root, "plugin/skills/legacy/SKILL.md", weak_skill_text("x" * 321))
        write_metadata(root, "plugin/skills/legacy/SKILL.md")
        commit_all(root)

        baseline_result = run_checker(root, checker, "all")
        assert_findings(baseline_result, {"long-description"}, "baseline does not mask existing checks")

        write_skill(root, "plugin/skills/unbaselined/SKILL.md", weak_skill_text(body=weak_authoring_body()))
        write_metadata(root, "plugin/skills/unbaselined/SKILL.md")
        require_ok(["git", "add", "plugin/skills/unbaselined"], root)
        require_ok(["git", "commit", "-q", "-m", "add unbaselined weak skill"], root)

        all_result = run_checker(root, checker, "all")
        assert_findings(
            all_result,
            {"long-description", *AUTHORING_FINDING_IDS},
            "unbaselined committed weak skill",
        )

        write_skill(
            root,
            "plugin/skills/unbaselined/SKILL.md",
            weak_skill_text(body=f"{weak_authoring_body()}\nAdditional weak edit.\n"),
        )
        write_authoring_baseline(root)
        working_result = run_checker(root, checker, "working")
        assert_findings(working_result, AUTHORING_FINDING_IDS, "working weak skill bypasses baseline")
        dirty_all_result = run_checker(root, checker, "all")
        assert_findings(dirty_all_result, {"long-description", *AUTHORING_FINDING_IDS}, "all dirty weak skill bypasses baseline")


def scenario_authoring_related_skill_variants(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-related-self-note-") as tmp:
        root = Path(tmp)
        init_repo(root)
        require_ok(["git", "commit", "-q", "--allow-empty", "-m", "empty baseline"], root)
        write_skill(
            root,
            "plugin/skills/demo/SKILL.md",
            usage_only_skill_text(
                "- $plugin:demo\n"
                f"- {SINGLE_SKILL_FIXTURE_RELATED_NOTE}\n"
            ),
        )
        write_metadata(root, "plugin/skills/demo/SKILL.md")
        result = run_checker(root, checker, "working")
        assert_pass(result, "self reference plus fixture note passes in single-skill repo")

    with TemporaryDirectory(prefix="skill-hygiene-related-self-only-") as tmp:
        root = Path(tmp)
        init_repo(root)
        require_ok(["git", "commit", "-q", "--allow-empty", "-m", "empty baseline"], root)
        write_skill(root, "plugin/skills/demo/SKILL.md", usage_only_skill_text("- $plugin:demo\n"))
        write_metadata(root, "plugin/skills/demo/SKILL.md")
        result = run_checker(root, checker, "working")
        assert_findings(result, {"missing-related-skills"}, "self reference alone fails")

    with TemporaryDirectory(prefix="skill-hygiene-related-non-self-") as tmp:
        root = Path(tmp)
        init_repo(root)
        write_skill(
            root,
            "plugin/skills/base/SKILL.md",
            usage_only_skill_text(
                "- $plugin:base\n"
                f"- {SINGLE_SKILL_FIXTURE_RELATED_NOTE}\n"
            ),
        )
        write_metadata(root, "plugin/skills/base/SKILL.md")
        commit_all(root)
        write_skill(root, "plugin/skills/demo/SKILL.md", usage_only_skill_text("- $plugin:base\n"))
        write_metadata(root, "plugin/skills/demo/SKILL.md")
        result = run_checker(root, checker, "working")
        assert_pass(result, "valid non-self related skill passes")

    with TemporaryDirectory(prefix="skill-hygiene-related-non-dollar-") as tmp:
        root = Path(tmp)
        init_repo(root)
        write_skill(root, "plugin/skills/base/SKILL.md", usage_only_skill_text("- $plugin:base\n" f"- {SINGLE_SKILL_FIXTURE_RELATED_NOTE}\n"))
        write_metadata(root, "plugin/skills/base/SKILL.md")
        commit_all(root)
        write_skill(root, "plugin/skills/demo/SKILL.md", usage_only_skill_text("- plugin:base\n"))
        write_metadata(root, "plugin/skills/demo/SKILL.md")
        result = run_checker(root, checker, "working")
        assert_pass(result, "valid non-dollar plugin related skill passes")

    with TemporaryDirectory(prefix="skill-hygiene-related-path-ref-") as tmp:
        root = Path(tmp)
        init_repo(root)
        write_skill(root, "plugin/skills/base/SKILL.md", usage_only_skill_text("- $plugin:base\n" f"- {SINGLE_SKILL_FIXTURE_RELATED_NOTE}\n"))
        write_metadata(root, "plugin/skills/base/SKILL.md")
        commit_all(root)
        write_skill(root, "plugin/skills/demo/SKILL.md", usage_only_skill_text("- plugin/skills/base/SKILL.md\n"))
        write_metadata(root, "plugin/skills/demo/SKILL.md")
        result = run_checker(root, checker, "working")
        assert_pass(result, "valid path related skill passes")

    with TemporaryDirectory(prefix="skill-hygiene-related-broken-") as tmp:
        root = Path(tmp)
        init_repo(root)
        require_ok(["git", "commit", "-q", "--allow-empty", "-m", "empty baseline"], root)
        write_skill(root, "plugin/skills/demo/SKILL.md", usage_only_skill_text("- $plugin:missing\n"))
        write_metadata(root, "plugin/skills/demo/SKILL.md")
        result = run_checker(root, checker, "working")
        assert_findings(result, {"broken-related-skill", "missing-related-skills"}, "broken related skill fails")


def scenario_authoring_related_skills_staged_inventory(checker: Path) -> None:
    with TemporaryDirectory(prefix="skill-hygiene-related-staged-added-") as tmp:
        root = Path(tmp)
        init_repo(root)
        write_skill(root, "plugin/skills/source/SKILL.md", usage_only_skill_text("- $plugin:target\n"))
        write_metadata(root, "plugin/skills/source/SKILL.md")
        write_skill(root, "plugin/skills/target/SKILL.md", usage_only_skill_text("- $plugin:source\n"))
        write_metadata(root, "plugin/skills/target/SKILL.md")
        require_ok(["git", "add", "."], root)
        result = run_checker(root, checker, "staged")
        assert_pass(result, "staged related ref resolves staged-added target")

    with TemporaryDirectory(prefix="skill-hygiene-related-staged-deleted-") as tmp:
        root = Path(tmp)
        init_repo(root)
        write_skill(root, "plugin/skills/source/SKILL.md", usage_only_skill_text("- $plugin:target\n"))
        write_metadata(root, "plugin/skills/source/SKILL.md")
        target_path = "plugin/skills/target/SKILL.md"
        write_skill(root, target_path, usage_only_skill_text("- $plugin:source\n"))
        write_metadata(root, target_path)
        commit_all(root)
        require_ok(["git", "rm", "-q", target_path], root)
        write_skill(root, target_path, usage_only_skill_text("- $plugin:source\n"))
        write_skill(root, "plugin/skills/source/SKILL.md", usage_only_skill_text("- $plugin:target\n- staged deletion check\n"))
        require_ok(["git", "add", "plugin/skills/source/SKILL.md"], root)
        result = run_checker(root, checker, "staged")
        assert_findings(
            result,
            {"broken-related-skill", "missing-related-skills"},
            "staged related ref ignores staged-deleted target",
        )

    with TemporaryDirectory(prefix="skill-hygiene-related-worktree-only-") as tmp:
        root = Path(tmp)
        init_repo(root)
        write_skill(
            root,
            "plugin/skills/source/SKILL.md",
            usage_only_skill_text(
                "- $plugin:source\n"
                f"- {SINGLE_SKILL_FIXTURE_RELATED_NOTE}\n"
            ),
        )
        write_metadata(root, "plugin/skills/source/SKILL.md")
        commit_all(root)
        write_skill(root, "plugin/skills/source/SKILL.md", usage_only_skill_text("- $plugin:target\n"))
        require_ok(["git", "add", "plugin/skills/source/SKILL.md"], root)
        write_skill(root, "plugin/skills/target/SKILL.md", usage_only_skill_text("- $plugin:source\n"))
        result = run_checker(root, checker, "staged")
        assert_findings(
            result,
            {"broken-related-skill", "missing-related-skills"},
            "staged related ref ignores worktree-only target",
        )


def run_all(repo_root: Path) -> int:
    checker = repo_root / "scripts" / "skill-hygiene-check.py"
    if not checker.is_file():
        print(f"Missing checker: {checker}", file=sys.stderr)
        return 2

    scenarios = (
        ("existing checks in all mode", scenario_existing_checks_all),
        (
            "all mode ignores committed legacy metadata",
            scenario_all_mode_ignores_committed_legacy_metadata,
        ),
        ("working added skill metadata", scenario_added_skill_metadata_working),
        ("staged deleted modified skill", scenario_staged_deleted_modified_skill),
        ("staged deleted added skill metadata", scenario_staged_deleted_added_skill_metadata),
        ("staged reads index not dirty worktree", scenario_staged_reads_index_not_worktree),
        (
            "candidate inventory classifies prompt and template",
            scenario_candidate_inventory_classifies_prompt_and_template,
        ),
        (
            "candidate inventory ignores ordinary sections",
            scenario_candidate_inventory_ignores_ordinary_sections,
        ),
        (
            "candidate inventory spans internal headings",
            scenario_candidate_inventory_spans_internal_headings,
        ),
        (
            "candidate inventory respects fence marker type",
            scenario_candidate_inventory_respects_fence_marker_type,
        ),
        (
            "candidate inventory classifier boundaries",
            scenario_candidate_inventory_classifier_boundaries,
        ),
        (
            "candidate inventory stops before plain internal heading",
            scenario_candidate_inventory_stops_before_plain_internal_heading,
        ),
        (
            "candidate inventory strips line numbers for fingerprints",
            scenario_candidate_inventory_strips_line_numbers_for_fingerprints,
        ),
        (
            "candidate inventory normalizes uppercase placeholders",
            scenario_candidate_inventory_normalizes_uppercase_placeholders,
        ),
        (
            "repetition baseline reports exact matches",
            scenario_repetition_baseline_reports_exact_matches,
        ),
        (
            "repetition baseline reports exact index metrics",
            scenario_repetition_baseline_reports_exact_index_metrics,
        ),
        (
            "output contract masking avoids contract-only matches",
            scenario_output_contract_masking_avoids_contract_only_matches,
        ),
        (
            "output contract markers in unrelated sections do not mask",
            scenario_output_contract_markers_in_unrelated_sections_do_not_mask,
        ),
        (
            "repeated inline prompt exact findings",
            scenario_repeated_inline_prompt_exact_findings,
        ),
        (
            "repeated inline prompt cross-file working targets",
            scenario_repeated_inline_prompt_cross_file_working_targets,
        ),
        (
            "repeated inline prompt fuzzy same-file",
            scenario_repeated_inline_prompt_fuzzy_same_file,
        ),
        (
            "repetition scan limited prompt budget and exception",
            scenario_repetition_scan_limited_prompt_budget_and_exception,
        ),
        (
            "repetition scan limited whole-run budget is family scoped",
            scenario_repetition_scan_limited_whole_run_budget_is_family_scoped,
        ),
        (
            "repeated inline template exact findings",
            scenario_repeated_inline_template_exact_findings,
        ),
        (
            "repeated inline template placeholder-heavy exact-only",
            scenario_repeated_inline_template_placeholder_heavy_exact_only,
        ),
        (
            "repeated inline template placeholder-heavy cross-file requires same anchors",
            scenario_repeated_inline_template_placeholder_heavy_cross_file_requires_same_anchors,
        ),
        (
            "repeated inline template placeholder-heavy all-mode canonical by anchors",
            scenario_repeated_inline_template_placeholder_heavy_all_mode_canonical_by_anchors,
        ),
        (
            "repeated inline template fuzzy same-file",
            scenario_repeated_inline_template_fuzzy_same_file,
        ),
        (
            "repetition scan limited template budget and exception",
            scenario_repetition_scan_limited_template_budget_and_exception,
        ),
        (
            "repetition scan limited aggregates prompt and template",
            scenario_repetition_scan_limited_aggregates_prompt_and_template,
        ),
        (
            "moderate skill bloat positive and exceptions",
            scenario_moderate_skill_bloat_positive_and_exceptions,
        ),
        (
            "authoring standard findings",
            scenario_authoring_standard_findings,
        ),
        (
            "authoring standard non findings",
            scenario_authoring_standard_non_findings,
        ),
        (
            "authoring edge findings",
            scenario_authoring_edge_findings,
        ),
        (
            "authoring baseline target selection",
            scenario_authoring_baseline_target_selection,
        ),
        (
            "authoring related skill variants",
            scenario_authoring_related_skill_variants,
        ),
        (
            "authoring related skills staged inventory",
            scenario_authoring_related_skills_staged_inventory,
        ),
    )

    failures = 0
    print("Skill hygiene checker fixtures")
    for name, scenario in scenarios:
        try:
            scenario(checker)
        except Exception as exc:  # noqa: BLE001 - fixture diagnostic
            failures += 1
            print(f"FAIL {name}: {exc}")
        else:
            print(f"PASS {name}")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        usage()
        return 2

    repo_root = Path(argv[1]).resolve()
    if not repo_root.is_dir():
        print(f"Repo root is not a directory: {repo_root}", file=sys.stderr)
        return 2

    return run_all(repo_root)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
