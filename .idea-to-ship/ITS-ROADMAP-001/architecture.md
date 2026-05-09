# Architecture - Repo-Wide Plugin Release Gates

**Slug:** ITS-ROADMAP-001
**Date:** 2026-05-09
**Status:** reviewed
**References:** requirements.md, `../roadmap.md`

## Summary

Build a repo-owned release gate around a single local command and a short
operator document. The recommended approach is **Option B: versioned gate
script plus release-gate documentation**. It keeps the first gate deterministic,
offline, and easy to run, while leaving hooks and CI as later rollout steps.

## Goals / Non-Goals

Goals:

- Make release checks repeatable for marketplace, plugin, skill, hook, and
  secret-scanner changes.
- Keep the first gate local, offline, and non-mutating by default.
- Separate blocking checks from advisory checks so adoption does not stall on
  checks that still need tuning.
- Produce a design that later implementation can build without re-deriving the
  command surface or check boundaries.

Non-goals:

- No release gate script is implemented in this step.
- No pre-commit/pre-push hook is installed in this step.
- No CI workflow is introduced in this step.
- No GitHub issue/PR/milestone access is required for the first gate.

## Codebase Context

The repo is a plugin marketplace with independent plugin directories:

- `.claude-plugin/marketplace.json` - repo-level plugin inventory.
- `*/.claude-plugin/plugin.json` - per-plugin manifests.
- `*/skills/*/SKILL.md` - skill definitions with YAML-like frontmatter.
- `auto-updater/hooks/hooks.json` and `skill-stats/hooks/hooks.json` -
  installed hook definitions.
- `auto-updater/scripts/check-update.sh` - SessionStart hook script that
  depends on `jq`, `git`, and `claude`, and intentionally exits cleanly when
  optional prerequisites are missing.
- `skill-stats/scripts/track-skill.sh` - PostToolUse hook script that appends
  to `~/.claude/skill-stats.jsonl`.
- `secret-scanner/scripts/scan.py` - standalone scanner with `--mode staged`,
  `--mode working`, `--mode all`, and `--format json`.
- `antifragile/skills/antifragile-agent/SKILL.md` - existing audit rubric for
  hook robustness, state pollution, and dependency fragility.

Conventions to honor:

- Skills are artifact-first and should not auto-commit or auto-push.
- Hook failures should fail locally and avoid blocking sessions on optional
  dependencies.
- Release gates should be objective commands rather than model self-grading.
- Current repo has no package manager, test runner, or CI framework to extend.

## Alternatives Considered

### Option A - Documentation-Only Release Checklist

A markdown file, for example `RELEASE-GATE.md`, lists every command an operator
should run before committing or pushing plugin changes.

**Module changes:** add `RELEASE-GATE.md`; no script.

**Data flow:** human reads checklist -> runs commands manually -> copies results
into handoff/commit summary.

**Interfaces:** no command interface; only documented snippets.

**Pros:**

- Lowest implementation cost.
- No new dependency surface.
- Easy to edit as the release process changes.

**Cons:**

- Still relies on memory and manual command ordering.
- Harder for agents to run consistently.
- Cannot easily separate blocking/advisory results in one report.

**Risk:** medium. The repo already reached the point where manual validation is
drifting; documentation alone does not materially improve enforcement.

### Option B - Versioned Gate Script Plus Documentation

Add a repo-owned script, for example `scripts/release-gate.sh`, plus a short
document, for example `RELEASE-GATE.md`. The script runs deterministic local
checks and prints a compact blocking/advisory report. The document explains
when to run it, how to interpret failures, and how future checks graduate from
advisory to blocking.

**Module changes:**

- `scripts/release-gate.sh` - future local gate entry point.
- `RELEASE-GATE.md` - future operator contract and troubleshooting guide.
- No changes to existing hooks in the first implementation stage.

**Data flow:**

```text
operator/agent
  -> scripts/release-gate.sh [--mode staged|working|all] [--strict]
      -> manifest JSON validation
      -> skill frontmatter validation
      -> git diff whitespace validation
      -> secret scan
      -> stale runtime-aware wording scan
      -> hook robustness static checks or advisory handoff
  -> concise result: blocking failures, advisory warnings, skipped checks
```

**Interfaces:**

```bash
scripts/release-gate.sh [--mode staged|working|all] [--strict] [--json]
```

- `--mode staged` checks what is about to be committed.
- `--mode working` checks unstaged and untracked work.
- `--mode all` checks the full tracked repo where practical.
- Default mode is `staged`.
- `--strict` upgrades selected advisory checks to blocking.
- `--json` emits machine-readable output for later eval fixtures or CI.

Mode semantics are check-specific:

| Check | `staged` | `working` | `all` |
|---|---|---|---|
| `manifest-json` | all repo manifests | all repo manifests | all repo manifests |
| `skill-frontmatter` | all repo skills | all repo skills | all repo skills |
| `diff-whitespace` | `git diff --cached --check` | `git diff --check` | `git diff --check HEAD` |
| `secret-scan` | scanner `--mode staged` | scanner `--mode working` | scanner `--mode all` |
| `runtime-aware-wording` | changed files only | changed and untracked files | all tracked docs/manifests/skills |
| `hook-robustness` | changed hook files only | changed and untracked hook files | all hook files |

`--mode all` is opt-in. It is useful for periodic hardening, not the default
command before every commit. `diff-whitespace` remains diff-based even in
`--mode all`; it checks changes relative to `HEAD`, not every unchanged line
already in history.

Operator guidance for the future `RELEASE-GATE.md`:

- Before commit: run `scripts/release-gate.sh --mode staged`.
- Before publishing a plugin release or pushing a release branch: run
  `scripts/release-gate.sh --mode all`.
- Before handing off dirty local work: run `scripts/release-gate.sh --mode working`.

The first implementation intentionally does not include a `--range <base..head>`
mode for only unpushed commits. Add that later if full-repo scanning is too
expensive for push-time use.

Initial blocking checks:

- `manifest-json`: validate `.claude-plugin/marketplace.json` and every
  `*/.claude-plugin/plugin.json` with `jq empty`, independent of `--mode`.
- `skill-frontmatter`: validate every `*/skills/*/SKILL.md` frontmatter
  structurally, independent of `--mode`. Blocking requirements are opening and
  closing `---` delimiters plus non-empty `name` and `description` keys. Do
  not require a full YAML parser in the first implementation.
- `diff-whitespace`: run the mode-specific git diff whitespace check described
  below. `--mode staged` must use `git diff --cached --check`; plain
  `git diff --check` is not sufficient for a pre-commit gate.
- `secret-scan`: run
  `python3 secret-scanner/scripts/scan.py --mode <mode> --format json`, capture
  its output, and translate its exit code into the release-gate result instead
  of letting shell `set -e` terminate before the report is printed.

Initial advisory checks:

- `runtime-aware-wording`: targeted scan of marketplace/plugin descriptions,
  READMEs, and skill descriptions for stale Codex-only wording such as
  "Codex-only", "requires Codex", or "via Codex" when the surrounding text is
  meant to describe runtime-aware behavior. Do not scan arbitrary prose for the
  word "Codex"; that will be noisy and punish accurate runtime-specific notes.
- `hook-robustness`: when hook definitions or hook scripts are in the selected
  change set, warn if scripts lack dependency guards for external commands,
  appear to mutate git state, or perform network calls without a bounded
  failure path.
- reminder to run `antifragile-agent` when hook files changed.

**Pros:**

- One command is easy for humans and agents to run.
- Keeps the first implementation offline and non-mutating.
- Provides a stable seam for future eval fixtures and CI.
- Can adopt checks incrementally by warning first, then promoting to blocking.

**Cons:**

- Introduces a script that itself needs maintenance.
- Needs careful dependency handling across macOS/Linux.
- Static hook checks can become noisy if they overfit shell text patterns.

**Risk:** medium. The main risk is making the script too broad. Keep stage 1
small and explicit; do not encode the full antifragile audit in the first gate.

### Option C - Pre-Commit / Pre-Push Gate

Install or document hooks so checks run automatically before commit or push.
This could use the existing secret-scanner install flow and add a repo-level
hook that calls the release gate script.

**Module changes:**

- `.pre-commit-config.yaml` or hook-install skill changes.
- Possible `.secret-scanner/scan.py` copy if using the existing scanner hook
  installation pattern.
- A release gate script may still be needed as the hook target.

**Data flow:** git commit/push -> hook -> release gate checks -> block or warn.

**Interfaces:**

```bash
pre-commit run --all-files
git commit
git push
```

**Pros:**

- Strongest enforcement once adopted.
- Reduces reliance on agents remembering to run the gate.
- Can reuse secret-scanner's hook installation design.

**Cons:**

- Mutates developer environment and can block normal work.
- Native git hooks are not versioned; pre-commit adds a team workflow decision.
- Too aggressive for the first release-gate design because hook robustness is
  itself still on the roadmap.

**Risk:** high for initial rollout. Hook changes have broad blast radius and
should follow an explicit baseline script.

## Recommendation

**We pick Option B.** A versioned local gate script plus a short release-gate
document gives the repo one repeatable command without immediately committing
to hooks or CI. The tradeoff accepted is that enforcement is still voluntary in
the first stage, but the command surface is stable enough to become a hook or
CI job later.

## Chosen Design - Detail

### Module Breakdown

- `scripts/release-gate.sh` - future shell entry point. Runs checks, classifies
  results as blocking/advisory/skipped, exits non-zero only on blocking
  failures.
- `RELEASE-GATE.md` - future operator document. Defines when to run the gate,
  what each check means, and how advisory checks graduate to blocking.
- `secret-scanner/scripts/scan.py` - reused as-is for secret scanning.
- `antifragile/skills/antifragile-agent/SKILL.md` - reused as a manual audit
  handoff for hook changes; not embedded wholesale in the first script.

### Data Flow

```text
release author
  -> scripts/release-gate.sh --mode staged
      -> resolve repo root
      -> check required commands
      -> run blocking checks
      -> run advisory checks
      -> print grouped report
      -> exit 0 only when blocking checks pass
```

The script should never stage files, commit, push, install hooks, update
plugins, or call GitHub.

### Interfaces

Primary command:

```bash
scripts/release-gate.sh [--mode staged|working|all] [--strict] [--json]
```

Default mode is `staged`. The future `RELEASE-GATE.md` should document
`staged` for pre-commit checks, `working` for dirty handoffs, and explicit
`all` for plugin release or push-time hardening.

Exit codes:

- `0`: blocking checks passed.
- `1`: at least one blocking check failed.
- `2`: usage error or required tool for a blocking check is missing.

Human output shape:

```text
Release gate: <mode>

Blocking
  PASS manifest-json
  PASS skill-frontmatter
  PASS diff-whitespace
  PASS secret-scan

Advisory
  WARN runtime-aware-wording: <N> matches
  WARN hook-robustness: hook files changed; run antifragile-agent

Skipped
  <none | reason>
```

JSON output shape for `--json`:

```json
{
  "mode": "staged",
  "strict": false,
  "checks": [
    {
      "id": "manifest-json",
      "category": "blocking",
      "status": "pass",
      "message": "validated 8 manifests",
      "evidence": [],
      "command": "jq empty ...",
      "exit_code": 0
    },
    {
      "id": "runtime-aware-wording",
      "category": "advisory",
      "status": "warn",
      "message": "2 stale runtime wording matches",
      "evidence": ["issue-evaluator/README.md:9"],
      "command": "rg ...",
      "exit_code": 0
    }
  ]
}
```

Allowed statuses are `pass`, `fail`, `warn`, and `skip`. Future fixtures should
assert `id`, `category`, `status`, and key evidence fields; human prose remains
free to change.

### Data / Schema Changes

None. The gate reads repo files and prints results. It does not create or
modify persistent state.

### Failure Modes & Handling

- Missing `jq`: exit `2` because manifest validation is blocking.
- Missing `python3`: exit `2` because secret scanning is blocking.
- Missing `rg`: either use `grep` fallback for advisory scans or mark advisory
  check skipped.
- Malformed manifest JSON: blocking failure with file path.
- Malformed skill frontmatter: blocking failure with file path and the missing
  delimiter/key. Full YAML syntax errors are not blocking until a portable
  parser is deliberately introduced.
- Secret scanner findings: blocking failure with scanner-provided redacted JSON
  by default. The release-gate script must capture scanner stdout/stderr and
  include the redacted evidence in its grouped report.
- Hook files changed: advisory warning to run `antifragile-agent`; `--strict`
  may turn hook robustness warnings into blocking once ITS-ROADMAP-004 defines
  the exact promotion rule.
- Runtime-aware wording matches: advisory warning initially; can become
  blocking after ITS-ROADMAP-003 provides the canonical runtime-aware wording.

### Rollout / Migration

Stage 1 should land only the script and documentation. No hooks, no CI, no
automatic enforcement.

After the script proves stable:

1. `ITS-ROADMAP-003` can remove stale runtime-aware wording and make that scan
   blocking.
2. `ITS-ROADMAP-004` can feed hook audit results back into the release gate.
3. `ITS-ROADMAP-006` can add fixture tests around the script's `--json` output.
4. `ITS-ROADMAP-007` can decide whether secret scanning remains a release
   command or becomes a hook.

### Test Strategy Hooks

- Unit-like shell tests can run the gate in a temporary copy or fixture repo.
- `--json` is the seam for assertions; tests should assert check IDs/statuses,
  not prose.
- Fixture cases:
  - valid repo returns pass.
  - malformed plugin JSON fails `manifest-json`.
  - malformed skill frontmatter fails `skill-frontmatter`.
  - staged whitespace error fails `diff-whitespace` via
    `git diff --cached --check`.
  - unstaged whitespace error fails `diff-whitespace` via `git diff --check`.
  - fake secret fixture fails `secret-scan` with redacted output.
  - hook file change emits advisory `hook-robustness`.
  - runtime wording fixture warns only on targeted stale phrases, not every
    legitimate mention of Codex.

## Staged Implementation Plan

1. **Stage 1 - Release gate contract:** Add `RELEASE-GATE.md` and a minimal
   `scripts/release-gate.sh` with manifest JSON, frontmatter, diff whitespace,
   and secret scan blocking checks. No hooks.
2. **Stage 2 - Advisory scans:** Add runtime-aware wording scan and hook-change
   advisory warnings. Keep them non-blocking until their false-positive rate is
   understood.
3. **Stage 3 - Machine-readable output:** Add `--json` output and fixture-based
   smoke tests for the gate command. The fixtures should exercise the status
   schema before any CI or hook integration depends on it.
4. **Stage 4 - Promotion decisions:** After ITS-ROADMAP-003 and
   ITS-ROADMAP-004, decide which advisory checks become blocking and whether
   secret scanning should move into a hook.

## Open Questions

- Should `secret-scan` be blocking for `--mode staged` from the first
  implementation, or advisory until false positives are reviewed? The
  recommendation is blocking for staged changes because redaction is already
  built in.
- Should `--mode all` run secret scanning as part of the default operator
  command? The recommendation is no for the first stage; `--mode all` exists
  for explicit periodic hardening because full-repo scanning can be noisy.
- Should frontmatter validation require a real YAML parser later? The
  recommendation is no for the first stage. Start with structural validation
  plus required-key checks, then upgrade only if malformed YAML becomes a real
  failure mode and the parser dependency is chosen deliberately.
