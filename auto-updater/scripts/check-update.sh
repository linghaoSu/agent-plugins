#!/usr/bin/env bash
# Compare each plugin's currently-staged version (from `claude plugin list
# --json`) against the HEAD commit of its directory-source marketplace.
# If they differ, run `claude plugin update <plugin>@<marketplace>` so the
# next session picks up the new version.
#
# The hook's stdout is injected as a system reminder, so we stay silent
# when there is nothing to update.

set -u

KNOWN="$HOME/.claude/plugins/known_marketplaces.json"
TIMEOUT_SECONDS="${CLAUDE_AUTO_UPDATER_TIMEOUT_SECONDS:-20}"

[ "${CLAUDE_AUTO_UPDATER_DISABLE:-}" = "1" ] && exit 0
[ -f "$KNOWN" ] || exit 0
command -v jq >/dev/null 2>&1 || exit 0
command -v git >/dev/null 2>&1 || exit 0
command -v claude >/dev/null 2>&1 || exit 0

run_with_timeout() {
  seconds="$1"
  shift

  case "$seconds" in
    ''|*[!0-9]*)
      "$@"
      return
      ;;
  esac

  if command -v timeout >/dev/null 2>&1; then
    timeout "$seconds" "$@"
    return
  fi

  if command -v gtimeout >/dev/null 2>&1; then
    gtimeout "$seconds" "$@"
    return
  fi

  if command -v perl >/dev/null 2>&1; then
    perl -e 'alarm shift; exec @ARGV' "$seconds" "$@"
    return
  fi

  "$@"
}

plugins_json=$(run_with_timeout "$TIMEOUT_SECONDS" claude plugin list --json 2>/dev/null) || exit 0
[ -z "$plugins_json" ] && exit 0

updates=""

while IFS=$'\t' read -r full_id staged_ver; do
  [ -z "$full_id" ] && continue
  marketplace="${full_id##*@}"

  src=$(jq -r --arg m "$marketplace" \
    '.[$m].source | select(.source=="directory") | .path // empty' \
    "$KNOWN" 2>/dev/null)
  [ -z "$src" ] && continue
  [ -d "$src/.git" ] || continue

  head_short=$(git -C "$src" rev-parse --short=12 HEAD 2>/dev/null || true)
  [ -z "$head_short" ] && continue

  if [ "$head_short" != "$staged_ver" ]; then
    out=$(run_with_timeout "$TIMEOUT_SECONDS" claude plugin update "$full_id" 2>&1 || true)
    updates+="- ${full_id}: ${staged_ver} → ${head_short}"$'\n'
    if [ -n "$out" ]; then
      updates+="$(printf '%s\n' "$out" | sed 's/^/    /')"$'\n'
    fi
  fi
done < <(printf '%s' "$plugins_json" | jq -r '.[] | "\(.id)\t\(.version)"' 2>/dev/null)

if [ -n "$updates" ]; then
  printf 'Plugin auto-updater: pulled newer commits (restart to apply).\n%s' "$updates"
fi
