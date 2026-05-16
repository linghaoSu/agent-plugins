#!/usr/bin/env bash
set -u

MODE="staged"
STRICT="false"
JSON_OUTPUT="false"
BLOCKING_FAILURE=0
USAGE_FAILURE=0

usage() {
  cat <<'USAGE'
Usage: scripts/release-gate.sh [--mode staged|working|all] [--strict] [--json]

Runs the repo-wide plugin release gate. Default mode is staged.
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --mode)
      shift
      if [ "$#" -eq 0 ]; then
        usage >&2
        exit 2
      fi
      MODE="$1"
      ;;
    --mode=*)
      MODE="${1#--mode=}"
      ;;
    --strict)
      STRICT="true"
      ;;
    --json)
      JSON_OUTPUT="true"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage >&2
      exit 2
      ;;
  esac
  shift
done

case "$MODE" in
  staged|working|all)
    ;;
  *)
    printf 'Invalid --mode: %s\n' "$MODE" >&2
    usage >&2
    exit 2
    ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RESULTS_FILE="$(mktemp "${TMPDIR:-/tmp}/release-gate-results.XXXXXX")"
SKILL_HYGIENE_INFRA_TARGETS=(
  "scripts/skill-hygiene-check.py"
  "scripts/release-gate.sh"
  "tests/skill-hygiene-*"
  "RELEASE-GATE.md"
)
trap 'rm -f "$RESULTS_FILE"' EXIT

cd "$ROOT" || exit 2

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'Missing required command: %s\n' "$1" >&2
    exit 2
  fi
}

status_label() {
  case "$1" in
    pass) printf 'PASS' ;;
    fail) printf 'FAIL' ;;
    warn) printf 'WARN' ;;
    skip) printf 'SKIP' ;;
    *) printf '%s' "$1" ;;
  esac
}

join_output() {
  printf '%s' "$1" | tr '\n' ' ' | cut -c 1-240
}

join_finding_output() {
  printf '%s' "$1" | sed '/^[[:space:]]*$/d' | paste -sd'|' -
}

add_result() {
  category="$1"
  status="$2"
  id="$3"
  message="$4"
  evidence="${5:-}"
  command_text="${6:-}"
  exit_code="${7:-0}"

  if [ "$STRICT" = "true" ] && [ "$category" = "advisory" ] && [ "$status" = "warn" ]; then
    status="fail"
    message="$message (strict mode)"
    BLOCKING_FAILURE=1
  fi

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$category" "$status" "$id" "$message" "$evidence" "$command_text" "$exit_code" \
    >>"$RESULTS_FILE"

  if [ "$category" = "blocking" ] && [ "$status" = "fail" ]; then
    BLOCKING_FAILURE=1
  fi
}

mark_usage_failure() {
  USAGE_FAILURE=1
  BLOCKING_FAILURE=1
}

list_plugin_manifests() {
  if [ "$MODE" = "staged" ]; then
    git ls-files -- '*/.claude-plugin/plugin.json'
  else
    find . -path './.git' -prune -o -path './*/.claude-plugin/plugin.json' -type f -print |
      sort |
      sed 's#^\./##'
  fi
}

list_skill_files() {
  if [ "$MODE" = "staged" ]; then
    git ls-files -- '*/skills/*/SKILL.md'
  else
    find . -path './.git' -prune -o -path './*/skills/*/SKILL.md' -type f -print |
      sort |
      sed 's#^\./##'
  fi
}

list_skill_metadata_files() {
  if [ "$MODE" = "staged" ]; then
    git ls-files -- '*/skills/*/agents/openai.yaml'
  else
    find . -path './.git' -prune -o -path './*/skills/*/agents/openai.yaml' -type f -print |
      sort |
      sed 's#^\./##'
  fi
}

index_has_file() {
  git cat-file -e ":$1" 2>/dev/null
}

require_cmd git
require_cmd jq
require_cmd python3

require_python_module() {
  module="$1"
  label="$2"
  if ! python3 - "$module" <<'PY' >/dev/null 2>&1
import importlib
import sys

importlib.import_module(sys.argv[1])
PY
  then
    printf 'Missing required Python module: %s\n' "$label" >&2
    exit 2
  fi
}

require_python_module yaml PyYAML

validate_manifest_file() {
  file="$1"
  err_file="$(mktemp "${TMPDIR:-/tmp}/release-gate-jq.XXXXXX")"

  if [ "$MODE" = "staged" ]; then
    content_file="$(mktemp "${TMPDIR:-/tmp}/release-gate-json.XXXXXX")"
    if ! git show ":$file" >"$content_file" 2>"$err_file"; then
      printf 'missing from index: %s' "$(join_output "$(cat "$err_file")")"
      rm -f "$content_file" "$err_file"
      return 1
    fi
    if ! jq empty "$content_file" >/dev/null 2>"$err_file"; then
      printf '%s' "$(join_output "$(cat "$err_file")")"
      rm -f "$content_file" "$err_file"
      return 1
    fi
    rm -f "$content_file" "$err_file"
    return 0
  fi

  if ! jq empty "$file" >/dev/null 2>"$err_file"; then
    printf '%s' "$(join_output "$(cat "$err_file")")"
    rm -f "$err_file"
    return 1
  fi

  rm -f "$err_file"
  return 0
}

check_manifest_json() {
  files_file="$(mktemp "${TMPDIR:-/tmp}/release-gate-manifests.XXXXXX")"
  failures_file="$(mktemp "${TMPDIR:-/tmp}/release-gate-manifest-failures.XXXXXX")"
  : >"$files_file"
  : >"$failures_file"

  if [ "$MODE" = "staged" ]; then
    if index_has_file ".claude-plugin/marketplace.json"; then
      printf '%s\n' ".claude-plugin/marketplace.json" >>"$files_file"
    else
      printf '%s\n' ".claude-plugin/marketplace.json: missing from index" >>"$failures_file"
    fi
  elif [ -f ".claude-plugin/marketplace.json" ]; then
    printf '%s\n' ".claude-plugin/marketplace.json" >>"$files_file"
  else
    printf '%s\n' ".claude-plugin/marketplace.json: missing file" >>"$failures_file"
  fi

  list_plugin_manifests >>"$files_file"

  count=0
  plugin_count=0
  while IFS= read -r file; do
    [ -n "$file" ] || continue
    count=$((count + 1))
    case "$file" in
      */.claude-plugin/plugin.json) plugin_count=$((plugin_count + 1)) ;;
    esac
    output="$(validate_manifest_file "$file" 2>&1)"
    code="$?"
    if [ "$code" -ne 0 ]; then
      printf '%s: %s\n' "$file" "$(join_output "$output")" >>"$failures_file"
    fi
  done <"$files_file"

  if [ "$plugin_count" -eq 0 ]; then
    printf '%s\n' "*/.claude-plugin/plugin.json: no plugin manifests found" >>"$failures_file"
  fi

  if [ -s "$failures_file" ]; then
    evidence="$(join_output "$(cat "$failures_file")")"
    add_result "blocking" "fail" "manifest-json" "manifest JSON validation failed" "$evidence" "jq empty" 1
  else
    add_result "blocking" "pass" "manifest-json" "validated $count manifest file(s)" "" "jq empty" 0
  fi

  rm -f "$files_file" "$failures_file"
}

validate_frontmatter_file() {
  python3 - "$MODE" "$1" <<'PY'
import subprocess
import sys
from pathlib import Path

import yaml

mode = sys.argv[1]
path = sys.argv[2]

if mode == "staged":
    result = subprocess.run(
        ["git", "show", f":{path}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print("missing from index: " + result.stderr.strip())
        sys.exit(1)
    text = result.stdout
else:
    text = Path(path).read_text(encoding="utf-8", errors="replace")

lines = text.splitlines()

if not lines or lines[0].strip() != "---":
    print("missing opening --- delimiter")
    sys.exit(1)

closing_index = None
for index, line in enumerate(lines[1:], start=1):
    if line.strip() == "---":
        closing_index = index
        break

if closing_index is None:
    print("missing closing --- delimiter")
    sys.exit(1)

frontmatter = "\n".join(lines[1:closing_index]) + "\n"

try:
    data = yaml.safe_load(frontmatter)
except yaml.YAMLError as exc:
    print("frontmatter YAML parse error: " + str(exc).replace("\n", " "))
    sys.exit(1)

if not isinstance(data, dict):
    print("frontmatter must parse to a mapping")
    sys.exit(1)

def has_nonempty_key(key: str) -> bool:
    if key not in data:
        return False
    value = data[key]
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True

missing = [key for key in ("name", "description") if not has_nonempty_key(key)]
if missing:
    print("missing required key(s): " + ", ".join(missing))
    sys.exit(1)
PY
}

check_skill_frontmatter() {
  files_file="$(mktemp "${TMPDIR:-/tmp}/release-gate-skills.XXXXXX")"
  failures_file="$(mktemp "${TMPDIR:-/tmp}/release-gate-skill-failures.XXXXXX")"
  : >"$files_file"
  : >"$failures_file"

  list_skill_files >"$files_file"

  count=0
  while IFS= read -r file; do
    [ -n "$file" ] || continue
    count=$((count + 1))
    output="$(validate_frontmatter_file "$file" 2>&1)"
    code="$?"
    if [ "$code" -ne 0 ]; then
      printf '%s: %s\n' "$file" "$(join_output "$output")" >>"$failures_file"
    fi
  done <"$files_file"

  if [ "$count" -eq 0 ]; then
    printf '%s\n' "*/skills/*/SKILL.md: no skill files found" >>"$failures_file"
  fi

  if [ -s "$failures_file" ]; then
    evidence="$(join_output "$(cat "$failures_file")")"
    add_result "blocking" "fail" "skill-frontmatter" "skill frontmatter validation failed" "$evidence" "YAML frontmatter validation" 1
  else
    add_result "blocking" "pass" "skill-frontmatter" "validated $count skill file(s)" "" "YAML frontmatter validation" 0
  fi

  rm -f "$files_file" "$failures_file"
}

validate_skill_metadata_file() {
  python3 - "$MODE" "$1" <<'PY'
import re
import subprocess
import sys
from pathlib import Path

mode = sys.argv[1]
path = sys.argv[2]

if mode == "staged":
    result = subprocess.run(
        ["git", "show", f":{path}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print("missing from index: " + result.stderr.strip())
        sys.exit(1)
    text = result.stdout
else:
    text = Path(path).read_text(encoding="utf-8", errors="replace")

lines = text.splitlines()
if not lines or lines[0].strip() != "interface:":
    print("missing top-level interface mapping")
    sys.exit(1)

fields: dict[str, str] = {}
for line in lines[1:]:
    if not line.strip():
        continue
    match = re.match(r'^  ([A-Za-z_][A-Za-z0-9_]*)\s*:\s*"(.*)"\s*$', line)
    if not match:
        print("unsupported or malformed line: " + line.strip())
        sys.exit(1)
    fields[match.group(1)] = match.group(2)

required = ("display_name", "short_description", "default_prompt")
missing = [field for field in required if not fields.get(field)]
if missing:
    print("missing required interface field(s): " + ", ".join(missing))
    sys.exit(1)

short_description = fields["short_description"]
if not 25 <= len(short_description) <= 64:
    print("short_description must be 25-64 characters")
    sys.exit(1)

if "$" not in fields["default_prompt"]:
    print("default_prompt must mention the skill with $skill-name")
    sys.exit(1)
PY
}

check_skill_metadata() {
  files_file="$(mktemp "${TMPDIR:-/tmp}/release-gate-metadata.XXXXXX")"
  failures_file="$(mktemp "${TMPDIR:-/tmp}/release-gate-metadata-failures.XXXXXX")"
  : >"$files_file"
  : >"$failures_file"

  list_skill_metadata_files >"$files_file"

  count=0
  while IFS= read -r file; do
    [ -n "$file" ] || continue
    count=$((count + 1))
    output="$(validate_skill_metadata_file "$file" 2>&1)"
    code="$?"
    if [ "$code" -ne 0 ]; then
      printf '%s: %s\n' "$file" "$(join_output "$output")" >>"$failures_file"
    fi
  done <"$files_file"

  if [ -s "$failures_file" ]; then
    evidence="$(join_output "$(cat "$failures_file")")"
    add_result "blocking" "fail" "skill-metadata" "skill metadata validation failed" "$evidence" "structural agents/openai.yaml validation" 1
  else
    add_result "blocking" "pass" "skill-metadata" "validated $count skill metadata file(s)" "" "structural agents/openai.yaml validation" 0
  fi

  rm -f "$files_file" "$failures_file"
}

check_diff_whitespace() {
  case "$MODE" in
    staged)
      command_text="git diff --cached --check"
      output="$(git diff --cached --check 2>&1)"
      code="$?"
      ;;
    working)
      command_text="git diff --check"
      output="$(git diff --check 2>&1)"
      code="$?"
      ;;
    all)
      command_text="git diff --check HEAD"
      output="$(git diff --check HEAD 2>&1)"
      code="$?"
      ;;
  esac

  if [ "$code" -eq 0 ]; then
    add_result "blocking" "pass" "diff-whitespace" "diff whitespace check passed" "" "$command_text" 0
  else
    add_result "blocking" "fail" "diff-whitespace" "diff whitespace check failed" "$(join_output "$output")" "$command_text" "$code"
  fi
}

check_secret_scan() {
  scanner="secret-scanner/scripts/scan.py"
  command_text="python3 $scanner --mode $MODE --format json"

  if [ ! -f "$scanner" ]; then
    mark_usage_failure
    add_result "blocking" "fail" "secret-scan" "secret scanner is missing" "$scanner" "$command_text" 2
    return
  fi

  output="$(python3 "$scanner" --mode "$MODE" --format json 2>&1)"
  code="$?"

  if [ "$code" -eq 0 ]; then
    add_result "blocking" "pass" "secret-scan" "secret scan passed" "" "$command_text" 0
    return
  fi

  evidence="$(printf '%s' "$output" | jq -r 'if type == "array" and length > 0 then .[0] | "\(.file):\(.line):\(.pattern)" else empty end' 2>/dev/null)"
  if [ -z "$evidence" ]; then
    evidence="$(join_output "$output")"
  fi

  if [ "$code" -eq 1 ]; then
    add_result "blocking" "fail" "secret-scan" "secret scanner reported findings" "$evidence" "$command_text" 1
  else
    mark_usage_failure
    add_result "blocking" "fail" "secret-scan" "secret scanner failed to run" "$evidence" "$command_text" "$code"
  fi
}

changed_paths_for() {
  target="$1"

  case "$MODE" in
    staged)
      git diff --cached --name-only -- "$target"
      ;;
    working)
      git diff --name-only HEAD -- "$target"
      git ls-files --others --exclude-standard -- "$target"
      ;;
    all)
      printf '%s\n' "$target"
      ;;
  esac
}

diff_touches_any() {
  if [ "$MODE" = "all" ]; then
    return 0
  fi

  for target in "$@"; do
    if [ -n "$(changed_paths_for "$target")" ]; then
      return 0
    fi
  done

  return 1
}

diff_touches_skill_hygiene_infra() {
  diff_touches_any "${SKILL_HYGIENE_INFRA_TARGETS[@]}"
}

check_skill_hygiene_infra_drift() {
  command_text="git diff --cached --name-only -- <skill hygiene infrastructure>; git diff --name-only -- <skill hygiene infrastructure>"

  if [ "$MODE" != "staged" ]; then
    return
  fi

  staged_paths="$(git diff --cached --name-only -- "${SKILL_HYGIENE_INFRA_TARGETS[@]}")"
  if [ -z "$staged_paths" ]; then
    add_result "skipped" "skip" "skill-hygiene-infra-drift" \
      "no staged diff touches skill hygiene infrastructure" "" "$command_text" 0
    return
  fi

  drift_paths="$(
    {
      git diff --name-only -- "${SKILL_HYGIENE_INFRA_TARGETS[@]}"
      git ls-files --others --exclude-standard -- "${SKILL_HYGIENE_INFRA_TARGETS[@]}"
    } | sed '/^$/d' | sort -u
  )"
  if [ -n "$drift_paths" ]; then
    first_path="$(printf '%s\n' "$drift_paths" | sed -n '1p')"
    add_result "blocking" "fail" "skill-hygiene-infra-drift" \
      "staged skill hygiene infrastructure differs from the worktree" \
      "$first_path" "$command_text" 1
    return
  fi

  add_result "blocking" "pass" "skill-hygiene-infra-drift" \
    "staged skill hygiene infrastructure matches the worktree" "" "$command_text" 0
}

check_idea_to_ship_fixtures() {
  command_text="bash tests/idea-to-ship-eval-fixtures.sh"

  if ! diff_touches_any \
    "idea-to-ship" \
    "tests/idea-to-ship-eval-fixtures.py" \
    "tests/idea-to-ship-eval-fixtures.sh"; then
    add_result "skipped" "skip" "idea-to-ship-fixtures" \
      "no $MODE diff touches idea-to-ship fixture scope" "" "$command_text" 0
    return
  fi

  if [ ! -f "tests/idea-to-ship-eval-fixtures.sh" ]; then
    add_result "advisory" "warn" "idea-to-ship-fixtures" \
      "idea-to-ship fixture command is missing" \
      "tests/idea-to-ship-eval-fixtures.sh" "$command_text" 2
    return
  fi

  output="$(bash tests/idea-to-ship-eval-fixtures.sh 2>&1)"
  code="$?"

  if [ "$code" -eq 0 ]; then
    add_result "advisory" "pass" "idea-to-ship-fixtures" \
      "idea-to-ship fixture checks passed" "" "$command_text" 0
  elif [ "$code" -eq 1 ]; then
    add_result "advisory" "warn" "idea-to-ship-fixtures" \
      "idea-to-ship fixture checks reported regressions" \
      "$(join_output "$output")" "$command_text" 1
  else
    add_result "advisory" "warn" "idea-to-ship-fixtures" \
      "idea-to-ship fixture checks could not run" \
      "$(join_output "$output")" "$command_text" "$code"
  fi
}

check_agent_playbook_fixtures() {
  command_text="bash tests/agent-playbook-eval-fixtures.sh"

  if ! diff_touches_any \
    "agent-playbook" \
    "antifragile" \
    "issue-evaluator" \
    "skill-stats" \
    "worktree-cleaner" \
    "tests/agent-playbook-eval-fixtures.py" \
    "tests/agent-playbook-eval-fixtures.sh"; then
    add_result "skipped" "skip" "agent-playbook-fixtures" \
      "no $MODE diff touches agent-playbook fixture scope" "" "$command_text" 0
    return
  fi

  if [ ! -f "tests/agent-playbook-eval-fixtures.sh" ]; then
    add_result "advisory" "warn" "agent-playbook-fixtures" \
      "agent-playbook fixture command is missing" \
      "tests/agent-playbook-eval-fixtures.sh" "$command_text" 2
    return
  fi

  output="$(bash tests/agent-playbook-eval-fixtures.sh 2>&1)"
  code="$?"

  if [ "$code" -eq 0 ]; then
    add_result "advisory" "pass" "agent-playbook-fixtures" \
      "agent-playbook fixture checks passed" "" "$command_text" 0
  elif [ "$code" -eq 1 ]; then
    add_result "advisory" "warn" "agent-playbook-fixtures" \
      "agent-playbook fixture checks reported regressions" \
      "$(join_output "$output")" "$command_text" 1
  else
    add_result "advisory" "warn" "agent-playbook-fixtures" \
      "agent-playbook fixture checks could not run" \
      "$(join_output "$output")" "$command_text" "$code"
  fi
}

check_skill_hygiene() {
  command_text="python3 scripts/skill-hygiene-check.py --mode $MODE ."

  if [ ! -f "scripts/skill-hygiene-check.py" ]; then
    add_result "advisory" "warn" "skill-hygiene" \
      "skill hygiene checker is missing" \
      "scripts/skill-hygiene-check.py" "$command_text" 2
    return
  fi

  output="$(python3 scripts/skill-hygiene-check.py --mode "$MODE" . 2>&1)"
  code="$?"

  if [ "$code" -eq 0 ]; then
    add_result "advisory" "pass" "skill-hygiene" \
      "skill hygiene checks passed" "" "$command_text" 0
  elif [ "$code" -eq 1 ]; then
    add_result "advisory" "warn" "skill-hygiene" \
      "skill hygiene checks reported issues" \
      "$(join_finding_output "$output")" "$command_text" 1
  else
    add_result "advisory" "warn" "skill-hygiene" \
      "skill hygiene checks could not run" \
      "$(join_output "$output")" "$command_text" "$code"
  fi
}

check_skill_hygiene_fixtures() {
  command_text="bash tests/skill-hygiene-check-fixtures.sh"

  if ! diff_touches_skill_hygiene_infra; then
    add_result "skipped" "skip" "skill-hygiene-fixtures" \
      "no $MODE diff touches skill hygiene fixture scope" "" "$command_text" 0
    return
  fi

  if [ ! -f "tests/skill-hygiene-check-fixtures.sh" ]; then
    add_result "advisory" "warn" "skill-hygiene-fixtures" \
      "skill hygiene fixture command is missing" \
      "tests/skill-hygiene-check-fixtures.sh" "$command_text" 2
    return
  fi

  output="$(bash tests/skill-hygiene-check-fixtures.sh 2>&1)"
  code="$?"

  if [ "$code" -eq 0 ]; then
    add_result "advisory" "pass" "skill-hygiene-fixtures" \
      "skill hygiene fixture checks passed" "" "$command_text" 0
  elif [ "$code" -eq 1 ]; then
    add_result "advisory" "warn" "skill-hygiene-fixtures" \
      "skill hygiene fixture checks reported regressions" \
      "$(join_output "$output")" "$command_text" 1
  else
    add_result "advisory" "warn" "skill-hygiene-fixtures" \
      "skill hygiene fixture checks could not run" \
      "$(join_output "$output")" "$command_text" "$code"
  fi
}

check_skill_hygiene_release_gate_fixtures() {
  command_text="bash tests/skill-hygiene-release-gate-fixtures.sh --self-check"

  if ! diff_touches_skill_hygiene_infra; then
    add_result "skipped" "skip" "skill-hygiene-release-gate-fixtures" \
      "no $MODE diff touches skill hygiene fixture scope" "" "$command_text" 0
    return
  fi

  if [ ! -f "tests/skill-hygiene-release-gate-fixtures.sh" ]; then
    add_result "advisory" "warn" "skill-hygiene-release-gate-fixtures" \
      "skill hygiene release-gate fixture command is missing" \
      "tests/skill-hygiene-release-gate-fixtures.sh" "$command_text" 2
    return
  fi

  output="$(bash tests/skill-hygiene-release-gate-fixtures.sh --self-check 2>&1)"
  code="$?"

  if [ "$code" -eq 0 ]; then
    add_result "advisory" "pass" "skill-hygiene-release-gate-fixtures" \
      "skill hygiene release-gate fixture self-check passed" "" "$command_text" 0
  elif [ "$code" -eq 1 ]; then
    add_result "advisory" "warn" "skill-hygiene-release-gate-fixtures" \
      "skill hygiene release-gate fixture self-check reported regressions" \
      "$(join_output "$output")" "$command_text" 1
  else
    add_result "advisory" "warn" "skill-hygiene-release-gate-fixtures" \
      "skill hygiene release-gate fixture self-check could not run" \
      "$(join_output "$output")" "$command_text" "$code"
  fi
}

emit_human() {
  printf 'Release gate: %s\n\n' "$MODE"
  printf 'Blocking\n'
  while IFS="$(printf '\t')" read -r category status id message evidence command_text exit_code; do
    [ "$category" = "blocking" ] || continue
    printf '  %s %s' "$(status_label "$status")" "$id"
    if [ -n "$message" ]; then
      printf ': %s' "$message"
    fi
    if [ -n "$evidence" ]; then
      printf ' (%s)' "$evidence"
    fi
    printf '\n'
  done <"$RESULTS_FILE"

  printf '\nAdvisory\n'
  advisory_found=0
  while IFS="$(printf '\t')" read -r category status id message evidence command_text exit_code; do
    [ "$category" = "advisory" ] || continue
    advisory_found=1
    printf '  %s %s' "$(status_label "$status")" "$id"
    if [ -n "$message" ]; then
      printf ': %s' "$message"
    fi
    if [ -n "$evidence" ]; then
      printf ' (%s)' "$evidence"
    fi
    printf '\n'
  done <"$RESULTS_FILE"
  if [ "$advisory_found" -eq 0 ]; then
    printf '  <none>\n'
  fi

  printf '\nSkipped\n'
  if grep -F "$(printf '\tskip\t')" "$RESULTS_FILE" >/dev/null 2>&1; then
    while IFS="$(printf '\t')" read -r category status id message evidence command_text exit_code; do
      [ "$status" = "skip" ] || continue
      printf '  SKIP %s: %s\n' "$id" "$message"
    done <"$RESULTS_FILE"
  else
    printf '  <none>\n'
  fi
}

emit_json() {
  jq -Rn --arg mode "$MODE" --argjson strict "$STRICT" '
    def evidence($value):
      if $value == "" then [] else ($value | split("|")) end;

    [inputs
      | split("\t")
      | {
          id: .[2],
          category: .[0],
          status: .[1],
          message: .[3],
          evidence: evidence(.[4]),
          command: .[5],
          exit_code: (.[6] | tonumber)
        }
    ] as $checks
    | {mode: $mode, strict: $strict, checks: $checks}
  ' <"$RESULTS_FILE"
}

check_manifest_json
check_skill_frontmatter
check_skill_metadata
check_diff_whitespace
check_secret_scan
check_skill_hygiene_infra_drift
check_skill_hygiene
check_skill_hygiene_fixtures
check_skill_hygiene_release_gate_fixtures
check_idea_to_ship_fixtures
check_agent_playbook_fixtures

if [ "$JSON_OUTPUT" = "true" ]; then
  emit_json
else
  emit_human
fi

if [ "$USAGE_FAILURE" -ne 0 ]; then
  exit 2
fi

if [ "$BLOCKING_FAILURE" -ne 0 ]; then
  exit 1
fi

exit 0
