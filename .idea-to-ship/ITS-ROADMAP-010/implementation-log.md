# Implementation Log - ITS-ROADMAP-010

**Architecture:** architecture.md
**Started:** 2026-05-15

## Stage Status
- [x] Stage 1 - Snapshot Regression Slice
- [x] Stage 2 - Fixture Gate Slice
- [x] Stage 3 - Candidate Inventory Slice
- [ ] Stage 4 - Baseline Dry Run And Contract Masking Slice
- [ ] Stage 5 - Moderate Bloat Slice
- [ ] Stage 6 - Prompt Exact Repetition Slice
- [ ] Stage 7 - Bounded Fuzzy Prompt Slice
- [ ] Stage 8 - Template Exact Repetition Slice
- [ ] Stage 9 - Bounded Fuzzy Template Slice
- [ ] Stage 10 - Final Regression

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
- Staged checker-infrastructure drift with blocking `skill-hygiene-infra-drift` remains deferred to a later implementation stage.

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
- Staged checker-infrastructure drift with blocking `skill-hygiene-infra-drift` remains deferred to a later implementation stage.

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
