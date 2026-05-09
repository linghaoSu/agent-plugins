# Release Gate

Use the release gate before committing or releasing plugin marketplace changes:

```bash
scripts/release-gate.sh --mode staged
```

Stage 1 is local, offline, and non-mutating. It does not install hooks, change
git state, call GitHub, or update plugin files.

## Modes

- `--mode staged` checks what is staged for commit. This is the default and
  uses `git diff --cached --check` for whitespace.
- `--mode working` checks unstaged tracked changes for whitespace and asks the
  secret scanner to include unstaged and untracked files.
- `--mode all` runs full-repo manifest, skill, and secret checks, and checks
  diff whitespace relative to `HEAD`. Use this before publishing a plugin
  release or doing push-time hardening.

`--strict` is accepted for forward compatibility. It has no effect in Stage 1
because advisory checks are not implemented yet.

`--json` emits the same Stage 1 check results as machine-readable JSON. Stage 3
will add dedicated fixture assertions around this output.

## Blocking Checks

| Check | What It Validates | Failure Exit |
|---|---|---|
| `manifest-json` | `.claude-plugin/marketplace.json` and every `*/.claude-plugin/plugin.json` parse with `jq empty`. | `1` |
| `skill-frontmatter` | Every `*/skills/*/SKILL.md` starts with frontmatter delimiters and has non-empty `name` and `description` keys. | `1` |
| `diff-whitespace` | Mode-specific git diff whitespace check passes. | `1` |
| `secret-scan` | `secret-scanner/scripts/scan.py --format json` reports no findings for the selected mode. | `1` |

Missing required tools (`git`, `jq`, `python3`) return exit `2`. A missing or
non-runnable blocking checker also returns exit `2`.

## Output

Human output groups the Stage 1 checks:

```text
Release gate: staged

Blocking
  PASS manifest-json: validated 10 manifest file(s)
  PASS skill-frontmatter: validated 27 skill file(s)
  PASS diff-whitespace: diff whitespace check passed
  PASS secret-scan: secret scan passed

Advisory
  <none>

Skipped
  <none>
```

Exit codes:

- `0`: all blocking checks passed.
- `1`: at least one blocking check failed.
- `2`: usage error, missing required command, or a blocking checker could not
  run.

## Stage Boundaries

Stage 1 intentionally excludes:

- runtime-aware wording advisory scans.
- hook robustness advisory scans.
- hook installation.
- CI wiring.
- release enforcement before `git push`.

Those belong to later roadmap stages after the blocking gate is stable.

## Idea-To-Ship Contract Fixtures

Critical idea-to-ship skill contracts have a separate offline fixture command:

```bash
bash tests/idea-to-ship-eval-fixtures.sh
```

This is currently a manually runnable contract check, not a blocking release
gate step. It validates that the `/roadmap`, `/test`, and `/review-code` skill
instructions still contain the required safety and traceability contracts. It
does not prove that a future live model run will obey those instructions.
