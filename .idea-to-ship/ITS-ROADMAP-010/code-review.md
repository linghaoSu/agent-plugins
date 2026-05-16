# Code Review - ITS-ROADMAP-010

**Date:** 2026-05-16
**Reviewer:** multi-agent: correctness/security -> reviewer subagents; traceability/testability -> reviewer subagents; maintainability/repo-fit -> reviewer subagents; UI/UX -> not applicable
**Iterations:** 17
**Result:** clean
**Mode:** multi-agent
**Degradation reason:** none
**Diff size:** 10 files changed, 3528 insertions(+), 132 deletions(-)

## Issues Raised & Resolution

| # | Severity | File:line | Issue | Resolution |
|---|---|---|---|---|
| 1 | warning | `tests/skill-hygiene-release-gate-fixtures.sh` | Temp dirs and release-gate fixture coverage were brittle. | Switched cleanup to an array, split hygiene strict evidence from self-check evidence, and added JSON assertions for warning families. |
| 2 | warning | `tests/skill-hygiene-check-fixtures.py` | Staged/index and all-mode metadata regressions were undercovered. | Added staged index-not-worktree, staged deleted worktree, and committed legacy metadata fixtures. |
| 3 | warning | `scripts/skill-hygiene-check.py` | Candidate classification and internal-heading extraction could absorb ordinary prose or miss structured prompts/templates. | Added weighted classification, line-number/placeholder normalization, and structure lookahead. |
| 4 | warning | `scripts/skill-hygiene-check.py` | Hygiene exceptions could be hidden in fenced, indented, or HTML-commented examples. | Replaced substring matching with visible `## Hygiene Exception` parsing, fence/comment awareness, and negative fixtures. |
| 5 | warning | `scripts/skill-hygiene-check.py` | Fuzzy scan-limit diagnostics lacked whole-run budgets and useful counters. | Added per-family total counters, nonzero pair-cost evidence, aggregation, and scan-limit baseline fields. |
| 6 | warning | `scripts/release-gate.sh` | Staged skill-hygiene infrastructure drift was not blocked. | Added blocking `skill-hygiene-infra-drift`, including untracked canonical infra paths and ordinary-skill negative coverage. |
| 7 | warning | `scripts/skill-hygiene-check.py` | Exact cross-file matching could fan out or scan too broadly. | Grouped exact matches, emitted representative duplicate counts, and exposed exact-index metrics. |
| 8 | warning | `scripts/skill-hygiene-check.py` | Markdown fences and output-contract masking had false-positive/false-negative edges. | Made fence parsing marker-aware, fixed closing fence rules, and masked owned contract subspans only. |
| 9 | warning | `tests/skill-hygiene-release-gate-fixtures.sh` | Reduced release-gate matrix initially lost template and scan-limit evidence. | Kept the reduced matrix but made all/working/staged runs assert repeated-template and template scan-limit evidence. |
| 10 | warning | `scripts/skill-hygiene-check.py` | Placeholder-heavy templates were either rejected too early or matched too broadly. | Added exact-only template candidates with stable-anchor guards, literal-wrapper minimums, and exact-only fuzzy exclusion. |
| 11 | warning | `scripts/release-gate.sh` | Skill-hygiene JSON evidence could truncate later finding lines. | Removed the hard cap from `join_finding_output`. |
| 12 | warning | `scripts/skill-hygiene-check.py` | Scan-limit exceptions accepted meaningless evidence. | Required `--dry-run-repetition-baseline` or skill-hygiene fixture evidence tokens. |
| 13 | warning | `scripts/skill-hygiene-check.py` | Exact-only cross-file canonical selection still used raw fingerprint groups. | Included stable anchors in exact keys for exact-only candidates and added all-mode subgroup coverage. |
| 14 | warning | `tests/skill-hygiene-release-gate-fixtures.sh` | Fixture canonical infra pathspecs could drift from release gate. | Added a self-check that compares the fixture list to `scripts/release-gate.sh`. |
| 15 | warning | `tests/skill-hygiene-release-gate-fixtures.sh` | Strict release-gate fixture did not prove `moderate-skill-bloat` or prompt-family `repetition-scan-limited` strict-upgrade evidence. | Added those samples to the working strict candidate repo and asserted `moderate-skill-bloat`, `families=prompt`, and `families=template` evidence. |
| 16 | warning | `scripts/skill-hygiene-check.py` | Exact candidate key annotations still described the old 3-field key after exact-only stable-anchor partitioning. | Added `ExactCandidateKey` and used it for the key function, exact reference groups, and canonical exact path map; used `Optional[...]` so candidate release-gate repos do not fail on runtime alias evaluation. |
| 17 | warning | `tests/skill-hygiene-release-gate-fixtures.sh` | TDD-6 fixture-advisory matrix coverage had been narrowed during runtime reduction. | Restored focused JSON assertions for staged skip, working pass, checker-fixture warn/strict, and release-gate self-check warn/strict. |
| 18 | warning | `.idea-to-ship/ITS-ROADMAP-010/code-review.md` | Diff-size metadata became stale during review-fix iterations. | Refreshed the diff-size line from `git diff --shortstat HEAD` after final artifact updates. |
| 19 | warning | `.idea-to-ship/ITS-ROADMAP-010/architecture.md` | Full release-gate fixture runtime grew to about 60s while architecture still targeted under 30s. | Updated architecture and BF-21 to explicitly accept about 60s for the full explicit meta-test while keeping only fast `--self-check` wired into release-gated paths. |
| 20 | warning | `tests/skill-hygiene-release-gate-fixtures.sh` | Non-strict staged scan-limit coverage proved generic and template-family evidence but not prompt-family evidence. | Added staged JSON evidence assertions for `scan-limited-prompt` and `families=prompt`. |
| 21 | warning | `.idea-to-ship/ITS-ROADMAP-010/test-plan.md` | BF-14/BF-15 and the TDD log still carried the superseded under-30s full release-gate fixture expectation. | Updated BF-14/BF-15 and appended a TDD log entry documenting BF-21's current split: fast release-gated `--self-check`, about 60s for the explicit full meta-test. |

## Out-of-Scope Issues Skipped

None.

## Design Drift

No unapproved drift remains. The implementation keeps the existing checker CLI and release-gate advisory path, adds the planned check IDs, keeps current accepted skills clean in `--mode all`, and documents review-driven hardening through BF-1 through BF-21.

## Test Traceability

Traceability is complete across requirements, architecture stages, TDD slices, implementation log entries, and regression fixtures. Final verification:

- `python3 -m py_compile scripts/skill-hygiene-check.py tests/skill-hygiene-check-fixtures.py` passed.
- `bash -n scripts/release-gate.sh tests/skill-hygiene-release-gate-fixtures.sh tests/skill-hygiene-check-fixtures.sh` passed.
- `bash tests/skill-hygiene-check-fixtures.sh` passed.
- `time bash tests/skill-hygiene-release-gate-fixtures.sh` passed in 57.439s.
- `python3 scripts/skill-hygiene-check.py --mode all --dry-run-repetition-baseline .` reported 25 prompt candidates, 1 template candidate, 0 matches, and no limits.
- `python3 scripts/skill-hygiene-check.py --mode all .` passed.
- `scripts/release-gate.sh --mode working --strict` passed.
- `scripts/release-gate.sh --mode all --strict` passed.
- `scripts/release-gate.sh --mode staged --strict` passed.
- `git diff --check HEAD` passed.
- `find . -name __pycache__ -type d -prune -print` returned no paths.

## Residual Open Issues

None.

## Final Verdict

| Angle | Verdict |
|---|---|
| correctness/security | LGTM |
| traceability/testability | LGTM |
| maintainability/repo-fit | LGTM |
| UI/UX | not applicable |
