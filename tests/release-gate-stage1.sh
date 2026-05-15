#!/usr/bin/env bash
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GATE_SRC="$ROOT/scripts/release-gate.sh"
HYGIENE_SRC="$ROOT/scripts/skill-hygiene-check.py"
SCANNER_SRC="$ROOT/secret-scanner/scripts/scan.py"
TMP_ROOT="$(mktemp -d)"
FAILURES=0

cleanup() {
  rm -rf "$TMP_ROOT"
}
trap cleanup EXIT

fail() {
  printf 'FAIL %s\n' "$1" >&2
  FAILURES=$((FAILURES + 1))
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'SKIP missing required command: %s\n' "$1" >&2
    exit 0
  fi
}

assert_exit() {
  actual="$1"
  expected="$2"
  label="$3"
  if [ "$actual" -ne "$expected" ]; then
    fail "$label: expected exit $expected, got $actual"
  fi
}

assert_contains() {
  file="$1"
  needle="$2"
  label="$3"
  if ! grep -F "$needle" "$file" >/dev/null 2>&1; then
    fail "$label: expected output to contain '$needle'"
    printf '%s output:\n' "$label" >&2
    sed -n '1,120p' "$file" >&2
  fi
}

make_fixture_repo() {
  name="$1"
  repo="$TMP_ROOT/$name"
  mkdir -p "$repo/scripts"
  mkdir -p "$repo/secret-scanner/scripts"
  mkdir -p "$repo/.claude-plugin"
  mkdir -p "$repo/demo/.claude-plugin"
  mkdir -p "$repo/demo/skills/example"

  cp "$GATE_SRC" "$repo/scripts/release-gate.sh"
  cp "$HYGIENE_SRC" "$repo/scripts/skill-hygiene-check.py"
  cp "$SCANNER_SRC" "$repo/secret-scanner/scripts/scan.py"
  chmod +x "$repo/scripts/release-gate.sh"

  cat >"$repo/.claude-plugin/marketplace.json" <<'JSON'
{
  "plugins": [
    {
      "name": "demo",
      "path": "demo"
    }
  ]
}
JSON

  cat >"$repo/demo/.claude-plugin/plugin.json" <<'JSON'
{
  "name": "demo",
  "version": "0.1.0",
  "description": "Demo plugin for release gate fixtures"
}
JSON

  cat >"$repo/demo/skills/example/SKILL.md" <<'MD'
---
name: example
description: Example skill fixture.
allowed-tools: [Read]
---

# Example
MD

  printf 'clean\n' >"$repo/tracked.md"

  (
    cd "$repo" &&
      git init -q &&
      git config user.email "release-gate@example.test" &&
      git config user.name "Release Gate Test" &&
      git add . &&
      git commit -qm "baseline"
  )

  printf '%s\n' "$repo"
}

run_gate() {
  repo="$1"
  shift
  (
    cd "$repo" &&
      ./scripts/release-gate.sh "$@"
  ) >"$repo/out.txt" 2>"$repo/err.txt"
}

test_valid_repo_passes() {
  repo="$(make_fixture_repo valid)"
  run_gate "$repo" --mode staged
  code="$?"
  assert_exit "$code" 0 "valid repo"
  assert_contains "$repo/out.txt" "PASS manifest-json" "valid repo"
  assert_contains "$repo/out.txt" "PASS skill-frontmatter" "valid repo"
  assert_contains "$repo/out.txt" "PASS skill-metadata" "valid repo"
  assert_contains "$repo/out.txt" "PASS diff-whitespace" "valid repo"
  assert_contains "$repo/out.txt" "PASS secret-scan" "valid repo"
  assert_contains "$repo/out.txt" "PASS skill-hygiene" "valid repo"
  assert_contains "$repo/out.txt" "SKIP idea-to-ship-fixtures" "valid repo"
  assert_contains "$repo/out.txt" "SKIP agent-playbook-fixtures" "valid repo"
}

test_malformed_manifest_fails() {
  repo="$(make_fixture_repo bad_manifest)"
  printf '{\n' >"$repo/demo/.claude-plugin/plugin.json"
  (
    cd "$repo" &&
      git add demo/.claude-plugin/plugin.json
  )
  run_gate "$repo" --mode staged
  code="$?"
  assert_exit "$code" 1 "malformed manifest"
  assert_contains "$repo/out.txt" "FAIL manifest-json" "malformed manifest"
}

test_malformed_frontmatter_fails() {
  repo="$(make_fixture_repo bad_frontmatter)"
  cat >"$repo/demo/skills/example/SKILL.md" <<'MD'
---
name: example
---

# Example
MD
  (
    cd "$repo" &&
      git add demo/skills/example/SKILL.md
  )
  run_gate "$repo" --mode staged
  code="$?"
  assert_exit "$code" 1 "malformed frontmatter"
  assert_contains "$repo/out.txt" "FAIL skill-frontmatter" "malformed frontmatter"
}

test_staged_manifest_reads_index() {
  repo="$(make_fixture_repo staged_manifest_index)"
  printf '{\n' >"$repo/demo/.claude-plugin/plugin.json"
  (
    cd "$repo" &&
      git add demo/.claude-plugin/plugin.json
  )
  cat >"$repo/demo/.claude-plugin/plugin.json" <<'JSON'
{
  "name": "demo",
  "version": "0.1.0",
  "description": "Worktree is valid after staging"
}
JSON
  run_gate "$repo" --mode staged
  code="$?"
  assert_exit "$code" 1 "staged manifest reads index"
  assert_contains "$repo/out.txt" "FAIL manifest-json" "staged manifest reads index"
}

test_staged_frontmatter_reads_index() {
  repo="$(make_fixture_repo staged_frontmatter_index)"
  cat >"$repo/demo/skills/example/SKILL.md" <<'MD'
---
name: example
---

# Example
MD
  (
    cd "$repo" &&
      git add demo/skills/example/SKILL.md
  )
  cat >"$repo/demo/skills/example/SKILL.md" <<'MD'
---
name: example
description: Worktree is valid after staging.
allowed-tools: [Read]
---

# Example
MD
  run_gate "$repo" --mode staged
  code="$?"
  assert_exit "$code" 1 "staged frontmatter reads index"
  assert_contains "$repo/out.txt" "FAIL skill-frontmatter" "staged frontmatter reads index"
}

test_malformed_skill_metadata_fails() {
  repo="$(make_fixture_repo bad_skill_metadata)"
  mkdir -p "$repo/demo/skills/example/agents"
  cat >"$repo/demo/skills/example/agents/openai.yaml" <<'YAML'
interface:
  display_name: "Example"
  short_description: "Too short"
YAML
  (
    cd "$repo" &&
      git add demo/skills/example/agents/openai.yaml
  )
  run_gate "$repo" --mode staged
  code="$?"
  assert_exit "$code" 1 "malformed skill metadata"
  assert_contains "$repo/out.txt" "FAIL skill-metadata" "malformed skill metadata"
}

test_staged_whitespace_fails() {
  repo="$(make_fixture_repo staged_whitespace)"
  printf 'bad trailing \n' >"$repo/new-file.md"
  (
    cd "$repo" &&
      git add new-file.md
  )
  run_gate "$repo" --mode staged
  code="$?"
  assert_exit "$code" 1 "staged whitespace"
  assert_contains "$repo/out.txt" "FAIL diff-whitespace" "staged whitespace"
}

test_working_whitespace_fails() {
  repo="$(make_fixture_repo working_whitespace)"
  printf 'bad trailing \n' >"$repo/tracked.md"
  run_gate "$repo" --mode working
  code="$?"
  assert_exit "$code" 1 "working whitespace"
  assert_contains "$repo/out.txt" "FAIL diff-whitespace" "working whitespace"
}

test_staged_secret_fails() {
  repo="$(make_fixture_repo staged_secret)"
  secret_part_one="1234567890"
  secret_part_two="abcdefABCDEF"
  printf 'api_%s = "%s%s"\n' "key" "$secret_part_one" "$secret_part_two" >"$repo/secrets.txt"
  (
    cd "$repo" &&
      git add secrets.txt
  )
  run_gate "$repo" --mode staged
  code="$?"
  assert_exit "$code" 1 "staged secret"
  assert_contains "$repo/out.txt" "FAIL secret-scan" "staged secret"
}

test_new_skill_missing_metadata_warns() {
  repo="$(make_fixture_repo new_skill_missing_metadata)"
  mkdir -p "$repo/demo/skills/new-skill"
  cat >"$repo/demo/skills/new-skill/SKILL.md" <<'MD'
---
name: new-skill
description: New skill fixture.
allowed-tools: [Read]
---

# New Skill
MD
  (
    cd "$repo" &&
      git add demo/skills/new-skill/SKILL.md
  )
  run_gate "$repo" --mode staged
  code="$?"
  assert_exit "$code" 0 "new skill missing metadata advisory"
  assert_contains "$repo/out.txt" "WARN skill-hygiene" "new skill missing metadata advisory"
  assert_contains "$repo/out.txt" "missing-openai-metadata" "new skill missing metadata advisory"
}

test_strict_advisory_fails() {
  repo="$(make_fixture_repo strict_advisory)"
  mkdir -p "$repo/demo/skills/new-skill"
  cat >"$repo/demo/skills/new-skill/SKILL.md" <<'MD'
---
name: new-skill
description: New skill fixture.
allowed-tools: [Read]
---

# New Skill
MD
  (
    cd "$repo" &&
      git add demo/skills/new-skill/SKILL.md
  )
  run_gate "$repo" --mode staged --strict
  code="$?"
  assert_exit "$code" 1 "strict advisory"
  assert_contains "$repo/out.txt" "FAIL skill-hygiene" "strict advisory"
  assert_contains "$repo/out.txt" "strict mode" "strict advisory"
}

test_invalid_mode_exits_2() {
  repo="$(make_fixture_repo invalid_mode)"
  run_gate "$repo" --mode banana
  code="$?"
  assert_exit "$code" 2 "invalid mode"
  assert_contains "$repo/err.txt" "Invalid --mode" "invalid mode"
}

test_missing_secret_scanner_exits_2() {
  repo="$(make_fixture_repo missing_scanner)"
  rm -f "$repo/secret-scanner/scripts/scan.py"
  run_gate "$repo" --mode staged
  code="$?"
  assert_exit "$code" 2 "missing secret scanner"
  assert_contains "$repo/out.txt" "FAIL secret-scan" "missing secret scanner"
}

test_all_mode_missing_idea_to_ship_fixture_is_advisory() {
  repo="$(make_fixture_repo all_missing_idea_to_ship_fixture)"
  run_gate "$repo" --mode all
  code="$?"
  assert_exit "$code" 0 "all mode missing idea-to-ship fixture advisory"
  assert_contains "$repo/out.txt" "WARN idea-to-ship-fixtures" \
    "all mode missing idea-to-ship fixture advisory"
  assert_contains "$repo/out.txt" "WARN agent-playbook-fixtures" \
    "all mode missing agent-playbook fixture advisory"
}

require_cmd git
require_cmd jq
require_cmd python3

if [ ! -f "$GATE_SRC" ]; then
  fail "missing release gate script at $GATE_SRC"
  exit 1
fi

if [ ! -f "$HYGIENE_SRC" ]; then
  fail "missing skill hygiene script at $HYGIENE_SRC"
  exit 1
fi

if [ ! -f "$SCANNER_SRC" ]; then
  fail "missing secret scanner at $SCANNER_SRC"
  exit 1
fi

test_valid_repo_passes
test_malformed_manifest_fails
test_malformed_frontmatter_fails
test_staged_manifest_reads_index
test_staged_frontmatter_reads_index
test_malformed_skill_metadata_fails
test_staged_whitespace_fails
test_working_whitespace_fails
test_staged_secret_fails
test_new_skill_missing_metadata_warns
test_strict_advisory_fails
test_invalid_mode_exits_2
test_missing_secret_scanner_exits_2
test_all_mode_missing_idea_to_ship_fixture_is_advisory

if [ "$FAILURES" -ne 0 ]; then
  printf '%s test(s) failed\n' "$FAILURES" >&2
  exit 1
fi

printf 'release gate stage 1 tests passed\n'
