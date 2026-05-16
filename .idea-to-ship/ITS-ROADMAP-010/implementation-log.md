# Implementation Log - ITS-ROADMAP-010

**Architecture:** architecture.md
**Started:** 2026-05-15

## Stage Status
- [x] Stage 1 - Snapshot Regression Slice
- [x] Stage 2 - Fixture Gate Slice
- [x] Stage 3 - Candidate Inventory Slice
- [x] Stage 4 - Baseline Dry Run And Contract Masking Slice
- [x] Stage 5 - Moderate Bloat Slice
- [x] Stage 6 - Prompt Exact Repetition Slice
- [x] Stage 7 - Bounded Fuzzy Prompt Slice
- [x] Stage 8 - Template Exact Repetition Slice
- [x] Stage 9 - Bounded Fuzzy Template Slice
- [x] Stage 10 - Final Regression

## Stage 1 - Snapshot Regression Slice

### Pre-stage assumptions
- Use the existing `scripts/skill-hygiene-check.py` CLI as the only production interface for this stage.
- Add a dedicated `tests/skill-hygiene-check-fixtures.py` plus shell wrapper, matching existing fixture style.
- Keep Stage 1 limited to mode snapshot/listing behavior and existing hygiene checks; do not add prompt/template repetition or moderate-bloat checks yet.
- Treat this as non-UI work because it only changes CLI/test behavior.

### Success criteria
- TDD gate: `bash tests/skill-hygiene-check-fixtures.sh` fails before production changes for staged index-only skill cases.
- Final verification: `bash tests/skill-hygiene-check-fixtures.sh` passes.
- Regression verification: `python3 scripts/skill-hygiene-check.py --mode all .` passes or reports only intentional current-diff findings.

**Completed:** 2026-05-15 16:55 CST

### Files touched
- `scripts/skill-hygiene-check.py` - made staged changed/added skill discovery return index paths without worktree `Path.is_file()` filtering.
- `tests/skill-hygiene-check-fixtures.py` - added deterministic temporary-repo fixtures for existing checks and staged index-only snapshot cases.
- `tests/skill-hygiene-check-fixtures.sh` - added repo-root wrapper for the fixture helper.
- `.idea-to-ship/ITS-ROADMAP-010/test-plan.md` - recorded Stage 1 TDD slices.
- `.idea-to-ship/ITS-ROADMAP-010/tdd-log.md` - recorded red-first evidence.
- `.idea-to-ship/ITS-ROADMAP-010/implementation-log.md` - recorded stage assumptions, success criteria, and completion evidence.

### Decisions made during implementation
- Staged mode now returns the `git diff --cached` path set directly: staged content is read via existing `git show :path`, so worktree deletion must not filter out the target.
- Staged added-skill metadata discovery now returns the cached added path set directly: metadata existence is already checked through `git cat-file -e`.
- Stage 1 fixtures use real temporary git repositories instead of mocking checker internals, so they verify the CLI contract and git snapshot behavior end to end.

### Deviations from design artifacts
- None.

### Adjacent issues noticed (NOT fixed here)
- `tests/skill-hygiene-check-fixtures.sh` is not yet wired into `scripts/release-gate.sh`; that is Stage 2 by design.
- Prompt/template repetition and moderate-bloat checks are intentionally not implemented in Stage 1.

### Verification
- tdd: `tdd-log.md` entry `2026-05-15 16:53 CST`; failing test then passed (`bash tests/skill-hygiene-check-fixtures.sh`).
- tests: `bash tests/skill-hygiene-check-fixtures.sh` passed.
- hygiene: `python3 scripts/skill-hygiene-check.py --mode all .` passed.
- release gate: `scripts/release-gate.sh --mode all --strict` passed.
- secret scan: `python3 secret-scanner/scripts/scan.py --mode working --format json` returned `[]`.

### Cross-Skill Checks
- `secret-scanner:scan-secrets --mode working` - triggered because this stage adds fixture files; deterministic scanner returned no findings.
## Stage 2 - Fixture Gate Slice

### Pre-stage assumptions
- Wire Stage 1's fast checker fixture into `scripts/release-gate.sh` as an advisory, without changing actual `skill-hygiene` finding semantics.
- Add a separate release-gate meta fixture command whose `--self-check` mode is safe to call from release gate without recursively invoking `scripts/release-gate.sh`.
- Keep full release-gate meta assertions in the explicit `bash tests/skill-hygiene-release-gate-fixtures.sh` command; release gate itself should call only `--self-check`.
- Treat this as non-UI work because it only changes CLI/test/docs behavior.

### Success criteria
- TDD gate: `bash tests/skill-hygiene-release-gate-fixtures.sh` fails before release-gate wiring because the new advisory IDs are absent.
- Final verification: `bash tests/skill-hygiene-release-gate-fixtures.sh` and `bash tests/skill-hygiene-release-gate-fixtures.sh --self-check` pass.
- Release-gate verification: `scripts/release-gate.sh --mode all --strict` and `scripts/release-gate.sh --mode working --strict` pass.

**Completed:** 2026-05-15 17:07 CST

### Files touched
- `scripts/release-gate.sh` - added `skill-hygiene-fixtures` and `skill-hygiene-release-gate-fixtures` advisory checks and wired them into the gate.
- `RELEASE-GATE.md` - documented the two skill hygiene fixture advisories and the non-recursive self-check boundary.
- `tests/skill-hygiene-release-gate-fixtures.sh` - added self-check and full JSON release-gate fixture assertions.
- `.idea-to-ship/ITS-ROADMAP-010/test-plan.md` - added Stage 2 TDD slices.
- `.idea-to-ship/ITS-ROADMAP-010/tdd-log.md` - recorded Stage 2 red-first evidence.
- `.idea-to-ship/ITS-ROADMAP-010/implementation-log.md` - recorded Stage 2 assumptions, verification, and completion evidence.

### Decisions made during implementation
- Both new advisories share the same skill-hygiene infrastructure trigger scope: `scripts/skill-hygiene-check.py`, `scripts/release-gate.sh`, `tests/skill-hygiene-*`, and `RELEASE-GATE.md`.
- The release gate calls `tests/skill-hygiene-release-gate-fixtures.sh --self-check` only. The default full command may call `scripts/release-gate.sh --mode all --json`, so it remains explicit verification and does not recurse.
- The fixture assertions use JSON `id`, `category`, `status`, and `exit_code` invariants instead of matching full prose.

### Deviations from design artifacts
- None.

### Adjacent issues noticed (NOT fixed here)
- Staged checker-infrastructure drift with blocking `skill-hygiene-infra-drift` was deferred at this point; it is resolved in Code Review Fixes - Iteration 5.

### Verification
- tdd: `tdd-log.md` entry `2026-05-15 17:05 CST`; failing test then passed (`bash tests/skill-hygiene-release-gate-fixtures.sh`).
- tests: `bash tests/skill-hygiene-release-gate-fixtures.sh` passed, including all-mode pass, staged skip, working pass, working warn, and working strict-upgrade scenarios.
- tests: `bash tests/skill-hygiene-release-gate-fixtures.sh --self-check` passed.
- tests: `bash tests/skill-hygiene-check-fixtures.sh` passed.
- hygiene: `python3 scripts/skill-hygiene-check.py --mode all .` passed.
- release gate: `scripts/release-gate.sh --mode all --strict` passed.
- release gate: `scripts/release-gate.sh --mode working --strict` passed.
- secret scan: `python3 secret-scanner/scripts/scan.py --mode working --format json` returned `[]`.

### Cross-Skill Checks
- `secret-scanner:scan-secrets --mode working` - triggered because this stage adds fixture code and release-gate/docs changes; deterministic scanner returned no findings.
## Stage 3 - Candidate Inventory Slice

### Pre-stage assumptions
- Add candidate inventory as hidden fixture/debug CLI output (`--dump-repetition-candidates`) because architecture reserves the public `--dry-run-repetition-baseline` mode for Stage 4.
- Keep normal `skill-hygiene` behavior unchanged: candidate extraction and classification must not emit new findings yet.
- Implement only deterministic extraction/classification metadata needed by Stage 3 fixtures: path, family, line span, normalized/literal lengths, placeholder ratio, stable anchors, fingerprint, and output-contract mask applicability.
- Treat this as non-UI work because it only changes CLI/test behavior.

### Success criteria
- TDD gate: `bash tests/skill-hygiene-check-fixtures.sh` fails before production changes because `--dump-repetition-candidates` is missing.
- Final verification: `bash tests/skill-hygiene-check-fixtures.sh` passes with prompt/template classification, ordinary-section negatives, internal-heading span fixtures, classifier boundary guardrails, placeholder-label and `## Output` wrapper template coverage, plain-internal-heading stop behavior, ordinary labeled final-report negatives, and line-number/uppercase-placeholder fingerprint normalization.
- Regression verification: normal `python3 scripts/skill-hygiene-check.py --mode all .` and strict release gates remain clean.

**Completed:** 2026-05-15 17:36 CST

### Files touched
- `scripts/skill-hygiene-check.py` - added candidate constants, `BlockCandidate`, normalization, stable-anchor extraction, prompt/template classifier scoring, non-overlapping candidate extraction, and hidden inventory output.
- `tests/skill-hygiene-check-fixtures.py` - added Stage 3 fixtures for prompt/template inventory, ordinary-section negatives, and internal-heading spans.
- `.idea-to-ship/ITS-ROADMAP-010/test-plan.md` - added Stage 3 TDD slices.
- `.idea-to-ship/ITS-ROADMAP-010/tdd-log.md` - recorded Stage 3 red-first evidence.
- `.idea-to-ship/ITS-ROADMAP-010/implementation-log.md` - recorded Stage 3 assumptions, verification, and completion evidence.

### Decisions made during implementation
- `--dump-repetition-candidates` is hidden from help output and intended only for deterministic fixtures; Stage 4 will add the public dry-run baseline CLI named in architecture.
- Output is tab-separated `key=value` records so fixtures can assert stable structural fields without golden prose snapshots.
- Output-contract masking is exposed as a boolean applicability signal only; actual subspan masking remains Stage 4.
- Candidate extraction currently owns fenced-block ranges first and skips overlapping non-fenced ranges, matching the Stage 3 de-overlap requirement without enabling duplicate matching.
- Classifier scoring now follows the architecture table with separate weighted prompt-role, prompt-phrase, prompt-input, output-heading, and skeleton scorers instead of one flat pattern list.
- Candidate normalization strips common line-number prefixes and normalizes uppercase placeholder names before lowercasing/fingerprinting.
- Placeholder labels such as `<severity>:` are treated as template anchors and skeleton scoring signals.
- Output-wrapper headings such as `## Output` can start template candidates only when nearby structure is present.
- Allowlisted internal headings are included only when nearby content has placeholder, table, known YAML skeleton, or model-output instruction structure.

### Deviations from design artifacts
- None. The hidden debug flag is a local fixture surface for Stage 3; it does not replace the Stage 4 public `--dry-run-repetition-baseline` interface.

### Adjacent issues noticed (NOT fixed here)
- Exact duplicate matching, dry-run baseline reporting, output-contract subspan masking, moderate-bloat findings, prompt/template findings, and bounded fuzzy matching remain deferred to later stages.
- Staged checker-infrastructure drift with blocking `skill-hygiene-infra-drift` was deferred at this point; it is resolved in Code Review Fixes - Iteration 5.

### Verification
- tdd: `tdd-log.md` entry `2026-05-15 17:29 CST`; failing test then passed (`bash tests/skill-hygiene-check-fixtures.sh`).
- tests: `bash tests/skill-hygiene-check-fixtures.sh` passed, including review-backfill coverage for classifier boundaries, plain internal-heading stops, line-number normalization, and uppercase-placeholder normalization.
- tests: `bash tests/skill-hygiene-release-gate-fixtures.sh` passed.
- tests: `bash tests/skill-hygiene-release-gate-fixtures.sh --self-check` passed.
- hygiene: `python3 scripts/skill-hygiene-check.py --mode all .` passed.
- release gate: `scripts/release-gate.sh --mode all --strict` passed.
- release gate: `scripts/release-gate.sh --mode working --strict` passed.
- secret scan: `python3 secret-scanner/scripts/scan.py --mode working --format json` returned `[]`.
- whitespace: `git diff --check HEAD` passed.

### Cross-Skill Checks
- `secret-scanner:scan-secrets --mode working` - triggered because this stage adds fixture samples and checker parsing code; deterministic scanner returned no findings.
## Stage 4 - Baseline Dry Run And Contract Masking Slice

### Pre-stage assumptions
- Add `--dry-run-repetition-baseline` as an analysis-only checker mode; it must not emit normal `Finding` records or affect strict release-gate behavior.
- Keep repeated-inline findings disabled until later stages. Stage 4 only exposes exact baseline evidence and output-contract masking.
- Use the existing prompt/template candidate inventory as the source of candidate blocks, then mask owned output-contract subspans before classification/fingerprinting.
- Treat this as non-UI work because it only changes CLI/test behavior.

### Success criteria
- TDD gate: `bash tests/skill-hygiene-check-fixtures.sh` fails before production changes because `--dry-run-repetition-baseline` is missing.
- Baseline verification: dry-run output reports exact same-file prompt and exact cross-file template matches in fixtures with path, family, line spans, fingerprint, matched path/span, and match type.
- Contract masking verification: repeated output-contract-only text is not treated as prompt/template repetition, while repeated prompt bodies with embedded output contracts still baseline as prompt matches.
- Current-repo decision gate: `python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .` shows no accepted exact prompt/template repetition before later repeated-inline findings are enabled.

**Completed:** 2026-05-16 10:57 CST

### Files touched
- `scripts/skill-hygiene-check.py` - added output-contract span masking, exact repetition matching, reference-corpus collection, and `--dry-run-repetition-baseline`.
- `tests/skill-hygiene-check-fixtures.py` - added exact baseline and output-contract masking fixtures.
- `.idea-to-ship/ITS-ROADMAP-010/test-plan.md` - added Stage 4 TDD slices.
- `.idea-to-ship/ITS-ROADMAP-010/tdd-log.md` - recorded Stage 4 red-first evidence.
- `.idea-to-ship/ITS-ROADMAP-010/implementation-log.md` - recorded Stage 4 assumptions, verification, and baseline decision.

### Decisions made during implementation
- Dry-run output is tab-separated `match` and `summary` records so tests can assert structural fields without snapshotting prose.
- Exact matching compares candidate family, normalized fingerprint, and normalized text; same-file matches require non-overlapping spans, and cross-file matches require different paths.
- Output-contract masking removes owned contract spans before classification and fingerprinting. Contract-only repeated blocks therefore remain covered by `inline-output-contract` without producing repetition evidence.
- Current repo baseline result: `prompt` candidates `25`, exact prompt matches `0`; `template` candidates `1`, exact template matches `0`; scan limited `false`. This is a go decision for Stage 6 and Stage 8 exact repeated-inline findings because there are no current accepted exact true positives or false positives to document.

### Deviations from design artifacts
- None.

### Adjacent issues noticed (NOT fixed here)
- Moderate-bloat findings, repeated-inline findings, bounded fuzzy matching, scan-limit findings, and staged checker-infrastructure drift were deferred at this point; they are resolved in later stages and Code Review Fixes - Iteration 5.

### Verification
- tdd: `tdd-log.md` entry `2026-05-16 10:54 CST`; failing test then passed (`bash tests/skill-hygiene-check-fixtures.sh`).
- tests: `bash tests/skill-hygiene-check-fixtures.sh` passed.
- tests: `bash tests/skill-hygiene-release-gate-fixtures.sh --self-check` passed.
- tests: `bash tests/skill-hygiene-release-gate-fixtures.sh` passed.
- baseline: `python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .` returned summary only: prompt candidates `25`, exact prompt matches `0`; template candidates `1`, exact template matches `0`; limited `false`.
- hygiene: `python3 scripts/skill-hygiene-check.py --mode all .` passed.
- release gate: `scripts/release-gate.sh --mode all --strict` passed.

### Cross-Skill Checks
- `secret-scanner:scan-secrets --mode working` - covered by `scripts/release-gate.sh --mode all --strict`; scanner returned no findings.
## Stage 5 - Moderate Bloat Slice

### Pre-stage assumptions
- Use `MODERATE_SKILL_LINES = 400` from architecture; keep the existing `MAX_SKILL_LINES = 750` hard warning unchanged.
- Add a visible `## Hygiene Exception` contract with a non-empty `moderate-skill-bloat:` reason to suppress only the moderate warning.
- Preserve advisory-by-default release-gate behavior by emitting the new check through the existing `skill-hygiene` checker path.
- Treat this as non-UI work because it only changes CLI/test/docs behavior.

### Success criteria
- Pre-enable audit: no accepted current skill is above 400 lines and below 750 lines.
- TDD gate: `bash tests/skill-hygiene-check-fixtures.sh` fails before production changes because `moderate-skill-bloat` is missing.
- Fixture verification: 401-line samples warn unless they have a valid exception; empty/unrelated exceptions still warn; >750-line skills still emit `oversized-skill`.
- Release-gate verification: a temp 401-line skill produces `WARN skill-hygiene` in non-strict mode and `FAIL skill-hygiene` in strict mode.

**Completed:** 2026-05-16 11:02 CST

### Files touched
- `scripts/skill-hygiene-check.py` - added `MODERATE_SKILL_LINES`, moderate-bloat finding logic, and the moderate-bloat hygiene exception parser.
- `tests/skill-hygiene-check-fixtures.py` - added moderate-bloat positive, exception, invalid-exception, and oversized guardrail fixtures.
- `tests/skill-hygiene-release-gate-fixtures.sh` - added a temp release-gate strict-upgrade fixture for a 401-line skill.
- `RELEASE-GATE.md` - documented moderate-bloat warnings and the exception boundary.
- `.idea-to-ship/ITS-ROADMAP-010/test-plan.md` - added Stage 5 TDD slices.
- `.idea-to-ship/ITS-ROADMAP-010/tdd-log.md` - recorded Stage 5 red-first evidence.
- `.idea-to-ship/ITS-ROADMAP-010/implementation-log.md` - recorded Stage 5 assumptions, audit, and verification.

### Decisions made during implementation
- The valid moderate-bloat exception requires the reason to appear on the same line as `moderate-skill-bloat:`. Empty reasons do not suppress warnings.
- The exception parser uses line-local whitespace matching so a following filler line cannot accidentally satisfy an empty exception.
- Audit command: `for f in */skills/*/SKILL.md; do wc -l "$f"; done | sort -nr | head -20`. Top counts were `375` (`issue-evaluator/skills/fix-pr-comments/SKILL.md`), `336` (`idea-to-ship/skills/roadmap/SKILL.md`), `327` (`idea-to-ship/skills/commercialize/SKILL.md`), `302`, and `300`. No current accepted skill crosses 400 lines, so the threshold is enabled without exceptions or retuning.

### Deviations from design artifacts
- None.

### Adjacent issues noticed (NOT fixed here)
- Repeated-inline prompt/template findings and bounded fuzzy scan-limit findings remain deferred to later stages.

### Verification
- tdd: `tdd-log.md` entry `2026-05-16 11:00 CST`; failing test then passed (`bash tests/skill-hygiene-check-fixtures.sh && bash tests/skill-hygiene-release-gate-fixtures.sh`).
- tests: `bash tests/skill-hygiene-check-fixtures.sh` passed.
- tests: `bash tests/skill-hygiene-release-gate-fixtures.sh` passed, including non-strict `WARN skill-hygiene` and strict `FAIL skill-hygiene` for a temp 401-line skill.
- hygiene: `python3 scripts/skill-hygiene-check.py --mode all .` passed.
- release gate: `scripts/release-gate.sh --mode all --strict` passed.
- whitespace: `git diff --check HEAD` passed.

### Cross-Skill Checks
- `secret-scanner:scan-secrets --mode working` - covered by `scripts/release-gate.sh --mode all --strict`; scanner returned no findings.
## Stage 6 - Prompt Exact Repetition Slice

### Pre-stage assumptions
- Reuse the Stage 4 exact match engine for normal-mode findings; enable only the `prompt` family in this stage.
- Keep template exact findings disabled until Stage 8, even though dry-run baseline can already report exact template matches.
- Emit one finding per target path for prompt duplicates and include stable `duplicate_count`, line spans, matched path/span, and extraction guidance.
- Treat this as non-UI work because it only changes CLI/test/docs behavior.

### Success criteria
- TDD gate: `bash tests/skill-hygiene-check-fixtures.sh` fails before production changes because exact prompt duplicates do not emit `repeated-inline-prompt`.
- Exact same-file prompt duplicates emit `repeated-inline-prompt` without `repeated-inline-template`.
- Working-mode copied prompt target skills emit findings for selected target paths whether the target path sorts before or after the reference source.
- Release-gate verification: a temp repeated-prompt skill produces `WARN skill-hygiene` in non-strict mode and `FAIL skill-hygiene` in strict mode.

**Completed:** 2026-05-16 11:06 CST

### Files touched
- `scripts/skill-hygiene-check.py` - added normal-mode repeated-inline finding aggregation and enabled exact prompt findings.
- `tests/skill-hygiene-check-fixtures.py` - added same-file and cross-file exact prompt finding fixtures.
- `tests/skill-hygiene-release-gate-fixtures.sh` - added a temp repeated-prompt strict-upgrade fixture.
- `RELEASE-GATE.md` - documented `repeated-inline-prompt`.
- `.idea-to-ship/ITS-ROADMAP-010/test-plan.md` - added Stage 6 TDD slices.
- `.idea-to-ship/ITS-ROADMAP-010/tdd-log.md` - recorded Stage 6 red-first evidence.
- `.idea-to-ship/ITS-ROADMAP-010/implementation-log.md` - recorded Stage 6 verification.

### Decisions made during implementation
- The repeated prompt message includes the first representative span and matched span rather than every duplicate pair, keeping output compact while preserving actionability.
- Source paths can appear as matched evidence in working-mode messages, but findings are emitted only for selected target paths.
- Current repo baseline still has exact prompt matches `0`, so no accepted prompt true positives or false positives needed exceptions or documented acceptance.

### Deviations from design artifacts
- None.

### Adjacent issues noticed (NOT fixed here)
- Fuzzy prompt matching, scan-limit findings, and template repetition findings remain deferred to later stages.

### Verification
- tdd: `tdd-log.md` entry `2026-05-16 11:06 CST`; failing test then passed (`bash tests/skill-hygiene-check-fixtures.sh && bash tests/skill-hygiene-release-gate-fixtures.sh`).
- tests: `bash tests/skill-hygiene-check-fixtures.sh` passed.
- tests: `bash tests/skill-hygiene-release-gate-fixtures.sh` passed, including non-strict `WARN skill-hygiene` and strict `FAIL skill-hygiene` for a temp repeated-prompt skill.
- baseline: `python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .` returned prompt candidates `25`, exact prompt matches `0`; template candidates `1`, exact template matches `0`; limited `false`.
- hygiene: `python3 scripts/skill-hygiene-check.py --mode all .` passed.
- release gate: `scripts/release-gate.sh --mode all --strict` passed.

### Cross-Skill Checks
- `secret-scanner:scan-secrets --mode working` - covered by `scripts/release-gate.sh --mode all --strict`; scanner returned no findings.
## Stage 7 - Bounded Fuzzy Prompt Slice

### Pre-stage assumptions
- Extend matching only for same-file prompt candidates in this stage; template fuzzy matching remains Stage 9.
- Use deterministic per-file budgets before `SequenceMatcher`: candidate size, pair cost, comparison count, and compared character caps.
- Emit `repetition-scan-limited` only when at least two plausible same-family candidates remain un-compared; a valid exception requires `repetition-scan-limited:` plus `reviewed-with:` or `cap-evidence:`.
- Treat this as non-UI work because it only changes CLI/test/docs behavior.

### Success criteria
- TDD gate: `bash tests/skill-hygiene-check-fixtures.sh` fails before production changes because near-duplicate prompts do not emit findings and scan-limit warnings are absent.
- Fuzzy prompt verification: same-file near-duplicate prompt candidates emit `repeated-inline-prompt` with `same-file-fuzzy` evidence and appear in dry-run baseline.
- Scan-limit verification: pair-cost-limited prompt candidates emit `repetition-scan-limited`, valid exceptions suppress only that ID, exact duplicates still emit, and lone large candidates stay clean.
- Release-gate verification: a temp scan-limited prompt skill produces `WARN skill-hygiene` in non-strict mode and `FAIL skill-hygiene` in strict mode.

**Completed:** 2026-05-16 11:11 CST

### Files touched
- `scripts/skill-hygiene-check.py` - added bounded same-file fuzzy prompt matching, scan-limit diagnostics, scan-limit exception parsing, and fuzzy dry-run output.
- `tests/skill-hygiene-check-fixtures.py` - added near-duplicate prompt and prompt scan-limit fixtures.
- `tests/skill-hygiene-release-gate-fixtures.sh` - added a temp scan-limited prompt strict-upgrade fixture.
- `RELEASE-GATE.md` - documented `repetition-scan-limited`.
- `.idea-to-ship/ITS-ROADMAP-010/test-plan.md` - added Stage 7 TDD slices.
- `.idea-to-ship/ITS-ROADMAP-010/tdd-log.md` - recorded Stage 7 red-first evidence.
- `.idea-to-ship/ITS-ROADMAP-010/implementation-log.md` - recorded Stage 7 baseline and verification.

### Decisions made during implementation
- Fuzzy matching uses the existing normalized candidate text plus a literal-token prefix prefilter before `SequenceMatcher`, keeping near-duplicate checks conservative.
- The scan-limit finding reports family, comparisons, compared chars, pair cost, and reasons in one path-level finding.
- Current repo fuzzy baseline result: `prompt` candidates `25`, exact/fuzzy prompt matches `0`, limited `false`; `template` candidates `1`, exact template matches `0`, limited `false`. This is a go decision for prompt fuzzy enablement with no accepted current findings.

### Deviations from design artifacts
- Stage 7 initially implemented per-file prompt caps only; review iteration 1 later added the architecture-required per-family whole-run caps and scaled fixture coverage.

### Adjacent issues noticed (NOT fixed here)
- Template exact and fuzzy findings remain deferred to Stages 8 and 9.

### Verification
- tdd: `tdd-log.md` entry `2026-05-16 11:12 CST`; failing test then passed (`bash tests/skill-hygiene-check-fixtures.sh && bash tests/skill-hygiene-release-gate-fixtures.sh`).
- tests: `bash tests/skill-hygiene-check-fixtures.sh` passed.
- tests: `bash tests/skill-hygiene-release-gate-fixtures.sh` passed, including non-strict `WARN skill-hygiene` and strict `FAIL skill-hygiene` for a temp scan-limited prompt skill.
- baseline: `python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .` returned prompt candidates `25`, matches `0`, limited `false`; template candidates `1`, matches `0`, limited `false`.
- hygiene: `python3 scripts/skill-hygiene-check.py --mode all .` passed.
- release gate: `scripts/release-gate.sh --mode all --strict` passed.

### Cross-Skill Checks
- `secret-scanner:scan-secrets --mode working` - covered by `scripts/release-gate.sh --mode all --strict`; scanner returned no findings.
## Stage 8 - Template Exact Repetition Slice

### Pre-stage assumptions
- Reuse the Stage 4 exact match engine for normal-mode template findings; do not enable template fuzzy matching until Stage 9.
- Keep output-contract masking active so duplicated output-contract-only text remains covered by `inline-output-contract` instead of `repeated-inline-template`.
- Emit one finding per target path for template duplicates with stable `duplicate_count`, line spans, matched path/span, and extraction guidance.
- Treat this as non-UI work because it only changes CLI/test/docs behavior.

### Success criteria
- TDD gate: `bash tests/skill-hygiene-check-fixtures.sh` fails before production changes because exact template duplicates do not emit `repeated-inline-template`.
- Same-file and working-mode cross-file template duplicates emit `repeated-inline-template` without `repeated-inline-prompt`.
- Release-gate verification: a temp repeated-template skill produces `WARN skill-hygiene` in non-strict mode and `FAIL skill-hygiene` in strict mode.

**Completed:** 2026-05-16 11:14 CST

### Files touched
- `scripts/skill-hygiene-check.py` - enabled normal-mode exact template findings.
- `tests/skill-hygiene-check-fixtures.py` - added same-file and cross-file exact template finding fixtures.
- `tests/skill-hygiene-release-gate-fixtures.sh` - added a temp repeated-template strict-upgrade fixture.
- `RELEASE-GATE.md` - documented `repeated-inline-template`.
- `.idea-to-ship/ITS-ROADMAP-010/test-plan.md` - added Stage 8 TDD slices.
- `.idea-to-ship/ITS-ROADMAP-010/tdd-log.md` - recorded Stage 8 red-first evidence.
- `.idea-to-ship/ITS-ROADMAP-010/implementation-log.md` - recorded Stage 8 verification.

### Decisions made during implementation
- Template findings use the same aggregation shape as prompt findings. The family-specific message recommends template artifacts instead of prompt artifacts.
- Current repo baseline still has exact template matches `0`, so no accepted template true positives or false positives needed exceptions or documented acceptance.

### Deviations from design artifacts
- None.

### Adjacent issues noticed (NOT fixed here)
- Template fuzzy matching and template scan-limit coverage remain deferred to Stage 9.

### Verification
- tdd: `tdd-log.md` entry `2026-05-16 11:13 CST`; failing test then passed (`bash tests/skill-hygiene-check-fixtures.sh && bash tests/skill-hygiene-release-gate-fixtures.sh`).
- tests: `bash tests/skill-hygiene-check-fixtures.sh` passed.
- tests: `bash tests/skill-hygiene-release-gate-fixtures.sh` passed, including non-strict `WARN skill-hygiene` and strict `FAIL skill-hygiene` for a temp repeated-template skill.
- baseline: `python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .` returned prompt candidates `25`, matches `0`, limited `false`; template candidates `1`, matches `0`, limited `false`.
- hygiene: `python3 scripts/skill-hygiene-check.py --mode all .` passed.
- release gate: `scripts/release-gate.sh --mode all --strict` passed.

### Cross-Skill Checks
- `secret-scanner:scan-secrets --mode working` - covered by `scripts/release-gate.sh --mode all --strict`; scanner returned no findings.
## Stage 9 - Bounded Fuzzy Template Slice

### Pre-stage assumptions
- Extend the existing same-file fuzzy matcher to templates using the same deterministic per-file budgets.
- Keep scan-limit exceptions family-agnostic but narrow: they suppress only `repetition-scan-limited`, not exact or fuzzy repeated-inline findings.
- Preserve exact matching before fuzzy caps so exact duplicates still emit even when fuzzy comparison is bounded.
- Treat this as non-UI work because it only changes CLI/test/docs behavior.

### Success criteria
- TDD gate: `bash tests/skill-hygiene-check-fixtures.sh` fails before production changes because near-duplicate templates do not emit findings and template scan-limit warnings are absent.
- Fuzzy template verification: same-file near-duplicate template candidates emit `repeated-inline-template` with `same-file-fuzzy` evidence and appear in dry-run baseline.
- Scan-limit verification: pair-cost-limited template candidates emit `repetition-scan-limited`, valid exceptions suppress only that ID, exact duplicates still emit, and lone large template candidates stay clean.
- Release-gate verification: a temp scan-limited template skill produces `WARN skill-hygiene` in non-strict mode and `FAIL skill-hygiene` in strict mode.

**Completed:** 2026-05-16 11:18 CST

### Files touched
- `scripts/skill-hygiene-check.py` - enabled template fuzzy matching and scan-limit coverage.
- `tests/skill-hygiene-check-fixtures.py` - added near-duplicate template and template scan-limit fixtures.
- `tests/skill-hygiene-release-gate-fixtures.sh` - added a temp scan-limited template strict-upgrade fixture.
- `RELEASE-GATE.md` - updated scan-limit docs to cover prompt and template families.
- `.idea-to-ship/ITS-ROADMAP-010/test-plan.md` - added Stage 9 TDD slices.
- `.idea-to-ship/ITS-ROADMAP-010/tdd-log.md` - recorded Stage 9 red-first evidence.
- `.idea-to-ship/ITS-ROADMAP-010/implementation-log.md` - recorded Stage 9 baseline and verification.

### Decisions made during implementation
- Template scan-limit fixtures use literal-heavy report rows rather than placeholder-heavy rows so they exercise the intended template rule without loosening classifier thresholds.
- Current repo fuzzy baseline remains clean: prompt candidates `25`, matches `0`, limited `false`; template candidates `1`, matches `0`, limited `false`.

### Deviations from design artifacts
- None. Review iteration 1 added the required per-family whole-run fuzzy budgets and scaled fixture coverage after this stage first landed.

### Adjacent issues noticed (NOT fixed here)
- Staged checker-infrastructure drift remained open at this point; it is resolved in Code Review Fixes - Iteration 5.

### Verification
- tdd: `tdd-log.md` entry `2026-05-16 11:15 CST`; failing test then passed (`bash tests/skill-hygiene-check-fixtures.sh && bash tests/skill-hygiene-release-gate-fixtures.sh`).
- tests: `bash tests/skill-hygiene-check-fixtures.sh` passed.
- tests: `bash tests/skill-hygiene-release-gate-fixtures.sh` passed, including non-strict `WARN skill-hygiene` and strict `FAIL skill-hygiene` for a temp scan-limited template skill.
- baseline: `python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .` returned prompt candidates `25`, matches `0`, limited `false`; template candidates `1`, matches `0`, limited `false`.
- hygiene: `python3 scripts/skill-hygiene-check.py --mode all .` passed.
- release gate: `scripts/release-gate.sh --mode all --strict` passed.
- whitespace: `git diff --check HEAD` passed.

### Cross-Skill Checks
- `secret-scanner:scan-secrets --mode working` - covered by `scripts/release-gate.sh --mode all --strict`; scanner returned no findings.
## Stage 10 - Final Regression

### Pre-stage assumptions
- No production behavior changes are made in this stage; it is a verification and handoff gate.
- Run staged strict even though no files are staged, because the user requested no skipped review/verification steps and the architecture says to run staged if the handoff uses staged changes.
- Treat this as non-UI work because it only verifies CLI/test behavior.

### Success criteria
- Fast checker fixtures pass.
- Full release-gate fixture meta-tests pass.
- Full-repo hygiene check passes.
- Working, all, and staged strict release gates pass.

**Completed:** 2026-05-16 11:19 CST

### Files touched
- `.idea-to-ship/ITS-ROADMAP-010/implementation-log.md` - recorded final regression evidence.

### Decisions made during implementation
- Ran `scripts/release-gate.sh --mode staged --strict` despite having no staged changes; it passed and skipped diff-scoped fixture advisories as expected.

### Deviations from design artifacts
- None.

### Verification
- tests: `bash tests/skill-hygiene-check-fixtures.sh` passed.
- tests: `bash tests/skill-hygiene-release-gate-fixtures.sh` passed.
- hygiene: `python3 scripts/skill-hygiene-check.py --mode all .` passed.
- release gate: `scripts/release-gate.sh --mode working --strict` passed.
- release gate: `scripts/release-gate.sh --mode all --strict` passed.
- release gate: `scripts/release-gate.sh --mode staged --strict` passed.

### Cross-Skill Checks
- `secret-scanner:scan-secrets --mode working` - covered by `scripts/release-gate.sh --mode working --strict`; scanner returned no findings.
- `secret-scanner:scan-secrets --mode all` - covered by `scripts/release-gate.sh --mode all --strict`; scanner returned no findings.
- `secret-scanner:scan-secrets --mode staged` - covered by `scripts/release-gate.sh --mode staged --strict`; scanner returned no findings.

## Code Review Fixes - Iteration 1

### Review findings fixed
- Fence-aware exceptions: replaced substring-based hygiene exception extraction with line-anchored markdown section parsing outside fenced blocks; added fixtures for fenced exception examples that must not suppress `moderate-skill-bloat` or `repetition-scan-limited`.
- Release-gate template scan-limit proof: fixed the template fixture substitution from `issue_alpha` to `issue alpha` and asserted JSON evidence contains `repetition-scan-limited`.
- FR-5 mode proof: added release-gate positive warning coverage for `skill-hygiene` in `working`, `all`, and `staged` modes, including a staged index-only/worktree-deleted repeated-prompt sample.
- Whole-run fuzzy budgets: added per-family total comparison, character, and pair-cost caps; added a scaled prompt-heavy fixture proving total caps emit `repetition-scan-limited` and do not starve template fuzzy checks.
- Pair-cost diagnostics: record attempted limiting pair cost so `repetition-scan-limited` evidence is nonzero.
- Docs and dead code: updated `RELEASE-GATE.md` to mention bounded same-file near-duplicates and removed the unused output-contract helper.

### Verification after fixes
- tests: `bash tests/skill-hygiene-check-fixtures.sh` passed.
- tests: `bash tests/skill-hygiene-release-gate-fixtures.sh` passed.
- baseline: `python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .` returned prompt candidates `25`, exact/fuzzy matches `0`, limited `false`; template candidates `1`, exact/fuzzy matches `0`, limited `false`.
- hygiene: `python3 scripts/skill-hygiene-check.py --mode all .` passed.
- release gate: `scripts/release-gate.sh --mode all --strict` passed.
- whitespace: `git diff --check HEAD` passed.

## Code Review Fixes - Iteration 2

### Review findings fixed
- Exception contract precision: restricted hygiene exception parsing to real level-2 `## Hygiene Exception` sections outside fences and stripped fenced example blocks before matching exception/evidence keys.
- Output-contract ownership: grouped output-contract markers by same fenced block or markdown section owner before masking; markers split across unrelated sections no longer create one owned output-contract span.
- Whole-run budget evidence: carried per-family total comparison, character, and pair-cost counters into `repetition-scan-limited` diagnostics and fixture assertions.

### Verification after fixes
- tests: `bash tests/skill-hygiene-check-fixtures.sh` passed.
- tests: `bash tests/skill-hygiene-release-gate-fixtures.sh` passed.
- baseline: `python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .` returned prompt candidates `25`, exact/fuzzy matches `0`, limited `false`; template candidates `1`, exact/fuzzy matches `0`, limited `false`.
- hygiene: `python3 scripts/skill-hygiene-check.py --mode all .` passed.
- release gate: `scripts/release-gate.sh --mode working --strict` passed.
- release gate: `scripts/release-gate.sh --mode all --strict` passed.
- release gate: `scripts/release-gate.sh --mode staged --strict` passed.
- whitespace: `git diff --check HEAD` passed.

## Code Review Fixes - Iteration 3

### Review findings fixed
- Dry-run budget evidence: returned per-family fuzzy budget totals from the matcher and added `total_comparisons`, `total_compared_chars`, and `total_pair_cost` to dry-run summary records.
- Stronger total-budget fixtures: parsed total counters and asserted nonzero values under `MAX_FUZZY_*_TOTAL`; kept template-family fuzzy coverage in the same scaled fixture.
- Release-gate mode coverage: added all-mode and staged index-only/worktree-deleted positive warning paths for `moderate-skill-bloat` and `repetition-scan-limited`, including strict-upgrade and evidence assertions.

### Verification after fixes
- tests: `bash tests/skill-hygiene-check-fixtures.sh` passed.
- tests: `bash tests/skill-hygiene-release-gate-fixtures.sh` passed.
- baseline: `python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .` returned prompt candidates `25`, exact/fuzzy matches `0`, limited `false`, totals `0`; template candidates `1`, exact/fuzzy matches `0`, limited `false`, totals `0`.
- hygiene: `python3 scripts/skill-hygiene-check.py --mode all .` passed.
- release gate: `scripts/release-gate.sh --mode working --strict` passed.
- release gate: `scripts/release-gate.sh --mode all --strict` passed.
- release gate: `scripts/release-gate.sh --mode staged --strict` passed.
- whitespace: `git diff --check HEAD` passed.

## Code Review Fixes - Iteration 4

### Review findings fixed
- Markdown code-block exception hardening: recognized tilde fences and four-space indented code when extracting `## Hygiene Exception` sections, and limited heading recognition to real markdown headings with at most three leading spaces.
- Code-block false-negative fixtures: added tilde-fenced and indented-code examples for both `moderate-skill-bloat` and `repetition-scan-limited`, including examples inside a real exception section.
- Template whole-run budget proof: added a template-heavy scaled fixture that independently exhausts the template-family whole-run pair-cost budget and asserts nonzero under-cap total counters.
- Review evidence completeness: recorded the missing full-repo hygiene, working/all/staged strict release gates, and whitespace checks for iteration 3, then reran the complete gate set after iteration 4 fixes.

### Verification after fixes
- compile: `python3 -m py_compile scripts/skill-hygiene-check.py tests/skill-hygiene-check-fixtures.py` passed.
- tests: `bash tests/skill-hygiene-check-fixtures.sh` passed.
- tests: `bash tests/skill-hygiene-release-gate-fixtures.sh` passed.
- baseline: `python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .` returned prompt candidates `25`, exact/fuzzy matches `0`, limited `false`, totals `0`; template candidates `1`, exact/fuzzy matches `0`, limited `false`, totals `0`.
- hygiene: `python3 scripts/skill-hygiene-check.py --mode all .` passed.
- release gate: `scripts/release-gate.sh --mode working --strict` passed.
- release gate: `scripts/release-gate.sh --mode all --strict` passed.
- release gate: `scripts/release-gate.sh --mode staged --strict` passed.
- whitespace: `git diff --check HEAD` passed.

## Code Review Fixes - Iteration 5

### Review findings fixed
- Staged infrastructure drift: added blocking `skill-hygiene-infra-drift` to `scripts/release-gate.sh` for staged runs where canonical skill-hygiene infrastructure is staged and the worktree copy differs from the index.
- Drift proof: added release-gate JSON, strict JSON, and human-output fixtures that stage `scripts/skill-hygiene-check.py`, dirty the worktree copy, and assert exit `1` with evidence naming the drifting path.
- Exact-match maintainability: reused target candidate maps for overlapping reference paths and grouped exact cross-file matching by `(family, fingerprint, normalized_text)` instead of scanning every reference candidate for each target candidate.
- Fixture precision: changed the exact-template fixture to assert a real same-file finding line for `template-same`, and changed the prompt whole-run budget fixture to discover the capped prompt path dynamically instead of hardcoding `prompt-budget-24`.
- Traceability cleanup: updated earlier implementation-log deferral notes so they point to this iteration instead of implying `skill-hygiene-infra-drift` is still out of scope.

### Verification after fixes
- syntax: `bash -n scripts/release-gate.sh tests/skill-hygiene-release-gate-fixtures.sh tests/skill-hygiene-check-fixtures.sh` passed.
- compile: `python3 -m py_compile scripts/skill-hygiene-check.py tests/skill-hygiene-check-fixtures.py` passed.
- tests: `bash tests/skill-hygiene-check-fixtures.sh` passed.
- tests: `bash tests/skill-hygiene-release-gate-fixtures.sh` passed, including staged infra-drift JSON/strict/human failures.
- baseline: `python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .` returned prompt candidates `25`, exact/fuzzy matches `0`, limited `false`, totals `0`; template candidates `1`, exact/fuzzy matches `0`, limited `false`, totals `0`.
- hygiene: `python3 scripts/skill-hygiene-check.py --mode all .` passed.
- release gate: `scripts/release-gate.sh --mode working --strict` passed.
- release gate: `scripts/release-gate.sh --mode all --strict` passed.
- release gate: `scripts/release-gate.sh --mode staged --strict` passed; `skill-hygiene-infra-drift` skipped because no staged diff touched skill-hygiene infrastructure.
- whitespace: `git diff --check HEAD` passed.

## Code Review Fixes - Iteration 6

### Review findings fixed
- Untracked staged-infra drift: included untracked canonical `tests/skill-hygiene-*` paths in `skill-hygiene-infra-drift` detection with `git ls-files --others --exclude-standard`.
- Drift negative case: added a staged ordinary skill fixture with unrelated dirty skill-hygiene infrastructure, asserting `skill-hygiene-infra-drift` is skipped and the staged skill warning still flows through `skill-hygiene`.
- Exact-index regression signal: added dry-run summary fields `exact_index_group_count` and `exact_index_max_group_size`, plus a scaled exact duplicate fixture proving duplicate candidates collapse into one exact-index bucket.
- Fixture runtime: reduced `tests/skill-hygiene-release-gate-fixtures.sh` to a representative real-gate matrix for all/working/staged, strict upgrade, self-check failure, staged ordinary negative, and untracked infra drift; candidate repos use a committed secret-scan stub because the real scanner is covered by final release-gate runs.

### Verification after fixes
- syntax: `bash -n scripts/release-gate.sh tests/skill-hygiene-release-gate-fixtures.sh tests/skill-hygiene-check-fixtures.sh` passed.
- compile: `python3 -m py_compile scripts/skill-hygiene-check.py tests/skill-hygiene-check-fixtures.py` passed.
- tests: `bash tests/skill-hygiene-check-fixtures.sh` passed, including `repetition baseline reports exact index metrics`.
- tests: `time bash tests/skill-hygiene-release-gate-fixtures.sh` passed in `23.670s`, including untracked infra drift and ordinary staged skill dirty-infra skip coverage.
- baseline: `python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .` returned prompt candidates `25`, exact/fuzzy matches `0`, limited `false`, exact-index groups `25`, max group `1`; template candidates `1`, exact/fuzzy matches `0`, limited `false`, exact-index groups `1`, max group `1`.
- hygiene: `python3 scripts/skill-hygiene-check.py --mode all .` passed.
- release gate: `scripts/release-gate.sh --mode working --strict` passed.
- release gate: `scripts/release-gate.sh --mode all --strict` passed.
- release gate: `scripts/release-gate.sh --mode staged --strict` passed; `skill-hygiene-infra-drift` skipped because no staged diff touched skill-hygiene infrastructure.
- whitespace: `git diff --check HEAD` passed.

## Code Review Fixes - Iteration 7

### Review findings fixed
- Visible exception contract: ignored HTML comment blocks while extracting `## Hygiene Exception` sections and while matching exception/evidence keys inside a real section.
- Fence parsing: made fence handling marker-aware so tilde fences are not closed by backtick examples, and applied that to exception parsing, output-contract span masking, and fenced candidate ranges.
- Exact duplicate groups: changed cross-file exact matching to emit one representative match per selected target/non-canonical holder, carrying the duplicate group size through `duplicate_count` instead of materializing every pair in the group.
- Release-gate fixture coverage: restored representative coverage for three warning families without returning to the large matrix: all-mode `moderate-skill-bloat`, working strict `repeated-inline-prompt`, and staged `repetition-scan-limited`.
- Strict evidence separation: split `skill-hygiene` strict-upgrade proof from `skill-hygiene-release-gate-fixtures` self-check failure proof so unrelated advisories do not account for the hygiene strict failure.

### Verification after fixes
- syntax: `bash -n scripts/release-gate.sh tests/skill-hygiene-release-gate-fixtures.sh tests/skill-hygiene-check-fixtures.sh` passed.
- compile: `python3 -m py_compile scripts/skill-hygiene-check.py tests/skill-hygiene-check-fixtures.py` passed.
- tests: `bash tests/skill-hygiene-check-fixtures.sh` passed, including HTML-comment exception, marker-aware fence, and representative exact-index coverage.
- tests: `time bash tests/skill-hygiene-release-gate-fixtures.sh` passed in `24.566s`, including moderate bloat, repeated prompt, scan-limit, self-check failure, staged ordinary dirty-infra skip, and untracked infra drift coverage.
- baseline: `python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .` returned prompt candidates `25`, exact/fuzzy matches `0`, limited `false`, exact-index groups `25`, max group `1`; template candidates `1`, exact/fuzzy matches `0`, limited `false`, exact-index groups `1`, max group `1`.
- hygiene: `python3 scripts/skill-hygiene-check.py --mode all .` passed.
- release gate: `scripts/release-gate.sh --mode working --strict` passed.
- release gate: `scripts/release-gate.sh --mode all --strict` passed.
- release gate: `scripts/release-gate.sh --mode staged --strict` passed; `skill-hygiene-infra-drift` skipped because no staged diff touched skill-hygiene infrastructure.
- whitespace: `git diff --check HEAD` passed.

## Code Review Fixes - Iteration 8

### Review findings fixed
- Inline HTML comments: stripped comment spans from retained lines before matching hygiene exception keys and scan-limit evidence, so hidden inline reason/evidence no longer suppresses findings.
- Fence/comment ordering: handled fence state before HTML comment transitions so comment markers inside fenced examples do not hide later visible `## Hygiene Exception` sections.
- Staged index proof: changed the staged scan-limit release-gate fixture to delete the worktree skill after `git add`, proving staged hygiene warnings read index content.
- Scan-limit aggregation: added a fixture where one skill emits both prompt and template scan-limit entries and asserts a single `families=prompt,template` finding.
- Output-contract marker-aware masking: added a tilde fenced output-contract wrapper with an inner backtick marker and asserted contract-only text remains masked through the closing tilde fence.
- Canonical harness copy: changed release-gate candidate repo setup to expand the same canonical `tests/skill-hygiene-*` pathspec family used by the release gate before copying and committing candidate infrastructure.

### Verification after fixes
- syntax: `bash -n scripts/release-gate.sh tests/skill-hygiene-release-gate-fixtures.sh tests/skill-hygiene-check-fixtures.sh` passed.
- compile: `python3 -m py_compile scripts/skill-hygiene-check.py tests/skill-hygiene-check-fixtures.py` passed.
- tests: `bash tests/skill-hygiene-check-fixtures.sh` passed, including inline HTML-comment exception, scan-limit family aggregation, staged-index-supporting checker fixtures, and output-contract marker-aware masking coverage.
- tests: `time bash tests/skill-hygiene-release-gate-fixtures.sh` passed in `24.981s`, including staged worktree-deleted scan-limit warning, repeated prompt strict failure, self-check strict failure, and untracked infra drift coverage.
- baseline: `python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .` returned prompt candidates `25`, exact/fuzzy matches `0`, limited `false`, exact-index groups `25`, max group `1`; template candidates `1`, exact/fuzzy matches `0`, limited `false`, exact-index groups `1`, max group `1`.
- hygiene: `python3 scripts/skill-hygiene-check.py --mode all .` passed.
- release gate: `scripts/release-gate.sh --mode working --strict` passed.
- release gate: `scripts/release-gate.sh --mode all --strict` passed.
- release gate: `scripts/release-gate.sh --mode staged --strict` passed; `skill-hygiene-infra-drift` skipped because no staged diff touched skill-hygiene infrastructure.
- whitespace: `git diff --check HEAD` passed.

## Code Review Fixes - Iteration 9

### Review findings fixed
- Template release-gate evidence: expanded the representative release-gate fixture so existing all/working/staged invocations also prove repeated-template and template scan-limit findings, and changed `skill-hygiene` JSON evidence to preserve full finding lines instead of truncating after 240 characters.
- Markdown fence correctness: required closing fences to have only trailing whitespace after the closing marker, so same-marker lines with info strings such as ````example` remain fenced content.
- Placeholder-heavy templates: admitted structurally anchored high-placeholder templates as `exact_only` candidates only when they retain the minimum literal wrapper text, preserving exact duplicate detection with matching stable anchors while excluding them from fuzzy matching.
- Output-contract subspan masking: started fenced output-contract masks at the contract heading/marker instead of the fence opener, leaving prompt bodies before embedded contracts visible to repetition detection.
- HTML-commented contract markers: stripped HTML comments outside fenced code while scanning output-contract markers, so commented markers do not mask visible prompt evidence.

### Verification after fixes
- syntax: `bash -n scripts/release-gate.sh tests/skill-hygiene-release-gate-fixtures.sh tests/skill-hygiene-check-fixtures.sh` passed.
- compile: `python3 -m py_compile scripts/skill-hygiene-check.py tests/skill-hygiene-check-fixtures.py` passed.
- tests: `bash tests/skill-hygiene-check-fixtures.sh` passed, including placeholder-heavy exact-only templates, fenced output-contract subspan masking, HTML-commented contract-marker handling, and same-marker info-string fence coverage.
- tests: `time bash tests/skill-hygiene-release-gate-fixtures.sh` passed in `26.846s`, including repeated-template and template scan-limit JSON evidence while keeping the representative matrix under 30 seconds.
- baseline: `python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .` returned prompt candidates `25`, exact/fuzzy matches `0`, limited `false`, exact-index groups `25`, max group `1`; template candidates `1`, exact/fuzzy matches `0`, limited `false`, exact-index groups `1`, max group `1`.
- hygiene: `python3 scripts/skill-hygiene-check.py --mode all .` passed.
- release gate: `scripts/release-gate.sh --mode working --strict` passed.
- release gate: `scripts/release-gate.sh --mode all --strict` passed.
- release gate: `scripts/release-gate.sh --mode staged --strict` passed; `skill-hygiene-infra-drift` skipped because no staged diff touched skill-hygiene infrastructure.

## Code Review Fixes - Iteration 10

### Review findings fixed
- Exact-only cross-file matching: filtered cross-file exact matches through `exact_candidate_match()`, so placeholder-heavy exact-only templates must share stable anchors before a repeated-template warning can emit.
- Output-contract masking: limited section/fence rewind to the real `## Output, Token, And Error Contract` heading, so ordinary heading-started prompt sections with `status` and `truncated` fields keep their prompt body visible.
- Scan-limit exceptions: required `reviewed-with` or `cap-evidence` values to name `--dry-run-repetition-baseline` or a skill-hygiene fixture command before suppressing `repetition-scan-limited`.
- Release-gate evidence: removed the remaining hard cap in `join_finding_output`, preserving all skill-hygiene finding lines in JSON evidence.
- Canonical infra self-check: added a release-gate fixture self-check that compares its `SKILL_HYGIENE_INFRA_TARGETS` list against `scripts/release-gate.sh`.

### Verification after fixes
- syntax: `bash -n scripts/release-gate.sh tests/skill-hygiene-release-gate-fixtures.sh tests/skill-hygiene-check-fixtures.sh` passed.
- compile: `python3 -m py_compile scripts/skill-hygiene-check.py tests/skill-hygiene-check-fixtures.py` passed.
- tests: `bash tests/skill-hygiene-check-fixtures.sh` passed, including cross-file exact-only stable-anchor negative coverage, ordinary-heading output-contract field masking coverage, and weak scan-limit evidence rejection.
- tests: `time bash tests/skill-hygiene-release-gate-fixtures.sh` passed in `26.190s`, including the new canonical infra-target list self-check.
- baseline: `python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .` returned prompt candidates `25`, exact/fuzzy matches `0`, limited `false`, exact-index groups `25`, max group `1`; template candidates `1`, exact/fuzzy matches `0`, limited `false`, exact-index groups `1`, max group `1`.
- hygiene: `python3 scripts/skill-hygiene-check.py --mode all .` passed.
- release gate: `scripts/release-gate.sh --mode working --strict` passed.
- release gate: `scripts/release-gate.sh --mode all --strict` passed.
- release gate: `scripts/release-gate.sh --mode staged --strict` passed; `skill-hygiene-infra-drift` skipped because no staged diff touched skill-hygiene infrastructure.
- whitespace: `git diff --check HEAD` passed.

## Code Review Fixes - Iteration 11

### Review findings fixed
- Exact-only canonical grouping: included stable anchors in `exact_candidate_key()` for exact-only candidates, so all-mode canonical selection happens per matchable placeholder-template subgroup instead of per raw normalized fingerprint.
- Regression proof: added a three-template all-mode fixture with one anchor-A exact-only template and two anchor-B exact-only templates sharing the same normalized fingerprint, asserting only the non-canonical anchor-B copy warns.

### Verification after fixes
- syntax: `bash -n scripts/release-gate.sh tests/skill-hygiene-release-gate-fixtures.sh tests/skill-hygiene-check-fixtures.sh` passed.
- compile: `python3 -m py_compile scripts/skill-hygiene-check.py tests/skill-hygiene-check-fixtures.py` passed.
- tests: `bash tests/skill-hygiene-check-fixtures.sh` passed, including `repeated inline template placeholder-heavy all-mode canonical by anchors`.
- tests: `time bash tests/skill-hygiene-release-gate-fixtures.sh` passed in `26.221s`.
- baseline: `python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .` returned prompt candidates `25`, exact/fuzzy matches `0`, limited `false`, exact-index groups `25`, max group `1`; template candidates `1`, exact/fuzzy matches `0`, limited `false`, exact-index groups `1`, max group `1`.
- hygiene: `python3 scripts/skill-hygiene-check.py --mode all .` passed.
- release gate: `scripts/release-gate.sh --mode working --strict` passed.
- release gate: `scripts/release-gate.sh --mode all --strict` passed.
- release gate: `scripts/release-gate.sh --mode staged --strict` passed; `skill-hygiene-infra-drift` skipped because no staged diff touched skill-hygiene infrastructure.
- whitespace: `git diff --check HEAD` passed.

## Code Review Fixes - Iteration 12

### Review findings fixed
- Strict-upgrade fixture coverage: the authorized re-review traceability/testability angle found that `tests/skill-hygiene-release-gate-fixtures.sh` proved non-strict `moderate-skill-bloat` and strict template scan-limit paths, but did not prove strict-upgrade evidence for `moderate-skill-bloat` or prompt-family `repetition-scan-limited`.
- Working strict proof: added `write_moderate_bloat_skill` and `write_scan_limited_prompt_skill` to the working strict candidate repo, then asserted JSON evidence contains `moderate-skill-bloat`, `repetition-scan-limited`, `families=prompt`, and `families=template`.
- Traceability artifact: added BF-20 to `test-plan.md` so the review-driven fixture coverage fix is recorded against FR-6, TDD-13, and TDD-19.

### Verification after fixes
- syntax: `bash -n tests/skill-hygiene-release-gate-fixtures.sh` passed.
- tests: `time bash tests/skill-hygiene-release-gate-fixtures.sh` passed in `29.258s`, including `json-working-moderate-bloat-evidence` and `json-working-prompt-scan-limited-evidence`.
- syntax: `bash -n scripts/release-gate.sh tests/skill-hygiene-release-gate-fixtures.sh tests/skill-hygiene-check-fixtures.sh` passed.
- compile: `python3 -m py_compile scripts/skill-hygiene-check.py tests/skill-hygiene-check-fixtures.py` passed.
- tests: `bash tests/skill-hygiene-check-fixtures.sh` passed.
- baseline: `python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .` returned prompt candidates `25`, exact/fuzzy matches `0`, limited `false`, exact-index groups `25`, max group `1`; template candidates `1`, exact/fuzzy matches `0`, limited `false`, exact-index groups `1`, max group `1`.
- hygiene: `python3 scripts/skill-hygiene-check.py --mode all .` passed.
- release gate: `scripts/release-gate.sh --mode working --strict` passed.
- release gate: `scripts/release-gate.sh --mode all --strict` passed.
- release gate: `scripts/release-gate.sh --mode staged --strict` passed; `skill-hygiene-infra-drift` skipped because no staged diff touched skill-hygiene infrastructure.
- whitespace: `git diff --check HEAD` passed.
- secret scan: `python3 secret-scanner/scripts/scan.py --mode working --format json` returned `[]`.
- generated files: `find . -name __pycache__ -type d -prune -print` returned no paths.

## Code Review Fixes - Iteration 13

### Review findings fixed
- Exact-key type contract: the authorized maintainability/repo-fit re-review found stale 3-field type annotations for exact candidate keys after BF-19 added stable-anchor partitioning. Added `ExactCandidateKey` and used it for `exact_candidate_key`, `exact_reference_groups`, and `canonical_exact_paths`.
- Python runtime compatibility: the first alias form used `tuple[...] | None`, which candidate release-gate repos evaluated at runtime and failed under their Python. Switched the alias to `typing.Optional[tuple[str, ...]]`, preserving compatibility with the repo's postponed annotation style.
- Fixture-advisory matrix: the authorized traceability/testability re-review found that TDD-6's pass/skip/warn/strict matrix had been narrowed. Restored focused JSON assertions for staged skip, working pass, checker-fixture non-strict warn/strict fail, and release-gate self-check non-strict warn/strict fail.
- Traceability artifact: added BF-21 to `test-plan.md` for the restored TDD-6 fixture-advisory matrix.

### Verification after fixes
- compile: `python3 -m py_compile scripts/skill-hygiene-check.py` passed.
- manual candidate: a temporary repo running `python3 scripts/skill-hygiene-check.py --mode all <repo>` emitted `moderate-skill-bloat` instead of the previous runtime alias error.
- syntax: `bash -n tests/skill-hygiene-release-gate-fixtures.sh` passed.
- tests: `time bash tests/skill-hygiene-release-gate-fixtures.sh` passed in `58.663s`, including working fixture pass, checker-fixture warn/strict, release-gate fixture warn/strict, and staged fixture skip assertions.
- syntax: `bash -n scripts/release-gate.sh tests/skill-hygiene-release-gate-fixtures.sh tests/skill-hygiene-check-fixtures.sh` passed.
- compile: `python3 -m py_compile scripts/skill-hygiene-check.py tests/skill-hygiene-check-fixtures.py` passed.
- tests: `bash tests/skill-hygiene-check-fixtures.sh` passed.
- baseline: `python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .` returned prompt candidates `25`, exact/fuzzy matches `0`, limited `false`, exact-index groups `25`, max group `1`; template candidates `1`, exact/fuzzy matches `0`, limited `false`, exact-index groups `1`, max group `1`.
- hygiene: `python3 scripts/skill-hygiene-check.py --mode all .` passed.
- release gate: `scripts/release-gate.sh --mode working --strict` passed.
- release gate: `scripts/release-gate.sh --mode all --strict` passed.
- release gate: `scripts/release-gate.sh --mode staged --strict` passed; `skill-hygiene-infra-drift` skipped because no staged diff touched skill-hygiene infrastructure.
- whitespace: `git diff --check HEAD` passed.
- secret scan: `python3 secret-scanner/scripts/scan.py --mode working --format json` returned `[]`.
- generated files: `find . -name __pycache__ -type d -prune -print` returned no paths.

## Code Review Fixes - Iteration 14

### Review findings fixed
- Explicit meta-test runtime contract: the authorized maintainability/repo-fit re-review found that the restored BF-21 full release-gate fixture matrix now runs in `58.663s`, while `architecture.md` still targeted under 30 seconds for the full explicit command.
- Design update: updated `architecture.md` to keep the release-gated fast subset under 10 seconds but allow about 60 seconds for the explicit `bash tests/skill-hygiene-release-gate-fixtures.sh` meta-test when it proves the full pass/skip/warn/strict matrix.
- Traceability update: updated BF-21 in `test-plan.md` to name the accepted explicit runtime tradeoff and preserve the distinction between release-gated `--self-check` and full implementation verification.

### Verification after fixes
- artifact check: `rg -n "60 seconds|58.663|BF-21|--self-check" .idea-to-ship/ITS-ROADMAP-010/architecture.md .idea-to-ship/ITS-ROADMAP-010/test-plan.md .idea-to-ship/ITS-ROADMAP-010/code-review.md .idea-to-ship/ITS-ROADMAP-010/implementation-log.md RELEASE-GATE.md` showed the runtime distinction is documented.
- whitespace: `git diff --check HEAD` passed.

## Code Review Fixes - Iteration 15

### Review findings fixed
- Prompt-family staged scan-limit proof: the authorized traceability/testability re-review found that the non-strict staged release-gate fixture asserted generic scan-limit evidence and template-family evidence, but not prompt-family evidence.
- Staged JSON assertions: added `scan-limited-prompt` and `families=prompt` evidence assertions to `tests/skill-hygiene-release-gate-fixtures.sh` for the staged index-only/worktree-deleted sample.
- Runtime traceability artifacts: updated BF-14/BF-15 and appended a TDD log entry so the historical under-30s full-fixture target is explicitly superseded by BF-21's split between fast release-gated `--self-check` and the about-60s explicit full meta-test.

### Verification after fixes
- syntax: `bash -n tests/skill-hygiene-release-gate-fixtures.sh` passed.
- compile: `python3 -m py_compile scripts/skill-hygiene-check.py tests/skill-hygiene-check-fixtures.py` passed.
- whitespace: `git diff --check HEAD` passed.
- secret scan: `python3 secret-scanner/scripts/scan.py --mode working --format json` returned `[]`.
- baseline: `python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .` returned prompt candidates `25`, exact/fuzzy matches `0`, limited `false`, exact-index groups `25`, max group `1`; template candidates `1`, exact/fuzzy matches `0`, limited `false`, exact-index groups `1`, max group `1`.
- tests: `time bash tests/skill-hygiene-release-gate-fixtures.sh` passed in `57.439s`, including `json-staged-prompt-scan-limited-evidence` and `json-staged-prompt-family-evidence`.
- tests: `bash tests/skill-hygiene-check-fixtures.sh` passed.
- hygiene: `python3 scripts/skill-hygiene-check.py --mode all .` passed.
- release gate: `scripts/release-gate.sh --mode working --strict` passed.
- release gate: `scripts/release-gate.sh --mode all --strict` passed.
- release gate: `scripts/release-gate.sh --mode staged --strict` passed; `skill-hygiene-infra-drift` skipped because no staged diff touches skill-hygiene infrastructure.
- generated files: `find . -name __pycache__ -type d -prune -print` returned no paths.
