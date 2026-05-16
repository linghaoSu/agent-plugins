#!/usr/bin/env bash
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RELEASE_GATE="$ROOT/scripts/release-gate.sh"
TMP_DIRS=()
TMP_DIRS_COUNT=0

failures=0
SKILL_HYGIENE_INFRA_TARGETS=(
  "scripts/skill-hygiene-check.py"
  "scripts/release-gate.sh"
  "tests/skill-hygiene-*"
  "RELEASE-GATE.md"
)

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

release_gate_infra_targets() {
  awk '
    /^SKILL_HYGIENE_INFRA_TARGETS=\(/ {
      in_targets = 1
      next
    }
    in_targets && /^\)/ {
      exit
    }
    in_targets {
      line = $0
      sub(/^[ \t]*/, "", line)
      gsub(/"/, "", line)
      if (line != "") {
        print line
      }
    }
  ' "$RELEASE_GATE"
}

require_infra_targets_match() {
  expected="$(release_gate_infra_targets)"
  actual="$(printf '%s\n' "${SKILL_HYGIENE_INFRA_TARGETS[@]}")"

  if [ "$actual" = "$expected" ]; then
    pass "self-check-skill-hygiene-infra-targets"
  else
    fail "self-check-skill-hygiene-infra-targets" "fixture target list differs from release gate"
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

assert_json_evidence_contains() {
  json="$1"
  check_id="$2"
  needle="$3"
  label="$4"

  output="$(
    printf '%s' "$json" | jq -r \
      --arg id "$check_id" \
      --arg needle "$needle" \
      '.checks[]? | select(.id == $id) |
       select(((.evidence // []) | if type == "array" then join(" ") else tostring end) | contains($needle)) |
       .id' 2>/dev/null
  )"

  if [ "$output" = "$check_id" ]; then
    pass "$label"
  else
    fail "$label" "expected $check_id evidence to contain: $needle"
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

  infra_files="$(
    git -C "$ROOT" ls-files --cached --others --exclude-standard -- "${SKILL_HYGIENE_INFRA_TARGETS[@]}"
  )"
  while IFS= read -r file; do
    [ -n "$file" ] || continue
    if [ -f "$ROOT/$file" ]; then
      mkdir -p "$repo/$(dirname "$file")"
      cp "$ROOT/$file" "$repo/$file"
    fi
  done <<EOF
$infra_files
EOF

  mkdir -p "$repo/secret-scanner/scripts"
  cat >"$repo/secret-scanner/scripts/scan.py" <<'EOF'
#!/usr/bin/env python3
import json

print(json.dumps([]))
EOF
  chmod +x "$repo/secret-scanner/scripts/scan.py"

  while IFS= read -r file; do
    [ -n "$file" ] || continue
    git -C "$repo" add "$file"
  done <<EOF
$infra_files
EOF
  git -C "$repo" add secret-scanner/scripts/scan.py
  git -C "$repo" commit -q -m "candidate skill hygiene fixture baseline"

  printf '%s\n' "$repo"
}

write_moderate_bloat_skill() {
  repo="$1"
  skill_dir="$repo/harness-engineering/skills/moderate-bloat"
  mkdir -p "$skill_dir/agents"
  {
    printf '%s\n' '---'
    printf '%s\n' 'name: moderate-bloat'
    printf '%s\n' 'description: Short routing description.'
    printf '%s\n' '---'
    printf '\n'
    printf '%s\n' '# Moderate Bloat'
    printf '\n'
    i=1
    while [ "$i" -le 394 ]; do
      printf 'Filler line %s\n' "$i"
      i=$((i + 1))
    done
  } >"$skill_dir/SKILL.md"
  cat >"$skill_dir/agents/openai.yaml" <<'EOF'
interface:
  display_name: "Moderate Bloat"
  short_description: "Fixture metadata for moderate bloat"
  default_prompt: "$moderate-bloat"
EOF
}

write_repeated_prompt_skill() {
  repo="$1"
  skill_dir="$repo/harness-engineering/skills/repeated-prompt"
  mkdir -p "$skill_dir/agents"
  prompt_text="$(
    cat <<'EOF'
Use this prompt when assigning an adversarial reviewer.
You are an independent reviewer. Your job is to inspect the changed skill file, name every concrete bug, and avoid style-only feedback.
Assigned angle: correctness and security.
READ-ONLY: Do not edit files, do not modify git state, and do not infer missing facts.
For each issue, report severity, path, line, concrete problem, and concrete fix.
If you find no material issue, respond with exactly LGTM.
Review the requirements, architecture, test plan, and implementation log before deciding.
Return only evidence-backed findings and keep speculative concerns out of the report.
EOF
  )"
  {
    printf '%s\n' '---'
    printf '%s\n' 'name: repeated-prompt'
    printf '%s\n' 'description: Short routing description.'
    printf '%s\n' '---'
    printf '\n'
    printf '%s\n' '# Repeated Prompt'
    printf '\n%s\n' "$prompt_text"
    printf '\n%s\n\n' '## Separator'
    printf '%s\n' "$prompt_text"
  } >"$skill_dir/SKILL.md"
  cat >"$skill_dir/agents/openai.yaml" <<'EOF'
interface:
  display_name: "Repeated Prompt"
  short_description: "Fixture metadata for repeated prompt"
  default_prompt: "$repeated-prompt"
EOF
}

write_repeated_template_skill() {
  repo="$1"
  skill_dir="$repo/harness-engineering/skills/repeated-template"
  mkdir -p "$skill_dir/agents"
  template_text="$(
    cat <<'EOF'
## Final Report
| Severity | File | Issue | Resolution |
|---|---|---|---|
| <severity> | <file> | <issue> | <resolution> |

status: <success-or-failure>
outputs_written: <artifact paths>
next_action: <command>
truncated: <true-or-false>
reviewed_with: <command evidence>
evidence_summary: record the command or artifact that proves each reported outcome and the exact reviewer-visible status used for handoff.
EOF
  )"
  {
    printf '%s\n' '---'
    printf '%s\n' 'name: repeated-template'
    printf '%s\n' 'description: Short routing description.'
    printf '%s\n' '---'
    printf '\n'
    printf '%s\n' '# Repeated Template'
    printf '\n%s\n' "$template_text"
    printf '\n%s\n\n' '## Separator'
    printf '%s\n' "$template_text"
  } >"$skill_dir/SKILL.md"
  cat >"$skill_dir/agents/openai.yaml" <<'EOF'
interface:
  display_name: "Repeated Template"
  short_description: "Fixture metadata for repeated template"
  default_prompt: "$repeated-template"
EOF
}

write_scan_limited_prompt_skill() {
  repo="$1"
  skill_dir="$repo/harness-engineering/skills/scan-limited-prompt"
  mkdir -p "$skill_dir/agents"
  long_prompt_alpha="$(
    {
      printf '%s\n' 'Use this prompt when assigning an adversarial reviewer.'
      printf '%s\n' 'You are an independent reviewer. Your job is to inspect the changed skill file, name every concrete bug, and avoid style-only feedback.'
      printf '%s\n' 'Assigned angle: correctness and security.'
      printf '%s\n' 'READ-ONLY: Do not edit files, do not modify git state, and do not infer missing facts.'
      printf '%s\n' 'For each issue, report severity, path, line, concrete problem, and concrete fix.'
      printf '%s\n' 'If you find no material issue, respond with exactly LGTM.'
      i=1
      while [ "$i" -le 18 ]; do
        printf 'Review evidence bundle alpha section %s: compare requirements, architecture, implementation log, test plan, and release-gate output; report only concrete issues with severity, path, line, problem, and fix.\n' "$i"
        i=$((i + 1))
      done
      printf '%s\n' 'Return only evidence-backed findings and keep speculative concerns out of the report.'
    }
  )"
  long_prompt_beta="$(printf '%s' "$long_prompt_alpha" | sed 's/bundle alpha/bundle beta/g')"
  {
    printf '%s\n' '---'
    printf '%s\n' 'name: scan-limited-prompt'
    printf '%s\n' 'description: Short routing description.'
    printf '%s\n' '---'
    printf '\n'
    printf '%s\n' '# Scan Limited Prompt'
    printf '\n%s\n' "$long_prompt_alpha"
    printf '\n%s\n\n' '## Near Duplicate'
    printf '%s\n' "$long_prompt_beta"
  } >"$skill_dir/SKILL.md"
  cat >"$skill_dir/agents/openai.yaml" <<'EOF'
interface:
  display_name: "Scan Limited Prompt"
  short_description: "Fixture metadata for scan limit"
  default_prompt: "$scan-limited-prompt"
EOF
}

long_template_text() {
  label="$1"
  printf '%s\n' '## Final Report'
  printf '%s\n' '| Severity | File | Issue | Resolution | Evidence |'
  printf '%s\n' '|---|---|---|---|---|'
  i=1
  while [ "$i" -le 28 ]; do
    printf '| warning | file-%s.md | issue %s %s compares requirements, architecture, implementation log, test plan, release-gate output, and reviewer evidence for concrete regressions | resolution %s records the exact fix and owner | evidence %s names the command and artifact |\n' "$i" "$label" "$i" "$i" "$i"
    i=$((i + 1))
  done
  printf '%s\n' 'status: <success-or-failure>'
  printf '%s\n' 'outputs_written: <artifact paths>'
  printf '%s\n' 'next_action: <command>'
  printf '%s\n' 'truncated: <true-or-false>'
  printf '%s\n' 'reviewed_with: <command evidence>'
  printf '%s\n' 'evidence_summary: record the command or artifact that proves each reported outcome and the exact reviewer-visible status used for handoff.'
}

write_scan_limited_template_skill() {
  repo="$1"
  skill_dir="$repo/harness-engineering/skills/scan-limited-template"
  mkdir -p "$skill_dir/agents"
  {
    printf '%s\n' '---'
    printf '%s\n' 'name: scan-limited-template'
    printf '%s\n' 'description: Short routing description.'
    printf '%s\n' '---'
    printf '\n'
    printf '%s\n' '# Scan Limited Template'
    long_template_text alpha
    printf '\n%s\n\n' '## Near Duplicate'
    long_template_text beta
  } >"$skill_dir/SKILL.md"
  cat >"$skill_dir/agents/openai.yaml" <<'EOF'
interface:
  display_name: "Scan Limited Template"
  short_description: "Fixture metadata for scan limit"
  default_prompt: "$scan-limited-template"
EOF
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
  require_grep "skill-hygiene-infra-drift" "$RELEASE_GATE" "self-check-skill-hygiene-infra-drift-id"
  require_grep "tests/skill-hygiene-check-fixtures.sh" "$RELEASE_GATE" "self-check-checker-fixture-command"
  require_grep "tests/skill-hygiene-release-gate-fixtures.sh --self-check" "$RELEASE_GATE" "self-check-non-recursive-command"
  require_infra_targets_match
}

full_check() {
  self_check

  if ! command -v jq >/dev/null 2>&1; then
    fail "jq-present" "missing required command: jq"
    return
  fi

  all_repo="$(make_candidate_repo)"
  write_moderate_bloat_skill "$all_repo"
  write_repeated_template_skill "$all_repo"

  all_json="$(run_gate_json "$all_repo" "all" "false" 0 "release-gate-all-json")"
  assert_json_check "$all_json" "skill-hygiene-fixtures" "advisory" "pass" 0
  assert_json_check "$all_json" "skill-hygiene-release-gate-fixtures" "advisory" "pass" 0
  assert_json_check "$all_json" "skill-hygiene" "advisory" "warn" 1
  assert_json_evidence_contains "$all_json" "skill-hygiene" "moderate-skill-bloat" "json-all-moderate-bloat-evidence"
  assert_json_evidence_contains "$all_json" "skill-hygiene" "repeated-inline-template" "json-all-repeated-template-evidence"

  working_repo="$(make_candidate_repo)"
  write_moderate_bloat_skill "$working_repo"
  write_repeated_prompt_skill "$working_repo"
  write_repeated_template_skill "$working_repo"
  write_scan_limited_prompt_skill "$working_repo"
  write_scan_limited_template_skill "$working_repo"

  working_strict_json="$(run_gate_json "$working_repo" "working" "true" 1 "release-gate-working-strict-json")"
  assert_json_check "$working_strict_json" "skill-hygiene" "advisory" "fail" 1
  assert_json_evidence_contains "$working_strict_json" "skill-hygiene" "moderate-skill-bloat" "json-working-moderate-bloat-evidence"
  assert_json_evidence_contains "$working_strict_json" "skill-hygiene" "repeated-inline-prompt" "json-working-repeated-prompt-evidence"
  assert_json_evidence_contains "$working_strict_json" "skill-hygiene" "repeated-inline-template" "json-working-repeated-template-evidence"
  assert_json_evidence_contains "$working_strict_json" "skill-hygiene" "repetition-scan-limited" "json-working-scan-limited-evidence"
  assert_json_evidence_contains "$working_strict_json" "skill-hygiene" "families=prompt" "json-working-prompt-scan-limited-evidence"
  assert_json_evidence_contains "$working_strict_json" "skill-hygiene" "families=template" "json-working-template-scan-limited-evidence"

  working_pass_repo="$(make_candidate_repo)"
  printf '\nfixture pass touch\n' >>"$working_pass_repo/RELEASE-GATE.md"

  working_pass_json="$(run_gate_json "$working_pass_repo" "working" "false" 0 "release-gate-working-fixtures-pass-json")"
  assert_json_check "$working_pass_json" "skill-hygiene-fixtures" "advisory" "pass" 0
  assert_json_check "$working_pass_json" "skill-hygiene-release-gate-fixtures" "advisory" "pass" 0

  checker_fixture_fail_repo="$(make_candidate_repo)"
  printf '\nchecker fixture failure touch\n' >>"$checker_fixture_fail_repo/RELEASE-GATE.md"
  cat >"$checker_fixture_fail_repo/tests/skill-hygiene-check-fixtures.sh" <<'EOF'
#!/usr/bin/env bash
exit 1
EOF
  chmod +x "$checker_fixture_fail_repo/tests/skill-hygiene-check-fixtures.sh"

  checker_fixture_warn_json="$(run_gate_json "$checker_fixture_fail_repo" "working" "false" 0 "release-gate-checker-fixture-warn-json")"
  assert_json_check "$checker_fixture_warn_json" "skill-hygiene-fixtures" "advisory" "warn" 1

  checker_fixture_strict_json="$(run_gate_json "$checker_fixture_fail_repo" "working" "true" 1 "release-gate-checker-fixture-strict-json")"
  assert_json_check "$checker_fixture_strict_json" "skill-hygiene-fixtures" "advisory" "fail" 1

  release_fixture_fail_repo="$(make_candidate_repo)"
  printf '\nrelease fixture failure touch\n' >>"$release_fixture_fail_repo/RELEASE-GATE.md"
  cat >"$release_fixture_fail_repo/tests/skill-hygiene-release-gate-fixtures.sh" <<'EOF'
#!/usr/bin/env bash
exit 1
EOF
  chmod +x "$release_fixture_fail_repo/tests/skill-hygiene-release-gate-fixtures.sh"

  release_fixture_warn_json="$(run_gate_json "$release_fixture_fail_repo" "working" "false" 0 "release-gate-self-check-warn-json")"
  assert_json_check "$release_fixture_warn_json" "skill-hygiene-release-gate-fixtures" "advisory" "warn" 1

  release_fixture_strict_json="$(run_gate_json "$release_fixture_fail_repo" "working" "true" 1 "release-gate-self-check-strict-json")"
  assert_json_check "$release_fixture_strict_json" "skill-hygiene-release-gate-fixtures" "advisory" "fail" 1

  staged_repo="$(make_candidate_repo)"
  write_scan_limited_prompt_skill "$staged_repo"
  write_scan_limited_template_skill "$staged_repo"
  git -C "$staged_repo" add harness-engineering/skills/scan-limited-prompt harness-engineering/skills/scan-limited-template
  rm -rf -- "$staged_repo/harness-engineering/skills/scan-limited-prompt"
  rm -rf -- "$staged_repo/harness-engineering/skills/scan-limited-template"
  printf '\n# unrelated dirty infrastructure allowed for ordinary staged skill checks\n' >>"$staged_repo/scripts/skill-hygiene-check.py"

  staged_json="$(run_gate_json "$staged_repo" "staged" "false" 0 "release-gate-staged-ordinary-skill-dirty-infra-json")"
  assert_json_check "$staged_json" "skill-hygiene-infra-drift" "skipped" "skip" 0
  assert_json_check "$staged_json" "skill-hygiene-fixtures" "skipped" "skip" 0
  assert_json_check "$staged_json" "skill-hygiene-release-gate-fixtures" "skipped" "skip" 0
  assert_json_check "$staged_json" "skill-hygiene" "advisory" "warn" 1
  assert_json_evidence_contains "$staged_json" "skill-hygiene" "repetition-scan-limited" "json-staged-scan-limited-evidence"
  assert_json_evidence_contains "$staged_json" "skill-hygiene" "scan-limited-prompt" "json-staged-prompt-scan-limited-evidence"
  assert_json_evidence_contains "$staged_json" "skill-hygiene" "families=prompt" "json-staged-prompt-family-evidence"
  assert_json_evidence_contains "$staged_json" "skill-hygiene" "scan-limited-template" "json-staged-template-scan-limited-evidence"
  assert_json_evidence_contains "$staged_json" "skill-hygiene" "families=template" "json-staged-template-family-evidence"

  drift_repo="$(make_candidate_repo)"
  printf '\n# staged candidate drift fixture\n' >>"$drift_repo/scripts/skill-hygiene-check.py"
  git -C "$drift_repo" add scripts/skill-hygiene-check.py
  cat >"$drift_repo/tests/skill-hygiene-helper.sh" <<'EOF'
#!/usr/bin/env bash
exit 0
EOF

  drift_json="$(run_gate_json "$drift_repo" "staged" "false" 1 "release-gate-staged-untracked-infra-drift-json")"
  assert_json_check "$drift_json" "skill-hygiene-infra-drift" "blocking" "fail" 1
  assert_json_evidence_contains "$drift_json" "skill-hygiene-infra-drift" "tests/skill-hygiene-helper.sh" "json-staged-untracked-infra-drift-evidence"

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
