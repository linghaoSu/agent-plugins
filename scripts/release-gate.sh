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

add_result() {
  category="$1"
  status="$2"
  id="$3"
  message="$4"
  evidence="${5:-}"
  command_text="${6:-}"
  exit_code="${7:-0}"

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

index_has_file() {
  git cat-file -e ":$1" 2>/dev/null
}

require_cmd git
require_cmd jq
require_cmd python3

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

frontmatter = lines[1:closing_index]

def has_nonempty_key(key: str) -> bool:
    pattern = re.compile(r"^\s*" + re.escape(key) + r"\s*:\s*\S")
    return any(pattern.search(line) for line in frontmatter)

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
    add_result "blocking" "fail" "skill-frontmatter" "skill frontmatter validation failed" "$evidence" "structural frontmatter validation" 1
  else
    add_result "blocking" "pass" "skill-frontmatter" "validated $count skill file(s)" "" "structural frontmatter validation" 0
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

check_idea_to_ship_fixtures() {
  command_text="bash tests/idea-to-ship-eval-fixtures.sh"

  if [ "$MODE" != "all" ]; then
    add_result "skipped" "skip" "idea-to-ship-fixtures" \
      "runs only in --mode all" "" "$command_text" 0
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
check_diff_whitespace
check_secret_scan
check_idea_to_ship_fixtures

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
