#!/usr/bin/env bash
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HELPER="$ROOT/tests/agent-playbook-eval-fixtures.py"

if ! command -v python3 >/dev/null 2>&1; then
  printf 'Missing required command: python3\n' >&2
  exit 2
fi

if [ ! -f "$HELPER" ]; then
  printf 'Missing eval fixture helper: %s\n' "$HELPER" >&2
  exit 2
fi

exec python3 "$HELPER" "$ROOT"
