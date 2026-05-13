#!/usr/bin/env bash
# Refresh local directory-marketplace plugins for every supported agent runtime
# present in the current environment. Missing runtimes or optional dependencies
# are silent no-ops because this script runs from SessionStart hooks.

set -u

TIMEOUT_SECONDS="${AUTO_UPDATER_TIMEOUT_SECONDS:-20}"
CLAUDE_TIMEOUT_SECONDS="${CLAUDE_AUTO_UPDATER_TIMEOUT_SECONDS:-$TIMEOUT_SECONDS}"
CODEX_TIMEOUT_SECONDS="${CODEX_AUTO_UPDATER_TIMEOUT_SECONDS:-$TIMEOUT_SECONDS}"
CLAUDE_KNOWN="${CLAUDE_AUTO_UPDATER_KNOWN:-$HOME/.claude/plugins/known_marketplaces.json}"
CODEX_CONFIG="${CODEX_AUTO_UPDATER_CONFIG:-$HOME/.codex/config.toml}"
CODEX_STATE="${CODEX_AUTO_UPDATER_STATE:-$HOME/.codex/plugins/auto-updater-codex-state.tsv}"
CODEX_CACHE_ROOT="${CODEX_AUTO_UPDATER_CACHE_ROOT:-$HOME/.codex/plugins/cache}"

[ "${AUTO_UPDATER_DISABLE:-}" = "1" ] && exit 0

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
    perl -e 'alarm shift; exec @ARGV; exit 127' "$seconds" "$@"
    return
  fi

  "$@"
}

updates=""

append_update() {
  local headline="$1"
  local detail="${2:-}"

  updates+="$headline"$'\n'
  if [ -n "$detail" ]; then
    updates+="$(printf '%s\n' "$detail" | sed 's/^/    /')"$'\n'
  fi
}

claude_plugin_source_path() {
  local marketplace_root="$1"
  local plugin_name="$2"

  [ -f "$marketplace_root/.claude-plugin/marketplace.json" ] || return 0
  jq -r --arg plugin "$plugin_name" '
    .plugins[]?
    | select(.name == $plugin)
    | .source // .path // empty
  ' "$marketplace_root/.claude-plugin/marketplace.json" 2>/dev/null | head -n 1
}

claude_dirty_paths() {
  local marketplace_root="$1"
  local plugin_rel="$2"

  if [ -n "$plugin_rel" ]; then
    git -C "$marketplace_root" status --porcelain --untracked-files=all -- \
      "$plugin_rel" ".claude-plugin/marketplace.json" 2>/dev/null || true
    return
  fi

  git -C "$marketplace_root" status --porcelain --untracked-files=all 2>/dev/null || true
}

run_claude_updates() {
  local plugins_json full_id staged_ver marketplace plugin_name src head_short plugin_rel dirty_paths reason out code

  [ "${CLAUDE_AUTO_UPDATER_DISABLE:-}" = "1" ] && return
  [ -f "$CLAUDE_KNOWN" ] || return
  command -v jq >/dev/null 2>&1 || return
  command -v git >/dev/null 2>&1 || return
  command -v claude >/dev/null 2>&1 || return

  plugins_json=$(run_with_timeout "$CLAUDE_TIMEOUT_SECONDS" claude plugin list --json 2>/dev/null) || return
  [ -z "$plugins_json" ] && return

  while IFS=$'\t' read -r full_id staged_ver; do
    [ -z "$full_id" ] && continue
    marketplace="${full_id##*@}"
    plugin_name="${full_id%@*}"

    src=$(jq -r --arg marketplace "$marketplace" \
      '.[$marketplace].source | select(.source=="directory") | .path // empty' \
      "$CLAUDE_KNOWN" 2>/dev/null)
    [ -z "$src" ] && continue
    [ -d "$src/.git" ] || continue

    head_short=$(git -C "$src" rev-parse --short=12 HEAD 2>/dev/null || true)
    [ -z "$head_short" ] && continue

    plugin_rel="$(claude_plugin_source_path "$src" "$plugin_name")"
    dirty_paths="$(claude_dirty_paths "$src" "$plugin_rel")"
    reason=""

    if [ "$head_short" != "$staged_ver" ]; then
      reason="${staged_ver:-unknown} -> $head_short"
    fi
    if [ -n "$dirty_paths" ]; then
      if [ -n "$reason" ]; then
        reason="$reason; dirty source changes"
      else
        reason="dirty source changes"
      fi
    fi
    if [ "${CLAUDE_AUTO_UPDATER_ALWAYS:-}" = "1" ] && [ -z "$reason" ]; then
      reason="forced refresh"
    fi
    [ -n "$reason" ] || continue

    out=$(run_with_timeout "$CLAUDE_TIMEOUT_SECONDS" claude plugin update "$full_id" 2>&1)
    code="$?"
    if [ "$code" -eq 0 ]; then
      append_update "- claude ${full_id}: ${reason}" "$out"
    else
      append_update "- claude ${full_id}: refresh failed (exit ${code})" "$out"
    fi
  done < <(printf '%s' "$plugins_json" | jq -r '.[] | "\(.id)\t\(.version // "")"' 2>/dev/null)
}

list_codex_local_plugins() {
  python3 - "$CODEX_CONFIG" <<'PY'
import json
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        sys.exit(0)

config = Path(sys.argv[1]).expanduser()
try:
    data = tomllib.loads(config.read_text(encoding="utf-8"))
except Exception:
    sys.exit(0)

plugins = data.get("plugins") or {}
plugin_enabled = {}

for full_id, plugin_config in plugins.items():
    if not isinstance(full_id, str) or "@" not in full_id:
        continue
    plugin_name, marketplace_name = full_id.rsplit("@", 1)
    if isinstance(plugin_config, dict) and plugin_config.get("enabled") is False:
        plugin_enabled[(marketplace_name, plugin_name)] = False
    else:
        plugin_enabled[(marketplace_name, plugin_name)] = True

for name, marketplace_config in (data.get("marketplaces") or {}).items():
    if not isinstance(marketplace_config, dict):
        continue
    if marketplace_config.get("source_type") != "local":
        continue
    source = marketplace_config.get("source")
    if not source:
        continue
    marketplace_root = Path(str(source)).expanduser()
    if not marketplace_root.is_absolute():
        marketplace_root = (config.parent / marketplace_root).resolve()
    manifest = marketplace_root / ".claude-plugin" / "marketplace.json"
    try:
        marketplace_data = json.loads(manifest.read_text(encoding="utf-8"))
    except Exception:
        continue

    for plugin in marketplace_data.get("plugins") or []:
        if not isinstance(plugin, dict):
            continue
        plugin_name = plugin.get("name")
        plugin_source = plugin.get("source") or plugin.get("path")
        if not plugin_name or not plugin_source:
            continue
        if plugin_enabled and plugin_enabled.get((name, plugin_name)) is not True:
            continue

        plugin_root = (marketplace_root / str(plugin_source)).resolve()
        plugin_manifest = plugin_root / ".claude-plugin" / "plugin.json"
        cache_version = "local"
        try:
            plugin_data = json.loads(plugin_manifest.read_text(encoding="utf-8"))
            cache_version = plugin_data.get("version") or "local"
        except Exception:
            pass

        print(f"{name}\t{marketplace_root}\t{plugin_name}\t{plugin_root}\t{cache_version}")
PY
}

codex_state_head() {
  local marketplace="$1"

  [ -f "$CODEX_STATE" ] || return 0
  awk -F '\t' -v marketplace="$marketplace" '$1 == marketplace { print $2; exit }' "$CODEX_STATE" 2>/dev/null
}

record_codex_state() {
  local marketplace="$1"
  local head_short="$2"
  local state_dir tmp_file

  [ -n "$head_short" ] || return
  state_dir="$(dirname "$CODEX_STATE")"
  mkdir -p "$state_dir" 2>/dev/null || return
  tmp_file="$(mktemp "${state_dir}/auto-updater-codex-state.XXXXXX" 2>/dev/null)" || return

  if [ -f "$CODEX_STATE" ]; then
    awk -F '\t' -v marketplace="$marketplace" '$1 != marketplace { print }' "$CODEX_STATE" >"$tmp_file" 2>/dev/null || true
  fi
  printf '%s\t%s\n' "$marketplace" "$head_short" >>"$tmp_file"
  mv "$tmp_file" "$CODEX_STATE" 2>/dev/null || rm -f "$tmp_file"
}

sync_codex_plugin_cache() {
  local marketplace="$1"
  local plugin_name="$2"
  local plugin_root="$3"
  local cache_version="$4"
  local cache_root dest

  [ -d "$plugin_root" ] || return 1
  command -v rsync >/dev/null 2>&1 || return 1

  cache_root="${CODEX_CACHE_ROOT%/}"
  dest="$cache_root/$marketplace/$plugin_name/$cache_version"
  case "$dest" in
    "$cache_root"/*) ;;
    *) return 1 ;;
  esac

  mkdir -p "$dest" || return 1
  rsync -a --delete --exclude='.git' "$plugin_root"/ "$dest"/
}

run_codex_updates() {
  local marketplace marketplace_root plugin_name plugin_root cache_version state_key head_short reason dirty_paths last_head out code

  [ "${CODEX_AUTO_UPDATER_DISABLE:-}" = "1" ] && return
  [ -f "$CODEX_CONFIG" ] || return
  command -v codex >/dev/null 2>&1 || return
  command -v python3 >/dev/null 2>&1 || return
  command -v git >/dev/null 2>&1 || return

  while IFS=$'\t' read -r marketplace marketplace_root plugin_name plugin_root cache_version; do
    [ -n "$marketplace" ] || continue
    [ -n "$plugin_name" ] || continue
    [ -d "$marketplace_root" ] || continue
    [ -d "$plugin_root" ] || continue
    if [ "${CODEX_AUTO_UPDATER_REQUIRE_GIT:-1}" = "1" ] && [ ! -d "$marketplace_root/.git" ]; then
      continue
    fi

    state_key="${marketplace}/${plugin_name}"
    head_short=""
    reason=""
    if [ -d "$marketplace_root/.git" ]; then
      head_short="$(git -C "$marketplace_root" rev-parse --short=12 HEAD 2>/dev/null || true)"
      dirty_paths="$(git -C "$marketplace_root" status --porcelain --untracked-files=all 2>/dev/null || true)"
      last_head="$(codex_state_head "$state_key")"
      if [ -n "$head_short" ] && [ "$head_short" != "$last_head" ]; then
        reason="${last_head:-unknown} -> $head_short"
      fi
      if [ -n "$dirty_paths" ]; then
        if [ -n "$reason" ]; then
          reason="$reason; dirty source changes"
        else
          reason="dirty source changes"
        fi
      fi
    else
      reason="local source refresh"
    fi
    if [ "${CODEX_AUTO_UPDATER_ALWAYS:-}" = "1" ] && [ -z "$reason" ]; then
      reason="forced refresh"
    fi
    [ -n "$reason" ] || continue

    out=$(sync_codex_plugin_cache "$marketplace" "$plugin_name" "$plugin_root" "$cache_version" 2>&1)
    code="$?"
    if [ "$code" -eq 0 ]; then
      record_codex_state "$state_key" "$head_short"
      append_update "- codex ${marketplace}/${plugin_name}: ${reason}" "$out"
    else
      append_update "- codex ${marketplace}/${plugin_name}: refresh failed (exit ${code})" "$out"
    fi
  done < <(list_codex_local_plugins 2>/dev/null)
}

run_claude_updates
run_codex_updates

if [ -n "$updates" ]; then
  printf 'Plugin auto-updater: refreshed local plugin marketplaces (restart to apply).\n%s' "$updates"
fi
