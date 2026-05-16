# Release Gate

Use the release gate before committing or releasing plugin marketplace changes:

```bash
scripts/release-gate.sh --mode staged
scripts/release-gate.sh --mode all --strict
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

`--strict` upgrades advisory warnings to failures. Use it before publishing or
when a staged/working diff touches skill contracts.

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
| `skill-hygiene-infra-drift` | In `--mode staged`, when staged changes touch skill-hygiene infrastructure, the corresponding worktree files match the index so staged gates do not validate mixed checker/fixture code. | `1` |

Missing required tools (`git`, `jq`, `python3`) return exit `2`. A missing or
non-runnable blocking checker also returns exit `2`.

## Advisory Checks

Advisory checks report risk without changing the release gate exit code unless
`--strict` is set.

| Check | Mode | What It Validates | Failure Status |
|---|---|---|---|
| `skill-hygiene` | `staged`, `working`, `all` | Runs `python3 scripts/skill-hygiene-check.py --mode <mode> .` to flag noisy skill routing: overlong frontmatter descriptions, moderate or oversized `SKILL.md` files, repeated inline prompts/templates, repeated inline output contracts, long runtime-routing sections that do not cite a shared `WORKFLOW-CONTRACTS.md`, duplicated code-style lifecycle blocks, and newly-added skills without `agents/openai.yaml`. | `WARN` |
| `skill-hygiene-fixtures` | `all`, or `staged`/`working` when the diff touches skill-hygiene checker, fixture, release-gate, or release-gate docs scope | Runs `bash tests/skill-hygiene-check-fixtures.sh` so checker snapshot and existing-check regression fixtures stay intact. | `WARN` (`FAIL` with `--strict`) |
| `skill-hygiene-release-gate-fixtures` | `all`, or `staged`/`working` when the diff touches skill-hygiene checker, fixture, release-gate, or release-gate docs scope | Runs `bash tests/skill-hygiene-release-gate-fixtures.sh --self-check` so the release-gate fixture harness remains wired without recursively invoking the full release gate. | `WARN` (`FAIL` with `--strict`) |
| `idea-to-ship-fixtures` | `all`, or `staged`/`working` when the diff touches `idea-to-ship/` or its fixture files | Runs `bash tests/idea-to-ship-eval-fixtures.sh` so critical idea-to-ship instruction contracts and artifact safety fixtures stay intact. | `WARN` (`FAIL` with `--strict`) |
| `agent-playbook-fixtures` | `all`, or `staged`/`working` when the diff touches agent-playbook fixture scope | Runs `bash tests/agent-playbook-eval-fixtures.sh` so critical agent-playbook/tool-safety instruction contracts and skill metadata fixtures stay intact. | `WARN` (`FAIL` with `--strict`) |

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
  PASS skill-hygiene: skill hygiene checks passed

Skipped
  SKIP idea-to-ship-fixtures: no staged diff touches idea-to-ship fixture scope
  SKIP agent-playbook-fixtures: no staged diff touches agent-playbook fixture scope
```

In `--mode all`, fixture checks appear under Advisory:

```text
Advisory
  PASS skill-hygiene: skill hygiene checks passed
  PASS skill-hygiene-fixtures: skill hygiene fixture checks passed
  PASS skill-hygiene-release-gate-fixtures: skill hygiene release-gate fixture self-check passed
  PASS idea-to-ship-fixtures: idea-to-ship fixture checks passed
  PASS agent-playbook-fixtures: agent-playbook fixture checks passed
```

Exit codes:

- `0`: all blocking checks passed.
- `1`: at least one blocking check failed, or an advisory warning was upgraded
  by `--strict`.
- `2`: usage error, missing required command, or a blocking checker could not
  run.

## Stage Boundaries

The current gate intentionally excludes:

- hook robustness advisory scans.
- hook installation.
- CI wiring.
- release enforcement before `git push`.

Those belong to later roadmap stages after the blocking gate and first advisory
fixture path stay stable.

## Skill Hygiene Fixtures

Skill hygiene checker fixtures have two offline commands:

```bash
bash tests/skill-hygiene-check-fixtures.sh
bash tests/skill-hygiene-release-gate-fixtures.sh
```

`skill-hygiene-fixtures` runs the checker fixture command in
`scripts/release-gate.sh --mode all`, and in `staged`/`working` mode when the
diff touches skill hygiene infrastructure: `scripts/skill-hygiene-check.py`,
`scripts/release-gate.sh`, `tests/skill-hygiene-*`, or `RELEASE-GATE.md`.
In staged mode, the blocking `skill-hygiene-infra-drift` check fails before
handoff when those canonical infrastructure paths are staged but differ from the
worktree copy.

`skill-hygiene-release-gate-fixtures` runs only
`bash tests/skill-hygiene-release-gate-fixtures.sh --self-check` from inside
the release gate. That self-check validates release-gate wiring and expected
advisory IDs without invoking `scripts/release-gate.sh`, so it cannot recurse.
The full `bash tests/skill-hygiene-release-gate-fixtures.sh` command may invoke
the real release gate and is intended for explicit implementation and final
regression verification.

The checker also warns on `moderate-skill-bloat` when a skill grows beyond 400
lines but remains below the hard oversized-skill limit. A visible
`## Hygiene Exception` section with a non-empty `moderate-skill-bloat:` reason
can suppress only that moderate warning; `oversized-skill` still fires above
750 lines.

The checker warns on `repeated-inline-prompt` when prompt-like blocks are
duplicated exactly in the same skill, copied exactly into a changed target
skill, or repeated as a bounded same-file near-duplicate. The remediation is
to extract reusable prompt text to a prompt artifact or cite a shared contract.

The checker warns on `repeated-inline-template` when template/report-wrapper
blocks are duplicated exactly in the same skill, copied exactly into a changed
target skill, or repeated as a bounded same-file near-duplicate. The
remediation is to extract reusable template text to a template artifact or cite
a shared contract.

The checker warns on `repetition-scan-limited` when prompt or template
near-duplicate coverage is bounded by deterministic comparison budgets while at
least two plausible same-family candidates remain. A visible
`## Hygiene Exception` section can suppress only this checker-health warning
when it includes both a
non-empty `repetition-scan-limited:` reason and `reviewed-with:` or
`cap-evidence:` evidence.

## Idea-To-Ship Contract Fixtures

Critical idea-to-ship skill contracts have a separate offline fixture command:

```bash
bash tests/idea-to-ship-eval-fixtures.sh
```

This command is also run as the `idea-to-ship-fixtures` advisory check in
`scripts/release-gate.sh --mode all`, and in `staged`/`working` mode when the
diff touches `idea-to-ship/` or its fixture files. It validates that the
`/roadmap`, `/test`, and `/review-code` skill instructions still contain the
required safety and traceability contracts, and that current roadmap/test-plan
artifacts satisfy the generated-marker, draft-fallback, lane-schema, and
traceability fixture checks. With `--strict`, fixture regressions block the
gate. It does not prove that a future live model run will obey those
instructions.

## Agent-Playbook Contract Fixtures

Critical agent-playbook workflow contracts have a separate offline fixture
command:

```bash
bash tests/agent-playbook-eval-fixtures.sh
```

This command is also run as the `agent-playbook-fixtures` advisory check in
`scripts/release-gate.sh --mode all`, and in `staged`/`working` mode when the
diff touches agent-playbook fixture scope: `agent-playbook/`, `antifragile/`,
`issue-evaluator/`, `skill-stats/`, `worktree-cleaner/`, or the fixture files.
It validates that `/vibe-coding-health-check` keeps its scorecard dimensions,
safe routing, stop rules, untracked-file handling, and artifact ownership
contract; that cross-plugin safety gates remain documented; that worktree
cleanup, issue-fix worktree setup, and PR-comment edit gates keep their
behavior scenarios; and that skill `agents/openai.yaml` metadata follows the
repo's expected interface shape. With `--strict`, fixture regressions block the
gate.
