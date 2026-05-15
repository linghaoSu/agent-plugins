#!/usr/bin/env python3
"""Deterministic fixtures for scripts/skill-hygiene-check.py."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory


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
    require_ok(["git", "add", "."], root)
    require_ok(["git", "commit", "-q", "-m", message], root)


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
        write_skill(root, "plugin/skills/new/SKILL.md", skill_text())

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

        write_skill(root, skill_path, skill_text("x" * 321))
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
        write_skill(root, skill_path, skill_text())
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

        write_skill(root, skill_path, skill_text("Safe staged description."))
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
