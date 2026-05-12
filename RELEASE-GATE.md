# Release Gate

Use the release gate before committing or releasing plugin marketplace changes:

```bash
scripts/release-gate.sh --mode staged
```

The release gate is local, offline, and non-mutating. It does not install hooks,
change git state, call GitHub, or update plugin files.

## Modes

- `--mode staged` checks what is staged for commit. This is the default and
  uses `git diff --cached --check` for whitespace.
- `--mode working` checks unstaged tracked changes for whitespace and asks the
  secret scanner to include unstaged and untracked files.
- `--mode all` runs full-repo manifest, skill, and secret checks, and checks
  diff whitespace relative to `HEAD`. Use this before publishing a plugin
  release or doing push-time hardening.

`--strict` is accepted for forward compatibility. Advisory checks remain
non-blocking in the current gate.

`--json` emits the same check results as machine-readable JSON, including
blocking, advisory, and skipped checks.

## Blocking Checks

| Check | What It Validates | Failure Exit |
|---|---|---|
| `manifest-json` | `.claude-plugin/marketplace.json` and every `*/.claude-plugin/plugin.json` parse with `jq empty`. | `1` |
| `skill-frontmatter` | Every `*/skills/*/SKILL.md` starts with frontmatter delimiters and has non-empty `name` and `description` keys. | `1` |
| `skill-metadata` | Every `*/skills/*/agents/openai.yaml` has the expected `interface` fields for UI metadata. | `1` |
| `diff-whitespace` | Mode-specific git diff whitespace check passes. | `1` |
| `secret-scan` | `secret-scanner/scripts/scan.py --format json` reports no findings for the selected mode. | `1` |

Missing required tools (`git`, `jq`, `python3`) return exit `2`. A missing or
non-runnable blocking checker also returns exit `2`.

## Advisory Checks

Advisory checks report risk without changing the release gate exit code.

| Check | Mode | What It Validates | Failure Status |
|---|---|---|---|
| `idea-to-ship-fixtures` | `all` | Runs `bash tests/idea-to-ship-eval-fixtures.sh` so critical idea-to-ship instruction contracts and artifact safety fixtures stay intact. | `WARN` |
| `agent-playbook-fixtures` | `all` | Runs `bash tests/agent-playbook-eval-fixtures.sh` so critical agent-playbook instruction contracts and skill metadata fixtures stay intact. | `WARN` |

## Secret Scan Hook Decision

Secret scanning is enforced through this command-based release gate, not through
repo-installed git hooks. The `secret-scanner` plugin still offers an explicit
opt-in `/install-precommit-hook` flow for local users, but hook installation is
not part of the repo-wide release gate unless explicitly approved later.

## Output

Human output groups blocking, advisory, and skipped checks:

```text
Release gate: staged

Blocking
  PASS manifest-json: validated 10 manifest file(s)
  PASS skill-frontmatter: validated 27 skill file(s)
  PASS skill-metadata: validated 2 skill metadata file(s)
  PASS diff-whitespace: diff whitespace check passed
  PASS secret-scan: secret scan passed

Advisory
  <none>

Skipped
  SKIP idea-to-ship-fixtures: runs only in --mode all
  SKIP agent-playbook-fixtures: runs only in --mode all
```

In `--mode all`, fixture checks appear under Advisory:

```text
Advisory
  PASS idea-to-ship-fixtures: idea-to-ship fixture checks passed
  PASS agent-playbook-fixtures: agent-playbook fixture checks passed
```

Exit codes:

- `0`: all blocking checks passed.
- `1`: at least one blocking check failed.
- `2`: usage error, missing required command, or a blocking checker could not
  run.

## Stage Boundaries

The current gate intentionally excludes:

- runtime-aware wording advisory scans.
- hook robustness advisory scans.
- hook installation.
- CI wiring.
- release enforcement before `git push`.

Those belong to later roadmap stages after the blocking gate and first advisory
fixture path stay stable.

## Idea-To-Ship Contract Fixtures

Critical idea-to-ship skill contracts have a separate offline fixture command:

```bash
bash tests/idea-to-ship-eval-fixtures.sh
```

This command is also run as the non-blocking `idea-to-ship-fixtures` advisory
check in `scripts/release-gate.sh --mode all`. It validates that the
`/roadmap`, `/test`, and `/review-code` skill instructions still contain the
required safety and traceability contracts, and that current roadmap/test-plan
artifacts satisfy the generated-marker, draft-fallback, lane-schema, and
traceability fixture checks. It does not prove that a future live model run
will obey those instructions.

## Agent-Playbook Contract Fixtures

Critical agent-playbook workflow contracts have a separate offline fixture
command:

```bash
bash tests/agent-playbook-eval-fixtures.sh
```

This command is also run as the non-blocking `agent-playbook-fixtures`
advisory check in `scripts/release-gate.sh --mode all`. It validates that the
`/vibe-coding-health-check` skill keeps its scorecard dimensions, safe routing,
stop rules, untracked-file handling, and artifact ownership contract, and that
skill `agents/openai.yaml` metadata follows the repo's expected interface
shape.
