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
