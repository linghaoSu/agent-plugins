# TDD Log - ITS-ROADMAP-010

## 2026-05-15 16:53 CST - stage-tdd
**Stage:** Stage 1 - Snapshot Regression Slice
**Mode:** stage-tdd
**Authority:** requirements.md + architecture.md Stage 1
**Files touched:** `tests/skill-hygiene-check-fixtures.py`, `tests/skill-hygiene-check-fixtures.sh`, `.idea-to-ship/ITS-ROADMAP-010/test-plan.md`
**Scenarios:** happy/regression for existing check IDs; edge/failure for staged index-only modified skills and staged index-only added skill metadata.
**Command:** `bash tests/skill-hygiene-check-fixtures.sh`
**Initial Result:** expected failure. `staged deleted modified skill` missed `long-description`; `staged deleted added skill metadata` missed `missing-openai-metadata`. Existing all-mode, working-added, and staged index-not-worktree guardrails passed.
**Implementation Gate:** ready for /implement; production code must make the targeted command pass without weakening the existing guardrails.

## 2026-05-15 17:05 CST - stage-tdd
**Stage:** Stage 2 - Fixture Gate Slice
**Mode:** stage-tdd
**Authority:** requirements.md + architecture.md Stage 2
**Files touched:** `tests/skill-hygiene-release-gate-fixtures.sh`, `.idea-to-ship/ITS-ROADMAP-010/test-plan.md`
**Scenarios:** release-gate all-mode JSON contains `skill-hygiene-fixtures`; release-gate all-mode JSON contains non-recursive `skill-hygiene-release-gate-fixtures`; self-check wiring names the expected commands; full fixture later verifies staged skip, working pass, working warn, and working strict-upgrade behavior in a candidate temp repo.
**Command:** `bash tests/skill-hygiene-release-gate-fixtures.sh`
**Initial Result:** expected failure before production changes because `scripts/release-gate.sh` does not yet define either new advisory ID or the non-recursive self-check command.
**Implementation Gate:** ready for /implement; production code must wire both advisory checks and keep the self-check non-recursive.

## 2026-05-15 17:29 CST - stage-tdd
**Stage:** Stage 3 - Candidate Inventory Slice
**Mode:** stage-tdd
**Authority:** requirements.md + architecture.md Stage 3
**Files touched:** `tests/skill-hygiene-check-fixtures.py`, `.idea-to-ship/ITS-ROADMAP-010/test-plan.md`
**Scenarios:** happy path for prompt/template candidate classification and inventory fields; negative path for ordinary sections named like internal headings; edge path for non-fenced prompt candidates spanning allowed internal headings.
**Command:** `bash tests/skill-hygiene-check-fixtures.sh`
**Initial Result:** expected failure before production changes because `scripts/skill-hygiene-check.py` does not yet expose fixture-visible candidate inventory output.
**Implementation Gate:** ready for /implement once the targeted fixture fails for the missing `--dump-repetition-candidates` behavior; production code must make the command pass without enabling new hygiene findings in normal mode.

## 2026-05-15 17:56 CST - test-backfill
**Stage:** Stage 3 - Candidate Inventory Slice
**Mode:** test-backfill
**Authority:** Stage 3 code review findings + architecture.md classifier and normalization rules
**Files touched:** `tests/skill-hygiene-check-fixtures.py`, `.idea-to-ship/ITS-ROADMAP-010/test-plan.md`
**Scenarios:** classifier boundary/tie-break guardrails including output-only input sections, placeholder-label templates, structured `## Output` wrappers, and ordinary labeled final-report prose negatives; plain internal heading stop condition including ordinary labeled prose; line-number and uppercase-placeholder fingerprint normalization.
**Command:** `bash tests/skill-hygiene-check-fixtures.sh`
**Initial Result:** review backfill exposed expected failures before fixes: ordinary internal headings were absorbed into candidates, ordinary labels after internal headings were treated as YAML skeletons, ordinary labeled final-report prose could classify as a template, structured `## Output` wrappers were not started as candidates, line-numbered prompts fingerprinted differently, classifier scoring could over-count a single prompt phrase, output-only input-section templates could receive prompt points, placeholder-label templates were not anchored/scored, and ALL_CAPS placeholders were not normalized before fingerprinting.
**Implementation Gate:** ready for /implement review-fix; production code must use architecture-weighted classifier scoring and normalize line-number/uppercase placeholder variants without enabling new normal-mode hygiene findings.

## 2026-05-16 10:54 CST - stage-tdd
**Stage:** Stage 4 - Baseline Dry Run And Contract Masking Slice
**Mode:** stage-tdd
**Authority:** requirements.md + architecture.md Stage 4
**Files touched:** `tests/skill-hygiene-check-fixtures.py`, `.idea-to-ship/ITS-ROADMAP-010/test-plan.md`
**Scenarios:** happy path for exact same-file prompt and exact cross-file template dry-run matches; edge path for output-contract-only duplicate masking; regression that normal checker mode still emits no new repeated-inline findings.
**Command:** `bash tests/skill-hygiene-check-fixtures.sh`
**Initial Result:** expected failure before production changes because `scripts/skill-hygiene-check.py` does not yet expose `--dry-run-repetition-baseline` or contract-subspan masking for repetition evidence.
**Implementation Gate:** ready for /implement once the targeted fixture fails for the missing dry-run baseline behavior; production code must keep repeated-inline findings disabled in normal mode.

## 2026-05-16 11:00 CST - stage-tdd
**Stage:** Stage 5 - Moderate Bloat Slice
**Mode:** stage-tdd
**Authority:** requirements.md + architecture.md Stage 5
**Files touched:** `tests/skill-hygiene-check-fixtures.py`, `tests/skill-hygiene-release-gate-fixtures.sh`, `.idea-to-ship/ITS-ROADMAP-010/test-plan.md`
**Scenarios:** happy path for a 401-line `moderate-skill-bloat` finding; exception path for a valid `## Hygiene Exception`; invalid/empty/unrelated exception sections that still warn; >750-line skill still emits `oversized-skill`; release-gate non-strict warn and strict failure through existing `skill-hygiene`.
**Command:** `bash tests/skill-hygiene-check-fixtures.sh && bash tests/skill-hygiene-release-gate-fixtures.sh`
**Initial Result:** expected failure before production changes because `scripts/skill-hygiene-check.py` does not yet define `moderate-skill-bloat` or the moderate-bloat exception contract.
**Implementation Gate:** ready for /implement once the targeted fixtures fail for the missing moderate-bloat behavior; production code must keep the full-repo strict gate clean after the line-count audit.

## 2026-05-16 11:06 CST - stage-tdd
**Stage:** Stage 6 - Prompt Exact Repetition Slice
**Mode:** stage-tdd
**Authority:** requirements.md + architecture.md Stage 6
**Files touched:** `tests/skill-hygiene-check-fixtures.py`, `tests/skill-hygiene-release-gate-fixtures.sh`, `.idea-to-ship/ITS-ROADMAP-010/test-plan.md`
**Scenarios:** exact same-file repeated prompt; exact cross-file copied prompt in working-mode selected targets that sort before and after sources; release-gate non-strict warn and strict failure through existing `skill-hygiene`.
**Command:** `bash tests/skill-hygiene-check-fixtures.sh && bash tests/skill-hygiene-release-gate-fixtures.sh`
**Initial Result:** expected failure before production changes because `scripts/skill-hygiene-check.py` can baseline exact prompt matches but does not yet emit `repeated-inline-prompt` findings in normal mode.
**Implementation Gate:** ready for /implement once targeted fixtures fail for missing repeated prompt findings; production code must keep template findings disabled until Stage 8.

## 2026-05-16 11:12 CST - stage-tdd
**Stage:** Stage 7 - Bounded Fuzzy Prompt Slice
**Mode:** stage-tdd
**Authority:** requirements.md + architecture.md Stage 7
**Files touched:** `tests/skill-hygiene-check-fixtures.py`, `tests/skill-hygiene-release-gate-fixtures.sh`, `.idea-to-ship/ITS-ROADMAP-010/test-plan.md`
**Scenarios:** same-file near-duplicate prompt emits `repeated-inline-prompt` with fuzzy evidence; dry-run baseline reports `same-file-fuzzy`; pair-cost-limited prompt candidates emit `repetition-scan-limited`; valid scan-limit exception suppresses only scan-limit; lone large candidate does not warn; release-gate non-strict warn and strict failure through existing `skill-hygiene`.
**Command:** `bash tests/skill-hygiene-check-fixtures.sh && bash tests/skill-hygiene-release-gate-fixtures.sh`
**Initial Result:** expected failure before production changes because `scripts/skill-hygiene-check.py` does not yet perform fuzzy prompt matching or emit `repetition-scan-limited`.
**Implementation Gate:** ready for /implement once targeted fixtures fail for missing fuzzy prompt/scan-limit behavior; production code must keep scan-limit prompt-only until Stage 9.

## 2026-05-16 11:13 CST - stage-tdd
**Stage:** Stage 8 - Template Exact Repetition Slice
**Mode:** stage-tdd
**Authority:** requirements.md + architecture.md Stage 8
**Files touched:** `tests/skill-hygiene-check-fixtures.py`, `tests/skill-hygiene-release-gate-fixtures.sh`, `.idea-to-ship/ITS-ROADMAP-010/test-plan.md`
**Scenarios:** same-file exact template/report-wrapper duplicate; working-mode cross-file template target copy; release-gate non-strict warn and strict failure through existing `skill-hygiene`.
**Command:** `bash tests/skill-hygiene-check-fixtures.sh && bash tests/skill-hygiene-release-gate-fixtures.sh`
**Initial Result:** expected failure before production changes because `scripts/skill-hygiene-check.py` can baseline exact template matches but does not yet emit `repeated-inline-template` findings in normal mode.
**Implementation Gate:** ready for /implement once targeted fixtures fail for missing repeated template findings; production code must keep template fuzzy matching deferred to Stage 9.

## 2026-05-16 11:15 CST - stage-tdd
**Stage:** Stage 9 - Bounded Fuzzy Template Slice
**Mode:** stage-tdd
**Authority:** requirements.md + architecture.md Stage 9
**Files touched:** `tests/skill-hygiene-check-fixtures.py`, `tests/skill-hygiene-release-gate-fixtures.sh`, `.idea-to-ship/ITS-ROADMAP-010/test-plan.md`
**Scenarios:** same-file near-duplicate template emits `repeated-inline-template` with fuzzy evidence; dry-run baseline reports template `same-file-fuzzy`; pair-cost-limited template candidates emit `repetition-scan-limited`; valid scan-limit exception suppresses only scan-limit; lone large template candidate does not warn; release-gate non-strict warn and strict failure through existing `skill-hygiene`.
**Command:** `bash tests/skill-hygiene-check-fixtures.sh && bash tests/skill-hygiene-release-gate-fixtures.sh`
**Initial Result:** expected failure before production changes because `scripts/skill-hygiene-check.py` currently applies fuzzy matching and scan-limit warnings to prompt candidates only.
**Implementation Gate:** ready for /implement once targeted fixtures fail for missing template fuzzy/scan-limit behavior; production code must keep full-repo strict gate clean.

## 2026-05-16 11:33 CST - test-backfill
**Stage:** Stage 4-10 review fixes
**Mode:** test-backfill
**Authority:** `/review-code --slug ITS-ROADMAP-010` iteration 1 findings + architecture.md hygiene exception, FR-5, and fuzzy budget rules
**Files touched:** `tests/skill-hygiene-check-fixtures.py`, `tests/skill-hygiene-release-gate-fixtures.sh`, `.idea-to-ship/ITS-ROADMAP-010/test-plan.md`
**Scenarios:** fenced hygiene exception examples do not suppress real findings; pair-cost-limited findings report nonzero pair cost; per-family whole-run fuzzy budgets cap prompt-heavy fixtures without starving template fuzzy checks; template scan-limit release-gate fixture creates a real near-duplicate; release-gate JSON evidence proves `skill-hygiene` warnings in working, all, and staged modes.
**Command:** `bash tests/skill-hygiene-check-fixtures.sh && bash tests/skill-hygiene-release-gate-fixtures.sh`
**Initial Result:** review backfill exposed expected failures before fixes: fenced exception parsing was substring-based, template scan-limit release-gate fixture used the wrong `sed` pattern, staged/all positive warning paths were not covered, pair-cost diagnostics could report zero, and fuzzy budgets had no whole-run per-family caps.
**Implementation Gate:** ready for /implement review-fix; production code and fixtures must satisfy every warning before review iteration 2.

## 2026-05-16 11:44 CST - test-backfill
**Stage:** Stage 4-10 review fixes
**Mode:** test-backfill
**Authority:** `/review-code --slug ITS-ROADMAP-010` iteration 2 findings + architecture.md output-contract ownership and hygiene exception contracts
**Files touched:** `tests/skill-hygiene-check-fixtures.py`, `.idea-to-ship/ITS-ROADMAP-010/test-plan.md`
**Scenarios:** only real level-2 `## Hygiene Exception` sections outside fences suppress findings; fenced example lines inside a real exception section do not suppress; output-contract markers split across unrelated sections do not mask repeated-inline evidence; total-budget findings include per-family total counters.
**Command:** `bash tests/skill-hygiene-check-fixtures.sh`
**Initial Result:** review backfill exposed expected failures before fixes: `### Hygiene Exception` could suppress findings, fenced exception lines inside a real section could suppress findings, output-contract marker ownership was too broad, and total-budget diagnostics lacked total counters.
**Implementation Gate:** ready for /implement review-fix; production code and fixtures must satisfy every warning before review iteration 3.

## 2026-05-16 11:53 CST - test-backfill
**Stage:** Stage 4-10 review fixes
**Mode:** test-backfill
**Authority:** `/review-code --slug ITS-ROADMAP-010` iteration 3 findings + architecture.md dry-run budget and release-gate mode coverage rules
**Files touched:** `scripts/skill-hygiene-check.py`, `tests/skill-hygiene-check-fixtures.py`, `tests/skill-hygiene-release-gate-fixtures.sh`, `.idea-to-ship/ITS-ROADMAP-010/test-plan.md`
**Scenarios:** dry-run summaries expose per-family total fuzzy counters; scaled whole-run budget fixture parses numeric totals and asserts nonzero/under-cap values; release-gate positive warnings cover `moderate-skill-bloat` and `repetition-scan-limited` in all, working, and staged modes.
**Command:** `bash tests/skill-hygiene-check-fixtures.sh && bash tests/skill-hygiene-release-gate-fixtures.sh`
**Initial Result:** review backfill exposed expected failures before fixes: summary records lacked total counters, whole-run budget fixture only checked field presence, and release-gate positive mode coverage for moderate/scan-limit was working-only.
**Implementation Gate:** ready for /implement review-fix; production code and fixtures must satisfy every warning before review iteration 4.

## 2026-05-16 12:07 CST - test-backfill
**Stage:** Stage 4-10 review fixes
**Mode:** test-backfill
**Authority:** `/review-code --slug ITS-ROADMAP-010` iteration 4 findings + architecture.md hygiene exception and fuzzy-budget contracts
**Files touched:** `scripts/skill-hygiene-check.py`, `tests/skill-hygiene-check-fixtures.py`, `.idea-to-ship/ITS-ROADMAP-010/test-plan.md`
**Scenarios:** tilde-fenced and four-space indented `## Hygiene Exception` examples do not suppress `moderate-skill-bloat` or `repetition-scan-limited`, including examples inside a real exception section; a template-heavy scaled fixture exhausts the template-family whole-run pair-cost budget and asserts numeric total counters remain nonzero and under cap.
**Command:** `bash tests/skill-hygiene-check-fixtures.sh`
**Initial Result:** review backfill exposed expected failures before fixes: exception extraction only understood backtick fences and accepted indented headings/keys, while the scaled budget fixture proved prompt-family total caps and template non-starvation but not template-family total-cap behavior.
**Implementation Gate:** ready for /implement review-fix; production code and fixtures must satisfy every warning before review iteration 5.

## 2026-05-16 12:24 CST - test-backfill
**Stage:** Stage 4-10 review fixes
**Mode:** test-backfill
**Authority:** `/review-code --slug ITS-ROADMAP-010` iteration 5 findings + architecture.md staged infrastructure drift and exact-match indexing contracts
**Files touched:** `scripts/release-gate.sh`, `scripts/skill-hygiene-check.py`, `tests/skill-hygiene-check-fixtures.py`, `tests/skill-hygiene-release-gate-fixtures.sh`, `.idea-to-ship/ITS-ROADMAP-010/test-plan.md`
**Scenarios:** staged release gate emits blocking `skill-hygiene-infra-drift` in JSON when staged canonical hygiene infrastructure differs from dirty worktree infrastructure; exact cross-file repetition uses grouped exact indexes instead of a per-target full-corpus scan; same-file exact template fixture asserts a finding line for the same-file path; prompt total-budget fixture discovers the capped prompt path dynamically.
**Command:** `bash tests/skill-hygiene-check-fixtures.sh && bash tests/skill-hygiene-release-gate-fixtures.sh`
**Initial Result:** review backfill exposed expected failures before fixes: staged infrastructure drift passed release gate, exact matching scanned all references for each target candidate, same-file template exact coverage could pass on matched evidence only, and the prompt budget fixture hardcoded the first capped path.
**Implementation Gate:** ready for /implement review-fix; production code and fixtures must satisfy every warning before the next full review loop.

## 2026-05-16 12:43 CST - test-backfill
**Stage:** Stage 4-10 review fixes
**Mode:** test-backfill
**Authority:** `/review-code --slug ITS-ROADMAP-010` iteration 6 findings + architecture.md staged infrastructure drift, exact indexing, and fixture runtime contracts
**Files touched:** `scripts/release-gate.sh`, `scripts/skill-hygiene-check.py`, `tests/skill-hygiene-check-fixtures.py`, `tests/skill-hygiene-release-gate-fixtures.sh`, `.idea-to-ship/ITS-ROADMAP-010/test-plan.md`
**Scenarios:** untracked canonical `tests/skill-hygiene-*` files fail `skill-hygiene-infra-drift` when canonical infrastructure is staged; ordinary staged skill changes with dirty infrastructure skip the drift guard; dry-run summaries expose exact-index group counts and max group size for a scaled duplicate fixture; release-gate fixture uses a reduced representative matrix and candidate secret-scan stub to stay under the 30-second target.
**Command:** `bash tests/skill-hygiene-check-fixtures.sh && time bash tests/skill-hygiene-release-gate-fixtures.sh`
**Initial Result:** review backfill exposed expected failures before fixes: untracked canonical infra files were invisible to drift detection, dirty infra negative coverage was missing, the exact-index change had no regression signal, and the release-gate fixture took about 94 seconds after the expanded matrix.
**Implementation Gate:** ready for /implement review-fix; production code and fixtures must satisfy every warning before the next full review loop.

## 2026-05-16 13:05 CST - test-backfill
**Stage:** Stage 4-10 review fixes
**Mode:** test-backfill
**Authority:** `/review-code --slug ITS-ROADMAP-010` iteration 7 findings + architecture.md visible exception, fence parsing, exact-index, and release-gate representative harness contracts
**Files touched:** `scripts/skill-hygiene-check.py`, `tests/skill-hygiene-check-fixtures.py`, `tests/skill-hygiene-release-gate-fixtures.sh`, `.idea-to-ship/ITS-ROADMAP-010/test-plan.md`
**Scenarios:** HTML-commented `## Hygiene Exception` examples do not suppress `moderate-skill-bloat` or `repetition-scan-limited`; tilde fences containing backtick examples remain one fenced candidate; exact duplicate groups emit representative cross-file matches with duplicate counts; release-gate fixture covers moderate bloat, repeated prompt, scan-limit, self-check failure, ordinary staged dirty-infra skip, and untracked infra drift without mixing unrelated strict-failure evidence.
**Command:** `bash tests/skill-hygiene-check-fixtures.sh && time bash tests/skill-hygiene-release-gate-fixtures.sh`
**Initial Result:** review backfill exposed expected failures before fixes: HTML comments could hide exceptions, fence scanners closed on mismatched marker types, exact duplicate groups still fanned out internally, and the reduced release-gate fixture no longer represented repeated-inline or scan-limit warnings cleanly.
**Implementation Gate:** ready for /implement review-fix; production code and fixtures must satisfy every warning before the next full review loop.

## 2026-05-16 13:18 CST - test-backfill
**Stage:** Stage 4-10 review fixes
**Mode:** test-backfill
**Authority:** `/review-code --slug ITS-ROADMAP-010` iteration 8 findings + architecture.md visible exception, staged index, scan-limit aggregation, output-contract masking, and canonical pathspec contracts
**Files touched:** `scripts/skill-hygiene-check.py`, `tests/skill-hygiene-check-fixtures.py`, `tests/skill-hygiene-release-gate-fixtures.sh`, `.idea-to-ship/ITS-ROADMAP-010/test-plan.md`
**Scenarios:** inline HTML comments cannot provide hidden exception reasons or hidden scan-limit evidence; `<!--` inside a fenced code block does not hide a later visible exception; staged scan-limit release-gate proof reads index content after the worktree skill path is removed; one skill can aggregate prompt and template scan-limit families into one finding; tilde fenced output-contract masking survives an inner backtick marker; candidate release-gate repos copy every canonical `tests/skill-hygiene-*` file.
**Command:** `bash tests/skill-hygiene-check-fixtures.sh && time bash tests/skill-hygiene-release-gate-fixtures.sh`
**Initial Result:** review backfill exposed expected failures before fixes: inline comments still satisfied exception regexes, comment parsing ran before fence state, staged positive coverage left the worktree skill present, prompt/template scan-limit aggregation was unproved, output-contract marker-aware masking was unproved, and candidate harness pathspecs omitted wildcard-matched helpers.
**Implementation Gate:** ready for /implement review-fix; production code and fixtures must satisfy every warning before the next full review loop.

## 2026-05-16 13:36 CST - test-backfill
**Stage:** Stage 4-10 review fixes
**Mode:** test-backfill
**Authority:** `/review-code --slug ITS-ROADMAP-010` iteration 9 findings + architecture.md template repetition, scan-limit, fence parsing, output-contract masking, and release-gate evidence contracts
**Files touched:** `scripts/skill-hygiene-check.py`, `scripts/release-gate.sh`, `tests/skill-hygiene-check-fixtures.py`, `tests/skill-hygiene-release-gate-fixtures.sh`, `.idea-to-ship/ITS-ROADMAP-010/test-plan.md`
**Scenarios:** release-gate JSON evidence includes repeated-template and template scan-limit warnings; same-marker fence lines with info strings remain fenced content; placeholder-heavy templates are exact-only candidates and still emit exact duplicate findings; fenced prompt bodies with embedded output contracts still match after contract-subspan masking; HTML-commented contract markers do not create masks.
**Command:** `bash tests/skill-hygiene-check-fixtures.sh && time bash tests/skill-hygiene-release-gate-fixtures.sh`
**Initial Result:** review backfill exposed expected failures before fixes: release-gate evidence truncation hid template findings, same-marker info-string lines could close fences early, high-placeholder templates were rejected before exact matching, fenced output-contract masks removed the whole prompt, and HTML-commented contract markers could produce false output-contract masks.
**Implementation Gate:** ready for /implement review-fix; production code and fixtures must satisfy every warning before the next full review loop.

## 2026-05-16 13:48 CST - test-backfill
**Stage:** Stage 4-10 review fixes
**Mode:** test-backfill
**Authority:** `/review-code --slug ITS-ROADMAP-010` iteration 10 findings + architecture.md exact-only template, output-contract masking, scan-limit exception, release-gate evidence, and canonical infrastructure contracts
**Files touched:** `scripts/skill-hygiene-check.py`, `scripts/release-gate.sh`, `tests/skill-hygiene-check-fixtures.py`, `tests/skill-hygiene-release-gate-fixtures.sh`, `.idea-to-ship/ITS-ROADMAP-010/test-plan.md`
**Scenarios:** cross-file placeholder-heavy exact-only templates with different stable anchors do not warn; heading-started prompts with `status` and `truncated` fields still produce repeated prompt matches; weak `reviewed-with: ok` evidence does not suppress scan-limit warnings; release-gate skill-hygiene evidence is not hard-truncated; the release-gate fixture self-check compares its canonical pathspec list against the release-gate script.
**Command:** `bash tests/skill-hygiene-check-fixtures.sh && time bash tests/skill-hygiene-release-gate-fixtures.sh`
**Initial Result:** review backfill exposed expected failures before fixes: cross-file exact-only matching bypassed the stable-anchor guard, section-owned output-contract masks rewound to ordinary headings, any non-empty evidence string could suppress scan-limit warnings, skill-hygiene evidence still had a hard cap, and the fixture's canonical infrastructure list could drift from `scripts/release-gate.sh`.
**Implementation Gate:** ready for /implement review-fix; production code and fixtures must satisfy every warning before the next full review loop.

## 2026-05-16 13:57 CST - test-backfill
**Stage:** Stage 4-10 review fixes
**Mode:** test-backfill
**Authority:** `/review-code --slug ITS-ROADMAP-010` iteration 11 finding + architecture.md placeholder-heavy exact-only template contract
**Files touched:** `scripts/skill-hygiene-check.py`, `tests/skill-hygiene-check-fixtures.py`, `.idea-to-ship/ITS-ROADMAP-010/test-plan.md`
**Scenarios:** all-mode exact-only canonical selection is per stable-anchor subgroup: one placeholder-heavy anchor-A template and two anchor-B templates with the same normalized fingerprint warn only for the non-canonical anchor-B copy.
**Command:** `bash tests/skill-hygiene-check-fixtures.sh`
**Initial Result:** review backfill exposed expected failure before fixes: all-mode canonical selection used raw fingerprint groups and could let a non-matchable exact-only anchor subgroup choose the canonical path for another subgroup.
**Implementation Gate:** ready for /implement review-fix; production code and fixtures must satisfy every warning before the next full review loop.

## 2026-05-16 16:18 CST - test-backfill
**Stage:** Stage 4-10 review fixes
**Mode:** test-backfill
**Authority:** authorized `/review-code --slug ITS-ROADMAP-010` re-review finding + architecture.md runtime contract + TDD-6/TDD-19/BF-21
**Files touched:** `tests/skill-hygiene-release-gate-fixtures.sh`, `.idea-to-ship/ITS-ROADMAP-010/test-plan.md`, `.idea-to-ship/ITS-ROADMAP-010/tdd-log.md`
**Scenarios:** non-strict staged release-gate JSON proves prompt-family scan-limit evidence with `scan-limited-prompt` and `families=prompt`; the runtime contract distinguishes fast release-gated `--self-check` from the explicit full release-gate meta-test that may run about 60 seconds while proving the pass/skip/warn/strict matrix.
**Command:** `bash tests/skill-hygiene-release-gate-fixtures.sh`
**Initial Result:** re-review exposed that staged non-strict scan-limit assertions proved the generic finding and template family but not prompt-family evidence, and that BF-14/BF-15 plus this log still carried the superseded under-30s full-fixture expectation.
**Implementation Gate:** ready for /implement review-fix; final review must rerun all required reviewer angles.
