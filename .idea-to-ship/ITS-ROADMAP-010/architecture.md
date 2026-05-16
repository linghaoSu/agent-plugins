# Architecture - Skill Hygiene Repetition And Bloat Checks

**Slug:** ITS-ROADMAP-010
**Date:** 2026-05-15
**Status:** draft
**References:** requirements.md

## Summary

Add conservative prompt/template repetition, scan-limit, and moderate-bloat checks to the existing `scripts/skill-hygiene-check.py` deep module. The chosen design keeps hygiene findings on the current `skill-hygiene` advisory path, adds stable check IDs, and introduces fast deterministic fixture advisories wired into the release gate so the new rules and their release-gate harness are protected without relying on brittle prose snapshots.

## Goals / Non-Goals

Goals:

- Detect repeated inline prompt-like blocks inside a skill file and high-confidence repeated prompt blocks copied across skill files.
- Detect repeated inline template/report-wrapper blocks inside a skill file and high-confidence repeated template blocks copied across skill files.
- Warn when a skill grows beyond a moderate threshold before the existing 750-line oversized limit.
- Preserve local, offline, read-only, Python-standard-library operation.
- Preserve release-gate semantics: hygiene findings are advisory by default and strict-upgraded failures with `--strict`.
- Add deterministic coverage for repeated-prompt, repeated-template, moderate-bloat, and release-gate wiring scenarios.
- Surface bounded near-duplicate scan degradation with a stable finding instead of silently returning clean output.

Non-goals:

- Do not extract or rewrite any existing skill prompts in this item.
- Do not add network access, GitHub access, model calls, or a third-party linter.
- Do not enforce a universal hard line limit for every skill.
- Do not scan generated scratch artifacts outside the existing skill-file scope.
- Do not fail on harmless wording edits or exact prose changes.

## Codebase Context

- `scripts/skill-hygiene-check.py` already owns skill-file discovery, staged/working/all mode handling, skill text reads, stable `Finding(check_id, path, message)` output, and exit codes. New content rules should live here rather than in `release-gate.sh`.
- Existing checker scope is `*/skills/*/SKILL.md`. `staged` reads file contents from the index with `git show :path`; `working` and `all` read from the filesystem. The staged path discovery currently filters with `path.is_file()`, which can skip a staged skill if the worktree copy has been deleted; this implementation should make staged target discovery index-based end to end.
- Current constants include `MAX_DESCRIPTION_CHARS = 320`, `MAX_SKILL_LINES = 750`, and shared-contract markers. The moderate threshold should be a new constant below 750, not a replacement for the oversized check.
- `scripts/release-gate.sh` always runs `python3 scripts/skill-hygiene-check.py --mode "$MODE" .` as advisory `skill-hygiene`. Advisory warnings are upgraded to failures by the existing `--strict` path.
- `RELEASE-GATE.md` documents `skill-hygiene` and should be updated to name the new warning classes.
- Current `python3 scripts/skill-hygiene-check.py --mode all .` passes. Sub-agent exploration found the largest accepted skills at 375, 336, 327, and 302 lines, so a 400-line moderate-bloat threshold avoids immediate all-repo noise while still warning earlier than 750.
- Existing fixture scripts use stable check IDs and structural invariants instead of golden prose snapshots. The new fixtures should follow that pattern.

## Cross-Skill Routing

| Signal | Routed skill | Result | Design impact |
|---|---|---|---|
| Release-gate tool output and skill contracts are part of agent/plugin infrastructure. | none | Existing release-gate and `Finding.check_id` contracts are sufficient; no new harness design is needed. | Treat check IDs, file scope, and exit-code behavior as public contracts. |
| Fixture samples could accidentally resemble secrets or credentials. | `secret-scanner:scan-secrets` | Not run at architecture stage; no executable fixture samples were added yet. | Implementation fixtures must use inert placeholders and final verification must include the release gate secret scan. |

## Alternatives Considered

### Option A - Extend The Existing Hygiene Checker

Add new checks inside `scripts/skill-hygiene-check.py` using conservative same-file matching plus constrained cross-file exact fingerprints, keep the existing checker CLI, surface bounded scan degradation, and add a focused fixture command for deterministic examples.

**Module changes:** `scripts/skill-hygiene-check.py`, `tests/skill-hygiene-check-fixtures.py`, `tests/skill-hygiene-check-fixtures.sh`, `scripts/release-gate.sh`, `RELEASE-GATE.md`.

**Data flow:** release gate invokes the existing checker -> checker discovers skill files for the selected mode -> new checks inspect each skill body -> findings render with stable IDs -> release gate maps exit `1` to advisory warning or strict failure.

**Interfaces:** existing checker CLI stays `python3 scripts/skill-hygiene-check.py --mode <mode> <repo-root>`. New check IDs: `repeated-inline-prompt`, `repeated-inline-template`, `moderate-skill-bloat`, `repetition-scan-limited`. New fixture commands: `bash tests/skill-hygiene-check-fixtures.sh` and `bash tests/skill-hygiene-release-gate-fixtures.sh --self-check`. Release gate adds advisory coverage checks `skill-hygiene-fixtures` and `skill-hygiene-release-gate-fixtures`; hygiene findings themselves still flow only through the existing `skill-hygiene` advisory path, satisfying FR-5.

**Pros:** Small runtime blast radius for hygiene findings; reuses existing mode handling and release-gate semantics; keeps the checker as one deep module; protects the new deterministic fixture suite and release-gate integration harness from rotting.

**Cons:** Conservative heuristics will miss some real duplication, especially cross-file near-duplicates that are not exact after normalization.

**Risk:** False positives if marker rules are too broad or if the rule treats two different prompt-like blocks as duplication. Mitigation: tune against `--mode all`, use a 400-line bloat threshold, require a matched repeated block pair before warning, use exact fingerprints for cross-file matches, and keep negative fixtures for distinct prompt/template blocks. The fixture advisory can create strict failures if the fixture harness regresses, but that is a test-health failure rather than a hygiene finding; document it separately from `skill-hygiene`.

### Option B - Add A Separate Skill Bulk Analyzer

Create a new script dedicated to prompt/template duplication and line-budget reporting, then call it from `release-gate.sh` as a separate advisory check.

**Module changes:** new analyzer under `scripts/`, new fixtures, release-gate wiring, `RELEASE-GATE.md`.

**Data flow:** release gate runs both the existing hygiene checker and the new analyzer -> each emits its own advisory result -> strict mode upgrades either warning.

**Interfaces:** new CLI such as `python3 scripts/skill-bulk-check.py --mode <mode> .`; new release-gate ID such as `skill-bulk`.

**Pros:** Clear separation if prompt/template heuristics grow substantially; easier to iterate without disturbing existing checks.

**Cons:** Duplicates git mode/file-scope logic that already exists; more release-gate surface; more commands for maintainers to understand.

**Risk:** The two scripts can drift on what counts as a skill file or changed file. Mitigation would require shared helpers, which is more refactor than this roadmap item needs.

### Option C - Cross-File Normalized Block Fingerprinting

Build a broad normalized markdown-block fingerprint pass that compares prompt/template-like blocks within and across all skill files, including near-duplicate matches.

**Module changes:** `scripts/skill-hygiene-check.py` or a new analyzer, plus fixtures and release-gate docs.

**Data flow:** checker extracts markdown/fenced blocks -> normalizes placeholder text and headings -> fingerprints block windows -> compares fingerprints across files -> emits repeated-block findings.

**Interfaces:** existing checker CLI could stay unchanged; findings would need extra evidence such as both paths and line ranges.

**Pros:** Finds the broadest class of duplication, including paraphrased repeated prompt blocks copied across skills.

**Cons:** Higher complexity and more false-positive risk from intentionally shared routing language, contract references, and common report headings.

**Risk:** Broad cross-file comparison can become noisy and harder to explain. The chosen design keeps only the low-noise subset: exact normalized fingerprints for cross-file duplicates, while leaving broad near-duplicate detection for a later roadmap item if evidence shows it is needed.

## Recommendation

**We pick Option A.** It fits the current codebase because `scripts/skill-hygiene-check.py` already owns skill discovery, content checks, findings, and release-gate exit behavior. The accepted tradeoff is that the first version is intentionally conservative: it catches same-file duplicates and exact normalized cross-file copies, but it intentionally misses fuzzy cross-file near-duplicates so it does not turn current accepted skills into broad `--mode all` noise.

## Chosen Design - Detail

### Module Breakdown

- `scripts/skill-hygiene-check.py` - add the new repetition, scan-limit, and bloat checks, constants, staged index-safe path discovery, and small helper functions for block extraction, classification, normalization, fingerprinting, and duplicate matching.
- `tests/skill-hygiene-check-fixtures.py` - create temporary sample repo trees and assert exact check-ID sets for positive and negative repeated prompt/template, cross-file duplicate, mode handling, and moderate bloat scenarios.
- `tests/skill-hygiene-check-fixtures.sh` - wrapper that runs the fixture script from repo root.
- `tests/skill-hygiene-release-gate-fixtures.sh` - explicit release-gate meta-test command for pass/skip/warn/strict wiring and strict-upgrade harnesses. It must also expose a non-recursive `--self-check` mode that validates the fixture harness contract without invoking `scripts/release-gate.sh`.
- `scripts/release-gate.sh` - add advisory `skill-hygiene-fixtures` and `skill-hygiene-release-gate-fixtures` in `--mode all`, or in `staged`/`working` when the diff touches any path in the canonical skill-hygiene infrastructure set.
- `RELEASE-GATE.md` - document the new hygiene finding classes under the existing `skill-hygiene` advisory check and document the separate coverage advisories `skill-hygiene-fixtures` and `skill-hygiene-release-gate-fixtures`.

### Data Flow

```text
release-gate.sh
  -> python3 scripts/skill-hygiene-check.py --mode <mode> .
    -> changed_skill_files() or iter_all_skill_files()
      -> read_skill_text(path)
        -> existing hygiene checks
        -> extract prompt/template block candidates from target files
        -> compare target candidates against same-file candidates and the all-skill reference corpus
        -> repeated-inline-prompt check
        -> repeated-inline-template check
        -> repetition-scan-limited check when fuzzy coverage is bounded
        -> moderate-skill-bloat check
          -> Finding(check_id, path, message)
  -> advisory PASS/WARN skill-hygiene
  -> bash tests/skill-hygiene-check-fixtures.sh when fixture scope is selected
  -> advisory PASS/WARN skill-hygiene-fixtures
  -> bash tests/skill-hygiene-release-gate-fixtures.sh --self-check when fixture scope is selected
  -> advisory PASS/WARN skill-hygiene-release-gate-fixtures
  -> strict mode upgrades WARN to release-gate exit 1
```

The checker fixture command should exercise the checker directly against temporary sample repos, not the live repo, so scenario coverage is deterministic. It is wired as `skill-hygiene-fixtures` to protect the checker coverage suite. The release-gate fixture command has two modes: `--self-check` is the fast non-recursive release-gated subset, while the default full command may invoke real release-gate runs inside temporary worktrees and is used by stage verification. This does not change FR-5: all actual hygiene findings still come from the existing `skill-hygiene` invocation of `scripts/skill-hygiene-check.py`; the fixture advisories validate coverage and release-gate harness health only.

To avoid recursion, `tests/skill-hygiene-check-fixtures.sh` must not invoke `scripts/release-gate.sh`. `tests/skill-hygiene-release-gate-fixtures.sh --self-check` also must not invoke `scripts/release-gate.sh`; it validates shell syntax, canonical trigger lists, expected advisory IDs, JSON assertion helpers, and temp-worktree helper wiring. Full release-gate pass/skip/warn/strict meta-tests live in the default explicit command, `tests/skill-hygiene-release-gate-fixtures.sh`, which is run by implementation stages but not by release gate itself.

Findings should be emitted only for the selected target skill files for the current mode. For repetition checks, the checker may read a reference corpus of all `*/skills/*/SKILL.md` files so a changed skill that copies an existing prompt/template is caught.

Mode snapshots for skill inputs must not mix index and worktree content. Introduce one mode-aware snapshot/listing interface used by changed-file checks, reference-corpus checks, and added-skill metadata checks:

- `staged` target paths come from `git diff --cached --name-only --diff-filter=ACMRT -- '*/skills/*/SKILL.md'`; staged reference paths come from `git ls-files -- '*/skills/*/SKILL.md'`; all staged reads use `git show :<path>`. Do not filter staged paths with `Path.is_file()`.
- Added-skill metadata discovery stays separate from target/reference discovery. In `staged`, it uses `git diff --cached --name-status --diff-filter=A -- '*/skills/*/SKILL.md'` and `git cat-file -e :<path>` for sibling `agents/openai.yaml`; it must not require the staged-added worktree path to exist. In `working`, it keeps the existing added-file behavior from `git diff --name-status --diff-filter=A HEAD` plus untracked skill files. In `all`, it must not treat every filesystem skill as newly added; it should preserve existing behavior by checking only untracked or otherwise added files if any are discoverable, and fixtures must prove legacy skills without new-skill status do not emit `missing-openai-metadata`.
- `working` target paths come from the existing working diff plus untracked skill files; working reference paths come from filesystem skill discovery; all working reads use the filesystem.
- `all` target and reference paths both come from filesystem skill discovery.

This keeps `--mode staged` deterministic for skill inputs: unstaged worktree duplicates cannot create staged findings, staged files deleted from the worktree are still checked, and staged-added skills deleted from the worktree still emit `missing-openai-metadata` when metadata is absent from the index. The release gate still executes scripts from the worktree, so staged verification of checker/fixture implementation changes requires either a clean worktree or the staged self-test path described in Test Strategy.

Define one canonical skill-hygiene infrastructure path set and reuse it for fixture triggering, staged drift detection, temp-worktree candidate copying, docs, and release-gate fixture assertions:

- `scripts/skill-hygiene-check.py`
- `scripts/release-gate.sh`
- `tests/skill-hygiene-check-fixtures.py`
- `tests/skill-hygiene-check-fixtures.sh`
- `tests/skill-hygiene-release-gate-fixtures.sh`
- any helper files matching `tests/skill-hygiene-*`
- `RELEASE-GATE.md`

For staged release-gate runs, enforce a clean-worktree precondition for the canonical set only when the staged diff touches at least one canonical infrastructure path. If staged changes are only ordinary skill files, unrelated unstaged infrastructure work does not block that staged skill check. When the staged diff touches any canonical infrastructure path and any canonical path differs between index and worktree, release gate must add a blocking `skill-hygiene-infra-drift` failure and exit `1` in both non-strict and strict modes. Human and JSON output should use category `blocking`, status `fail`, id `skill-hygiene-infra-drift`, and evidence naming the first drifting path. Do not silently validate staged infrastructure changes with unstaged checker/release-gate/fixture code. Because `scripts/release-gate.sh` itself executes from the worktree, staged self-verification of changes to `scripts/release-gate.sh` still requires the temp worktree candidate harness from the test strategy; the drift guard prevents mixed staged/unstaged infrastructure during normal staged gates.

### Interfaces

Existing public CLI remains unchanged:

```bash
python3 scripts/skill-hygiene-check.py --mode staged .
python3 scripts/skill-hygiene-check.py --mode working .
python3 scripts/skill-hygiene-check.py --mode all .
```

Baseline dry-run uses the same script with an explicit analysis-only flag:

```bash
python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .
```

Dry-run baseline behavior:

- Exit `0` when no candidate repetitions are found, or when candidates are reported for human triage. It is informational, not a release-gate finding path.
- Exit `2` only for runtime errors, matching existing checker failure semantics.
- Output line-oriented records with path, family, line span, fingerprint, matched path/span, and whether the match would be `same-file-exact` or `cross-file-exact`. Near-duplicate dry-run analysis is added later with bounded fuzzy matching, before fuzzy findings are enabled.
- It must not emit normal `Finding` check IDs or trigger strict release-gate behavior. Its purpose is to classify current-repo candidates before enabling the warning rules.
- Fixture assertions should verify the dry-run reports known sample matches and does not affect normal `--mode all` checker exit behavior.

New stable check IDs:

- `repeated-inline-prompt` - a target skill contains a matched duplicate or near-duplicate same-file pair, or an exact normalized cross-file copied pair, of prompt-like blocks with enough literal body length to indicate embedded prompt bulk.
- `repeated-inline-template` - a target skill contains a matched duplicate or near-duplicate same-file pair, or an exact normalized cross-file copied pair, of template/report-wrapper-like blocks with enough literal body length to indicate embedded template bulk.
- `moderate-skill-bloat` - a skill exceeds `MODERATE_SKILL_LINES = 400` but does not exceed `MAX_SKILL_LINES = 750`.
- `repetition-scan-limited` - checker-health warning emitted on the existing `skill-hygiene` path when fuzzy near-duplicate coverage is bounded by deterministic count or character budgets while comparing at least two plausible same-family candidates for a target file. Because it is emitted through the current checker exit-code contract, an unsuppressed finding follows FR-6 like other hygiene warnings: advisory by default and strict-upgraded failure. Exact duplicate detection still ran, but near-duplicate coverage was incomplete. It is emitted once per path even if multiple families limit; the message must include deterministic family and counter details such as `families=prompt,template`, comparison counts, character counts, and pair-cost totals. It is not emitted for a lone oversized candidate. A narrow `## Hygiene Exception` contract may suppress only this checker-health ID for an intentionally self-contained candidate-heavy skill, but only when it includes `repetition-scan-limited:` with a human-readable reason plus `reviewed-with:` or `cap-evidence:` naming the dry-run command or fixture evidence used to accept the bounded fuzzy coverage. The exception does not suppress `repeated-inline-prompt`, `repeated-inline-template`, or exact duplicate checks. If current accepted skills produce unsuppressed scan-limit warnings during the fuzzy baseline, implementation must stop before enabling `repetition-scan-limited` until the maintainer chooses simplification/extraction, prefilter tuning, cap tuning with runtime evidence, or an explicit exception.

Build repetition candidates once per checker run, then match from grouped indexes rather than rescanning the corpus per target. The run-level index should include selected target paths, all `BlockCandidate`s by family, exact fingerprint groups by family, same-file candidate groups by `(source_path, family)`, and selected-target membership. Cross-file exact matching is `O(total_candidates)` to build groups plus `O(number_of_duplicate_group_members)` to emit findings; it is not a per-target full-corpus scan.

New internal check interfaces should follow the existing style while carrying explicit reporting policy:

```python
def check_repeated_inline_prompt_blocks(index: RepetitionIndex, mode: str, reporting_policy: ReportingPolicy, budget: FuzzyBudget) -> list[Finding]: ...
def check_repeated_inline_template_blocks(index: RepetitionIndex, mode: str, reporting_policy: ReportingPolicy, budget: FuzzyBudget) -> list[Finding]: ...
def check_moderate_skill_bloat(path: str, text: str) -> list[Finding]: ...
```

`mode` is the public checker mode (`staged`, `working`, or `all`). `reporting_policy` owns cross-file emission: `all` reports canonicalized non-canonical holders only; `staged` and `working` report any selected target that duplicates another file. Matching may be separated from finding emission if that keeps the implementation cleaner, but the mode-aware caller must own the final reporting decision.

`BlockCandidate` is an internal value object with deterministic identity:

```python
@dataclass(frozen=True)
class BlockCandidate:
    source_path: str
    start_line: int
    end_line: int
    heading: str
    family: Literal["prompt", "template"]
    mode_source: Literal["index", "worktree"]
    normalized_text: str
    literal_text: str
    fingerprint: str
```

The block ID is `(source_path, start_line, end_line, family)`. Same-file matching may compare only distinct non-overlapping spans. Cross-file matching must require `source_path != target_path`; it must never match a candidate to itself through the all-skill reference corpus.

Cross-file duplicate reporting is mode-specific for stable, actionable output, but it always emits file-path findings because the existing `Finding` schema has a single `path`. For each exact fingerprint group, sort candidates by `(source_path, start_line, end_line)`. In `--mode all`, emit one `Finding` per non-canonical holder path, with `path` set to that holder and the message naming the canonical holder plus the duplicate group size; the canonical holder is skipped only to avoid symmetric noise, not because it is known to be the source or clean. In `staged`/`working`, emit for any selected target candidate that shares a fingerprint with any other file, regardless of whether the selected target sorts before or after the reference holder. This ensures a changed skill that copies an existing block is always reportable. If two selected targets duplicate each other, each selected target may receive a finding pointing at the lowest-sorted other holder.

Hygiene exception contract:

- A skill may include a visible `## Hygiene Exception` section.
- That section may suppress only `moderate-skill-bloat` and `repetition-scan-limited`, not repeated prompt/template findings.
- To suppress `moderate-skill-bloat`, the section must include `moderate-skill-bloat:` followed by a human-readable reason.
- To suppress `repetition-scan-limited`, the section must include `repetition-scan-limited:` followed by a human-readable reason plus `reviewed-with:` or `cap-evidence:` naming the dry-run command or fixture evidence used to accept the bounded fuzzy coverage for this skill.
- The checker should still count oversized skills above 750 lines with the existing oversized check.

### Detection Rules

Prompt repetition should be conservative:

- Only extract candidate blocks from files in the existing `*/skills/*/SKILL.md` scope. Findings are emitted only for selected target files, while cross-file comparison may use the all-skill reference corpus.
- Candidate blocks can be fenced blocks or contiguous markdown sections split on `##` or deeper headings. Extraction must either produce non-overlapping ranges or matching must ignore overlapping ranges from the same file, so one fenced prompt inside a section cannot match its containing section as a duplicate.
- Non-fenced prompt/template candidates must be able to span internal input/output headings. Use a concrete boundary algorithm:
  1. Fenced blocks are extracted first and own their exact line ranges.
  2. Non-fenced candidates start only at trigger lines with prompt/template intent, such as "Use this prompt", "Run this prompt", "Adversarial ... review", "For each issue", "If you find no", "Final Report", or a report/template wrapper heading followed within five lines by table/YAML/placeholder structure.
  3. Candidate extension may include internal headings from an allowlist (`## Requirements`, `## Architecture`, `## Issue Details`, `## Final Report`, `## Review Rounds`, `## Output`, `## Handoff`) only when the candidate already has a start trigger and the heading is followed by placeholder text, table/YAML skeleton, or model-output instructions.
  4. Stop at the next top-level workflow heading that is not in the internal allowlist, the next same-level heading after `MAX_CANDIDATE_LINES = 80`, a horizontal rule, frontmatter boundary, or a fenced-block boundary.
  5. Ignore or de-overlap any section candidate that overlaps a fenced candidate.
  Ordinary skill sections named `Requirements`, `Architecture`, or `Final Report` without a nearby trigger and placeholder/output structure are not candidates.
- A prompt candidate should have prompt/agent intent plus enough bulk: at least two prompt signals such as `Use this prompt`, `You are`, `Assigned angle`, `READ-ONLY`, `Round`, explicit reviewer/agent-role language, or imperative model instructions with placeholder inputs; at least `MIN_REPEATED_LITERAL_CHARS = 300` literal characters after removing placeholder bodies; and either at least `MIN_REPEATED_BLOCK_CHARS = 600` normalized characters or `MIN_REPEATED_BLOCK_LINES = 8` nonblank lines.
- Normalize candidate text before matching: remove fence delimiters, lowercase, collapse whitespace, trim markdown heading markers, replace placeholder bodies like `<...>` and `{...}` with stable tokens for candidate comparison, keep a separate literal-only normalized string with placeholders removed, and drop line numbers if present.
- Reject prompt candidates with `PROMPT_PLACEHOLDER_RATIO > 0.35`; a mostly-placeholder prompt is too generic to prove repeated prompt bulk.
- Classify blocks into one primary family before matching using dominant-family scoring, not a blanket template precedence rule. A block with explicit reviewer/agent prompt instructions and an output table/YAML/report section remains `prompt` when the instruction body before the output wrapper has enough literal bulk and prompt score is at least the template score. A block is `template` only when output/report wrapper signals dominate or the section is primarily a reusable artifact body. This prevents duplicate IDs while preserving the right remediation for reviewer prompts with structured output.
- Use the concrete classifier below:

| Signal | Prompt score | Template score |
|---|---:|---:|
| `You are`, `Your job`, `Assigned angle`, `READ-ONLY`, `Do not edit`, `Do NOT modify`, `reviewer`, `agent`, `sub-agent` | +2 each | 0 |
| `Use this prompt`, `Run this prompt`, `For each issue`, `If you find no`, `respond with exactly` | +2 each | 0 |
| Explicit input placeholders such as `## Requirements`, `## Architecture`, `## Issue Details`, `<full content`, `<ANGLE>` | +1 each | 0 |
| `## Final Report`, `## Issues Raised`, `## Review Rounds`, `## Residual`, `## Output`, `## Handoff`, `## Summary` when used as an output artifact section | 0 | +2 each |
| YAML/table skeleton lines such as `status:`, `outputs_written:`, `| Severity |`, `| Round |`, `| Check |`, or placeholder labels inside an output body | 0 | +1 each |
| Imperative line addressed to a model before the first output-wrapper heading | +1 each, max +4 | 0 |

Classification rules:

- Split each candidate into an instruction prefix and output wrapper suffix at the first output-wrapper heading, fenced YAML/report template, or markdown table header.
- Count prompt signals only in the instruction prefix, plus prompt-only phrases anywhere in the block.
- Count template signals only in the output wrapper suffix unless the whole block has no instruction prefix.
- Classify as `prompt` when `prompt_score >= 4`, `prompt_score >= template_score`, and the instruction prefix has at least `MIN_REPEATED_LITERAL_CHARS` literal characters.
- Classify as `template` when `template_score >= 4`, `template_score > prompt_score`, and the stable-anchor requirements below are met.
- If neither threshold is met, or the scores tie below the prompt rule, the block is not a repetition candidate.
- Placeholder ratio is `placeholder_chars / max(1, normalized_chars_before_placeholder_replacement)`. Placeholder chars are spans matching `<...>`, `{...}`, or ALL_CAPS placeholder tokens longer than 3 chars inside template bodies.
- Template stable anchors are normalized headings, YAML keys, table column names, numbered output section labels, and placeholder labels before `:`; repeated anchors must match exactly after lowercasing and whitespace collapse.
- A finding requires a matched pair, not merely two candidates. A same-file matched pair is either exact normalized equality or near-duplicate similarity above `REPEATED_BLOCK_SIMILARITY = 0.92` using Python standard-library `difflib.SequenceMatcher` on normalized text, with both blocks independently satisfying the prompt-candidate rules and sharing at least `MIN_REPEATED_LITERAL_CHARS` of literal content after placeholders are removed.
- A cross-file matched pair must use exact equality of the literal-aware normalized fingerprint. Do not use fuzzy cross-file matching in this item.
- Finding cardinality is one finding per `(target_path, check_id, family)` per run. Aggregate all matched pairs for that file/check/family into one finding with a representative first pair, `duplicate_count`, and any cross-file holder paths needed for actionability. In `--mode all`, this means one finding for each non-canonical holder file in a duplicate group, not a synthetic group-level path. Cap listed examples in the message to keep output compact, but keep the count deterministic. Fixtures should assert the aggregated count for multi-duplicate samples.
- Fuzzy same-file comparison must stay bounded and observable. Route fuzzy comparison through a helper such as `find_near_duplicate_pairs(candidates, budget) -> (pairs, budget, limited_targets)` that sorts target files and candidates deterministically by `(source_path, start_line, end_line)`, compares only same-family candidates whose normalized length ratio is between `0.80` and `1.25`, and buckets by stable literal token-prefix signatures before calling `SequenceMatcher`.
- `FuzzyBudget` is shared across the whole checker run per family, not globally across prompt and template families. Prompt and template matching each receive their own budget counters so prompt-heavy files cannot starve template checks or vice versa. Each family budget tracks per-file and total counters: `MAX_FUZZY_COMPARISONS_PER_FILE = 2000`, `MAX_FUZZY_COMPARE_CHARS_PER_FILE = 500_000`, `MAX_FUZZY_PAIR_COST_PER_COMPARISON = 4_000_000`, `MAX_FUZZY_PAIR_COST_TOTAL = 20_000_000`, `MAX_FUZZY_COMPARISONS_TOTAL = 10_000`, and `MAX_FUZZY_COMPARE_CHARS_TOTAL = 2_000_000`. Same-file exact/fuzzy matching runs only for selected target paths; reference-only files are used for cross-file exact fingerprint groups but must not consume fuzzy budget in `staged` or `working`. Pair cost is `len(a) * len(b)` for the two normalized strings sent to `SequenceMatcher`; skip fuzzy comparison and mark the target limited before calling `SequenceMatcher` if a pair or whole-run pair-cost cap would be exceeded. The helper must expose family, comparison, character, and pair-cost counts for fixture assertions.
- Skip fuzzy matching for an individual candidate whose normalized text exceeds `MAX_FUZZY_CANDIDATE_CHARS = 8_000`, while exact fingerprint matching still covers it. If any per-file, per-pair, or whole-run cap is hit while at least two plausible same-family candidates remain un-compared, add that target path to `limited_targets` and queue a deterministic `repetition-scan-limited` advisory finding for that target, subject to the narrow scan-limit exception contract. When the whole-run budget is exhausted, continue exact fingerprint matching for later files but skip fuzzy matching for later files in deterministic path order and mark only selected target files with un-compared plausible same-family candidates. Do not emit `repetition-scan-limited` for a single large candidate with no plausible partner. Exact fingerprint matches still run before and outside the fuzzy helper and are not capped.
- The finding message should name the file and the first matched pair's headings or line spans so the maintainer can extract the duplicated prompt without reading every candidate.
- The message should recommend extracting reusable prompt text to a prompt artifact or citing a shared contract.

Template repetition should also be conservative:

- Only extract candidate blocks from files in the existing `*/skills/*/SKILL.md` scope. Findings are emitted only for selected target files, while cross-file comparison may use the all-skill reference corpus.
- Candidate blocks should look like inline output/report wrappers, not ordinary references to external templates.
- Strong signals include repeated final report headings, structured output sections, placeholder-heavy report bodies, table or YAML wrapper text intended to be copied into model prompts, and explicit "write the following report/template" language.
- Use the same normalization and matched-pair shape as prompt repetition, but use template-specific size and placeholder policy rather than prompt literal-size or placeholder caps.
- Template candidates may be placeholder-heavy when the stable wrapper structure is repeated. Accept `TEMPLATE_PLACEHOLDER_RATIO <= 0.70` when the block has at least `MIN_TEMPLATE_STRUCTURE_ANCHORS = 5` stable anchors such as headings, table column names, YAML keys, section labels, or placeholder labels, and at least `MIN_TEMPLATE_LITERAL_CHARS = 160` literal wrapper characters outside placeholder values. Above that ratio, findings still require `MIN_TEMPLATE_STRUCTURE_ANCHORS` and `MIN_TEMPLATE_LITERAL_CHARS`, plus exact fingerprint equality and the same stable anchor set. Generic skeletons with fewer anchors or less literal wrapper text must not warn.
- Avoid duplicate noise with the existing `inline-output-contract` check. Keep the existing file-level `inline-output-contract` finding behavior unchanged: if a file contains at least two `FULL_CONTRACT_MARKERS`, it can emit `inline-output-contract` as it does today. Separately, define an output-contract span detector only for masking repeated-inline evidence: at least two `FULL_CONTRACT_MARKERS` in the same fenced block or the same markdown section form an owned span when their line distance is `<= OUTPUT_CONTRACT_MAX_MARKER_SPAN_LINES = 40`. The owned span starts at the nearest preceding heading or fence start before the first marker, and ends at the nearest following heading at the same-or-higher level, fence end, or 40 lines after the first marker, whichever comes first. Markers in separate sections or farther apart still satisfy the existing file-level `inline-output-contract` check but do not create one owned span for repetition masking. Output-contract span ownership is applied before both prompt and template repetition checks. Repetition matching should remove or mask only the owned output-contract subspan and still classify/match the remaining prompt/template body. Suppress `repeated-inline-*` only when the duplicate evidence is entirely inside the output-contract span. A repeated reviewer prompt with substantial duplicated prompt body plus an embedded output contract still emits `repeated-inline-prompt`; a duplicated block whose repeated content is only the output contract emits only `inline-output-contract`.
- A single template block, template-reference-only section, two distinct report wrappers, or a block pair already classified as prompt-only must not produce `repeated-inline-template`.
- The message should recommend extracting reusable templates to a template artifact or citing a shared contract.

Moderate bloat:

- Set `MODERATE_SKILL_LINES = 400`.
- Warn only when `400 < line_count <= 750`.
- Suppress only when the skill has the visible `## Hygiene Exception` contract for `moderate-skill-bloat`.
- Keep the existing oversized check for `line_count > 750` unchanged.
- The finding path must be the target skill path, and the message must include the actual line count, the `MODERATE_SKILL_LINES` threshold, and an action recommendation to extract inline prompts/templates or cite shared contracts. When a valid `## Hygiene Exception` exists, it documents why the skill remains intentionally self-contained instead of emitting `moderate-skill-bloat`.

### Data / Schema Changes

None. No persisted state, database schema, generated cache, or network data is introduced.

### Failure Modes & Handling

- False-positive prompt/template warning: keep marker thresholds high, require a normalized matched pair in the same file or an exact normalized fingerprint across files, cap placeholder-heavy blocks, and verify `--mode all` plus negative fixtures before hand-off.
- False-negative duplication: accepted for Stage 1; this design prioritizes low noise over broad similarity detection.
- Moderate-bloat warning on intentionally self-contained skill: allow only the visible `## Hygiene Exception` section for the moderate warning.
- Scan-limit warning on intentionally self-contained candidate-heavy skill: allow only the narrow `## Hygiene Exception` section for `repetition-scan-limited`, require reviewed-with/cap evidence, and keep exact duplicate and repeated-inline findings unsuppressible.
- Release-gate strict failure surprises maintainers: document the check IDs and preserve existing advisory-by-default behavior. `repetition-scan-limited` is checker-health, but an unsuppressed finding still follows the existing strict-upgrade contract because it is emitted through `skill-hygiene`.
- Fixture command creates secret-like text: use inert placeholders and rely on release-gate `secret-scan` during verification.
- Cross-file duplicate missed on earlier-sorting changed targets: in staged/working mode, emit for any selected target that duplicates another file, independent of canonical sort order; add fixtures where the changed/copied target path sorts before and after the existing source.
- Duplicate prompt/template/output-contract findings: assign each candidate block to one primary family with dominant-family scoring, remove shared output-contract subspans from both prompt and template repetition evidence, and assert exact expected check-ID sets in fixtures.
- Staged content skipped because worktree file is missing: use one mode-aware snapshot/listing interface for changed targets, reference corpus, and added-skill metadata detection; add fixtures where the staged file exists only in the index and where a staged-added skill deleted from the worktree still emits `missing-openai-metadata`.
- Staged content polluted by unstaged worktree text: build both staged target and staged reference corpora from the index only, and add a fixture where the worktree has an unstaged duplicate but the index does not.
- Staged checker infrastructure drift: hard-fail staged release gate with blocking `skill-hygiene-infra-drift` when staged changes touch the canonical skill-hygiene infrastructure set and any canonical infrastructure path differs between index and worktree.
- Self/overlap duplicate false positives: use `BlockCandidate` identity, require distinct non-overlapping same-file spans, require different paths for cross-file matches, and add a fixture with one fenced prompt inside a section.
- Slow release gate on many candidates: apply cheap same-family, length-ratio, token-bucket, comparison-count, candidate-size, pair-cost, and total-compared-character caps before `SequenceMatcher`; route fuzzy matching through a helper whose `comparison_count`, `compared_chars`, `pair_cost`, and `limited_reason` can be asserted; emit `repetition-scan-limited` only when at least two plausible same-family candidates are left un-compared, instead of silently hiding incomplete fuzzy coverage.
- Checker runtime failure: preserve existing exit `2` behavior so release gate reports "could not run" instead of misclassifying runtime errors as hygiene findings.

### Rollout / Migration

No migration is required. The checker CLI and existing `skill-hygiene` release-gate ID remain stable. Start implementation with a candidate-inventory dry run, then a baseline match report against the current repo, before enabling release-gate findings. If the baseline finds likely false positives, retune thresholds and fixtures. If it finds true repeated prompt/template bulk in accepted skills, pause before enabling `repeated-inline-*` and make the scope decision explicit: either add a linked prerequisite cleanup commit/item, or ask the user to accept documented existing advisory findings as allowed by the requirements. Stages that enable strict-upgraded repetition findings may start only after that decision is recorded. If the baseline finds scan-limit hits in accepted skills, resolve them through simplification, prefilter/cap tuning with runtime evidence, or a documented scan-limit exception before enabling `repetition-scan-limited`. The preferred final hand-off remains `python3 scripts/skill-hygiene-check.py --mode all .` and `scripts/release-gate.sh --mode all --strict` clean; accepted existing true positives must be documented in `implementation-log.md` with the user decision and any strict-mode impact.

Before enabling `moderate-skill-bloat`, run a fresh line-count audit over current accepted skills. If any accepted skill is between 401 and 750 lines, pause before enabling the warning and choose one explicit path: user-approved `## Hygiene Exception`, threshold retuning with evidence that it still warns earlier than `MAX_SKILL_LINES`, or prerequisite cleanup. Record the audit command, top line counts, and decision in `implementation-log.md`.

### Test Strategy Hooks

- Unit-style fixture script creates temporary git repos with sample plugin layouts, valid baseline `*/skills/*/SKILL.md` files, and sibling `agents/openai.yaml` where needed so unrelated existing hygiene checks do not pollute assertions.
- Assert exact expected check-ID sets and affected paths, not complete warning sentences. A scenario that emits the expected new ID plus an unrelated ID is a failure.
- Release-gated fixture subsets must stay fast. `skill-hygiene-fixtures` plus `skill-hygiene-release-gate-fixtures --self-check` should target a combined local runtime under 10 seconds and must exclude scaled performance cases and recursive real-release-gate runs. The full explicit `bash tests/skill-hygiene-release-gate-fixtures.sh` may run temp-worktree release-gate meta-tests and is allowed to take about 60 seconds on the current repo when it is proving the full pass/skip/warn/strict matrix. If it grows materially beyond that, split or optimize the explicit meta-test while keeping only the non-recursive `--self-check` subset wired into release-gated paths.
- Existing-check regression scenarios: before enabling new repetition rules, verify current check IDs still fire in `staged`, `working`, and `all` for representative samples: `long-description`, `inline-output-contract`, `oversized-skill`, and `missing-openai-metadata`. These fixtures should prove the new snapshot API preserves old target selection and read semantics across modes.
- Positive scenarios: repeated same-file prompt-like sections produce only `repeated-inline-prompt`; repeated same-file report/template sections produce only `repeated-inline-template`; a copied prompt/template block across two skills produces the relevant repeated-inline ID on the target file and reports both paths or line spans; a 401-line sample skill below 750 lines produces only `moderate-skill-bloat`. The 401-line sample must assert stable message invariants for the actual line count, the `400` threshold, and recommendation terms covering prompt/template extraction or shared-contract citation without snapshotting the full prose.
- Extraction scenarios: non-fenced repeated reviewer prompts and non-fenced repeated report templates with internal `## Requirements`, `## Architecture`, `## Final Report`, tables, and YAML/report sections stay intact as single candidate blocks and produce the expected finding.
- Classifier boundary scenarios: exact fixtures for every score threshold and tie-break path in the scoring table, including prompt-only reviewer instructions, template-only report wrappers, reviewer prompts with structured output that remain `repeated-inline-prompt`, template-dominant repeated wrappers that emit only `repeated-inline-template`, and below-threshold blocks that emit no repeated-inline finding.
- Negative scenarios: two distinct prompt-like blocks do not warn; two distinct report/template blocks do not warn; one prompt/template block does not warn; one fenced prompt/template inside a containing section does not warn; prompt candidates over the prompt placeholder-ratio cap do not warn; a section that only references an external template file does not warn; a `>750`-line skill still produces `oversized-skill` even when it has a valid moderate-bloat `## Hygiene Exception`.
- Template boundary scenarios: placeholder-heavy but structurally repeated report wrappers within the template placeholder policy produce `repeated-inline-template`; placeholder-heavy wrappers without enough stable anchors do not warn; a two-marker shared output-contract copy produces only `inline-output-contract`.
- Output-contract ownership scenarios: a repeated reviewer prompt whose duplicated evidence is only two `FULL_CONTRACT_MARKERS` in the same owned span produces only `inline-output-contract`; a repeated reviewer prompt with substantial duplicated prompt body plus an embedded output contract still produces `repeated-inline-prompt` after the contract subspan is masked; two markers in unrelated sections do not create one owned output-contract span.
- Aggregation scenarios: multiple duplicate pairs in one file produce one finding per `(path, check_id, family)` with deterministic `duplicate_count` and representative spans.
- Exception scenario: a moderate-bloat sample with a valid `## Hygiene Exception` section does not produce `moderate-skill-bloat`; an empty, malformed, or unrelated `## Hygiene Exception` section still emits `moderate-skill-bloat` with the same FR-4 message invariants.
- Mode matrix: fixture coverage must run at least one positive finding through `--mode all`, `--mode working`, and `--mode staged`; include one staged case where the index contains the warning sample but the worktree has been edited back to clean, one staged case where the index contains the warning sample but the worktree path is deleted, one staged-added skill that exists only in the index and still emits `missing-openai-metadata`, and one staged case where only the worktree has an unstaged duplicate so staged mode stays clean. Cross-file fixtures must cover copied target paths that sort before and after the existing source.
- Added-skill metadata negative scenario: legacy existing skills without new-skill status do not emit `missing-openai-metadata` in `--mode all`.
- Extraction negative scenarios: ordinary skill sections named `Requirements`, `Architecture`, or `Final Report` without prompt/template triggers are not absorbed into candidates.
- Limited-scan/performance fixture: include many same-family nonmatching candidate blocks and assert the fuzzy helper's `comparison_count <= MAX_FUZZY_COMPARISONS_PER_FILE`, `compared_chars <= MAX_FUZZY_COMPARE_CHARS_PER_FILE`, and per-pair cost does not exceed `MAX_FUZZY_PAIR_COST_PER_COMPARISON`; include long candidates that trigger the character/candidate-size/pair-cost budget only when there are at least two plausible same-family candidates and assert `repetition-scan-limited`; include a matching sample with a valid scan-limit `## Hygiene Exception` and assert the finding is suppressed while exact duplicates still emit repeated-inline IDs; include a lone large candidate and assert it does not emit `repetition-scan-limited`; include an exact duplicate in the same fixture to prove exact fingerprint matches still run when fuzzy comparison is capped. Separately run the full-repo command as supporting timing evidence for the 5-second local gate target.
- Scan-limit aggregation fixture: when prompt and template scans both limit on the same path, emit one `repetition-scan-limited` finding for that path with deterministic family/counter details in the message.
- Whole-run performance fixture: expose a metrics summary from the checker or helper with total candidate count, total fuzzy comparisons, total compared characters, total pair cost, family, and whether any file was limited. Add a scaled multi-file fixture that creates several candidate-heavy prompt and template skills and asserts each family budget stays below `MAX_FUZZY_COMPARISONS_TOTAL = 10_000`, `MAX_FUZZY_COMPARE_CHARS_TOTAL = 2_000_000`, and `MAX_FUZZY_PAIR_COST_TOTAL = 20_000_000`, with `repetition-scan-limited` emitted for selected files skipped by those whole-run caps. Include a prompt-heavy case that does not starve template fuzzy checks. This scaled fixture belongs to explicit implementation verification or the full release-gate meta-test command, not the release-gated fast fixture subset. Current-repo timing remains supporting evidence, not the only proof.
- Reference-only budget fixture: in `staged` and `working`, a large unmodified reference file must not consume same-file fuzzy budget or emit `repetition-scan-limited` for a selected target.
- Release-gate path: run the strict-upgrade harness against the candidate implementation, not plain `HEAD`. Use a clean temporary git worktree created from the current repo, then apply or copy the current working-tree candidate changes for every path in the canonical skill-hygiene infrastructure set into that temp worktree. Commit those copied candidate changes inside the temp worktree as a local fixture baseline so the subsequent sample skill edit is the only working/staged change. Assert the temp worktree contains the candidate versions and the checker under test contains the new check IDs before running release gate. Then inject exactly one inert skill change outside the idea-to-ship and agent-playbook fixture trigger scopes, such as a `harness-engineering/skills/*/SKILL.md` file. Run the real release gate from that temp worktree and assert non-strict/strict behavior for `--mode working`, `--mode staged` with an index-only or worktree-deleted sample, and `--mode all`. For all unsuppressed `skill-hygiene` warnings, including checker-health `repetition-scan-limited`, non-strict should return exit `0` with `WARN skill-hygiene` and strict should return exit `1` with `FAIL skill-hygiene`. Add a matching strict fixture proving a valid scan-limit exception suppresses only `repetition-scan-limited`. No blocking check or unrelated advisory check should account for the expected strict failure. Repeat this harness for `moderate-skill-bloat`, at least one repetition finding, and `repetition-scan-limited`.
- JSON release-gate fixture: assert `--json` output for `skill-hygiene` warn/strict-fail, `skill-hygiene-fixtures` pass/skip/warn, and `skill-hygiene-release-gate-fixtures` pass/skip/warn, including `category`, `status`, `id`, `exit_code`, and overall command exit behavior.
- Fixture release-gate path: `scripts/release-gate.sh --mode all --strict` must run `skill-hygiene-fixtures` and `skill-hygiene-release-gate-fixtures --self-check`; staged/working release gate runs them only when the canonical infrastructure path set changes. Add release-gate fixture tests for pass, skip, warn, strict-upgraded failure, JSON output, staged checker-infrastructure drift as blocking `skill-hygiene-infra-drift`, and temp-worktree candidate verification for staged `scripts/release-gate.sh` changes. Include a non-recursive validation that changes to `tests/skill-hygiene-release-gate-fixtures.sh` are in the trigger scope and exercised by the release-gated `--self-check` subset plus the full Stage 2/Stage 10 verification.
- Regression check: current repo `python3 scripts/skill-hygiene-check.py --mode all .` and `scripts/release-gate.sh --mode all --strict` remain clean.

## Staged Implementation Plan

1. **Stage 1 - Snapshot Regression Slice:** Add the initial `tests/skill-hygiene-check-fixtures.*` harness with only snapshot and existing-check regression scenarios, then make one mode-aware snapshot/listing interface index-safe for changed targets, reference corpus, and added-skill metadata checks. Add staged fixtures for worktree-clean, worktree-deleted, staged-added-metadata, and unstaged-duplicate cases, plus existing-check regression fixtures across `staged`, `working`, and `all` for `long-description`, `inline-output-contract`, `oversized-skill`, and `missing-openai-metadata`. Verify `bash tests/skill-hygiene-check-fixtures.sh` and existing release-gate behavior remain clean.
2. **Stage 2 - Fixture Gate Slice:** Wire the fast checker fixture harness into `scripts/release-gate.sh` as `skill-hygiene-fixtures`, add `tests/skill-hygiene-release-gate-fixtures.sh` with a non-recursive `--self-check`, wire that self-check as `skill-hygiene-release-gate-fixtures`, and document both coverage advisories. Verify fixture pass/skip/warn/strict behavior with `bash tests/skill-hygiene-check-fixtures.sh`, `bash tests/skill-hygiene-release-gate-fixtures.sh --self-check`, and the full explicit `bash tests/skill-hygiene-release-gate-fixtures.sh`; then run `scripts/release-gate.sh --mode all --strict` on the real repo before adding the new hygiene findings. Later stages append fast deterministic scenarios to the release-gated fixture subset and keep scaled/meta scenarios in explicit verification; each stage must leave all relevant commands green.
3. **Stage 3 - Candidate Inventory Slice:** Add block extraction, candidate classification, normalization, fingerprinting, candidate de-overlap, and fixture-visible candidate inventory output without enabling any new hygiene finding. The analysis output should expose path, family, line span, normalized length, literal length, placeholder ratio, stable anchors, fingerprint, and whether output-contract subspan masking would apply. Add fixtures for classifier thresholds, ordinary-section negatives, internal-heading spans, and normal-mode no-finding behavior. Verify fast fixture commands, `python3 scripts/skill-hygiene-check.py --mode all .`, and `scripts/release-gate.sh --mode all --strict`.
4. **Stage 4 - Baseline Dry Run And Contract Masking Slice:** Add shared output-contract subspan detection/masking, dry-run fixtures for known exact prompt/template matches, line-oriented output invariants, and the `--dry-run-repetition-baseline` analysis-only mode for exact current-repo repetition candidates. Record every baseline run in `implementation-log.md`: command, candidate counts, false-positive/true-positive classification, scan-limit diagnostics if any, and the explicit decision that allows repeated-inline findings to proceed. If true accepted bulk is found, stop before Stage 6/7/8/9 until the user chooses prerequisite cleanup or documented acceptance for the affected family. Verify both fast fixture commands, the full explicit release-gate fixture command, `python3 scripts/skill-hygiene-check.py --mode all .`, and `scripts/release-gate.sh --mode all --strict`.
5. **Stage 5 - Moderate Bloat Slice:** Run and record the pre-enable line-count audit, then add `moderate-skill-bloat`, its `## Hygiene Exception` contract, fixtures, and `RELEASE-GATE.md` documentation. Fixtures must assert the 401-line positive case, the stable FR-4 message invariants, valid exception suppression, and invalid/empty/unrelated exception sections that still warn. Verify fixture commands, a temp full-repo release-gate positive fixture with a 401-line skill (`WARN skill-hygiene`/exit `0` non-strict and `FAIL skill-hygiene`/exit `1` strict), `python3 scripts/skill-hygiene-check.py --mode all .`, and `scripts/release-gate.sh --mode all --strict`.
6. **Stage 6 - Prompt Exact Repetition Slice:** Enable prompt scoring, exact same-file prompt matching, exact cross-file prompt fingerprints, prompt classifier fixtures, and docs for `repeated-inline-prompt`. Do not enable fuzzy matching or `repetition-scan-limited` yet. Verify fixture commands, full-repo hygiene, full release gate, and the temp full-repo release-gate strict-upgrade harness.
7. **Stage 7 - Bounded Fuzzy Prompt Slice:** Add same-file fuzzy prompt matching, a mandatory pre-enable fuzzy dry-run baseline for current-repo near-duplicate prompt candidates, limited-scan character/count/pair-cost/whole-run budgets, the narrow scan-limit exception contract, `repetition-scan-limited`, and docs for bounded fuzzy coverage. Record fuzzy candidate counts, examples, false-positive/true-positive classification, scan-limit hits, exceptions if any, and the explicit stop/go decision in `implementation-log.md` before enabling fuzzy findings. In this stage, `repetition-scan-limited` applies to prompt candidates only. Verify fixture commands, full-repo hygiene, full release gate, and the temp full-repo release-gate strict-upgrade harness.
8. **Stage 8 - Template Exact Repetition Slice:** Enable exact template classification/matching, output-contract span exclusion using the existing two-marker threshold, template exact fixtures, and docs for `repeated-inline-template`. Do not enable template fuzzy matching yet. Verify fixture commands, full-repo hygiene, full release gate, and the temp full-repo release-gate strict-upgrade harness.
9. **Stage 9 - Bounded Fuzzy Template Slice:** Extend bounded fuzzy matching and `repetition-scan-limited` to template candidates with a mandatory pre-enable fuzzy dry-run baseline for current-repo near-duplicate template candidates. Record fuzzy candidate counts, examples, false-positive/true-positive classification, scan-limit hits, exceptions if any, and the explicit stop/go decision in `implementation-log.md` before enabling fuzzy findings. Verify fixture commands, full-repo hygiene, full release gate, family-specific budget fixtures, and the temp full-repo release-gate strict-upgrade harness.
10. **Stage 10 - Final Regression:** Re-run fast fixture commands, the full explicit `bash tests/skill-hygiene-release-gate-fixtures.sh`, `python3 scripts/skill-hygiene-check.py --mode all .`, `scripts/release-gate.sh --mode working --strict`, and `scripts/release-gate.sh --mode all --strict`; if the handoff uses staged changes, also run `scripts/release-gate.sh --mode staged --strict`. Retune thresholds only for proven false positives and keep the full-repo strict gate clean unless the user explicitly accepted documented existing true positives in Stage 4.

## Open Questions

No blocking open questions remain for implementation. Design choices are: 400-line moderate threshold, same-file normalized matched-pair repetition plus exact normalized cross-file fingerprints, documented `repetition-scan-limited` for bounded fuzzy coverage, visible `## Hygiene Exception` only for `moderate-skill-bloat` and checker-health `repetition-scan-limited`, no accepted strict-mode failures unless explicitly decided in Stage 4, new coverage advisories `skill-hygiene-fixtures` and `skill-hygiene-release-gate-fixtures` but no new release-gate advisory ID for hygiene findings, and no user-facing token/character budget report in this item.
