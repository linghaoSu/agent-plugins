#!/usr/bin/env bash
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RELEASE_GATE="$ROOT/scripts/release-gate.sh"
TMP_DIRS=()
TMP_DIRS_COUNT=0

failures=0

cleanup() {
  if [ "$TMP_DIRS_COUNT" -eq 0 ]; then
    return
  fi

  for dir in "${TMP_DIRS[@]}"; do
    rm -rf -- "$dir"
  done
}

trap cleanup EXIT

fail() {
  printf 'FAIL %s: %s\n' "$1" "$2" >&2
  failures=$((failures + 1))
}

pass() {
  printf 'PASS %s\n' "$1" >&2
}

require_file() {
  if [ ! -f "$1" ]; then
    fail "$2" "missing file: $1"
    return 1
  fi
  return 0
}

require_grep() {
  pattern="$1"
  file="$2"
  check_id="$3"
  if grep -F "$pattern" "$file" >/dev/null 2>&1; then
    pass "$check_id"
  else
    fail "$check_id" "missing literal: $pattern"
  fi
}

assert_json_check() {
  json="$1"
  check_id="$2"
  expected_category="$3"
  expected_status="$4"
  expected_exit="$5"

  output="$(
    printf '%s' "$json" | jq -r \
      --arg id "$check_id" \
      --arg category "$expected_category" \
      --arg status "$expected_status" \
      --argjson exit_code "$expected_exit" \
      '.checks[]? | select(.id == $id) |
       select(.category == $category and .status == $status and .exit_code == $exit_code) |
       .id' 2>/dev/null
  )"

  if [ "$output" = "$check_id" ]; then
    pass "json-$check_id"
  else
    fail "json-$check_id" "expected $expected_category/$expected_status exit $expected_exit"
  fi
}

make_candidate_repo() {
  tmp="$(mktemp -d "${TMPDIR:-/tmp}/skill-hygiene-release-gate.XXXXXX")"
  TMP_DIRS+=("$tmp")
  TMP_DIRS_COUNT=$((TMP_DIRS_COUNT + 1))
  repo="$tmp/repo"

  git clone -q "$ROOT" "$repo"
  git -C "$repo" config user.email "fixtures@example.com"
  git -C "$repo" config user.name "Skill Hygiene Fixtures"

  for file in \
    "scripts/release-gate.sh" \
    "scripts/skill-hygiene-check.py" \
    "tests/skill-hygiene-check-fixtures.py" \
    "tests/skill-hygiene-check-fixtures.sh" \
    "tests/skill-hygiene-release-gate-fixtures.sh" \
    "RELEASE-GATE.md"; do
    if [ -f "$ROOT/$file" ]; then
      mkdir -p "$repo/$(dirname "$file")"
      cp "$ROOT/$file" "$repo/$file"
    fi
  done

  git -C "$repo" add \
    scripts/release-gate.sh \
    scripts/skill-hygiene-check.py \
    tests/skill-hygiene-check-fixtures.py \
    tests/skill-hygiene-check-fixtures.sh \
    tests/skill-hygiene-release-gate-fixtures.sh \
    RELEASE-GATE.md
  git -C "$repo" commit -q -m "candidate skill hygiene fixture baseline"

  printf '%s\n' "$repo"
}

run_gate_json() {
  repo="$1"
  mode="$2"
  strict="$3"
  expected_code="$4"
  check_id="$5"

  if [ "$strict" = "true" ]; then
    json="$(bash "$repo/scripts/release-gate.sh" --mode "$mode" --strict --json 2>&1)"
  else
    json="$(bash "$repo/scripts/release-gate.sh" --mode "$mode" --json 2>&1)"
  fi
  code="$?"

  if [ "$code" -eq "$expected_code" ]; then
    pass "$check_id"
  else
    fail "$check_id" "expected exit $expected_code, got $code: $json"
  fi

  printf '%s' "$json"
}

self_check() {
  require_file "$RELEASE_GATE" "release-gate-present" || return
  require_file "$ROOT/tests/skill-hygiene-check-fixtures.sh" "checker-fixture-present" || return

  require_grep "skill-hygiene-fixtures" "$RELEASE_GATE" "self-check-skill-hygiene-fixtures-id"
  require_grep "skill-hygiene-release-gate-fixtures" "$RELEASE_GATE" "self-check-release-gate-fixtures-id"
  require_grep "tests/skill-hygiene-check-fixtures.sh" "$RELEASE_GATE" "self-check-checker-fixture-command"
  require_grep "tests/skill-hygiene-release-gate-fixtures.sh --self-check" "$RELEASE_GATE" "self-check-non-recursive-command"
}

full_check() {
  self_check

  if ! command -v jq >/dev/null 2>&1; then
    fail "jq-present" "missing required command: jq"
    return
  fi

  json="$(run_gate_json "$ROOT" "all" "false" 0 "release-gate-all-json")"

  assert_json_check "$json" "skill-hygiene-fixtures" "advisory" "pass" 0
  assert_json_check "$json" "skill-hygiene-release-gate-fixtures" "advisory" "pass" 0

  candidate_repo="$(make_candidate_repo)"

  staged_json="$(run_gate_json "$candidate_repo" "staged" "false" 0 "release-gate-staged-skip-json")"
  assert_json_check "$staged_json" "skill-hygiene-fixtures" "skipped" "skip" 0
  assert_json_check "$staged_json" "skill-hygiene-release-gate-fixtures" "skipped" "skip" 0

  printf '\nfixture touch\n' >>"$candidate_repo/RELEASE-GATE.md"
  working_json="$(run_gate_json "$candidate_repo" "working" "false" 0 "release-gate-working-pass-json")"
  assert_json_check "$working_json" "skill-hygiene-fixtures" "advisory" "pass" 0
  assert_json_check "$working_json" "skill-hygiene-release-gate-fixtures" "advisory" "pass" 0

  cat >"$candidate_repo/tests/skill-hygiene-check-fixtures.sh" <<'EOF'
#!/usr/bin/env bash
exit 1
EOF
  chmod +x "$candidate_repo/tests/skill-hygiene-check-fixtures.sh"

  warn_json="$(run_gate_json "$candidate_repo" "working" "false" 0 "release-gate-working-warn-json")"
  assert_json_check "$warn_json" "skill-hygiene-fixtures" "advisory" "warn" 1

  strict_json="$(run_gate_json "$candidate_repo" "working" "true" 1 "release-gate-working-strict-json")"
  assert_json_check "$strict_json" "skill-hygiene-fixtures" "advisory" "fail" 1

  release_gate_candidate_repo="$(make_candidate_repo)"
  printf '\nfixture touch\n' >>"$release_gate_candidate_repo/RELEASE-GATE.md"
  mv \
    "$release_gate_candidate_repo/tests/skill-hygiene-check-fixtures.sh" \
    "$release_gate_candidate_repo/tests/skill-hygiene-check-fixtures.sh.disabled"

  self_warn_json="$(
    run_gate_json \
      "$release_gate_candidate_repo" \
      "working" \
      "false" \
      0 \
      "release-gate-self-check-warn-json"
  )"
  assert_json_check "$self_warn_json" "skill-hygiene-release-gate-fixtures" "advisory" "warn" 1

  self_strict_json="$(
    run_gate_json \
      "$release_gate_candidate_repo" \
      "working" \
      "true" \
      1 \
      "release-gate-self-check-strict-json"
  )"
  assert_json_check "$self_strict_json" "skill-hygiene-release-gate-fixtures" "advisory" "fail" 1
}

case "${1:-}" in
  --self-check)
    self_check
    ;;
  "")
    full_check
    ;;
  *)
    printf 'Usage: %s [--self-check]\n' "$0" >&2
    exit 2
    ;;
esac

if [ "$failures" -ne 0 ]; then
  exit 1
fi

exit 0
