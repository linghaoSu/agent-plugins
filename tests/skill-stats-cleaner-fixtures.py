#!/usr/bin/env python3
"""Deterministic fixtures for skill-stats skill-cleaner wrapper."""

from __future__ import annotations

import json
import hashlib
import os
import stat
import subprocess
import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any


def usage() -> None:
    print("Usage: skill-stats-cleaner-fixtures.py <repo-root>", file=sys.stderr)


def run_command(args: list[str], cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, env=env, check=False, capture_output=True, text=True)


def assert_contains(haystack: str, needle: str, scenario: str) -> None:
    if needle not in haystack:
        raise AssertionError(f"{scenario}: missing {needle!r}\ncontent:\n{haystack}")


def assert_not_contains(haystack: str, needle: str, scenario: str) -> None:
    if needle in haystack:
        raise AssertionError(f"{scenario}: unexpected {needle!r}\ncontent:\n{haystack}")


def assert_mode(report: dict[str, Any], status: str, scenario: str) -> None:
    actual = report.get("status")
    if actual != status:
        raise AssertionError(f"{scenario}: expected status {status!r}, got {actual!r}\nreport:\n{report}")
    if report.get("mode") != "skill-cleaner-report":
        raise AssertionError(f"{scenario}: wrong mode\nreport:\n{report}")


def load_json_stdout(result: subprocess.CompletedProcess[str], scenario: str) -> dict[str, Any]:
    if result.returncode != 0:
        raise AssertionError(
            f"{scenario}: expected wrapper JSON exit 0, got {result.returncode}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"{scenario}: stdout is not JSON: {exc}\nstdout:\n{result.stdout}") from exc
    if not isinstance(data, dict):
        raise AssertionError(f"{scenario}: stdout JSON is not an object: {data!r}")
    return data


def write_file(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def write_skill(root: Path, slug: str, description: str = "Fixture skill.") -> Path:
    return write_file(
        root / "skills" / slug / "SKILL.md",
        "---\n"
        f"name: {slug}\n"
        f"description: {description}\n"
        "---\n\n"
        f"# {slug}\n",
    )


def write_identity_analyzer(checkout: Path) -> Path:
    return write_file(
        checkout / "skills" / "skill-cleaner" / "scripts" / "skill-cleaner.ts",
        "// fixture identity for skill-cleaner\n"
        "const sections = ['Skill Budget', 'Description candidates', 'Duplicates', 'Unused'];\n"
        "console.log(sections.join('\\n'));\n",
    )


def write_node_stub(bin_dir: Path) -> Path:
    node = bin_dir / "node"
    write_file(
        node,
        "#!/usr/bin/env bash\n"
        "set -u\n"
        "if [ -n \"${NODE_ARGV_LOG:-}\" ]; then\n"
        "  printf '%s\\n' \"$@\" > \"$NODE_ARGV_LOG\"\n"
        "fi\n"
        "case \"${FIXTURE_NODE_MODE:-success}\" in\n"
        "  nonzero)\n"
        "    printf 'fixture analyzer failed\\n' >&2\n"
        "    exit 9\n"
        "    ;;\n"
        "  nonzero_with_sections)\n"
        "    cat \"${FIXTURE_NODE_STDOUT:?missing fixture stdout}\"\n"
        "    printf 'fixture analyzer failed after partial report\\n' >&2\n"
        "    exit 9\n"
        "    ;;\n"
        "  huge)\n"
        "    i=0\n"
        "    while [ \"$i\" -lt 9000 ]; do\n"
        "      printf 'Huge analyzer line %04d with repeated content for truncation checks.\\n' \"$i\"\n"
        "      i=$((i + 1))\n"
        "    done\n"
        "    exit 0\n"
        "    ;;\n"
        "  *)\n"
        "    cat \"${FIXTURE_NODE_STDOUT:?missing fixture stdout}\"\n"
        "    ;;\n"
        "esac\n",
    )
    node.chmod(node.stat().st_mode | stat.S_IXUSR)
    return node


def base_env(tmp: Path, node_bin: Path) -> dict[str, str]:
    env = os.environ.copy()
    env.pop("SKILL_STATS_CLEANER_ANALYZER", None)
    env["PATH"] = f"{node_bin}{os.pathsep}{env.get('PATH', '')}"
    env["HOME"] = str(tmp / "home")
    env["CODEX_HOME"] = str(tmp / "codex-home")
    env["OPENCLAW_HOME"] = str(tmp / "openclaw-home")
    env["TMPDIR"] = str(tmp / "tmp")
    for key in ("HOME", "CODEX_HOME", "OPENCLAW_HOME", "TMPDIR"):
        Path(env[key]).mkdir(parents=True, exist_ok=True)
    return env


def run_report(
    repo_root: Path,
    wrapper: Path,
    args: list[str],
    env: dict[str, str],
    scenario: str,
) -> dict[str, Any]:
    result = run_command(["python3", str(wrapper), "report", *args], repo_root, env)
    return load_json_stdout(result, scenario)


def assert_no_target_mutation(paths: list[Path], before: dict[Path, str], scenario: str) -> None:
    for path in paths:
        actual = path.read_text(encoding="utf-8") if path.exists() else "<missing>"
        if actual != before[path]:
            raise AssertionError(f"{scenario}: target mutated unexpectedly: {path}")


def scenario_missing_analyzer(repo_root: Path, wrapper: Path) -> None:
    with TemporaryDirectory(prefix="skill-cleaner-missing-") as tmp_text:
        tmp = Path(tmp_text)
        node_bin = tmp / "bin"
        node_bin.mkdir()
        write_node_stub(node_bin)
        env = base_env(tmp, node_bin)
        report = run_report(repo_root, wrapper, [], env, "missing analyzer")
        assert_mode(report, "needs_user", "missing analyzer")
        if report.get("outputs_written") != []:
            raise AssertionError(f"missing analyzer: expected no outputs_written\nreport:\n{report}")
        assert_contains(json.dumps(report), "SKILL_STATS_CLEANER_ANALYZER", "missing analyzer guidance")


def scenario_invalid_analyzer_identity(repo_root: Path, wrapper: Path) -> None:
    with TemporaryDirectory(prefix="skill-cleaner-identity-") as tmp_text:
        tmp = Path(tmp_text)
        node_bin = tmp / "bin"
        node_bin.mkdir()
        write_node_stub(node_bin)
        env = base_env(tmp, node_bin)
        invalid = write_file(tmp / "checkout" / "skills" / "skill-cleaner" / "scripts" / "skill-cleaner.ts", "nope\n")
        report = run_report(repo_root, wrapper, ["--analyzer", str(invalid)], env, "invalid analyzer identity")
        assert_mode(report, "needs_user", "invalid analyzer identity")
        assert_contains(json.dumps(report), "identity", "invalid analyzer identity")
        if report.get("outputs_written") != []:
            raise AssertionError(f"invalid analyzer identity: expected no outputs_written\nreport:\n{report}")


def write_logs(env: dict[str, str]) -> None:
    home = Path(env["HOME"])
    codex = Path(env["CODEX_HOME"])
    openclaw = Path(env["OPENCLAW_HOME"])
    write_file(home / ".claude" / "skill-stats.jsonl", '{"skill":"demo"}\n')
    write_file(home / ".claude" / "archive" / "old.jsonl", '{"skill":"archived"}\n')
    write_file(codex / "sessions" / "recent.jsonl", '{"session":"codex"}\n')
    write_file(codex / "skills" / "not-a-log.txt", "must not be scanned\n")
    write_file(openclaw / "logs" / "recent.log", "openclaw log\n")


def scenario_success_report(repo_root: Path, wrapper: Path) -> None:
    with TemporaryDirectory(prefix="skill-cleaner-success-") as tmp_text:
        tmp = Path(tmp_text)
        node_bin = tmp / "bin"
        node_bin.mkdir()
        write_node_stub(node_bin)
        env = base_env(tmp, node_bin)
        write_logs(env)

        analyzer = write_identity_analyzer(tmp / "agent-scripts")
        personal_root = Path(env["HOME"]) / "personal-skills"
        duplicate = write_skill(personal_root, "duplicate-skill", "Duplicate skill.")
        kept = write_skill(personal_root, "kept-skill", "Kept skill.")
        unused = write_skill(personal_root, "unused-skill", "Unused candidate.")
        config = write_json(tmp / "settings.json", {"disabledSkills": []})
        symlink_root = tmp / "personal-link"
        symlink_root.symlink_to(personal_root, target_is_directory=True)
        output = write_file(
            tmp / "analyzer-output.txt",
            "## Skill Budget\n"
            "- Budget pressure: demo skill names consume context.\n\n"
            "## Description candidates\n"
            f"- {kept}: shorten this long description.\n\n"
            f"- description: {kept} old: Kept skill. new: Kept. confidence: high\n\n"
            "## Duplicates\n"
            f"- duplicate: {duplicate.parent} kept: {kept} confidence: high\n\n"
            "## Unused candidates\n"
            f"- {unused.parent}: heuristic only; not safe to delete.\n\n"
            "## Root summary\n"
            "- roots scanned: repo and explicit personal roots.\n",
        )
        env["FIXTURE_NODE_STDOUT"] = str(output)
        env["NODE_ARGV_LOG"] = str(tmp / "node-argv.log")

        before = {duplicate: duplicate.read_text(encoding="utf-8"), kept: kept.read_text(encoding="utf-8")}
        report = run_report(
            repo_root,
            wrapper,
            [
                "--analyzer",
                str(analyzer),
                "--root",
                str(personal_root),
                "--root",
                str(symlink_root),
                "--config",
                str(config),
                "--months",
                "4",
                "--no-logs",
            ],
            env,
            "success report",
        )

        assert_mode(report, "success", "success report")
        stdout_json = json.dumps(report, sort_keys=True)
        assert_not_contains(stdout_json, str(Path(env["HOME"])), "home redaction")
        assert_contains(stdout_json, "~/personal-skills", "home redaction label")
        section_names = [section.get("name") for section in report.get("sections", [])]
        for expected in ("Skill Budget", "Description candidates", "Duplicates", "Unused candidates", "Root summary"):
            if expected not in section_names:
                raise AssertionError(f"success report: missing section {expected!r}\nsections:\n{section_names}")

        explicit_roots = [
            root for root in report["inputs"]["scan_roots"] if root.get("source") == "explicit_user_root"
        ]
        if len(explicit_roots) != 1:
            raise AssertionError(f"success report: expected realpath-deduped explicit root\n{explicit_roots}")

        assert_not_contains(stdout_json, "not-a-log.txt", "non-log exclusion")

        outputs = report.get("outputs_written", [])
        if len(outputs) != 1:
            raise AssertionError(f"success report: expected one evidence output\nreport:\n{report}")
        evidence_path = Path(outputs[0])
        if not evidence_path.exists():
            raise AssertionError(f"success report: missing evidence bundle {evidence_path}")
        mode = stat.S_IMODE(evidence_path.stat().st_mode)
        if mode != 0o600:
            raise AssertionError(f"success report: evidence mode expected 0600, got {oct(mode)}")
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        if evidence.get("report_id") != report.get("report_id"):
            raise AssertionError("success report: evidence/report id mismatch")
        findings = evidence.get("findings", [])
        if not any(candidate.get("action") == "delete_path" for finding in findings for candidate in finding.get("action_candidates", [])):
            raise AssertionError(f"success report: expected delete action candidate\n{evidence}")
        if not any(candidate.get("action") == "edit_skill_description" for finding in findings for candidate in finding.get("action_candidates", [])):
            raise AssertionError(f"success report: expected description action candidate\n{evidence}")
        if not any(candidate.get("action") == "disable_json_config_entry" for finding in findings for candidate in finding.get("action_candidates", [])):
            raise AssertionError(f"success report: expected config disable action candidate\n{evidence}")
        display_findings = report.get("display_findings", [])
        if not any(
            candidate.get("action_id")
            for finding in display_findings
            for candidate in finding.get("action_candidates", [])
        ):
            raise AssertionError(f"success report: missing display action ids\n{report}")
        argv = Path(env["NODE_ARGV_LOG"]).read_text(encoding="utf-8")
        assert_contains(argv, "--experimental-strip-types", "node argv")
        assert_contains(argv, "--months", "node argv")
        assert_no_target_mutation([duplicate, kept], before, "success report")


def scenario_log_resolution_degrades_without_cleanup_authority(repo_root: Path, wrapper: Path) -> None:
    with TemporaryDirectory(prefix="skill-cleaner-logs-") as tmp_text:
        tmp = Path(tmp_text)
        node_bin = tmp / "bin"
        node_bin.mkdir()
        write_node_stub(node_bin)
        env = base_env(tmp, node_bin)
        write_logs(env)
        write_file(Path(env["HOME"]) / ".claude" / "logs" / "malformed.jsonl", "{not valid json MALFORMED_LOG_SENTINEL}\n")
        write_file(Path(env["CODEX_HOME"]) / "sessions" / "malformed.log", "MALFORMED_SESSION_SENTINEL\n")

        codex_sessions = Path(env["CODEX_HOME"]) / "sessions"
        now = int(time.time())
        for index in range(25):
            path = write_file(codex_sessions / f"recent-{index:02d}.jsonl", '{"session":"codex"}\n')
            os.utime(path, (now - 1000 + index, now - 1000 + index))
        openclaw_logs = Path(env["OPENCLAW_HOME"]) / "logs"
        for index in range(21):
            path = write_file(openclaw_logs / f"large-{index:02d}.log", "x" * (1200 * 1024))
            os.utime(path, (now - 500 + index, now - 500 + index))

        analyzer = write_identity_analyzer(tmp / "agent-scripts")
        root = Path(env["HOME"]) / "personal-skills"
        duplicate = write_skill(root, "duplicate-skill", "Duplicate skill.")
        kept = write_skill(root, "kept-skill", "Kept skill.")
        output = write_file(
            tmp / "analyzer-output.txt",
            "## Skill Budget\n"
            "- ok\n\n"
            "## Duplicates\n"
            f"- duplicate: {duplicate.parent} kept: {kept} confidence: high\n",
        )
        env["FIXTURE_NODE_STDOUT"] = str(output)
        report = run_report(repo_root, wrapper, ["--analyzer", str(analyzer), "--root", str(root)], env, "log resolution")
        assert_mode(report, "degraded", "log resolution")
        if report.get("truncated") is not True:
            raise AssertionError(f"log resolution: expected truncated true for capped logs\n{report}")
        stdout_json = json.dumps(report, sort_keys=True)
        assert_not_contains(stdout_json, "MALFORMED_LOG_SENTINEL", "malformed log redaction")
        assert_not_contains(stdout_json, "MALFORMED_SESSION_SENTINEL", "malformed session redaction")
        log_sources = report["inputs"]["log_sources"]
        source_counts: dict[str, int] = {}
        for entry in log_sources:
            source_counts[entry["source"]] = source_counts.get(entry["source"], 0) + 1
        if source_counts.get("codex_recent", 0) > 20:
            raise AssertionError(f"log resolution: codex source cap not enforced\n{source_counts}")
        skipped_reasons = {entry["reason"] for entry in report["inputs"]["skipped_logs"]}
        for expected in ("archive_or_deep_not_requested", "source_file_cap", "total_log_cap"):
            if expected not in skipped_reasons:
                raise AssertionError(f"log resolution: missing skipped reason {expected!r}\n{report['inputs']['skipped_logs']}")
        if any(finding.get("action_candidates") for finding in report.get("display_findings", [])):
            raise AssertionError(f"log resolution: degraded log-scoped report must not have cleanup actions\n{report}")


def scenario_log_discovery_cap_degrades_without_cleanup_authority(repo_root: Path, wrapper: Path) -> None:
    with TemporaryDirectory(prefix="skill-cleaner-log-scan-cap-") as tmp_text:
        tmp = Path(tmp_text)
        node_bin = tmp / "bin"
        node_bin.mkdir()
        write_node_stub(node_bin)
        env = base_env(tmp, node_bin)
        env["SKILL_STATS_CLEANER_LOG_DISCOVERY_ENTRY_CAP"] = "5"

        sessions = Path(env["CODEX_HOME"]) / "sessions"
        for index in range(8):
            write_file(sessions / f"deep-{index}" / "nested" / "not-a-log.dat", "ignored\n")

        analyzer = write_identity_analyzer(tmp / "agent-scripts")
        root = Path(env["HOME"]) / "personal-skills"
        duplicate = write_skill(root, "duplicate-skill", "Duplicate skill.")
        kept = write_skill(root, "kept-skill", "Kept skill.")
        output = write_file(
            tmp / "analyzer-output.txt",
            "## Skill Budget\n"
            "- ok\n\n"
            "## Duplicates\n"
            f"- duplicate: {duplicate.parent} kept: {kept} confidence: high\n",
        )
        env["FIXTURE_NODE_STDOUT"] = str(output)
        report = run_report(repo_root, wrapper, ["--analyzer", str(analyzer), "--root", str(root)], env, "log scan cap")
        assert_mode(report, "degraded", "log scan cap")
        if report.get("truncated") is not True:
            raise AssertionError(f"log scan cap: expected truncated true\n{report}")
        skipped_reasons = {entry["reason"] for entry in report["inputs"]["skipped_logs"]}
        if "source_scan_cap" not in skipped_reasons:
            raise AssertionError(f"log scan cap: expected source_scan_cap\n{report['inputs']['skipped_logs']}")
        if any(finding.get("action_candidates") for finding in report.get("display_findings", [])):
            raise AssertionError(f"log scan cap: degraded capped log discovery must not have cleanup actions\n{report}")


def scenario_log_discovery_is_streaming(wrapper: Path) -> None:
    source = wrapper.read_text(encoding="utf-8")
    start = source.index("def capped_log_files(")
    end = source.index("def log_cap_reasons(", start)
    body = source[start:end]
    forbidden = (
        "sorted(os.scandir",
        "list(os.scandir",
        ".rglob(",
        "os.walk(",
    )
    for pattern in forbidden:
        if pattern in body:
            raise AssertionError(f"log discovery streaming: forbidden materializing traversal {pattern!r}")


def scenario_analyzer_path_shapes(repo_root: Path, wrapper: Path) -> None:
    with TemporaryDirectory(prefix="skill-cleaner-paths-") as tmp_text:
        tmp = Path(tmp_text)
        node_bin = tmp / "bin"
        node_bin.mkdir()
        write_node_stub(node_bin)
        env = base_env(tmp, node_bin)
        analyzer = write_identity_analyzer(tmp / "agent-scripts")
        output = write_file(tmp / "analyzer-output.txt", "## Skill Budget\n- ok\n")
        env["FIXTURE_NODE_STDOUT"] = str(output)
        candidates = [
            tmp / "agent-scripts",
            tmp / "agent-scripts" / "skills" / "skill-cleaner",
            analyzer,
        ]
        for candidate in candidates:
            report = run_report(
                repo_root,
                wrapper,
                ["--analyzer", str(candidate), "--no-logs"],
                env,
                f"analyzer path shape {candidate}",
            )
            assert_mode(report, "success", f"analyzer path shape {candidate}")


def scenario_malformed_output(repo_root: Path, wrapper: Path) -> None:
    with TemporaryDirectory(prefix="skill-cleaner-malformed-") as tmp_text:
        tmp = Path(tmp_text)
        node_bin = tmp / "bin"
        node_bin.mkdir()
        write_node_stub(node_bin)
        env = base_env(tmp, node_bin)
        analyzer = write_identity_analyzer(tmp / "agent-scripts")
        output = write_file(tmp / "analyzer-output.txt", "unheaded output with /private/local/path and no known sections\n")
        env["FIXTURE_NODE_STDOUT"] = str(output)
        report = run_report(repo_root, wrapper, ["--analyzer", str(analyzer), "--no-logs"], env, "malformed output")
        assert_mode(report, "degraded", "malformed output")
        section_names = [section.get("name") for section in report.get("sections", [])]
        if "Raw analyzer excerpt" not in section_names:
            raise AssertionError(f"malformed output: expected raw excerpt section\n{report}")
        if any(finding.get("action_candidates") for finding in report.get("display_findings", [])):
            raise AssertionError(f"malformed output: expected no cleanup authority\n{report}")


def scenario_truncated_output(repo_root: Path, wrapper: Path) -> None:
    with TemporaryDirectory(prefix="skill-cleaner-truncated-") as tmp_text:
        tmp = Path(tmp_text)
        node_bin = tmp / "bin"
        node_bin.mkdir()
        write_node_stub(node_bin)
        env = base_env(tmp, node_bin)
        env["FIXTURE_NODE_MODE"] = "huge"
        analyzer = write_identity_analyzer(tmp / "agent-scripts")
        report = run_report(repo_root, wrapper, ["--analyzer", str(analyzer), "--no-logs"], env, "truncated output")
        if report.get("truncated") is not True:
            raise AssertionError(f"truncated output: expected truncated true\n{report}")
        assert_mode(report, "degraded", "truncated output")
        if any(finding.get("action_candidates") for finding in report.get("display_findings", [])):
            raise AssertionError(f"truncated output: expected no cleanup action candidates\n{report}")


def scenario_degraded_output_has_no_cleanup_authority(repo_root: Path, wrapper: Path) -> None:
    with TemporaryDirectory(prefix="skill-cleaner-degraded-actions-") as tmp_text:
        tmp = Path(tmp_text)
        node_bin = tmp / "bin"
        node_bin.mkdir()
        write_node_stub(node_bin)
        env = base_env(tmp, node_bin)
        env["FIXTURE_NODE_MODE"] = "nonzero_with_sections"
        analyzer = write_identity_analyzer(tmp / "agent-scripts")
        root = Path(env["HOME"]) / "personal-skills"
        duplicate = write_skill(root, "duplicate-skill", "Duplicate skill.")
        kept = write_skill(root, "kept-skill", "Kept skill.")
        output = write_file(
            tmp / "analyzer-output.txt",
            "## Skill Budget\n"
            "- partial report\n\n"
            "## Duplicates\n"
            f"- duplicate: {duplicate.parent} kept: {kept} confidence: high\n",
        )
        env["FIXTURE_NODE_STDOUT"] = str(output)
        report = run_report(repo_root, wrapper, ["--analyzer", str(analyzer), "--root", str(root), "--no-logs"], env, "degraded sections")
        assert_mode(report, "degraded", "degraded sections")
        if any(finding.get("action_candidates") for finding in report.get("display_findings", [])):
            raise AssertionError(f"degraded sections: expected no cleanup action candidates\n{report}")
        evidence = json.loads(Path(report["outputs_written"][0]).read_text(encoding="utf-8"))
        if any(finding.get("action_candidates") for finding in evidence.get("findings", [])):
            raise AssertionError(f"degraded sections: expected evidence without cleanup authority\n{evidence}")


def scenario_missing_kept_copy_is_manual(repo_root: Path, wrapper: Path) -> None:
    with TemporaryDirectory(prefix="skill-cleaner-missing-kept-") as tmp_text:
        tmp = Path(tmp_text)
        node_bin = tmp / "bin"
        node_bin.mkdir()
        write_node_stub(node_bin)
        env = base_env(tmp, node_bin)
        analyzer = write_identity_analyzer(tmp / "agent-scripts")
        root = Path(env["HOME"]) / "personal-skills"
        duplicate = write_skill(root, "duplicate-skill", "Duplicate skill.")
        missing = root / "skills" / "missing-kept" / "SKILL.md"
        output = write_file(
            tmp / "analyzer-output.txt",
            "## Skill Budget\n"
            "- ok\n\n"
            "## Duplicates\n"
            f"- duplicate: {duplicate.parent} kept: {missing} confidence: high\n",
        )
        env["FIXTURE_NODE_STDOUT"] = str(output)
        report = run_report(repo_root, wrapper, ["--analyzer", str(analyzer), "--root", str(root), "--no-logs"], env, "missing kept")
        assert_mode(report, "success", "missing kept")
        findings = report.get("display_findings", [])
        if not findings or findings[0].get("manual_only") is not True:
            raise AssertionError(f"missing kept: expected manual-only finding\n{report}")
        if any(finding.get("action_candidates") for finding in findings):
            raise AssertionError(f"missing kept: expected no cleanup action candidates\n{report}")


def scenario_actions_are_section_scoped_and_kept_loaded(repo_root: Path, wrapper: Path) -> None:
    with TemporaryDirectory(prefix="skill-cleaner-section-scope-") as tmp_text:
        tmp = Path(tmp_text)
        node_bin = tmp / "bin"
        node_bin.mkdir()
        write_node_stub(node_bin)
        env = base_env(tmp, node_bin)
        analyzer = write_identity_analyzer(tmp / "agent-scripts")
        root = Path(env["HOME"]) / "personal-skills"
        duplicate = write_skill(root, "duplicate-skill", "Duplicate skill.")
        kept_outside = write_skill(tmp / "outside-skills", "kept-skill", "Kept skill.")
        output = write_file(
            tmp / "analyzer-output.txt",
            "## Skill Budget\n"
            f"- duplicate: {duplicate.parent} kept: {kept_outside} confidence: high\n"
            f"- description: {duplicate} old: Duplicate skill. new: Dup. confidence: high\n\n"
            "## Duplicates\n"
            f"- duplicate: {duplicate.parent} kept: {kept_outside} confidence: high\n",
        )
        env["FIXTURE_NODE_STDOUT"] = str(output)
        report = run_report(repo_root, wrapper, ["--analyzer", str(analyzer), "--root", str(root), "--no-logs"], env, "section scoped")
        assert_mode(report, "success", "section scoped")
        findings = report.get("display_findings", [])
        if not findings:
            raise AssertionError(f"section scoped: expected duplicate manual finding\n{report}")
        if any(finding.get("action_candidates") for finding in findings):
            raise AssertionError(f"section scoped: stray or unloaded-kept evidence produced action candidates\n{report}")


def scenario_description_target_must_be_loaded(repo_root: Path, wrapper: Path) -> None:
    with TemporaryDirectory(prefix="skill-cleaner-description-scope-") as tmp_text:
        tmp = Path(tmp_text)
        node_bin = tmp / "bin"
        node_bin.mkdir()
        write_node_stub(node_bin)
        env = base_env(tmp, node_bin)
        analyzer = write_identity_analyzer(tmp / "agent-scripts")
        root = Path(env["HOME"]) / "personal-skills"
        write_skill(root, "loaded-skill", "Loaded skill.")
        personal = write_skill(Path(env["HOME"]) / "not-a-default-root", "personal-skill", "Personal skill.")
        outside = write_skill(tmp / "outside-personal", "outside-skill", "Outside skill.")
        default_output = write_file(
            tmp / "default-analyzer-output.txt",
            "## Skill Budget\n"
            "- ok\n\n"
            "## Description candidates\n"
            f"- description: {personal} old: Personal skill. new: Personal. confidence: high\n",
        )
        env["FIXTURE_NODE_STDOUT"] = str(default_output)
        default_report = run_report(
            repo_root,
            wrapper,
            ["--analyzer", str(analyzer), "--no-logs"],
            env,
            "default personal description exclusion",
        )
        assert_mode(default_report, "success", "default personal description exclusion")
        if any(finding.get("action_candidates") for finding in default_report.get("display_findings", [])):
            raise AssertionError(f"default personal description exclusion: expected no action candidates\n{default_report}")

        output = write_file(
            tmp / "analyzer-output.txt",
            "## Skill Budget\n"
            "- ok\n\n"
            "## Description candidates\n"
            f"- description: {outside} old: Outside skill. new: Outside. confidence: high\n",
        )
        env["FIXTURE_NODE_STDOUT"] = str(output)
        report = run_report(
            repo_root,
            wrapper,
            ["--analyzer", str(analyzer), "--root", str(root), "--no-logs"],
            env,
            "description outside scan root",
        )
        assert_mode(report, "success", "description outside scan root")
        findings = report.get("display_findings", [])
        if not findings or findings[0].get("manual_only") is not True:
            raise AssertionError(f"description outside scan root: expected manual-only finding\n{report}")
        if any(finding.get("action_candidates") for finding in findings):
            raise AssertionError(f"description outside scan root: expected no action candidates\n{report}")


def scenario_unknown_heading_suppresses_cleanup_authority(repo_root: Path, wrapper: Path) -> None:
    with TemporaryDirectory(prefix="skill-cleaner-unknown-heading-") as tmp_text:
        tmp = Path(tmp_text)
        node_bin = tmp / "bin"
        node_bin.mkdir()
        write_node_stub(node_bin)
        env = base_env(tmp, node_bin)
        analyzer = write_identity_analyzer(tmp / "agent-scripts")
        root = Path(env["HOME"]) / "personal-skills"
        duplicate = write_skill(root, "duplicate-skill", "Duplicate skill.")
        kept = write_skill(root, "kept-skill", "Kept skill.")
        output = write_file(
            tmp / "analyzer-output.txt",
            "## Skill Budget\n"
            "- ok\n\n"
            "## Duplicates\n"
            f"- duplicate: {duplicate.parent} kept: {kept} confidence: high\n\n"
            f"## New Analyzer Section {Path(env['HOME'])}/private\n"
            "- UNKNOWN_SECTION_BODY_SHOULD_NOT_APPEAR\n"
            f"- duplicate: {duplicate.parent} kept: {kept} confidence: high\n",
        )
        env["FIXTURE_NODE_STDOUT"] = str(output)
        report = run_report(repo_root, wrapper, ["--analyzer", str(analyzer), "--root", str(root), "--no-logs"], env, "unknown heading")
        assert_mode(report, "degraded", "unknown heading")
        stdout_json = json.dumps(report, sort_keys=True)
        assert_not_contains(stdout_json, str(Path(env["HOME"])), "unknown heading redaction")
        assert_not_contains(stdout_json, "UNKNOWN_SECTION_BODY_SHOULD_NOT_APPEAR", "unknown heading section isolation")
        if any(finding.get("action_candidates") for finding in report.get("display_findings", [])):
            raise AssertionError(f"unknown heading: expected no cleanup action candidates\n{report}")


def canonical_hash(data: Any) -> str:
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, data: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def run_preflight(
    repo_root: Path,
    wrapper: Path,
    args: list[str],
    env: dict[str, str],
    scenario: str,
) -> dict[str, Any]:
    result = run_command(["python3", str(wrapper), "preflight-plan", *args], repo_root, env)
    return load_json_stdout(result, scenario)


def run_apply(
    repo_root: Path,
    wrapper: Path,
    args: list[str],
    env: dict[str, str],
    scenario: str,
) -> dict[str, Any]:
    result = run_command(["python3", str(wrapper), "apply", *args], repo_root, env)
    return load_json_stdout(result, scenario)


def scenario_report_produced_evidence_plan_apply(repo_root: Path, wrapper: Path) -> None:
    with TemporaryDirectory(prefix="skill-cleaner-report-plan-") as tmp_text:
        tmp = Path(tmp_text)
        node_bin = tmp / "bin"
        node_bin.mkdir()
        write_node_stub(node_bin)
        env = base_env(tmp, node_bin)

        analyzer = write_identity_analyzer(tmp / "agent-scripts")
        root = Path(env["HOME"]) / "personal-skills"
        target = write_skill(root, "edit-skill", "Kept skill.")
        output = write_file(
            tmp / "analyzer-output.txt",
            "## Skill Budget\n"
            "- ok\n\n"
            "## Description candidates\n"
            f"- description: {target} old: Kept skill. new: Kept. confidence: high\n\n"
            "## Duplicates\n"
            "- none\n\n"
            "## Unused candidates\n"
            "- none\n\n"
            "## Root summary\n"
            "- ok\n",
        )
        env["FIXTURE_NODE_STDOUT"] = str(output)
        report = run_report(
            repo_root,
            wrapper,
            ["--analyzer", str(analyzer), "--root", str(root), "--no-logs"],
            env,
            "report-produced evidence",
        )
        assert_mode(report, "success", "report-produced evidence")
        edit_action_id = ""
        for finding in report.get("display_findings", []):
            for candidate in finding.get("action_candidates", []):
                if candidate.get("action") == "edit_skill_description":
                    edit_action_id = candidate["action_id"]
        if not edit_action_id:
            raise AssertionError(f"report-produced evidence: missing edit action id\n{report}")

        plan = run_preflight(
            repo_root,
            wrapper,
            [
                "--evidence-bundle",
                report["outputs_written"][0],
                "--action-id",
                edit_action_id,
                "--root",
                str(root),
                "--plan-dir",
                str(tmp / "plans"),
            ],
            env,
            "report-produced plan",
        )
        if plan.get("status") != "success":
            raise AssertionError(f"report-produced plan: expected success\n{plan}")
        action = plan["display_plan"]["actions"][0]
        if action.get("old_description") != "Kept skill." or action.get("new_description") != "Kept.":
            raise AssertionError(f"report-produced plan: display plan omitted description payload\n{action}")

        applied = run_apply(
            repo_root,
            wrapper,
            [
                "--plan-bundle",
                plan["plan_bundle"]["path"],
                "--approved-plan-sha",
                plan["plan_id"],
                "--root",
                str(root),
            ],
            env,
            "report-produced apply",
        )
        if applied.get("status") != "success":
            raise AssertionError(f"report-produced apply: expected success\n{applied}")
        assert_contains(target.read_text(encoding="utf-8"), "description: Kept.", "report-produced apply")


def scenario_private_output_failures_are_typed(repo_root: Path, wrapper: Path) -> None:
    with TemporaryDirectory(prefix="skill-cleaner-output-failure-") as tmp_text:
        tmp = Path(tmp_text)
        node_bin = tmp / "bin"
        node_bin.mkdir()
        write_node_stub(node_bin)
        env = base_env(tmp, node_bin)

        analyzer = write_identity_analyzer(tmp / "agent-scripts")
        output = write_file(
            tmp / "analyzer-output.txt",
            "## Skill Budget\n"
            "- ok\n",
        )
        env["FIXTURE_NODE_STDOUT"] = str(output)
        env["TMPDIR"] = str(tmp / "missing-tmp")
        report = run_report(
            repo_root,
            wrapper,
            ["--analyzer", str(analyzer), "--no-logs"],
            env,
            "default tempdir failure",
        )
        assert_mode(report, "needs_user", "default tempdir failure")
        if report.get("outputs_written") != []:
            raise AssertionError(f"default tempdir failure: expected no outputs\n{report}")

        env["TMPDIR"] = str(tmp / "tmp")
        Path(env["TMPDIR"]).mkdir(exist_ok=True)
        bad_evidence_dir = write_file(tmp / "not-a-dir", "file\n")
        report = run_report(
            repo_root,
            wrapper,
            ["--analyzer", str(analyzer), "--no-logs", "--evidence-dir", str(bad_evidence_dir)],
            env,
            "explicit evidence dir failure",
        )
        assert_mode(report, "needs_user", "explicit evidence dir failure")


def failing_wrapper(wrapper: Path, tmp: Path, action: str) -> Path:
    replacements = {
        "delete_path": (
            "rollback.append((\"delete_path\", path, backup, None))\n"
            "                    shutil.rmtree(path)",
            "rollback.append((\"delete_path\", path, backup, None))\n"
            "                    shutil.rmtree(path)\n"
            "                    raise NeedsUser('forced post-mutation failure for delete_path')",
        ),
        "edit_skill_description": (
            "replace_description(path, action[\"old_description\"], action[\"new_description\"])",
            "replace_description(path, action[\"old_description\"], action[\"new_description\"])\n"
            "                raise NeedsUser('forced post-mutation failure for edit_skill_description')",
        ),
        "disable_json_config_entry": (
            "append_config_value(path, action[\"json_pointer\"], action[\"value\"])",
            "append_config_value(path, action[\"json_pointer\"], action[\"value\"])\n"
            "                raise NeedsUser('forced post-mutation failure for disable_json_config_entry')",
        ),
    }
    source = wrapper.read_text(encoding="utf-8")
    old, new = replacements[action]
    if old not in source:
        raise AssertionError(f"failing wrapper: injection point missing for {action}")
    path = tmp / f"skill_cleaner_wrapper_fail_{action}.py"
    path.write_text(source.replace(old, new, 1), encoding="utf-8")
    path.chmod(0o700)
    return path


def write_plan_evidence(root: Path, repo_root: Path, config: Path, manual_only: bool = False, expired: bool = False) -> Path:
    duplicate = root / "skills" / "duplicate-skill"
    kept_skill = write_skill(root, "kept-skill", "Kept skill.")
    edit_skill = write_skill(root, "edit-skill", "Old description.")
    write_skill(root, "untouched-skill", "Must stay untouched.")
    duplicate.mkdir(parents=True, exist_ok=True)
    (duplicate / "SKILL.md").write_text(
        "---\nname: duplicate-skill\ndescription: Duplicate skill.\n---\n\n# duplicate\n",
        encoding="utf-8",
    )
    config.write_text('{"disabledSkills": []}\n', encoding="utf-8")
    config_data = json.loads(config.read_text(encoding="utf-8"))
    evidence = {
        "report_id": "report:fixture-plan",
        "repo_root": str(repo_root),
        "wrapper_version": 1,
        "created_at": 1 if expired else int(os.path.getmtime(config)),
        "expires_at": 1 if expired else int(os.path.getmtime(config)) + 7200,
        "findings": [
            {
                "finding_id": "finding:disable:003",
                "finding_type": "config_disable_candidate",
                "source_section": "Duplicates",
                "source_excerpt": "disable duplicate skill",
                "evidence_order": 3,
                "confidence": "high",
                "manual_only": manual_only,
                "canonical_target_path": str(config),
                "display_target_path": str(config),
                "action_candidates": [
                    {
                        "action_id": "action:disable:003",
                        "action": "disable_json_config_entry",
                        "canonical_target_path": str(config),
                        "display_target_path": str(config),
                        "payload": {
                            "json_pointer": "/disabledSkills",
                            "value": "skill-stats:duplicate-skill",
                            "kept_copy": str(kept_skill),
                            "duplicate_target_path": str(duplicate),
                            "duplicate_skill_name": "duplicate-skill",
                            "prior_value_present": False,
                            "prior_list_values_hash": canonical_hash(config_data["disabledSkills"]),
                            "rollback_snapshot_hash": file_hash(config),
                        },
                        "required_authorization": "explicit_config",
                        "preconditions": ["json_pointer_list", "value_absent_before"],
                        "rollback": "restore JSON file from captured rollback snapshot",
                    }
                ],
            },
            {
                "finding_id": "finding:duplicate:001",
                "finding_type": "duplicate",
                "source_section": "Duplicates",
                "source_excerpt": "delete duplicate skill",
                "evidence_order": 1,
                "confidence": "high",
                "manual_only": manual_only,
                "canonical_target_path": str(duplicate),
                "display_target_path": str(duplicate),
                "action_candidates": [
                    {
                        "action_id": "action:delete:001",
                        "action": "delete_path",
                        "canonical_target_path": str(duplicate),
                        "display_target_path": str(duplicate),
                        "payload": {
                            "kept_copy": str(kept_skill),
                            "untracked_policy": "disposable_confirmed",
                            "disposable_rationale": "fixture target is a disposable temp skill",
                        },
                        "required_authorization": "mutation_root",
                        "preconditions": ["kept_copy_exists", "target_is_skill", "disposable_confirmed"],
                        "rollback": "restore from git or named backup",
                    }
                ],
            },
            {
                "finding_id": "finding:description:002",
                "finding_type": "description_candidate",
                "source_section": "Description candidates",
                "source_excerpt": "shorten description",
                "evidence_order": 2,
                "confidence": "high",
                "manual_only": manual_only,
                "canonical_target_path": str(edit_skill),
                "display_target_path": str(edit_skill),
                "action_candidates": [
                    {
                        "action_id": "action:description:002",
                        "action": "edit_skill_description",
                        "canonical_target_path": str(edit_skill),
                        "display_target_path": str(edit_skill),
                        "payload": {
                            "old_description": "Old description.",
                            "new_description": "Short description.",
                        },
                        "required_authorization": "mutation_root",
                        "preconditions": ["old_description_matches"],
                        "rollback": "restore old_description",
                    }
                ],
            },
        ],
    }
    path = root / "evidence" / "fixture-plan.json"
    write_json(path, evidence)
    path.chmod(0o600)
    return path


def assert_needs_user(report: dict[str, Any], scenario: str) -> None:
    if report.get("status") != "needs_user":
        raise AssertionError(f"{scenario}: expected needs_user\n{report}")


def scenario_preflight_and_apply_gate(repo_root: Path, wrapper: Path) -> None:
    with TemporaryDirectory(prefix="skill-cleaner-plan-") as tmp_text:
        tmp = Path(tmp_text)
        env = os.environ.copy()
        env["HOME"] = str(tmp / "home")
        Path(env["HOME"]).mkdir(parents=True, exist_ok=True)
        root = Path(env["HOME"]) / "personal-skills"
        config = tmp / "settings.json"
        evidence = write_plan_evidence(root, repo_root, config)
        duplicate_dir = root / "skills" / "duplicate-skill"
        edit_skill = root / "skills" / "edit-skill" / "SKILL.md"
        untouched = root / "skills" / "untouched-skill" / "SKILL.md"
        before = {
            edit_skill: edit_skill.read_text(encoding="utf-8"),
            untouched: untouched.read_text(encoding="utf-8"),
            config: config.read_text(encoding="utf-8"),
        }

        selected = [
            "--action-id",
            "action:disable:003",
            "--action-id",
            "action:description:002",
            "--action-id",
            "action:delete:001",
        ]
        common = [
            "--evidence-bundle",
            str(evidence),
            "--root",
            str(root),
            "--config",
            str(config),
            "--plan-dir",
            str(tmp / "plans"),
        ]
        plan = run_preflight(repo_root, wrapper, [*common, *selected], env, "preflight plan")
        if plan.get("status") != "success" or plan.get("mode") != "skill-cleaner-plan":
            raise AssertionError(f"preflight plan: expected success skill-cleaner-plan\n{plan}")
        actions = plan["display_plan"]["actions"]
        if [action["id"] for action in actions] != ["A001", "A002", "A003"]:
            raise AssertionError(f"preflight plan: unstable action ids\n{actions}")
        actions_by_name = {action["action"]: action for action in actions}
        delete_row = actions_by_name["delete_path"]
        if not delete_row.get("kept_copy") or delete_row.get("untracked_policy") != "disposable_confirmed":
            raise AssertionError(f"preflight plan: delete display payload incomplete\n{delete_row}")
        if delete_row.get("disposable_rationale") != "fixture target is a disposable temp skill":
            raise AssertionError(f"preflight plan: delete disposable rationale missing\n{delete_row}")
        edit_row = actions_by_name["edit_skill_description"]
        if edit_row.get("old_description") != "Old description." or edit_row.get("new_description") != "Short description.":
            raise AssertionError(f"preflight plan: description display payload incomplete\n{edit_row}")
        config_row = actions_by_name["disable_json_config_entry"]
        if config_row.get("json_pointer") != "/disabledSkills" or config_row.get("value") != "skill-stats:duplicate-skill":
            raise AssertionError(f"preflight plan: config display payload incomplete\n{config_row}")
        if not config_row.get("duplicate_target") or config_row.get("duplicate_skill_name") != "duplicate-skill" or not config_row.get("kept_copy"):
            raise AssertionError(f"preflight plan: config duplicate proof omitted\n{config_row}")
        plan_bundle = Path(plan["plan_bundle"]["path"])
        if not plan_bundle.exists():
            raise AssertionError(f"preflight plan: missing plan bundle {plan_bundle}")
        if stat.S_IMODE(plan_bundle.stat().st_mode) != 0o600:
            raise AssertionError("preflight plan: plan bundle mode is not 0600")

        reversed_plan = run_preflight(
            repo_root,
            wrapper,
            [
                *common,
                "--action-id",
                "action:delete:001",
                "--action-id",
                "action:description:002",
                "--action-id",
                "action:disable:003",
            ],
            env,
            "preflight reversed",
        )
        if reversed_plan.get("plan_id") != plan.get("plan_id"):
            raise AssertionError(f"preflight reversed: expected stable plan_id\n{plan}\n{reversed_plan}")

        no_hash = run_apply(repo_root, wrapper, ["--plan-bundle", str(plan_bundle), "--root", str(root), "--config", str(config)], env, "apply no hash")
        assert_needs_user(no_hash, "apply no hash")
        wrong_hash = run_apply(
            repo_root,
            wrapper,
            [
                "--plan-bundle",
                str(plan_bundle),
                "--approved-plan-sha",
                "sha256:" + "0" * 64,
                "--root",
                str(root),
                "--config",
                str(config),
            ],
            env,
            "apply wrong hash",
        )
        assert_needs_user(wrong_hash, "apply wrong hash")
        assert duplicate_dir.exists(), "apply wrong hash: duplicate should remain"
        assert_no_target_mutation([edit_skill, untouched, config], before, "apply wrong hash")

        applied = run_apply(
            repo_root,
            wrapper,
            [
                "--plan-bundle",
                str(plan_bundle),
                "--approved-plan-sha",
                plan["plan_id"],
                "--root",
                str(root),
                "--config",
                str(config),
            ],
            env,
            "apply approved",
        )
        if applied.get("status") != "success" or applied.get("mode") != "skill-cleaner-apply":
            raise AssertionError(f"apply approved: expected success\n{applied}")
        if duplicate_dir.exists():
            raise AssertionError("apply approved: duplicate directory still exists")
        assert_contains(edit_skill.read_text(encoding="utf-8"), "description: Short description.", "apply approved")
        disabled = json.loads(config.read_text(encoding="utf-8"))["disabledSkills"]
        if disabled != ["skill-stats:duplicate-skill"]:
            raise AssertionError(f"apply approved: config value not appended once\n{disabled}")
        if untouched.read_text(encoding="utf-8") != before[untouched]:
            raise AssertionError("apply approved: unapproved file changed")
        if plan_bundle.exists():
            raise AssertionError("apply approved: plan bundle should be deleted after success")


def scenario_overlapping_config_delete_refused(repo_root: Path, wrapper: Path) -> None:
    with TemporaryDirectory(prefix="skill-cleaner-overlap-") as tmp_text:
        tmp = Path(tmp_text)
        env = os.environ.copy()
        env["HOME"] = str(tmp / "home")
        Path(env["HOME"]).mkdir(parents=True, exist_ok=True)
        root = Path(env["HOME"]) / "personal-skills"
        config = tmp / "settings.json"
        evidence = write_plan_evidence(root, repo_root, config)
        duplicate_dir = root / "skills" / "duplicate-skill"
        overlapping_config = write_json(duplicate_dir / "settings.json", {"disabledSkills": []})
        evidence_data = json.loads(evidence.read_text(encoding="utf-8"))
        config_finding = evidence_data["findings"][0]
        config_finding["canonical_target_path"] = str(overlapping_config)
        config_finding["display_target_path"] = str(overlapping_config)
        config_action = config_finding["action_candidates"][0]
        config_action["canonical_target_path"] = str(overlapping_config)
        config_action["display_target_path"] = str(overlapping_config)
        config_action["payload"]["prior_list_values_hash"] = canonical_hash([])
        config_action["payload"]["rollback_snapshot_hash"] = file_hash(overlapping_config)
        overlap_evidence = root / "evidence" / "overlap.json"
        write_json(overlap_evidence, evidence_data)
        overlap_evidence.chmod(0o600)

        plan = run_preflight(
            repo_root,
            wrapper,
            [
                "--evidence-bundle",
                str(overlap_evidence),
                "--action-id",
                "action:delete:001",
                "--action-id",
                "action:disable:003",
                "--root",
                str(root),
                "--config",
                str(overlapping_config),
            ],
            env,
            "overlapping config delete",
        )
        assert_needs_user(plan, "overlapping config delete")
        if not duplicate_dir.exists() or not overlapping_config.exists():
            raise AssertionError("overlapping config delete: preflight mutated targets")


def scenario_plan_evidence_provenance_and_rollback(repo_root: Path, wrapper: Path) -> None:
    with TemporaryDirectory(prefix="skill-cleaner-provenance-") as tmp_text:
        tmp = Path(tmp_text)
        env = os.environ.copy()
        env["HOME"] = str(tmp / "home")
        Path(env["HOME"]).mkdir(parents=True, exist_ok=True)
        root = Path(env["HOME"]) / "personal-skills"
        config = tmp / "settings.json"
        evidence = write_plan_evidence(root, repo_root, config)
        edit_skill = root / "skills" / "edit-skill" / "SKILL.md"
        before_edit = edit_skill.read_text(encoding="utf-8")

        plan = run_preflight(
            repo_root,
            wrapper,
            [
                "--evidence-bundle",
                str(evidence),
                "--action-id",
                "action:description:002",
                "--root",
                str(root),
                "--config",
                str(config),
                "--plan-dir",
                str(tmp / "plans"),
            ],
            env,
            "provenance plan",
        )
        if plan.get("status") != "success":
            raise AssertionError(f"provenance plan: expected success\n{plan}")
        plan_bundle = Path(plan["plan_bundle"]["path"])
        bundle = json.loads(plan_bundle.read_text(encoding="utf-8"))
        bundle["evidence_digest"] = "sha256:" + "1" * 64
        write_json(plan_bundle, bundle)
        tampered = run_apply(
            repo_root,
            wrapper,
            [
                "--plan-bundle",
                str(plan_bundle),
                "--approved-plan-sha",
                plan["plan_id"],
                "--root",
                str(root),
                "--config",
                str(config),
            ],
            env,
            "tampered evidence digest",
        )
        assert_needs_user(tampered, "tampered evidence digest")
        if edit_skill.read_text(encoding="utf-8") != before_edit:
            raise AssertionError("tampered evidence digest: target mutated")

        plan = run_preflight(
            repo_root,
            wrapper,
            [
                "--evidence-bundle",
                str(evidence),
                "--action-id",
                "action:description:002",
                "--root",
                str(root),
                "--config",
                str(config),
                "--plan-dir",
                str(tmp / "plans"),
            ],
            env,
            "forged canonical plan source",
        )
        plan_bundle = Path(plan["plan_bundle"]["path"])
        forged = json.loads(plan_bundle.read_text(encoding="utf-8"))
        forged["canonical_plan"]["actions"][0]["new_description"] = "Forged description."
        forged["plan_id"] = canonical_hash(forged["canonical_plan"])
        write_json(plan_bundle, forged)
        forged_result = run_apply(
            repo_root,
            wrapper,
            [
                "--plan-bundle",
                str(plan_bundle),
                "--approved-plan-sha",
                forged["plan_id"],
                "--root",
                str(root),
                "--config",
                str(config),
            ],
            env,
            "forged canonical plan",
        )
        assert_needs_user(forged_result, "forged canonical plan")
        if edit_skill.read_text(encoding="utf-8") != before_edit:
            raise AssertionError("forged canonical plan: target mutated")

        rollback_cases = (
            ("action:delete:001", "delete_path"),
            ("action:description:002", "edit_skill_description"),
            ("action:disable:003", "disable_json_config_entry"),
        )
        for action_id, action_name in rollback_cases:
            case_root = Path(env["HOME"]) / f"personal-skills-{action_name}"
            case_config = tmp / f"settings-{action_name}.json"
            case_evidence = write_plan_evidence(case_root, repo_root, case_config)
            duplicate_dir = case_root / "skills" / "duplicate-skill"
            edit_target = case_root / "skills" / "edit-skill" / "SKILL.md"
            before_delete = (duplicate_dir / "SKILL.md").read_text(encoding="utf-8")
            before_description = edit_target.read_text(encoding="utf-8")
            before_config = case_config.read_text(encoding="utf-8")
            link_path = duplicate_dir / "outside-link.txt"
            link_target = ""
            if action_name == "delete_path":
                outside = write_file(tmp / "outside-link-target.txt", "outside data\n")
                link_path.symlink_to(outside)
                link_target = os.readlink(link_path)
            plan = run_preflight(
                repo_root,
                wrapper,
                [
                    "--evidence-bundle",
                    str(case_evidence),
                    "--action-id",
                    action_id,
                    "--root",
                    str(case_root),
                    "--config",
                    str(case_config),
                    "--plan-dir",
                    str(tmp / "plans"),
                ],
                env,
                f"rollback plan {action_name}",
            )
            failed = run_apply(
                repo_root,
                failing_wrapper(wrapper, tmp, action_name),
                [
                    "--plan-bundle",
                    str(plan["plan_bundle"]["path"]),
                    "--approved-plan-sha",
                    plan["plan_id"],
                    "--root",
                    str(case_root),
                    "--config",
                    str(case_config),
                ],
                env,
                f"forced rollback {action_name}",
            )
            assert_needs_user(failed, f"forced rollback {action_name}")
            if not duplicate_dir.exists() or (duplicate_dir / "SKILL.md").read_text(encoding="utf-8") != before_delete:
                raise AssertionError(f"forced rollback {action_name}: duplicate skill was not restored")
            if action_name == "delete_path" and (not link_path.is_symlink() or os.readlink(link_path) != link_target):
                raise AssertionError(f"forced rollback {action_name}: symlink was not preserved")
            if edit_target.read_text(encoding="utf-8") != before_description:
                raise AssertionError(f"forced rollback {action_name}: description was not restored")
            if case_config.read_text(encoding="utf-8") != before_config:
                raise AssertionError(f"forced rollback {action_name}: config was not restored")


def scenario_malformed_bundles_return_typed_json(repo_root: Path, wrapper: Path) -> None:
    with TemporaryDirectory(prefix="skill-cleaner-malformed-bundles-") as tmp_text:
        tmp = Path(tmp_text)
        env = os.environ.copy()
        env["HOME"] = str(tmp / "home")
        Path(env["HOME"]).mkdir(parents=True, exist_ok=True)
        root = Path(env["HOME"]) / "personal-skills"
        config = tmp / "settings.json"
        evidence = write_plan_evidence(root, repo_root, config)
        evidence_data = json.loads(evidence.read_text(encoding="utf-8"))
        evidence_data["expires_at"] = "not-an-int"
        malformed_evidence = root / "evidence" / "malformed.json"
        write_json(malformed_evidence, evidence_data)
        malformed_evidence.chmod(0o600)
        plan = run_preflight(
            repo_root,
            wrapper,
            ["--evidence-bundle", str(malformed_evidence), "--action-id", "action:delete:001", "--root", str(root)],
            env,
            "malformed evidence metadata",
        )
        assert_needs_user(plan, "malformed evidence metadata")

        for field in ("repo_root", "wrapper_version", "expires_at"):
            field_data = json.loads(evidence.read_text(encoding="utf-8"))
            field_data.pop(field, None)
            missing_field_evidence = root / "evidence" / f"missing-{field}.json"
            write_json(missing_field_evidence, field_data)
            missing_field_evidence.chmod(0o600)
            field_plan = run_preflight(
                repo_root,
                wrapper,
                [
                    "--evidence-bundle",
                    str(missing_field_evidence),
                    "--action-id",
                    "action:description:002",
                    "--root",
                    str(root),
                    "--config",
                    str(config),
                ],
                env,
                f"missing evidence {field}",
            )
            assert_needs_user(field_plan, f"missing evidence {field}")

        wrong_repo_data = json.loads(evidence.read_text(encoding="utf-8"))
        wrong_repo_data["repo_root"] = str(tmp / "other-repo")
        wrong_repo_evidence = root / "evidence" / "wrong-repo.json"
        write_json(wrong_repo_evidence, wrong_repo_data)
        wrong_repo_evidence.chmod(0o600)
        wrong_repo_plan = run_preflight(
            repo_root,
            wrapper,
            ["--evidence-bundle", str(wrong_repo_evidence), "--action-id", "action:description:002", "--root", str(root), "--config", str(config)],
            env,
            "wrong repo evidence",
        )
        assert_needs_user(wrong_repo_plan, "wrong repo evidence")

        wrong_version_data = json.loads(evidence.read_text(encoding="utf-8"))
        wrong_version_data["wrapper_version"] = 2
        wrong_version_evidence = root / "evidence" / "wrong-version.json"
        write_json(wrong_version_evidence, wrong_version_data)
        wrong_version_evidence.chmod(0o600)
        wrong_version_plan = run_preflight(
            repo_root,
            wrapper,
            ["--evidence-bundle", str(wrong_version_evidence), "--action-id", "action:description:002", "--root", str(root), "--config", str(config)],
            env,
            "wrong version evidence",
        )
        assert_needs_user(wrong_version_plan, "wrong version evidence")

        good_plan = run_preflight(
            repo_root,
            wrapper,
            ["--evidence-bundle", str(evidence), "--action-id", "action:description:002", "--root", str(root), "--config", str(config)],
            env,
            "malformed plan source",
        )
        plan_bundle = Path(good_plan["plan_bundle"]["path"])
        bundle = json.loads(plan_bundle.read_text(encoding="utf-8"))
        bundle["created_at"] = "not-an-int"
        write_json(plan_bundle, bundle)
        applied = run_apply(
            repo_root,
            wrapper,
            [
                "--plan-bundle",
                str(plan_bundle),
                "--approved-plan-sha",
                good_plan["plan_id"],
                "--root",
                str(root),
                "--config",
                str(config),
            ],
            env,
            "malformed plan metadata",
        )
        assert_needs_user(applied, "malformed plan metadata")

        bad_plan_dir = write_file(tmp / "not-a-plan-dir", "file\n")
        bad_plan = run_preflight(
            repo_root,
            wrapper,
            [
                "--evidence-bundle",
                str(evidence),
                "--action-id",
                "action:description:002",
                "--root",
                str(root),
                "--config",
                str(config),
                "--plan-dir",
                str(bad_plan_dir),
            ],
            env,
            "explicit plan dir failure",
        )
        assert_needs_user(bad_plan, "explicit plan dir failure")


def scenario_atomic_writes_preserve_mode_and_config_order(repo_root: Path, wrapper: Path) -> None:
    with TemporaryDirectory(prefix="skill-cleaner-mode-order-") as tmp_text:
        tmp = Path(tmp_text)
        env = os.environ.copy()
        env["HOME"] = str(tmp / "home")
        Path(env["HOME"]).mkdir(parents=True, exist_ok=True)
        root = Path(env["HOME"]) / "personal-skills"
        config = tmp / "settings.json"
        evidence = write_plan_evidence(root, repo_root, config)
        edit_skill = root / "skills" / "edit-skill" / "SKILL.md"
        edit_skill.chmod(0o640)
        config.write_text('{"z": 1, "disabledSkills": [], "a": 2}\n', encoding="utf-8")
        config.chmod(0o640)
        evidence_data = json.loads(evidence.read_text(encoding="utf-8"))
        config_payload = evidence_data["findings"][0]["action_candidates"][0]["payload"]
        config_payload["prior_list_values_hash"] = canonical_hash([])
        config_payload["rollback_snapshot_hash"] = file_hash(config)
        updated_evidence = root / "evidence" / "mode-order.json"
        write_json(updated_evidence, evidence_data)
        updated_evidence.chmod(0o600)

        plan = run_preflight(
            repo_root,
            wrapper,
            [
                "--evidence-bundle",
                str(updated_evidence),
                "--action-id",
                "action:description:002",
                "--action-id",
                "action:disable:003",
                "--root",
                str(root),
                "--config",
                str(config),
                "--plan-dir",
                str(tmp / "plans"),
            ],
            env,
            "mode and config order plan",
        )
        if plan.get("status") != "success":
            raise AssertionError(f"mode and config order plan: expected success\n{plan}")
        applied = run_apply(
            repo_root,
            wrapper,
            [
                "--plan-bundle",
                plan["plan_bundle"]["path"],
                "--approved-plan-sha",
                plan["plan_id"],
                "--root",
                str(root),
                "--config",
                str(config),
            ],
            env,
            "mode and config order apply",
        )
        if applied.get("status") != "success":
            raise AssertionError(f"mode and config order apply: expected success\n{applied}")
        if stat.S_IMODE(edit_skill.stat().st_mode) != 0o640:
            raise AssertionError("mode and config order apply: description edit did not preserve mode")
        if stat.S_IMODE(config.stat().st_mode) != 0o640:
            raise AssertionError("mode and config order apply: config edit did not preserve mode")
        config_keys = list(json.loads(config.read_text(encoding="utf-8")).keys())
        if config_keys != ["z", "disabledSkills", "a"]:
            raise AssertionError(f"mode and config order apply: config key order changed\n{config.read_text(encoding='utf-8')}")
        config_text = config.read_text(encoding="utf-8")
        assert_contains(config_text, '{"z": 1, "disabledSkills": ["skill-stats:duplicate-skill"], "a": 2}', "mode and config order apply")


def scenario_yaml_scalar_description_is_refused(repo_root: Path, wrapper: Path) -> None:
    with TemporaryDirectory(prefix="skill-cleaner-yaml-scalar-") as tmp_text:
        tmp = Path(tmp_text)
        node_bin = tmp / "bin"
        node_bin.mkdir()
        write_node_stub(node_bin)
        env = base_env(tmp, node_bin)

        analyzer = write_identity_analyzer(tmp / "agent-scripts")
        report_root = Path(env["HOME"]) / "unsafe-report"
        target = write_skill(report_root, "edit-skill", "Old description.")
        output = write_file(
            tmp / "analyzer-output.txt",
            "## Skill Budget\n"
            "- ok\n\n"
            "## Description candidates\n"
            f"- description: {target} old: Old description. new: bad: value confidence: high\n",
        )
        env["FIXTURE_NODE_STDOUT"] = str(output)
        report = run_report(
            repo_root,
            wrapper,
            ["--analyzer", str(analyzer), "--root", str(report_root), "--no-logs"],
            env,
            "unsafe yaml report",
        )
        assert_mode(report, "success", "unsafe yaml report")
        if any(candidate.get("action") == "edit_skill_description" for finding in report.get("display_findings", []) for candidate in finding.get("action_candidates", [])):
            raise AssertionError(f"unsafe yaml report: expected no description action candidate\n{report}")

        plan_root = Path(env["HOME"]) / "unsafe-plan"
        config = tmp / "settings.json"
        evidence = write_plan_evidence(plan_root, repo_root, config)
        edit_skill = plan_root / "skills" / "edit-skill" / "SKILL.md"
        before = edit_skill.read_text(encoding="utf-8")
        evidence_data = json.loads(evidence.read_text(encoding="utf-8"))
        evidence_data["findings"][2]["action_candidates"][0]["payload"]["new_description"] = "bad: value"
        unsafe_evidence = plan_root / "evidence" / "unsafe-description.json"
        write_json(unsafe_evidence, evidence_data)
        unsafe_evidence.chmod(0o600)
        plan = run_preflight(
            repo_root,
            wrapper,
            [
                "--evidence-bundle",
                str(unsafe_evidence),
                "--action-id",
                "action:description:002",
                "--root",
                str(plan_root),
                "--config",
                str(config),
            ],
            env,
            "unsafe yaml plan",
        )
        assert_needs_user(plan, "unsafe yaml plan")
        if edit_skill.read_text(encoding="utf-8") != before:
            raise AssertionError("unsafe yaml plan: target mutated")


def scenario_broad_roots_and_tracked_only_refused(repo_root: Path, wrapper: Path) -> None:
    with TemporaryDirectory(prefix="skill-cleaner-root-refuse-") as tmp_text:
        tmp = Path(tmp_text)
        env = os.environ.copy()
        env["HOME"] = str(tmp / "home")
        home = Path(env["HOME"])
        home.mkdir(parents=True, exist_ok=True)
        root = home / "personal-skills"
        config = tmp / "settings.json"
        evidence = write_plan_evidence(root, repo_root, config)

        for broad_root, scenario in ((Path("/"), "root slash"), (home, "root home"), (repo_root, "root repo")):
            plan = run_preflight(
                repo_root,
                wrapper,
                [
                    "--evidence-bundle",
                    str(evidence),
                    "--action-id",
                    "action:delete:001",
                    "--root",
                    str(broad_root),
                ],
                env,
                scenario,
            )
            assert_needs_user(plan, scenario)

        evidence_data = json.loads(evidence.read_text(encoding="utf-8"))
        delete_payload = evidence_data["findings"][1]["action_candidates"][0]["payload"]
        delete_payload["untracked_policy"] = "tracked_only"
        delete_payload.pop("disposable_rationale", None)
        tracked_only_evidence = root / "evidence" / "tracked-only.json"
        write_json(tracked_only_evidence, evidence_data)
        tracked_only_evidence.chmod(0o600)

        tracked_only_plan = run_preflight(
            repo_root,
            wrapper,
            [
                "--evidence-bundle",
                str(tracked_only_evidence),
                "--action-id",
                "action:delete:001",
                "--root",
                str(root),
            ],
            env,
            "tracked-only untracked",
        )
        assert_needs_user(tracked_only_plan, "tracked-only untracked")


def scenario_config_drift_refused(repo_root: Path, wrapper: Path) -> None:
    with TemporaryDirectory(prefix="skill-cleaner-drift-") as tmp_text:
        tmp = Path(tmp_text)
        env = os.environ.copy()
        env["HOME"] = str(tmp / "home")
        Path(env["HOME"]).mkdir(parents=True, exist_ok=True)
        root = Path(env["HOME"]) / "personal-skills"
        config = tmp / "settings.json"
        evidence = write_plan_evidence(root, repo_root, config)
        write_json(config, {"disabledSkills": ["skill-stats:duplicate-skill"]})
        before = config.read_text(encoding="utf-8")
        plan = run_preflight(
            repo_root,
            wrapper,
            [
                "--evidence-bundle",
                str(evidence),
                "--action-id",
                "action:disable:003",
                "--root",
                str(root),
                "--config",
                str(config),
            ],
            env,
            "config drift",
        )
        assert_needs_user(plan, "config drift")
        if config.read_text(encoding="utf-8") != before:
            raise AssertionError("config drift: config mutated")


def scenario_manual_and_expired_evidence_refused(repo_root: Path, wrapper: Path) -> None:
    with TemporaryDirectory(prefix="skill-cleaner-refuse-") as tmp_text:
        tmp = Path(tmp_text)
        env = os.environ.copy()
        env["HOME"] = str(tmp / "home")
        Path(env["HOME"]).mkdir(parents=True, exist_ok=True)
        root = Path(env["HOME"]) / "personal-skills"
        manual_config = tmp / "manual-settings.json"
        manual = write_plan_evidence(root, repo_root, manual_config, manual_only=True)
        manual_plan = run_preflight(
            repo_root,
            wrapper,
            ["--evidence-bundle", str(manual), "--action-id", "action:delete:001", "--root", str(root)],
            env,
            "manual finding",
        )
        assert_needs_user(manual_plan, "manual finding")

        expired_config = tmp / "expired-settings.json"
        expired = write_plan_evidence(root, repo_root, expired_config, expired=True)
        expired_plan = run_preflight(
            repo_root,
            wrapper,
            ["--evidence-bundle", str(expired), "--action-id", "action:delete:001", "--root", str(root)],
            env,
            "expired evidence",
        )
        assert_needs_user(expired_plan, "expired evidence")


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        usage()
        return 2

    repo_root = Path(argv[0]).resolve()
    wrapper = repo_root / "skill-stats" / "scripts" / "skill_cleaner_wrapper.py"
    if not wrapper.exists():
        raise AssertionError(f"missing skill cleaner wrapper: {wrapper}")

    scenario_missing_analyzer(repo_root, wrapper)
    scenario_invalid_analyzer_identity(repo_root, wrapper)
    scenario_success_report(repo_root, wrapper)
    scenario_log_resolution_degrades_without_cleanup_authority(repo_root, wrapper)
    scenario_log_discovery_cap_degrades_without_cleanup_authority(repo_root, wrapper)
    scenario_log_discovery_is_streaming(wrapper)
    scenario_analyzer_path_shapes(repo_root, wrapper)
    scenario_malformed_output(repo_root, wrapper)
    scenario_truncated_output(repo_root, wrapper)
    scenario_degraded_output_has_no_cleanup_authority(repo_root, wrapper)
    scenario_missing_kept_copy_is_manual(repo_root, wrapper)
    scenario_actions_are_section_scoped_and_kept_loaded(repo_root, wrapper)
    scenario_description_target_must_be_loaded(repo_root, wrapper)
    scenario_unknown_heading_suppresses_cleanup_authority(repo_root, wrapper)
    scenario_report_produced_evidence_plan_apply(repo_root, wrapper)
    scenario_private_output_failures_are_typed(repo_root, wrapper)
    scenario_preflight_and_apply_gate(repo_root, wrapper)
    scenario_overlapping_config_delete_refused(repo_root, wrapper)
    scenario_plan_evidence_provenance_and_rollback(repo_root, wrapper)
    scenario_malformed_bundles_return_typed_json(repo_root, wrapper)
    scenario_atomic_writes_preserve_mode_and_config_order(repo_root, wrapper)
    scenario_yaml_scalar_description_is_refused(repo_root, wrapper)
    scenario_broad_roots_and_tracked_only_refused(repo_root, wrapper)
    scenario_config_drift_refused(repo_root, wrapper)
    scenario_manual_and_expired_evidence_refused(repo_root, wrapper)
    print("skill-stats cleaner fixtures passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
