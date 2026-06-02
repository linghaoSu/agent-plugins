# Architecture - Skill Cleaner Wrapper For Skill Stats

**Slug:** ITS-ROADMAP-021
**Date:** 2026-06-01
**Status:** complete
**References:** requirements.md

## Summary

Build the skill-cleaner integration as a local guarded adapter inside the
existing `skill-stats` plugin. The chosen approach adds a small Python wrapper
script that validates the user-configured external `skill-cleaner` analyzer,
runs it through an allowlisted command shape, normalizes bounded report output,
and enforces a separate apply-plan schema with an immutable plan hash.
`skill-stats` remains report-only by default. The current-session `/plan`
approval gate is enforced by the skill workflow, while the wrapper enforces the
machine-checkable boundaries: hash, schema, roots, preconditions, target scope,
and no commit or push behavior.

## Goals / Non-Goals

Goals:

- Extend the existing public `skill-stats` skill instead of adding a new public
  skill entry.
- Preserve the current usage-statistics path while adding a separate
  skill-cleaner report mode.
- Use a user-configured external analyzer path, with `--analyzer` taking
  precedence over `SKILL_STATS_CLEANER_ANALYZER`.
- Keep default skill-cleaner runs non-mutating and bounded.
- Make personal roots, archive/deep logs, and cleanup application explicit.
- Require a concrete plan plus current-session `/plan` approval before any
  delete, description edit, or config-disable mutation.
- Add deterministic fixtures that cover missing analyzer, malformed output,
  duplicate/kept-copy safety, symlink roots, explicit personal roots,
  truncation, report-only dry run, confirmation refusal, and apply scoping.

Non-goals:

- No vendored copy of `steipete/agent-scripts` in this repo.
- No `.claude/workflows/` artifact or Claude Code dynamic workflow dependency
  in the first pass.
- No release-gate blocker based on personal skill roots or local personal logs.
- No automatic cleanup, commit, push, hook install, or GitHub mutation.
- No replacement for repo-local `scripts/skill-hygiene-check.py`,
  `scripts/skill-topology-scan.py`, or `agent-playbook:context-audit`.

## Codebase Context

Exploration was done in main context because no runtime-native Explore
sub-agent is available in this host. Relevant files and conventions:

- `skill-stats/skills/skill-stats/SKILL.md` is currently a Bash/Read skill
  with no argument surface. It reads `~/.claude/skill-stats.jsonl` with `jq`,
  compares against model-visible installed skills, and declares itself
  read-only and conversation-only.
- `skill-stats/WORKFLOW-CONTRACTS.md` currently fixes `mode: read-only` and
  `outputs_written: []`, with budgets for top 20 usage entries, top 20 stale
  skills, and 50 never-called skills. This contract must be split into
  usage-stats, skill-cleaner-report, skill-cleaner-plan, and
  skill-cleaner-apply modes.
- `skill-stats/scripts/track-skill.sh` is a PostToolUse hook writer. It appends
  JSONL to `~/.claude/skill-stats.jsonl`; it should remain unchanged except for
  documentation references if needed.
- `skill-stats/hooks/hooks.json` wires only the tracking hook. The new analyzer
  wrapper is user-invoked through the skill and should not become a hook.
- `worktree-cleaner/skills/clean-worktrees/SKILL.md` and
  `worktree-cleaner/WORKFLOW-CONTRACTS.md` provide the closest local precedent:
  report-only default, `--apply` only entering a confirmation gate, explicit
  safety summary, and `outputs_written: []` until confirmed mutation.
- `tests/agent-playbook-eval-fixtures.py` already guards skill-stats output
  contract text and worktree-cleaner apply-confirm behavior. It can keep
  contract-level checks, but script behavior should live in a focused
  skill-stats fixture.
- `scripts/release-gate.sh` has advisory fixture wiring patterns for
  agent-playbook, idea-to-ship, skill hygiene, and skill topology. A new
  `skill-stats-cleaner-fixtures` advisory check should run in `--mode all` and
  when the diff touches `skill-stats`, the new fixture files, release-gate
  wiring, README, or portfolio docs.
- `README.md` and `PORTFOLIO.md` currently describe the user-facing
  `skill-stats` skill as read-only. They must be updated once apply-confirm is
  introduced.
- The external `skill-cleaner` SKILL describes a Node command using
  `node --experimental-strip-types .../skill-cleaner.ts`, report sections named
  Skill Budget, Description candidates, Duplicates, Unused candidates, and Root
  summary, default normal Codex/plugin/repo roots, opt-in `--root`, realpath
  root dedupe, heuristic usage evidence, and suggest-before-edit cleanup
  policy.
- Claude Code dynamic workflows are only a design influence here. They move the
  orchestration plan into a rerunnable script and require plan approval before
  a run, but they also have no mid-run user input. That reinforces a two-stage
  report/plan and later apply split rather than a single long run.

## Cross-Skill Routing

| Signal | Routed skill | Result | Design impact |
|---|---|---|---|
| External Node analyzer dependency, missing runtime/path, malformed output, bounded fallback | `antifragile:antifragile-system` | Same-context read-only resilience pass applied; no separate artifact written. | Add analyzer path resolution, no shell command interpolation, `node` availability checks, timeout, bounded stdout/stderr, typed `needs_user`/`degraded` results, and no cleanup authority from failed analyzer output. |
| Delete/edit/disable apply behavior against repo or personal roots | `antifragile:antifragile-system` | Same-context read-only data-safety pass applied. | Split plan validation from apply, require current-session approval of a plan hash, validate every target against explicit roots, require rollback notes, verify kept copies for duplicate deletes, and forbid git commit/push. |
| External analyzer report is tool output that an agent may turn into a cleanup plan | `harness-engineering:sprint-contract` | Recommended but not run; it would create a separate `.harness-engineering` artifact and is larger than this first-pass design needs. | Encode the evaluator contract in deterministic fixtures, skill text, and the apply plan schema: machine checks first; current-session `/plan` approval remains a skill-level gate. |
| Secrets/credentials in generated examples | none | No credential, webhook, signing-key, or secret-storage change is part of architecture. | Do not run `secret-scanner:scan-secrets` at architecture time; rely on release gate for implementation diffs and keep examples redacted/path-generic. |

## Alternatives Considered

### Option A - Prompt-Only External Analyzer Instructions

Modify `skill-stats/skills/skill-stats/SKILL.md` so the agent directly runs the
external `node --experimental-strip-types .../skill-cleaner.ts` command and
manually summarizes its output.

**Module changes:** `skill-stats/skills/skill-stats/SKILL.md`,
`skill-stats/WORKFLOW-CONTRACTS.md`, README/portfolio docs, fixture text
updates.

**Data flow:** User invokes `skill-stats --cleaner`; the skill resolves an
analyzer path from the prompt/environment, runs Node directly, reads stdout,
and writes a conversation report. Apply behavior is described as manual
instructions in the skill.

**Interfaces:** Skill arguments only: `--cleaner`, `--analyzer`, `--root`,
`--deep-logs`, `--no-logs`, `--months`, `--apply`.

**Pros:**

- Smallest code diff.
- No new repo script or parser to maintain.
- Closest to the external SKILL's documented workflow.

**Cons:**

- Hard to fixture real behavior because the safety logic lives in prose.
- No deterministic target validation for apply mode.
- Easy for future edits to drift into unbounded command/output handling.
- No central place for timeout, truncation, root realpath, or plan-hash checks.

**Risk:** Medium-high. It meets the "external wrapper" idea superficially but
does not create the testable safety boundary required by FR-8 through FR-12.

### Option B - Local Guard/Normalizer Around External Analyzer

Add `skill-stats/scripts/skill_cleaner_wrapper.py` as the only executable entry
point for skill-cleaner integration. The skill calls this wrapper for reports,
plan validation, and approved apply. The wrapper invokes the external analyzer
only through a validated path and allowlisted flags, normalizes bounded output,
and performs apply actions only from an approved structured plan.

**Module changes:** New `skill-stats/scripts/skill_cleaner_wrapper.py`; new
`tests/skill-stats-cleaner-fixtures.py` and `.sh`; update
`skill-stats/skills/skill-stats/SKILL.md`,
`skill-stats/WORKFLOW-CONTRACTS.md`, `README.md`, `PORTFOLIO.md`,
`tests/agent-playbook-eval-fixtures.py`, `scripts/release-gate.sh`, and
`RELEASE-GATE.md`.

**Data flow:** User invokes `skill-stats --cleaner`; the skill runs the local
wrapper in `report` mode. The wrapper resolves and validates the external
analyzer, calls Node with allowlisted flags, captures stdout/stderr under
budget, extracts known report sections, writes a local canonical evidence
bundle, and emits redacted normalized JSON with opaque action ids. If the user
asks to apply, the skill selects action ids, asks the wrapper to preflight
those ids into a redacted display plan plus local plan bundle, asks for `/plan`
approval, then passes the approved plan bundle to the wrapper's `apply` mode.

**Interfaces:**

```bash
python3 skill-stats/scripts/skill_cleaner_wrapper.py report \
  --analyzer <path-or-env> \
  [--months <n>] [--max-log-mb <mb>] [--context-tokens <n>] \
  [--budget-percent <n>] [--root <path> ...] [--deep-logs] [--no-logs] \
  [--config <json-path> ...] \
  [--evidence-dir <path>]

python3 skill-stats/scripts/skill_cleaner_wrapper.py preflight-plan \
  --evidence-bundle <path> \
  --action-id <id> ... \
  [--root <explicit-root> ...] \
  [--config <json-path> ...] \
  [--plan-dir <path>]

python3 skill-stats/scripts/skill_cleaner_wrapper.py apply \
  --plan-bundle <path> \
  --approved-plan-sha sha256:<hex> \
  [--root <explicit-root> ...] \
  [--config <json-path> ...]
```

Skill-facing arguments:

```text
[--cleaner] [--apply] [--analyzer <path>] [--root <path> ...]
[--config <json-path> ...] [--months <n>] [--max-log-mb <mb>]
[--context-tokens <n>] [--budget-percent <n>] [--deep-logs] [--no-logs]
```

`--apply` means "enter the plan confirmation gate"; it never implies mutation
by itself.
The skill forwards the same explicit `--config` paths through `report`,
`preflight-plan`, and `apply` so config-disable candidates are generated and
authorized only for named JSON files.

**Pros:**

- Creates a deep module: one simple skill interface hides path validation,
  analyzer invocation, truncation, plan hashing, action allowlists, and target
  safety checks.
- Testable without the real external checkout by using fake analyzer fixtures.
- Keeps external analyzer ownership outside this repo while protecting local
  users from unstable output and risky cleanup behavior.
- Mirrors the existing `worktree-cleaner` confirmation pattern.
- Easy to roll back by removing the script, skill argument branch, and fixture
  wiring.

**Cons:**

- Adds a local script and fixtures to maintain.
- The external analyzer appears to output human text, so section extraction
  must be conservative and degrade cleanly when headings change.
- Apply mode still relies on the agent/user to create and approve the plan
  content; the script can verify schema/hash/scope but cannot know whether the
  conversation truly used `/plan`.

**Risk:** Medium. The main risk is over-trusting external human-readable
output; the design counters this by treating it as advisory, not cleanup
authority.

### Option C - Native/Vendored Skill Cleaner Implementation

Port or vendor the skill-cleaner analyzer into this repo so `skill-stats` owns
root discovery, usage-log parsing, duplicate detection, prompt-budget math, and
cleanup planning directly.

**Module changes:** New analyzer under `skill-stats/scripts/` or `scripts/`;
larger parser/model code; broad tests; docs/contracts/release gate updates.

**Data flow:** User invokes `skill-stats --cleaner`; local code scans
Codex/plugin/repo/personal roots and logs itself, computes all findings, and
applies confirmed actions without calling the external analyzer.

**Interfaces:** Similar to Option B, but no `--analyzer` path.

**Pros:**

- Most deterministic and easiest to test end-to-end.
- No Node/runtime dependency or external checkout drift.
- Full control over JSON output and apply plan generation.

**Cons:**

- Violates the user-selected external-wrapper direction and the first-pass
  non-goal of not vendoring external `skill-cleaner`.
- Much larger blast radius and maintenance burden.
- Requires re-deriving analyzer behavior and likely license/attribution review.

**Risk:** High for this roadmap item. It may be a later path if the external
contract stabilizes poorly, but it is too broad for ITS-ROADMAP-021.

## Recommendation

**We pick Option B.** A local guard/normalizer is the smallest design that
meets the report-only default, explicit external dependency, apply-confirm
gate, and fixture requirements. The accepted tradeoff is maintaining a small
adapter and conservative text-section parser so that mutation safety becomes
deterministic instead of living only in skill prose.

## Chosen Design - Detail

### Module Breakdown

- `skill-stats/scripts/skill_cleaner_wrapper.py` - New Python CLI. Resolves the
  external analyzer path, invokes Node with allowlisted flags, normalizes
  bounded report output, validates cleanup plan JSON, computes plan hashes, and
  applies only approved scoped actions.
- `tests/skill-stats-cleaner-fixtures.py` - New deterministic fixture runner
  using temporary skill roots, fake analyzer scripts, symlinked paths, and
  throwaway files/configs.
- `tests/skill-stats-cleaner-fixtures.sh` - Shell wrapper matching existing
  fixture style.
- `skill-stats/skills/skill-stats/SKILL.md` - Add argument parsing and a
  "Skill Cleaner Report / Apply" workflow branch while preserving the existing
  default usage-statistics branch.
- `skill-stats/WORKFLOW-CONTRACTS.md` - Replace the single read-only contract
  with mode-specific contracts: `read-only`, `skill-cleaner-report`,
  `skill-cleaner-plan`, and `skill-cleaner-apply`.
- `tests/agent-playbook-eval-fixtures.py` - Update text-contract assertions so
  `skill-stats` is still report-only by default but documents the explicit
  apply-confirm path and no commit/push boundary.
- `scripts/release-gate.sh` - Add an advisory `skill-stats-cleaner-fixtures`
  check, strict-upgraded like existing fixture checks.
- `tests/skill-hygiene-release-gate-fixtures.sh` - Extend static
  `--self-check` coverage for the new advisory id, command text, trigger
  target arrays/scope, and docs examples; extend the full fixture command for
  skip/pass/warn and strict-upgrade JSON behavior.
- `RELEASE-GATE.md` - Document the new advisory fixture and its trigger scope.
- `README.md` - Update the `skill-stats` catalog row to mention skill-cleaner
  report mode and explicit apply-confirm cleanup.
- `PORTFOLIO.md` - Update lifecycle notes: hook writes usage JSONL; user skill
  is report-only by default; apply-confirm is mutating and target-scoped.

### Data Flow

Report mode:

```text
user -> skill-stats --cleaner
  -> resolve --analyzer or SKILL_STATS_CLEANER_ANALYZER
  -> skill_cleaner_wrapper.py report
  -> node --experimental-strip-types <resolved skill-cleaner.ts> <allowlisted flags>
  -> capture stdout/stderr with timeout and byte caps
  -> extract known sections, typed warnings, and opaque action ids
  -> write 0600 canonical evidence bundle under temp evidence directory
  -> skill renders redacted bounded report + action ids + shared contract
```

Apply mode:

```text
user -> skill-stats --cleaner --apply
  -> report evidence already shown or regenerated
  -> skill selects action ids from redacted report candidates
  -> skill runs preflight-plan with evidence bundle, action ids, and --root/--config authorization inputs
  -> wrapper validates full plan, writes 0600 local plan bundle, prints plan_id
  -> stop with status needs_user unless the agent observes exact /plan approval
  -> after approval, skill calls apply with plan bundle path + approved plan_id
  -> wrapper validates schema, hash, roots, kept copies, and all preconditions
  -> wrapper mutates only named targets after a full preflight passes
  -> wrapper verifies target state and reports touched paths
```

The design intentionally splits plan and apply. Claude Code dynamic workflows
show the value of repeatable scripts and plan approval, but their no-mid-run
user-input limit makes a single combined scan/approve/apply run the wrong shape
for this feature.

### Interfaces

#### Skill Arguments

The `skill-stats` skill keeps existing behavior when no cleaner flag is present.
Add:

- `--cleaner` - Run skill-cleaner report mode.
- `--apply` - Enter apply-confirm mode. Without current-session plan approval,
  this only emits/validates the plan and returns `needs_user`.
- `--analyzer <path>` - External analyzer checkout, skill directory, or script
  path. Overrides `SKILL_STATS_CLEANER_ANALYZER`.
- `--root <path>` - Explicit extra skill root. May be repeated. This is the
  only way to include personal/archive roots.
- `--months <n>` - Forwarded to analyzer, default `3`.
- `--max-log-mb <n>` - Forwarded only when provided.
- `--context-tokens <n>` - Forwarded only when provided; default remains the
  external analyzer default/fallback.
- `--budget-percent <n>` - Forwarded only when provided.
- `--deep-logs` - Opt into archive/OpenClaw-style deep logs.
- `--no-logs` - Disable usage-log scanning.
- `--config <json-path>` - Explicit JSON config file eligible for
  `disable_json_config_entry` action-candidate generation in report mode and
  authorization in plan/apply mode. May be repeated. It never broadens
  skill-root mutation scope.

Do not add `--commit`, `--push`, `--force`, or broad home-directory scan flags.

#### Approval Boundary

The wrapper cannot inspect conversation state or prove that a `/plan` approval
occurred. The enforceable boundary is split deliberately:

- `skill-stats/skills/skill-stats/SKILL.md` owns current-session approval. In
  `--apply` mode it must render the exact cleanup plan, run `preflight-plan`,
  show the resulting redacted display plan and `plan_id`, and stop with
  `status: needs_user` unless the user approves that exact `plan_id` through
  `/plan` in the current session.
- `skill_cleaner_wrapper.py` owns deterministic validation. It refuses mutation
  when `--approved-plan-sha` is missing, when the hash does not match canonical
  plan JSON, or when schema/root/precondition checks fail. It does not claim to
  verify human approval.
- Fixtures must cover both sides: wrapper refusal without a bundle/hash or with
  a mismatched hash, plus text-contract fixtures requiring the skill to stop
  before mutation until exact current-session `/plan` approval is present.

#### External Analyzer Trust Boundary

The external `skill-cleaner` analyzer is a trusted, user-configured local
dependency. This first pass does not sandbox arbitrary Node code. In report
mode, "non-mutating" means the local wrapper performs no target, config, or
skill-root mutation and passes only report/scan flags to the analyzer. Report
mode may still write wrapper-owned evidence artifacts under the configured
temp evidence directory; it cannot prove that a malicious or buggy external
analyzer is read-only.

The skill and wrapper must say this plainly when resolving the analyzer path.
They should accept only the documented `skill-cleaner.ts` path shapes below and
must invoke Node with `shell=False`, allowlisted flags, timeout, and output
caps. A future hardening pass can add sandboxing or a vendored/native analyzer
if stronger read-only guarantees are required.

#### Analyzer Path Resolution

`skill_cleaner_wrapper.py report` resolves `--analyzer` or
`SKILL_STATS_CLEANER_ANALYZER` as:

1. Existing file path whose basename is exactly `skill-cleaner.ts` and whose
   parent path is `scripts/` -> use that file.
2. Existing directory containing `skills/skill-cleaner/scripts/skill-cleaner.ts`
   -> treat as `agent-scripts` checkout root.
3. Existing directory containing `scripts/skill-cleaner.ts` -> treat as the
   `skills/skill-cleaner` directory.
4. Anything else -> `needs_user` with setup guidance.

Before execution, the wrapper must reject arbitrary `.ts` files and confirm
the resolved file contains high-signal identity text from the external
analyzer contract, including `skill-cleaner` and at least two known section
labels such as `Skill Budget`, `Duplicates`, or `Unused`. This is not a full
supply-chain guarantee, but it catches mistyped or unrelated TypeScript files.

The wrapper must invoke `node` without `shell=True`:

```python
[
    "node",
    "--experimental-strip-types",
    str(analyzer_script),
    "--months",
    str(months),
    ...
]
```

Only documented analyzer flags are forwarded.

#### Scan Root Resolution

Default roots are first-class data, not implicit external analyzer behavior.
Before invoking the analyzer, the wrapper resolves a bounded scan root set:

| Source label | Resolution rule | Included by default |
|---|---|---|
| `repo` | current git repo root, when present, for discovery only | yes |
| `repo_plugin` | repo-local plugin directories containing `skills/*/SKILL.md` | yes |
| `codex_home` | `$CODEX_HOME/skills` or `~/.codex/skills`, when present | yes |
| `codex_plugin_cache` | `$CODEX_HOME/plugins/cache` or `~/.codex/plugins/cache`, when present | yes |
| `explicit_user_root` | each `--root <path>` after realpath resolution | only when passed |

Each root is resolved with `Path.resolve()`, realpath-deduped, capped at 20
entries by default, and recorded in normalized report `inputs.scan_roots` with
its `source` label and `explicit` boolean. The wrapper passes resolved roots to
the analyzer explicitly when the analyzer supports root arguments; otherwise it
must report `degraded` and include the analyzer-root limitation in `skipped`.

Personal/archive roots are never inferred from arbitrary home-directory paths.
They may appear only as `explicit_user_root` entries, and only those explicit
roots can later authorize apply targets outside default repo/Codex roots.

Scan roots are broader than mutation roots. `repo` is useful for discovering
repo-local plugin directories and logs, but it does not by itself authorize
deleting arbitrary repo files. Mutation authorization is derived during apply
from independently re-resolved roots:

- default mutation roots are only directories that contain skill leaves
  (`*/skills/*/SKILL.md`) or the exact repo-local plugin directories that own
  those leaves;
- explicit mutation roots are accepted only when the same resolved path is
  supplied to `apply --root` after the user saw it in the approved plan;
- the plan's `allowed_apply_roots` must exactly match a subset of those
  independently resolved mutation roots. Plan-provided labels are never trusted
  by themselves.

The wrapper must reject forged or broad mutation roots such as `/`, the whole
home directory, the whole repo root for delete actions, or a personal path
mislabeled as `repo`, `codex_home`, or `explicit_user_root`.

#### Log Source Resolution

FR-4 also requires recent Codex/OpenClaw/Claude-style logs by default. Log
sources are first-class report inputs:

| Source label | Resolution rule | Included by default |
|---|---|---|
| `claude_recent` | recent `~/.claude` JSONL/log files used by skill usage and Claude-style sessions, capped by age/size | yes |
| `codex_recent` | recent `~/.codex` session/log files, capped by age/size | yes |
| `openclaw_recent` | recent OpenClaw-style logs only when the conventional directory exists, capped by age/size | yes |
| `archive_or_deep` | archive, backup, Dropbox-style, or broad historical logs | only with `--deep-logs` |

First-pass enumeration defaults:

- Base directories come from `HOME`, `CODEX_HOME`, and `OPENCLAW_HOME`; fixtures
  may override them with temp directories through those environment variables.
- `claude_recent` patterns: `~/.claude/skill-stats.jsonl`,
  `~/.claude/projects/**/*.jsonl`, and `~/.claude/logs/**/*.{jsonl,log,txt}`.
- `codex_recent` patterns: session/log/history directories only:
  `$CODEX_HOME/sessions/**/*.{jsonl,log,txt}`,
  `$CODEX_HOME/logs/**/*.{jsonl,log,txt}`,
  `$CODEX_HOME/history/**/*.{jsonl,log,txt}` when `CODEX_HOME` is set,
  otherwise the same patterns under `~/.codex/`.
- `openclaw_recent` patterns:
  `$OPENCLAW_HOME/sessions/**/*.{jsonl,log,txt}`,
  `$OPENCLAW_HOME/logs/**/*.{jsonl,log,txt}`,
  `$OPENCLAW_HOME/history/**/*.{jsonl,log,txt}` when `OPENCLAW_HOME` is set,
  otherwise the same patterns under `~/.openclaw/` only if that directory
  exists.
- Recent means file mtime within 90 days of the run.
- Stable order is newest mtime first, then lexical path.
- Caps are 20 files per source label, 2 MiB per file, and 20 MiB total log
  bytes per run.
- Files omitted by age, count, per-file bytes, total bytes, unreadable paths,
  or deep/archive exclusion are summarized in structured `skipped_logs`
  entries with stable reason codes: `older_than_90d`, `source_file_cap`,
  `source_scan_cap`, `file_too_large`, `total_log_cap`, `unreadable`, or
  `archive_or_deep_not_requested`.
- Path matching excludes any case-insensitive path segment exactly equal to
  `archive`, `archives`, `backup`, `backups`, `dropbox`, `.trash`, `old`, or
  `historical` unless `--deep-logs` is present.
- The resolver explicitly excludes `skills/`, `plugins/cache/`, `.git/`, repo
  source trees, config files outside the log/session/history directories, and
  arbitrary `.txt` files outside the allowed log globs.

The wrapper may delegate actual log parsing to the trusted external analyzer,
but it must still record `inputs.log_sources` and `skipped_logs`. If the
analyzer cannot accept explicit log-source arguments, report mode returns
`degraded` and names that limitation. Raw log content is never emitted; only
counts, paths with home-prefix redaction, and bounded findings may appear.

#### Normalized Report Shape

The wrapper prints redacted JSON to stdout for tests and skill consumption.
Canonical absolute target paths are retained only inside evidence and plan JSON
that is being validated/applied; report JSON uses `display_path` fields and
redacts home or personal prefixes for roots, logs, config targets, and
findings. The exceptions are wrapper-owned local artifact handles:
`evidence_bundle.path` and matching `outputs_written` entries may be absolute
temp paths because they are intentionally passed unchanged to `preflight-plan`.
`evidence_bundle.display_path` is the human display form. Target and config
paths remain redacted in report stdout.

```json
{
  "status": "success | needs_user | terminal | degraded",
  "mode": "skill-cleaner-report",
  "report_id": "report:abc123",
  "evidence_bundle": {
    "path": "/tmp/skill-stats-cleaner-evidence/abc123.json",
    "display_path": "/tmp/skill-stats-cleaner-evidence/abc123.json",
    "sha256": "abc123"
  },
  "inputs": {
    "analyzer": {"display_path": "~/agent-scripts/skills/skill-cleaner/scripts/skill-cleaner.ts"},
    "months": 3,
    "scan_roots": [
      {"display_path": "/repo", "source": "repo", "explicit": false},
      {"display_path": "~/personal-skills", "source": "explicit_user_root", "explicit": true}
    ],
    "log_sources": [
      {"display_path": "~/.claude/skill-stats.jsonl", "source": "claude_recent", "explicit": false}
    ],
    "skipped_logs": [
      {"source": "claude_recent", "display_path": "~/.claude/archive/old.jsonl", "reason": "archive_or_deep_not_requested"}
    ],
    "deep_logs": false,
    "no_logs": false
  },
  "sections": [
    {
      "name": "Skill Budget",
      "lines": ["bounded markdown line"],
      "truncated": false
    }
  ],
  "display_findings": [
    {
      "finding_id": "finding:duplicate:001",
      "finding_type": "duplicate",
      "display_target_path": "~/redacted/duplicate-skill",
      "confidence": "high",
      "manual_only": false,
      "action_candidates": [
        {
          "action_id": "action:delete:001",
          "action": "delete_path",
          "display_target_path": "~/redacted/duplicate-skill",
          "rationale": "near-copy duplicate reported by analyzer"
        }
      ]
    }
  ],
  "skipped": ["deep/archive logs: not requested"],
  "errors": [
    {"type": "degraded", "message": "analyzer stderr was truncated"}
  ],
  "outputs_written": ["/tmp/skill-stats-cleaner-evidence/abc123.json"],
  "truncated": false
}
```

The skill must use `evidence_bundle.path` and selected
`display_findings[].action_candidates[].action_id` values to call
`preflight-plan`. `report_id` is read from report stdout for display and
cross-checking, then validated from the evidence bundle by `preflight-plan`;
it is not a separate CLI argument. The skill must not scrape human section text
or reconstruct canonical paths from `display_target_path`.

Known sections are `Skill Budget`, `Description candidates`, `Duplicates`,
`Unused candidates`, and `Root summary`.

Unknown output is kept only as a bounded `Raw analyzer excerpt` section with
`status: degraded`, after redaction. Redaction happens before rendering or JSON
emission:

- Replace the current user's home directory prefix with `~`.
- Replace explicit personal-root prefixes with their configured display labels.
- Suppress raw log lines by default; show parser-failure context only when it
  explains why known sections could not be extracted.
- Redact obvious token-like strings, private-key markers, and long opaque
  base64/hex substrings.
- Preserve enough structure to debug parser drift without dumping local logs.

Default caps:

- Analyzer timeout: 90 seconds.
- Captured stdout: 256 KiB.
- Captured stderr: 32 KiB.
- Section rendering: 20 lines per known section.
- Explicit roots: 20 resolved roots per run.

When any cap is hit, set `truncated: true` and return a narrower follow-up
command in the skill's `next_action`.

#### Cleanup Plan Shape

There are three cleanup artifacts:

- **Canonical evidence bundle:** report-mode, wrapper-owned JSON containing
  absolute canonical findings, apply-capable action candidates, analyzer
  metadata, resolved roots/logs, and redacted display rows. It is never
  reconstructed from displayed paths.
- **Canonical internal plan JSON:** wrapper-generated JSON derived only from
  selected `action_id` values in the evidence bundle, plus explicit
  `--root`/`--config` authorization inputs. It is stored in a local plan bundle
  and is the hash input for `plan_id`.
- **Redacted display plan:** repo-relative paths, `~`-redacted personal paths,
  action ids, rationales, rollback notes, and `plan_id`. This is what the skill
  shows the user for `/plan` approval by default.

The skill must not paste canonical absolute-path JSON into normal user-facing
output. If the user explicitly asks to inspect canonical JSON, the skill may
show it only after warning that it contains absolute local paths; fixtures
should cover the default redacted display path.

`report` owns the report-to-plan canonical handoff. It writes an evidence
bundle and returns only redacted display data plus opaque `action_id` values.
The skill must pass `evidence_bundle.path` and selected
`display_findings[].action_candidates[].action_id` values to `preflight-plan`;
it must not reconstruct absolute paths from `display_path` or scrape rendered
section text. `preflight-plan` reads and validates `report_id` from the bundle
before copying it into `source_report_id`.

`preflight-plan` owns the handoff across the approval boundary. It receives the
evidence bundle path, selected `action_id` values, and the same explicit
`--root` and `--config` inputs needed for authorization. It verifies the
evidence bundle, derives canonical plan actions from wrapper-owned evidence,
performs full preflight without mutation, computes `plan_id`, writes a local
plan bundle, and returns only a redacted display plan, the `plan_id`, and the
bundle path. It refuses arbitrary candidate plan JSON. `apply` reads the bundle
by path and refuses raw `--plan-json`, so the exact canonical plan used for
approval is the one used for mutation.

Evidence bundles:

- Default directory: `${TMPDIR:-/tmp}/skill-stats-cleaner-evidence/`.
- Override: `--evidence-dir <path>` for fixtures.
- File name: `<report_id-without-prefix>.json`.
- Permissions: create directory `0700`, file `0600`.
- Contents: canonical findings, action candidates, redacted display rows,
  `report_id`, analyzer path hash, analyzer identity metadata, resolved
  root/log/config metadata, wrapper version, repo/worktree root, and creation
  time.
- Lifetime: current-session artifact; plan bundles reference its `report_id`
  and SHA-256 digest.
- Provenance boundary: evidence bundles are trusted local artifacts produced by
  `skill_cleaner_wrapper.py report`. They protect against accidental path
  reconstruction and malformed hand-built plans, not against a malicious local
  user who can forge files under the same account. `preflight-plan` verifies
  schema, wrapper version, repo/worktree binding, analyzer identity metadata,
  digest, TTL, and authorization inputs, then records that this is a local
  trust boundary rather than cryptographic proof of analyzer provenance.

Plan bundles:

- Default directory: `${TMPDIR:-/tmp}/skill-stats-cleaner-plans/`.
- Override: `--plan-dir <path>` for fixtures.
- File name: `<plan_id-without-sha256-prefix>.json`.
- Permissions: create directory `0700`, file `0600`.
- Contents: canonical plan JSON, `plan_id`, redacted display plan, explicit
  roots/configs used for authorization, `source_report_id`, evidence bundle
  digest, selected `action_id` values, authorization input digest, wrapper
  version, repo/worktree root, and creation time.
- Lifetime: current-session artifact; `apply` deletes the bundle after a
  successful apply and reports stale bundles as manual cleanup.
- Validity: evidence and plan bundles expire after two hours. `preflight-plan`
  and `apply` must refuse expired bundles, wrapper-version mismatch,
  repo/worktree-root mismatch, evidence-digest mismatch, or changed explicit
  `--root`/`--config` authorization inputs.

Evidence bundle schema:

```json
{
  "report_id": "report:abc123",
  "findings": [
    {
      "finding_id": "finding:duplicate:001",
      "finding_type": "duplicate | description_candidate | unused_candidate | config_disable_candidate | root_summary | budget_pressure",
      "source_section": "Duplicates",
      "source_excerpt": "redacted bounded evidence line",
      "evidence_order": 1,
      "confidence": "high | medium | low",
      "manual_only": false,
      "canonical_target_path": "/absolute/path/to/SKILL.md",
      "display_target_path": "~/redacted/SKILL.md",
      "action_candidates": [
        {
          "action_id": "action:delete:001",
          "action": "delete_path",
          "canonical_target_path": "/absolute/path/to/duplicate-skill",
          "display_target_path": "~/redacted/duplicate-skill",
          "payload": {
            "kept_copy": "/absolute/path/to/kept/SKILL.md",
            "untracked_policy": "tracked_only"
          },
          "required_authorization": "mutation_root",
          "preconditions": ["kept_copy_exists", "target_is_skill"],
          "rollback": "restore from git or named backup"
        }
      ]
    }
  ]
}
```

Rules:

- Only `action_candidates` attached to `manual_only: false` findings and
  carrying concrete payloads may be selected by `preflight-plan`.
- `unused_candidate`, `budget_pressure`, low-confidence duplicate evidence, and
  malformed analyzer output are report-only unless the wrapper can produce a
  fully populated action candidate.
- Description actions must include `old_description` and `new_description` in
  `payload`; config-disable actions must include `json_pointer`, `value`,
  `prior_value_present: false`, `prior_list_values_hash`, and
  `rollback_snapshot_hash`; delete actions must include `kept_copy` and
  `untracked_policy`.
- Config-disable payloads record the report-time before-state for the named
  JSON pointer: the value must be absent, the list hash must match at
  preflight/apply time, and the rollback snapshot hash must identify the full
  pre-mutation JSON file bytes used for rollback if a postcondition fails.
- Config-disable action candidates are generated only during `report` for JSON
  files explicitly passed with `--config`; `preflight-plan` must not synthesize
  config-disable actions later.
- If a config value already exists at report time, the wrapper marks the
  finding report-only/manual and must not emit an apply-capable
  config-disable action.
- If a config value appears after report but before `preflight-plan` or
  `apply`, the list hash/precondition check fails with no mutation; the wrapper
  must not rewrite the original report finding retroactively.
- `preflight-plan` refuses selected action ids not present in the evidence
  bundle, action candidates attached to manual-only findings, and action
  candidates whose required payload/preconditions are incomplete.
- Selected action ids are canonicalized before plan generation: deduplicate
  input ids, sort selected candidates by `(evidence_order, action_id)`, then
  assign stable plan action ids `A001`, `A002`, ... before hashing. Reversed CLI
  action-id order must produce the same display plan, canonical plan, and
  `plan_id`.

The wrapper canonicalizes plan JSON and computes:

```text
plan_id = "sha256:" + sha256(canonical_plan_bytes).hexdigest()
```

Canonicalization algorithm:

1. Parse JSON with a duplicate-key rejecting loader.
2. Resolve and normalize all filesystem paths before hashing.
3. Normalize Unicode strings to NFC.
4. Emit UTF-8 JSON with sorted object keys, compact separators `,` and `:`, no
   insignificant whitespace, and no trailing newline.
5. Hash those exact bytes.

Plan schema:

```json
{
  "version": 1,
  "created_from": "skill-cleaner-report",
  "source_report_id": "report:abc123",
  "allowed_apply_roots": [
    {"path": "/absolute/repo/skill-stats", "source": "repo_plugin", "explicit": false},
    {"path": "/absolute/repo/skill-stats/skills/duplicate-skill", "source": "repo_skill", "explicit": false},
    {"path": "/absolute/personal", "source": "explicit_user_root", "explicit": true}
  ],
  "authorized_config_targets": [
    {"path": "/absolute/config/settings.json", "source": "explicit_config", "explicit": true}
  ],
  "actions": [
    {
      "id": "A001",
      "action": "delete_path",
      "source_finding_id": "finding:duplicate:001",
      "source_action_id": "action:delete:001",
      "path": "/absolute/path/to/duplicate/skill",
      "rationale": "near-copy duplicate reported by analyzer",
      "kept_copy": "/absolute/path/to/kept/SKILL.md",
      "rollback": "restore from git or named backup",
      "untracked_policy": "tracked_only | destination_named | disposable_confirmed"
    },
    {
      "id": "A002",
      "action": "edit_skill_description",
      "source_finding_id": "finding:description:002",
      "source_action_id": "action:description:002",
      "path": "/absolute/path/to/SKILL.md",
      "old_description": "long text",
      "new_description": "short text",
      "rationale": "description budget candidate",
      "rollback": "restore old_description"
    },
    {
      "id": "A003",
      "action": "disable_json_config_entry",
      "source_finding_id": "finding:disable:003",
      "source_action_id": "action:disable:003",
      "path": "/absolute/path/to/settings.json",
      "json_pointer": "/disabledSkills",
      "value": "plugin:skill",
      "prior_value_present": false,
      "prior_list_values_hash": "sha256:abc123",
      "rollback_snapshot_hash": "sha256:def456",
      "rationale": "duplicate disabled in explicitly named config",
      "rollback": "restore JSON file from captured rollback snapshot"
    }
  ]
}
```

`repo` may appear in `inputs.scan_roots` for discovery, but it must not appear
in `allowed_apply_roots` as the whole repo root. `allowed_apply_roots` contains
only independently authorized mutation roots: `repo_plugin`, `repo_skill`,
`codex_home`, `codex_plugin_cache`, or `explicit_user_root` after apply-time
re-resolution. Delete actions still require the target itself to be a skill
directory or `SKILL.md`; a broad root never makes an arbitrary child path
mutable.

Apply constraints:

- Refuse if `--approved-plan-sha` is missing or does not match the canonical
  plan bundle hash.
- Refuse any plan action without a valid `source_report_id`,
  `source_finding_id`, and `source_action_id` from the wrapper-owned evidence
  bundle.
- Treat current-session `/plan` approval as a skill-level gate, not something
  the wrapper can independently observe. The wrapper enforces immutability and
  scope after the skill has obtained approval.
- Re-resolve default mutation roots during `apply`; accept explicit roots only
  from `apply --root`; then require plan `allowed_apply_roots` to exactly match
  a subset of those independently authorized roots.
- Refuse forged or broad roots, including `/`, a home directory, the whole repo
  root as a delete-authorizing root, or any mislabeled personal path.
- Refuse any action whose `path` is outside the independently authorized
  mutation roots.
- Refuse any personal/archive target unless its containing root is labeled
  `explicit_user_root` and the same path was passed to `apply --root`.
- Re-resolve config targets during `apply`; accept config-disable targets only
  when the same resolved JSON file is supplied with `apply --config` and appears
  in plan `authorized_config_targets` with source `explicit_config`.
- Refuse `delete_path` unless the target is a skill directory or `SKILL.md`
  under an authorized mutation root, the target has a valid `SKILL.md`
  relationship, and `kept_copy` exists as another valid `SKILL.md`.
- Refuse deleting ignored/untracked directories unless `untracked_policy` is
  `destination_named` or `disposable_confirmed` and the plan contains the
  corresponding destination/disposable rationale.
- Refuse description edits unless the target is a `SKILL.md` with a simple
  single-line `description:` in YAML frontmatter and `old_description` matches.
- Refuse JSON config disables unless the target is JSON, the pointer resolves
  to a list, the operation is append-unique string, the payload proves
  `prior_value_present: false`, and a rollback snapshot/hash is available.
- Never run `git add`, `git commit`, `git stash`, `git push`, or GitHub writes.

Apply is two-phase:

1. **Preflight all actions before mutation:** validate schema, plan hash,
   allowed roots, explicit-root labels, kept copies, tracked/ignored/untracked
   state, `old_description` matches, JSON pointers, output paths, and action
   independence for every action. If any preflight fails, mutate nothing.
2. **Apply with rollback snapshots:** capture reversible before-state for every
   action, apply only after the full preflight passes, verify postconditions,
   and stop on the first failed postcondition. If a postcondition fails, roll
   back already-applied actions in reverse order where possible and report
   rollback success or the exact residual touched paths.

Action independence rules:

- Reject duplicate action ids.
- Reject duplicate filesystem target paths across delete and description-edit
  actions.
- Reject ancestor/descendant overlaps, such as deleting a skill directory while
  editing its child `SKILL.md`.
- Reject duplicate description edits for the same `SKILL.md`.
- Reject duplicate config-disable operations with the same
  `(config path, json_pointer, value)`.
- Reject any action whose before-state or rollback path depends on another
  action in the same plan.

### Data / Schema Changes

No database, API, or persistent repo schema changes.

New local schemas:

- Normalized report JSON emitted by `skill_cleaner_wrapper.py report`.
- Canonical evidence bundle JSON written by `report` and consumed by
  `preflight-plan`.
- Cleanup plan JSON accepted by `preflight-plan`, then stored in a local
  current-session plan bundle consumed by `apply`.

No target project artifact is written in report-only mode, but
`skill-cleaner-report` explicitly writes a local temp evidence bundle so
canonical paths never have to be reconstructed from redacted output.
`outputs_written` for `skill-cleaner-report` lists only that evidence bundle
path. `skill-cleaner-plan` writes only the current-session plan bundle path
returned by `preflight-plan`. In `skill-cleaner-apply`, `outputs_written` lists
the approved target paths actually edited, deleted, or config-updated, plus
bundle deletion when successful.

### Failure Modes & Handling

- Missing `--analyzer` and missing `SKILL_STATS_CLEANER_ANALYZER`: return
  `needs_user`, show setup examples, do not scan or mutate.
- Analyzer path exists but cannot resolve to `skill-cleaner.ts`: return
  `needs_user`, include accepted path shapes.
- `node` unavailable or analyzer exits with unsupported runtime error: return
  `needs_user` if no report exists; `degraded` if a partial bounded report is
  usable.
- Analyzer timeout/nonzero exit: return `degraded` with bounded stderr and no
  cleanup authority.
- Analyzer output headings change: return `degraded`, include bounded raw
  redacted excerpt only when needed to explain parser drift, and skip apply
  recommendation.
- Output/root budgets exceeded: set `truncated: true`, summarize omitted
  sections/roots, and provide a narrower command.
- Personal roots not explicit: report `skipped` entry; do not infer from home
  folders or archive names.
- Duplicate delete candidate lacks existing kept copy: downgrade to manual
  finding; no delete action may be generated.
- Delete target is not a skill directory or `SKILL.md`: refuse during preflight,
  no filesystem change.
- Plan carries a forged or broad allowed root: refuse during preflight, no
  filesystem change.
- Config-disable target is not provided through `apply --config`: refuse during
  preflight, no filesystem change.
- Config-disable value already exists in the explicit config before plan
  generation: downgrade to report-only/manual and emit no apply-capable
  action candidate.
- Config-disable value appears between report and preflight/apply: refuse as
  config drift with no filesystem change.
- Cleanup plan has duplicate, overlapping, or dependent actions: refuse during
  preflight, no filesystem change.
- Recent log resolver cannot enumerate a conventional log source: record
  `skipped_logs`; do not scan arbitrary home folders as a substitute.
- Symlinked roots point to same real path: dedupe before analyzer invocation
  and in fixtures.
- `--apply` without current-session `/plan` approval: the skill returns
  `needs_user` after `preflight-plan`; it must not call wrapper `apply`.
- Plan hash mismatch or plan content changed after approval: return
  `needs_user`, no filesystem change.
- Plan bundle missing, unreadable, malformed, stale, or hash-mismatched: return
  `needs_user`, no filesystem change.
- Evidence bundle missing, unreadable, malformed, expired, repo/worktree
  mismatched, wrapper-version mismatched, or digest mismatched: return
  `needs_user`, no plan or filesystem mutation.
- Selected action id missing from evidence bundle: return `needs_user`, no
  plan or filesystem mutation.
- Selected action candidate is manual-only or lacks required payload fields:
  return `needs_user`, no plan or filesystem mutation.
- Any apply action precondition fails during full preflight: return
  `needs_user` or `terminal`, no filesystem change.
- Any postcondition fails after mutation begins: stop, roll back prior actions
  where possible, report typed error, and list any residual touched paths.
- Config-disable postcondition fails after append: restore the captured JSON
  rollback snapshot, verify its hash, and report residual touched paths if the
  snapshot cannot be restored exactly.
- Any apply mutation succeeds: verify target postcondition, include touched
  path in `outputs_written`, and do not commit.

### Rollout / Migration

1. Land report wrapper behind `--cleaner` while keeping the no-argument
   `skill-stats` path unchanged.
2. Update contracts/docs only after behavior and fixtures exist, so the repo
   never advertises apply-confirm before the safety gate is implemented.
3. Wire the new fixtures into release gate as advisory/strict. Do not make
   personal usage logs or personal roots release-blocking.
4. Keep `agent-playbook:context-audit` as a consumer/reference only. If it
   later cites skill-cleaner output, it should ask users to run
   `skill-stats --cleaner`; it should not duplicate analyzer ownership.
5. Leave `.claude/workflows/` as a future follow-up. If added later, it should
   orchestrate report/review only and still split apply into a separate
   approval-confirmed command.

### Test Strategy Hooks

The list below is the target contract for this integration, not a claim that
every bullet is fully automated in the first pass. Implemented fixture coverage
is enumerated in `test-plan.md`; bullets not represented there are deferred
follow-up coverage and remain part of the intended safety contract.

Machine-checkable fixtures:

- Missing analyzer path -> `needs_user`, no mutation.
- Missing `node` -> `needs_user` or `degraded`, no mutation.
- Analyzer path as checkout root, skill directory, and script file all resolve.
- Arbitrary `.ts` files and `skill-cleaner.ts` files missing identity text are
  refused.
- Fake analyzer emits the five known sections -> normalized report contains
  bounded sections.
- Fake analyzer emits malformed/unheaded output -> `degraded` with raw bounded
  redacted excerpt.
- Huge analyzer output -> `truncated: true`, per-section caps held.
- Report mode writes a 0600 evidence bundle with canonical findings,
  action-candidate schema, redacted display rows, opaque action ids,
  repo/worktree binding, wrapper version, and a two-hour TTL.
- Report mode with `--config` generates config-disable action candidates from
  the explicit config files; report mode without `--config` produces no
  config-disable action candidates.
- Config-disable fixture where the value already exists in the explicit config
  produces a report-only/manual finding and no selectable action candidate.
- Config-disable drift fixture where the value is added after report but before
  `preflight-plan` or `apply` refuses with no mutation.
- `preflight-plan` refuses missing, expired, wrong-repo, digest-mismatched, or
  wrapper-version-mismatched evidence bundles.
- `preflight-plan` refuses selected action ids that are not present in the
  evidence bundle, manual-only findings, incomplete action payloads, and
  arbitrary raw plan JSON.
- Evidence schema fixtures prove duplicate, description, and config-disable
  action candidates deterministically generate the expected redacted display
  plan and canonical plan actions.
- Evidence schema fixtures prove report-only/manual findings cannot generate
  apply actions.
- Action ordering fixtures prove reversed `--action-id` input produces the same
  redacted display plan, canonical plan, and `plan_id`.
- Release-gate fixtures stub `node` on `PATH`; real external Node analyzer
  smoke tests are optional and never part of strict release gate.
- Default scan roots are resolved into `inputs.scan_roots`; personal/archive
  roots are excluded unless passed with `--root`.
- Default recent log sources are resolved into `inputs.log_sources`;
  deep/archive logs are excluded by default and listed in `skipped_logs`.
- Log resolver fixtures cover 90-day recency, newest-then-path sorting,
  20-file-per-source caps, 2 MiB per-file caps, 20 MiB total cap, unreadable
  files, and archive/deep exclusions.
- Log resolver fixtures prove Codex `skills/`, `plugins/cache/`, config files,
  and arbitrary non-log `.txt` files outside `sessions/`, `logs/`, or
  `history/` are excluded by default.
- Log resolver fixtures prove OpenClaw non-log files outside `sessions/`,
  `logs/`, or `history/` are excluded by default and expected recent OpenClaw
  log files in those directories are included.
- `skipped_logs` fixtures assert structured entries with `source`,
  `display_path`, and stable `reason` values.
- Path redaction fixtures cover analyzer path, scan roots, explicit personal
  roots, log sources, and skipped logs in stdout JSON.
- Repeated symlink roots -> one realpath root passed to analyzer.
- Default run omits personal roots; explicit `--root` includes them.
- Deep/archive logs are skipped by default; `--deep-logs` forwards only when
  explicit.
- Duplicate delete plan with missing kept copy is refused.
- Delete plan for a non-skill repo file or directory under the repo root is
  refused.
- Forged/broad root labels such as `/`, `$HOME`, repo-root delete roots, and
  fabricated `explicit_user_root` entries are refused.
- Plan examples and fixtures must never put the whole repo root with source
  `repo` into `allowed_apply_roots`; broad `repo` is discovery-only.
- Report-only mode and `--apply` without approval leave fixture files unchanged.
- Skill text-contract fixture requires `--apply` to stop after `preflight-plan`
  until exact current-session `/plan` approval for `plan_id`.
- Default display-plan fixture shows redacted paths and `plan_id`, not
  canonical absolute-path JSON.
- `preflight-plan` writes a 0600 local plan bundle and returns its path;
  `apply` consumes the same bundle and refuses raw plan JSON.
- Plan bundle fixtures cover two-hour TTL expiry, wrong repo/worktree root,
  changed `--root`/`--config` authorization inputs, and evidence digest
  mismatch.
- Plan canonicalization computes stable `sha256:<hex>` for equivalent reordered
  JSON, and duplicate object keys are rejected.
- Wrapper apply without `--plan-bundle` or `--approved-plan-sha` is refused.
- Apply with mismatched hash leaves files unchanged.
- Apply preflight failure in one action leaves all targets unchanged.
- Config-disable without explicit `--config` authorization is refused; a
  matching `--config` JSON path may be disabled only for the named pointer/value.
- Config-disable postcondition failure restores the captured JSON rollback
  snapshot and reports any residual touched path if rollback verification fails.
- Overlapping delete/edit actions, duplicate description edits, and duplicate
  config pointer/value actions fail preflight before mutation.
- Approved delete/edit/disable actions touch only named targets.
- Extra unapproved files in the same root remain unchanged.
- Apply never runs git commit/push commands; fixture can assert no `.git` state
  mutation in a temp repo.
- Release-gate static self-check fixtures assert the
  `skill-stats-cleaner-fixtures` advisory id, command text, trigger target
  arrays/scope, and `RELEASE-GATE.md` examples.
- The full `bash tests/skill-hygiene-release-gate-fixtures.sh` command asserts
  skip/pass/warn and strict-upgrade JSON behavior for
  `skill-stats-cleaner-fixtures`.

Verification commands for implementation:

```bash
bash tests/skill-stats-cleaner-fixtures.sh
bash tests/agent-playbook-eval-fixtures.sh
bash tests/skill-hygiene-release-gate-fixtures.sh --self-check
bash tests/skill-hygiene-release-gate-fixtures.sh
python3 scripts/skill-hygiene-check.py --mode working .
scripts/release-gate.sh --mode all --strict
git diff --check
```

## Staged Implementation Plan

1. **Stage 1 - Report Wrapper Tracer Bullet:** Add red-first
   `tests/skill-stats-cleaner-fixtures.py` scenarios for missing analyzer,
   analyzer identity refusal, fake analyzer report normalization, evidence
   bundle generation, malformed output, truncation, symlink root dedupe,
   explicit personal roots, redacted stdout paths, and log-source resolution
   through temp `HOME`/`CODEX_HOME`/
   `OPENCLAW_HOME`: recent-log inclusion, deep/archive exclusion, 90-day
   recency, per-source file cap, per-file cap, total cap, unreadable files,
   structured `skipped_logs`, and `--deep-logs` inclusion. Implement
   `skill_cleaner_wrapper.py report` until those pass. Do not expose apply yet.
2. **Stage 2 - Public Report Mode:** Update `skill-stats` skill arguments,
   report workflow, workflow contract, README, PORTFOLIO, and contract
   fixtures so `--cleaner` is report-only by default and the existing
   usage-statistics mode still works.
3. **Stage 3 - Apply Plan Gate:** Add red-first plan/apply fixtures for
   approval refusal, hash mismatch, duplicate kept-copy checks, scoped
   delete/edit/disable, explicit `--config` authorization, redacted display
   plans, source-finding/action binding, current-session plan bundles,
   canonical JSON hashing, duplicate-key rejection, action-independence
   rejection, bundle TTL and repo/auth-input binding, unapproved file
   preservation, and no git mutation. Implement `preflight-plan` and `apply`,
   then update
   skill/contracts/docs to describe the mutating apply-confirm mode.
4. **Stage 4 - Release Gate Wiring And Final Verification:** Add the advisory
   release-gate fixture check, static release-gate self-check coverage, full
   release-gate JSON behavior fixtures, and docs. Run the fixture suite,
   `bash tests/skill-hygiene-release-gate-fixtures.sh`,
   `bash tests/skill-hygiene-release-gate-fixtures.sh --self-check`, skill
   hygiene, strict release gate, whitespace check, and `/review-code --slug
   ITS-ROADMAP-021` after implementation. `/review-design --slug
   ITS-ROADMAP-021` is the current pre-implementation gate and must be clean
   before Stage 1 starts.

## Open Questions

- The first-pass design resolves analyzer configuration to `--analyzer` plus
  `SKILL_STATS_CLEANER_ANALYZER`. A personal config file can be added later if
  users want persistence without shell environment setup.
- `disable_json_config_entry` intentionally supports only explicit JSON list
  appends. If Codex/OpenClaw disabled-skill config uses a different stable
  schema, architecture should be revised before broadening this action.
- The external analyzer implementation was not retrieved reliably during this
  design pass; implementation must treat its stdout format as unstable and rely
  on fake-analyzer fixtures for local contracts.
- A future Claude dynamic workflow may orchestrate multi-agent review of the
  report, but first-pass implementation should not depend on workflow runtime,
  paid-plan workflow availability, or `ultracode`.
