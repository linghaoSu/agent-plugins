#!/usr/bin/env bash
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_SRC="$ROOT/auto-updater/scripts/check-update.sh"
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

assert_contains() {
  file="$1"
  needle="$2"
  label="$3"
  if ! grep -F -- "$needle" "$file" >/dev/null 2>&1; then
    fail "$label: expected '$needle'"
    sed -n '1,160p' "$file" >&2
  fi
}

make_marketplace_repo() {
  repo="$(mktemp -d "$TMP_ROOT/marketplace.XXXXXX")"
  mkdir -p "$repo/.claude-plugin" "$repo/demo/skills/example"

  cat >"$repo/.claude-plugin/marketplace.json" <<'JSON'
{
  "plugins": [
    {
      "name": "demo",
      "source": "./demo"
    }
  ]
}
JSON

  cat >"$repo/demo/skills/example/SKILL.md" <<'MD'
---
name: example
description: Example skill fixture.
---

# Example
MD

  (
    cd "$repo" &&
      git init -q &&
      git config user.email "auto-updater@example.test" &&
      git config user.name "Auto Updater Test" &&
      git add . &&
      git commit -qm "baseline"
  )

  printf '\nDirty local skill edit.\n' >>"$repo/demo/skills/example/SKILL.md"
  printf '%s\n' "$repo"
}

write_runtime_stubs() {
  bin="$TMP_ROOT/bin"
  mkdir -p "$bin"

  cat >"$bin/claude" <<'SH'
#!/usr/bin/env bash
set -u

case "$1 $2" in
  "plugin list")
    printf '[{"id":"demo@local","version":"same-head"}]'
    ;;
  "plugin update")
    printf 'claude %s\n' "$*"
    printf 'claude %s\n' "$*" >>"$AUTO_UPDATER_CALLS"
    ;;
  *)
    exit 2
    ;;
esac
SH

  cat >"$bin/codex" <<'SH'
#!/usr/bin/env bash
set -u

if [ "$1 $2 $3" = "plugin marketplace upgrade" ]; then
  printf 'codex %s\n' "$*"
  printf 'codex %s\n' "$*" >>"$AUTO_UPDATER_CALLS"
  exit 0
fi

exit 2
SH

  chmod +x "$bin/claude" "$bin/codex"
  printf '%s\n' "$bin"
}

test_claude_and_codex_both_run() {
  home="$TMP_ROOT/home"
  calls="$TMP_ROOT/calls.log"
  out="$TMP_ROOT/out.log"
  repo="$(make_marketplace_repo)"
  bin="$(write_runtime_stubs)"

  mkdir -p "$home/.claude/plugins" "$home/.codex"
  cat >"$home/.claude/plugins/known_marketplaces.json" <<JSON
{
  "local": {
    "source": {
      "source": "directory",
      "path": "$repo"
    }
  }
}
JSON

  cat >"$home/.codex/config.toml" <<TOML
[plugins."demo@local"]
enabled = true

[marketplaces.local]
source_type = "local"
source = "$repo"
TOML

  : >"$calls"
  HOME="$home" \
    PATH="$bin:$PATH" \
    AUTO_UPDATER_CALLS="$calls" \
    AUTO_UPDATER_TIMEOUT_SECONDS=5 \
    "$SCRIPT_SRC" >"$out" 2>&1
  code="$?"

  if [ "$code" -ne 0 ]; then
    fail "script should never fail hooks, got exit $code"
  fi

  assert_contains "$calls" "claude plugin update demo@local" "claude runtime"
  assert_contains "$home/.codex/plugins/cache/local/demo/local/skills/example/SKILL.md" "Dirty local skill edit" "codex cache sync"
  assert_contains "$out" "- codex local/demo:" "codex runtime"
  assert_contains "$out" "Plugin auto-updater: refreshed local plugin marketplaces" "summary"
}

test_disable_silences_everything() {
  home="$TMP_ROOT/disabled-home"
  calls="$TMP_ROOT/disabled-calls.log"
  out="$TMP_ROOT/disabled-out.log"
  repo="$(make_marketplace_repo)"
  bin="$(write_runtime_stubs)"

  mkdir -p "$home/.claude/plugins" "$home/.codex"
  printf '{}\n' >"$home/.claude/plugins/known_marketplaces.json"
  cat >"$home/.codex/config.toml" <<TOML
[marketplaces.local]
source_type = "local"
source = "$repo"
TOML

  : >"$calls"
  HOME="$home" \
    PATH="$bin:$PATH" \
    AUTO_UPDATER_CALLS="$calls" \
    AUTO_UPDATER_DISABLE=1 \
    "$SCRIPT_SRC" >"$out" 2>&1
  code="$?"

  if [ "$code" -ne 0 ]; then
    fail "disabled script should exit 0, got $code"
  fi
  if [ -s "$calls" ] || [ -s "$out" ]; then
    fail "disabled script should be silent"
  fi
}

test_claude_and_codex_both_run
test_disable_silences_everything

if [ "$FAILURES" -ne 0 ]; then
  exit 1
fi

printf 'PASS auto-updater fixtures\n'
