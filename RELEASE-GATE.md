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
| `skill-frontmatter` | Every `*/skills/*/SKILL.md` starts with frontmatter delimiters, parses as YAML, and has non-empty `name` and `description` keys. | `1` |
| `skill-metadata` | Every `*/skills/*/agents/openai.yaml` has the expected `interface` fields for UI metadata. | `1` |
| `diff-whitespace` | Mode-specific git diff whitespace check passes. | `1` |
| `secret-scan` | `secret-scanner/scripts/scan.py --format json` reports no findings for the selected mode. | `1` |
| `skill-hygiene-infra-drift` | In `--mode staged`, when staged changes touch skill-hygiene infrastructure, the corresponding worktree files match the index so staged gates do not validate mixed checker/fixture code. | `1` |
| `skill-topology-infra-drift` | In `--mode staged`, when staged changes touch skill-topology infrastructure, the corresponding worktree files match the index so staged gates do not validate mixed scanner/fixture code. | `1` |
| `skill-stats-cleaner-scope-drift` | In `--mode staged`, when staged changes touch skill-stats cleaner scope, the corresponding worktree files match the index so staged gates do not validate mixed wrapper/fixture code. | `1` |
| `agent-playbook-fixture-scope-drift` | In `--mode staged`, when staged changes touch agent-playbook fixture scope or broad-orchestrator scan surfaces, the corresponding worktree files match the index before worktree-based fixture scans run. | `1` |

Missing required tools (`git`, `jq`, `python3`) or the required Python `yaml`
module from PyYAML return exit `2`. A missing or non-runnable blocking checker
also returns exit `2`.

The gate validates the source checkout or staged index only. Installed plugin
caches are not mutated or synchronized by this script; after source
frontmatter changes, refresh installed/cache copies through the owning plugin
installation workflow before treating runtime loader warnings as resolved.

## Advisory Checks

Advisory checks report risk without changing the release gate exit code unless
`--strict` is set.

| Check | Mode | What It Validates | Failure Status |
|---|---|---|---|
| `skill-hygiene` | `staged`, `working`, `all` | Runs `python3 scripts/skill-hygiene-check.py --mode <mode> .` to flag overlong descriptions, SKILL.md bloat, repeated prompts/templates/contracts, unshared runtime routing, duplicated code-style lifecycle blocks, missing metadata, missing actionable usage, broken optional skill references, unsafe command examples, and unexplained placeholders. | `WARN` |
| `skill-hygiene-fixtures` | `all`, or `staged`/`working` when the diff touches skill-hygiene checker, fixture, release-gate, or release-gate docs scope | Runs `bash tests/skill-hygiene-check-fixtures.sh` so checker snapshot and existing-check regression fixtures stay intact. | `WARN` (`FAIL` with `--strict`) |
| `skill-hygiene-release-gate-fixtures` | `all`, or `staged`/`working` when the diff touches skill-hygiene checker, fixture, release-gate, or release-gate docs scope | Runs `bash tests/skill-hygiene-release-gate-fixtures.sh --self-check` so the release-gate fixture harness remains wired without recursively invoking the full release gate. | `WARN` (`FAIL` with `--strict`) |
| `skill-topology-fixtures` | `all`, or `staged`/`working` when the diff touches skill-topology scanner, fixture, release-gate, or release-gate docs scope | Runs `bash tests/skill-topology-scan-fixtures.sh` so the read-only topology scanner keeps reporting broken references, orphan skills, hub skills, skill-tree output, and README coverage gaps deterministically. | `WARN` (`FAIL` with `--strict`) |
| `skill-stats-cleaner-fixtures` | `all`, or `staged`/`working` when the diff touches `skill-stats`, skill-stats plugin metadata, marketplace metadata, `tests/skill-stats-cleaner-*`, release-gate wiring, README, or portfolio docs | Runs `bash tests/skill-stats-cleaner-fixtures.sh` so the skill-cleaner report/apply wrapper keeps its analyzer setup, evidence bundle, plan hash, approval, and scoped mutation fixtures intact. | `WARN` (`FAIL` with `--strict`) |
| `idea-to-ship-fixtures` | `all`, or `staged`/`working` when the diff touches `idea-to-ship/` or its fixture files | Runs `bash tests/idea-to-ship-eval-fixtures.sh` so critical idea-to-ship instruction contracts and artifact safety fixtures stay intact. | `WARN` (`FAIL` with `--strict`) |
| `agent-playbook-fixtures` | `all`, or `staged`/`working` when the diff touches agent-playbook fixture scope, `.idea-to-ship/ITS-ROADMAP-020/`, or a broad-orchestrator scan surface (`README.md`, `*/README.md`, `.claude-plugin/marketplace.json`, `*/.claude-plugin/plugin.json`, `*/skills/*/SKILL.md`, `*/skills/*/agents/openai.yaml`) | Runs `bash tests/agent-playbook-eval-fixtures.sh` so critical agent-playbook/tool-safety instruction contracts, orchestration-boundary guards, and skill metadata fixtures stay intact. | `WARN` (`FAIL` with `--strict`) |

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
  PASS skill-topology-fixtures: skill topology fixture checks passed
  PASS skill-stats-cleaner-fixtures: skill-stats cleaner fixture checks passed
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
`scripts/skill-authoring-baseline.txt`, `scripts/release-gate.sh`,
`tests/skill-hygiene-*`, or `RELEASE-GATE.md`.
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

The checker also warns on `moderate-skill-bloat` when a skill grows beyond 150
lines but remains below the hard oversized-skill limit. A visible
`## Hygiene Exception` section with a non-empty `moderate-skill-bloat:` reason
can suppress only that moderate warning; `oversized-skill` still fires above
250 lines.

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

The checker also applies stronger skill authoring checks to new or changed
skills. It warns when a skill lacks actionable usage/workflow guidance
(`missing-actionable-usage`), when an optional related-skill
reference is unknown (`broken-related-skill`),
and when command examples contain risky chained/destructive/heredoc forms or
unexplained placeholders (`unsafe-command-example`,
`unexplained-command-placeholder`).

Current legacy skills are recorded in `scripts/skill-authoring-baseline.txt` so
strict all-mode does not force a one-time catalog rewrite. The baseline applies
only to authoring-standard checks; existing hygiene checks still scan their
normal target set. Staged and working modes always check touched skill files, so
a baseline edit does not hide a weak changed skill. Accepted exceptions for
touched skills should be visible in that skill's `## Hygiene Exception`
section.

## Skill Topology Fixtures

The read-only skill topology scanner has a dedicated offline fixture command:

```bash
bash tests/skill-topology-scan-fixtures.sh
```

The scanner itself is report-only:

```bash
python3 scripts/skill-topology-scan.py .
```

It inventories local `*/skills/*/SKILL.md` files, renders a deterministic
Markdown skill tree, and reports broken skill references, orphan skills, hub
skills, and root README catalog coverage gaps. The release gate runs
`skill-topology-fixtures` in `--mode all`, and in `staged`/`working` mode when
the diff touches `scripts/skill-topology-scan.py`,
`tests/skill-topology-*`, `scripts/release-gate.sh`, or `RELEASE-GATE.md`.
In staged mode, the blocking `skill-topology-infra-drift` check fails before
handoff when those topology infrastructure paths are staged but differ from the
worktree copy.

## Idea-To-Ship Contract Fixtures

Critical idea-to-ship skill contracts have a separate offline fixture command:

```bash
bash tests/idea-to-ship-eval-fixtures.sh
```

This command is also run as the `idea-to-ship-fixtures` advisory check in
`scripts/release-gate.sh --mode all`, and in `staged`/`working` mode when the
diff touches `idea-to-ship/` or its fixture files. It validates that the
`/roadmap`, `/test`, `/visual-test`, and `/review --target code` instructions
still contain the required safety, visual-evidence, and traceability contracts,
and that current roadmap/test-plan artifacts satisfy the generated-marker,
draft-fallback, lane-schema, and traceability fixture checks. With `--strict`,
fixture regressions block the gate. It does not prove that a future live model
run will obey those instructions.

## Agent-Playbook Contract Fixtures

Critical agent-playbook workflow contracts have a separate offline fixture
command:

```bash
bash tests/agent-playbook-eval-fixtures.sh
```

This command is also run as the `agent-playbook-fixtures` advisory check in
`scripts/release-gate.sh --mode all`, and in `staged`/`working` mode when the
diff touches agent-playbook fixture scope: `agent-playbook/`, `antifragile/`,
`issue-evaluator/`, `skill-stats/`, `worktree-cleaner/`,
`.idea-to-ship/ITS-ROADMAP-020/`, root/plugin README files,
`.claude-plugin/marketplace.json`, plugin manifests, skill files, skill
`agents/openai.yaml`, or the fixture files. It validates the host-neutral role
and capability schema, unified harness and antifragile modes, commit and
tournament safety, deleted-skill absence, and the idea-to-ship consolidation
contracts. In staged mode, the blocking
`agent-playbook-fixture-scope-drift` check fails when a staged scan-surface file
differs from its worktree copy. With `--strict`, fixture regressions block the
gate.
