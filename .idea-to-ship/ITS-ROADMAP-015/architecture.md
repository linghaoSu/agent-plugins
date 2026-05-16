# Architecture - Skill Authoring Standards

**Slug:** ITS-ROADMAP-015
**Date:** 2026-05-16
**Status:** draft
**References:** requirements.md

## Summary

Extend `scripts/skill-hygiene-check.py` with conservative authoring-standard
warnings for newly added or changed skills, then document those checks in
`RELEASE-GATE.md` and cover them with deterministic fixtures. The chosen design
keeps legacy skills from failing `--mode all --strict` until they are touched,
while still preventing newly edited skill work from shipping with missing
usage guidance, workflow metadata, related-skill links, or unsafe command
examples.

## Goals / Non-Goals

Goals:

- Catch weak skill authoring structure for new or changed `SKILL.md` files.
- Keep warnings deterministic and release-gate advisory, with strict-mode
  promotion already handled by `scripts/release-gate.sh`.
- Reuse existing skill discovery, Markdown section parsing, fence parsing, and
  fixture style.
- Translate Kagenti's command-safety ideas into runtime-neutral local checks
  instead of importing Claude-specific auto-approve policy.

Non-goals:

- No blanket cleanup of every existing skill in this roadmap item.
- No `.claude/settings.json`, installed-cache, or runtime permission mutation.
- No automatic diagram generation or exact semantic diagram/prose equivalence
  proof.
- No new `skill-creator` plugin, because this source repo has no editable local
  `skill-creator` implementation.

## Codebase Context

- `scripts/skill-hygiene-check.py` already owns advisory source-based checks.
  It exposes reusable helpers for skill discovery by mode, staged-index reads,
  frontmatter extraction, Markdown heading extraction, fenced-code detection,
  invisible-block stripping, and visible `## Hygiene Exception` parsing.
- `tests/skill-hygiene-check-fixtures.py` uses temporary git repos and exact
  check IDs to cover checker behavior. New checks should add one focused
  scenario and register it in `run_all`.
- `tests/skill-hygiene-release-gate-fixtures.sh` asserts that release-gate
  JSON evidence includes expected `skill-hygiene` warning IDs. New check IDs
  should be added to the existing skill-hygiene evidence assertions only where
  the fixture creates a weak skill.
- `scripts/release-gate.sh` already runs `skill-hygiene` in all modes and
  promotes advisory warnings to failures with `--strict`; no new gate category
  is needed.
- `scripts/skill-topology-scan.py` already defines local skill-reference
  conventions: plugin-qualified `$plugin:skill` / `plugin:skill` and
  `plugin/skills/skill/SKILL.md` path references. The hygiene checker should
  reuse those conventions locally rather than importing Kagenti colon-directory
  rules.
- Root `README.md` and repo search show no local `skill-creator` source under
  this repository. This item should update repo-wide authoring guidance and
  validator behavior, not invent a new plugin.

## Cross-Skill Routing

| Signal | Routed skill | Result | Design impact |
|---|---|---|---|
| Local validation script and fixture command; no external APIs or persistent app state | none | no architecture-stage routed skill needed | Keep the design local, offline, and additive. |
| Implementation will edit fixtures/examples that may contain command snippets | `secret-scanner:scan-secrets --mode working` during implementation | required implementation-stage check | Run a working-tree secret scan before marking implementation complete. |

## Alternatives Considered

### Option A - Incremental Hygiene Checks For New/Changed Skills

Add authoring-standard checks inside `skill-hygiene-check.py`, scoped to
new/changed `SKILL.md` files for all modes, and document them in
`RELEASE-GATE.md`.

**Module changes:** `scripts/skill-hygiene-check.py`,
`tests/skill-hygiene-check-fixtures.py`,
`tests/skill-hygiene-release-gate-fixtures.sh`, `RELEASE-GATE.md`.

**Data flow:** choose target skill files -> parse visible headings and fenced
commands -> classify workflow/router skills -> validate sections, related
references, and command examples -> emit advisory `Finding` rows.

**Interfaces:** existing
`python3 scripts/skill-hygiene-check.py --mode <staged|working|all> .`.

**Pros:** Smallest blast radius; preserves strict all-mode on the current repo;
fits existing release-gate behavior.

**Cons:** Legacy untouched skills are not fully backfilled by `--mode all`.

**Risk:** Low-medium; heuristic checks can false-positive if they are too broad.

### Option B - Enforce Standards Across Every Existing Skill

Run the new checks against every skill in `--mode all` and update all current
skills until strict all-mode passes.

**Module changes:** checker, fixtures, docs, and many existing skills.

**Pros:** Strongest immediate consistency.

**Cons:** Large unrelated churn; turns a validator roadmap item into a broad
skill rewrite; high risk of altering public workflows unintentionally.

**Risk:** High; false positives and drive-by skill edits would dominate review.

### Option C - Add A Separate `skill-authoring-check.py`

Create a new validator script for authoring standards and wire it into the
release gate as a separate advisory check.

**Module changes:** new script, new fixtures, release-gate wiring, docs.

**Pros:** Keeps new heuristics isolated from existing hygiene code.

**Cons:** Duplicates skill discovery, staged-index reads, Markdown parsing, and
release-gate fixture scope.

**Risk:** Medium; more infrastructure to maintain for checks that naturally
belong to skill hygiene.

## Recommendation

**We pick Option A.** The repo already has a skill hygiene checker and release
gate path for advisory skill-quality warnings, so extending it is the most
surgical implementation. The accepted tradeoff is that legacy skill cleanup is
deferred until those skills are edited or a future roadmap item intentionally
backfills the catalog.

## Chosen Design - Detail

### Module Breakdown

- `scripts/skill-hygiene-check.py` - add authoring-standard helper functions
  and `Finding` producers.
- `scripts/skill-authoring-baseline.txt` - committed legacy baseline of
  `SKILL.md` content hashes that are exempt from the new authoring checks until
  changed.
- `scripts/release-gate.sh` - add the baseline file to skill-hygiene
  infrastructure drift scope so staged gates do not validate against a mixed
  index/worktree baseline.
- `tests/skill-hygiene-check-fixtures.py` - add fixture scenarios for bad and
  acceptable changed skills.
- `tests/skill-hygiene-release-gate-fixtures.sh` - extend existing JSON
  evidence checks to ensure release-gate output carries new authoring IDs and
  mirror the baseline file in the skill-hygiene infrastructure target list.
- `RELEASE-GATE.md` - document the new authoring checks and their advisory /
  strict-mode behavior.
- `.idea-to-ship/ITS-ROADMAP-015/*` - record requirements, architecture, test,
  implementation, and review evidence.

### Data Flow

```
repo root + mode
  -> changed_skill_files(root, mode) for existing hygiene checks
  -> authoring_target_skill_files(root, mode)
       staged: staged added/modified skills, read from the index
       working: tracked diffs against HEAD + untracked skills, read from worktree
       all: union of:
            - every skill whose current content hash is absent from or differs
              from scripts/skill-authoring-baseline.txt
            - tracked dirty skill paths from git diff HEAD
            - untracked skill paths from git ls-files --others
            Dirty/new paths always bypass baseline exemption even if the
            baseline already contains their current hash.
  -> parse skill text using read_skill_text(...)
  -> strip invisible markdown blocks for heading/section checks
  -> build mode-aware known-skill inventory for related-skill validation
  -> collect fenced command blocks with language bash/sh/zsh/shell/console/terminal
     and untyped fences whose first nonblank line looks like a shell command
  -> classify workflow/router skills deterministically
  -> validate:
       usage/actionability section
       task tracking for workflow skills
       embedded mermaid diagram for workflow/router skills
       Related Skills section
       broken related-skill references
       unsafe or non-copy-pasteable command examples
  -> emit Finding(check_id, path, message)
```

### Interfaces

No new public command. Existing commands remain:

```bash
python3 scripts/skill-hygiene-check.py --mode working .
python3 scripts/skill-hygiene-check.py --mode all .
scripts/release-gate.sh --mode all --strict
```

New check IDs:

- `missing-actionable-usage`
- `missing-task-tracking`
- `missing-workflow-diagram`
- `missing-related-skills`
- `broken-related-skill`
- `unsafe-command-example`
- `unexplained-command-placeholder`

### Data / Schema Changes

- Add `scripts/skill-authoring-baseline.txt`, a sorted tab-separated file:
  `<relative SKILL.md path>\t<sha256 of normalized file bytes>`.
- Baseline entries are a legacy compatibility snapshot for current untouched
  skills. Staged/working mode must not let a baseline edit suppress authoring
  findings for newly added, modified, or staged-dirty skills. Accepted
  exceptions for touched skills must live visibly in that skill's
  `## Hygiene Exception` section.
- `--mode all` cannot prove historical intent after a weak skill and a matching
  baseline entry have both been committed. Its enforceable guarantee is narrower:
  committed weak skills that are absent from or different from the baseline are
  checked and fail under strict mode. The non-waiver guarantee is enforced in
  staged/working mode before that commit boundary.
- Add `scripts/skill-authoring-baseline.txt` to `SKILL_HYGIENE_INFRA_TARGETS`
  in both `scripts/release-gate.sh` and
  `tests/skill-hygiene-release-gate-fixtures.sh`.
- Existing hygiene checks keep their current target behavior. The baseline and
  `authoring_target_skill_files(...)` apply only to the new authoring-standard
  checks, not to description length, size, output-contract, repetition, runtime
  routing, or metadata checks.

### Deterministic Authoring Rules

- **Actionable usage:** visible Markdown must contain at least one heading whose
  normalized title is one of `workflow`, `when to use`, `usage`, `steps`,
  `arguments`, or `examples`.
- **Workflow/router classification:** a skill is workflow/router-like when it
  has a `## Workflow` heading, mentions `Step 1`, has three or more headings
  beginning with `Step`, or contains routing language such as `route to`,
  `handoff`, `phase gate`, or `stage`.
- **Task tracking:** workflow/router-like skills must visibly mention at least
  one of `todo`, `checklist`, `task list`, `update_plan`, `stage status`,
  `track progress`, `tracking status`, `update status`, or `record status`
  outside fenced code. Bare `plan` or `status` does not satisfy this check.
- **Workflow diagram:** workflow/router-like skills must contain a fenced
  `mermaid` block with at least one Mermaid flow keyword (`flowchart`,
  `graph`, `sequenceDiagram`, or `stateDiagram`) and at least one edge marker
  such as `-->`, `->>`, or `-->|`.
- **Related skills:** authoring-target skills must contain a visible
  `## Related Skills` section. Inside that section, validate only
  plugin-qualified `$plugin:skill`, `plugin:skill`, and
  `plugin/skills/skill/SKILL.md` references. Ignore unqualified prose. A
  self-reference alone does not satisfy the section unless the section also
  contains the exact visible text `No other local related skills in this fixture
  repo.`; that fixture-only escape exists so single-skill temporary repos can
  test unrelated authoring checks without inventing broken refs.
- **Known skill inventory:** build from local skill paths using the same mode as
  the target. Staged mode must include staged additions, exclude staged
  deletions even if the worktree file still exists, and ignore dirty
  worktree-only target skills. Related refs to staged-added skills pass; refs
  to staged-deleted or worktree-only skills fail.
- **Command fences:** scan fenced languages `bash`, `sh`, `zsh`, `shell`,
  `console`, and `terminal`; also scan untyped fences whose first nonblank line
  starts with `$`, `git`, `rm`, `python`, `python3`, `bash`, `npm`, `pnpm`,
  `yarn`, `uv`, `make`, `scripts/`, or `./`.
- **Unsafe command examples:** warn on `&&`, `||`, `;`, heredoc operators
  matching `<<-?['"]?[A-Za-z_][A-Za-z0-9_-]*['"]?`, or destructive commands
  (`rm -rf`, `git reset --hard`, `git clean -fd`, `git checkout --`,
  `curl ... | sh`) unless the same paragraph or preceding five visible lines
  contain safety language:
  `approval`, `confirm`, `dry-run`, `non-mutating`, `read-only`, `explicit
  authorization`, or `review before running`.
- **Command placeholders:** warn when command fences contain `<...>`, `{...}`,
  or uppercase placeholders with underscores unless the preceding five visible
  lines explain them with `replace`, `set`, `export`, or `placeholder`.

### Failure Modes & Handling

- False-positive authoring checks: keep checks scoped to new/changed skills and
  document the expected remediation. Use `## Hygiene Exception` only for checks
  where a justified local exception is useful. The baseline is the primary
  compatibility mechanism for untouched legacy skills only. Staged/working
  fixtures must prove that a weak changed skill still warns even if its new hash
  appears in the baseline.
- Missing related target due to plain prose: validation is limited to
  `## Related Skills`, plugin-qualified references, and path references. Broken
  refs are resolved against the mode-aware known-skill inventory.
- Command safety ambiguity: the exact scanned fence languages, risky patterns,
  destructive patterns, and safety-language proximity rules above are the only
  automated standard in this item.
- Mermaid formatting ambiguity: fenced Mermaid content is scanned as diagram
  content even when edge lines use common four-space indentation inside the
  fence; indented code outside fences stays ignored.
- Current repo has legacy skills without all new sections: do not backfill them
  in this item; hash-baseline them so strict all-mode remains green, but any
  content change removes the implicit legacy exemption.

### Rollout / Migration

Land as additive authoring warnings in the existing hygiene checker plus a
committed baseline for current legacy skill hashes. Existing skills are not
migrated. New or touched skills receive advisory findings in staged/working mode
and strict failures through the existing release-gate promotion until the skill
is fixed or given a visible, targeted `## Hygiene Exception`. All-mode strict
continues to catch unbaselined weak committed skills and does not replace the
staged/working gate for baseline edits.

### Test Strategy Hooks

- Stage-local TDD fixture should first add failing scenarios proving weak
  changed skills produce the new check IDs.
- Fixtures must include positive and non-finding coverage for each new check:
  valid/invalid usage section, workflow skill with/without task tracking,
  workflow skill with/without Mermaid, related section with valid refs, related
  section with broken refs, safe/unsafe command examples, explained/unexplained
  placeholders, and baseline behavior in `all`.
- Mode fixtures must cover `working`, staged index reads with a dirtied
  worktree, and `all` mode where a committed weak skill not present in the
  baseline fails while committed baseline legacy stays quiet.
- Baseline fixtures must prove in staged/working mode that a modified weak skill
  still warns even if the baseline contains the modified hash, and release-gate
  JSON must include an `all + strict` failure for an unbaselined weak committed
  skill.
- Existing-check regression fixtures must prove a baselined legacy skill still
  reports existing all-mode hygiene findings such as `long-description` or
  `oversized-skill`; the authoring baseline must not mask old checks.
- Existing fixture helpers must be migrated deliberately: make the default
  `skill_text()` helper authoring-compliant and add an explicit weak-skill
  helper for new authoring finding tests, or seed fixture baselines where the
  scenario is intentionally about legacy behavior. Single-skill valid fixtures
  may satisfy `## Related Skills` with a self-reference plus the exact fixture
  note `No other local related skills in this fixture repo.`; tests must cover
  self-only, self-plus-note, non-self, and broken-reference cases.
- Related-skill staged fixtures must prove: staged ref to staged-added skill
  passes; staged ref to staged-deleted skill fails even if the file exists in
  the worktree; staged ref to a worktree-only unstaged skill fails.
- Release-gate fixture coverage must include baseline file infra drift in
  staged mode.
- Full verification commands:
  - `bash tests/skill-hygiene-check-fixtures.sh`
  - `bash tests/skill-hygiene-release-gate-fixtures.sh --self-check`
  - `bash tests/skill-hygiene-release-gate-fixtures.sh`
  - `python3 scripts/skill-hygiene-check.py --mode working .`
  - `scripts/release-gate.sh --mode all --strict`
  - `python3 secret-scanner/scripts/scan.py --mode working --format json`

## Staged Implementation Plan

1. **Stage 1A - Baseline and target selection**: Add baseline generation data,
   target selection, baseline non-waiver behavior, and fixtures for working,
   staged, all, baseline-drift, and unbaselined committed weak skills.
2. **Stage 1B - Fixture helper migration and section/workflow checks**: Make
   default fixture skills authoring-compliant or explicitly baselined, add a
   weak-skill helper, then add usage, task-tracking, and
   Mermaid workflow checks with positive and non-finding fixtures.
3. **Stage 1C - Related-skill validation**: Add `## Related Skills` parsing,
   mode-aware known-skill inventory, broken-ref checks, and staged-added /
   staged-deleted / worktree-only fixtures.
4. **Stage 1D - Command-fence checks**: Add command-fence scanning, exact risky
   pattern detection including non-EOF heredocs, destructive command detection,
   placeholder explanation checks, and positive / non-finding fixtures.
5. **Stage 1E - Release-gate docs and evidence**: Update release-gate fixture
   JSON assertions, infra target lists, release docs, and idea-to-ship
   implementation evidence. The stage is shippable when the targeted fixture
   fails before production code, then all verification commands above pass.

## Open Questions

- None blocking. Exact diagram/prose semantic equivalence remains a documented
  manual review expectation rather than an automated parser in this stage.
