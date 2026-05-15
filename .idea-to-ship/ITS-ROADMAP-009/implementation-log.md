# Implementation Log - ITS-ROADMAP-009

**Architecture:** architecture.md
**Started:** 2026-05-15

## Stage Status
- [x] Stage 1 - Extract and Guard Evaluate-Issue Prompts

## Stage 1 - Extract and Guard Evaluate-Issue Prompts
**Started:** 2026-05-15 13:36
**Completed:** 2026-05-15 13:36

### Assumptions and success criteria
- Use the existing `tests/agent-playbook-eval-fixtures.py` `ContractCheck` and `InvariantGroup` pattern; no new fixture command.
- Keep extraction mechanically faithful: add fixture checks first, then copy existing prompt/template blocks into new files, then replace inline blocks with references.
- This stage is not UI work; no `interface-design.md` is required.
- Success criteria: red-first `bash tests/agent-playbook-eval-fixtures.sh` fails after fixture checks are added and before prompt files exist; after implementation, `python3 -m py_compile tests/agent-playbook-eval-fixtures.py`, `bash tests/agent-playbook-eval-fixtures.sh`, staged strict release gate, and full strict release gate pass.

### Files touched
- `.idea-to-ship/ITS-ROADMAP-009/requirements.md` - brainstormed requirements artifact for this slug.
- `.idea-to-ship/ITS-ROADMAP-009/architecture.md` - reviewed architecture artifact for this stage.
- `.idea-to-ship/ITS-ROADMAP-009/design-review.md` - multi-agent design review log.
- `.idea-to-ship/ITS-ROADMAP-009/test-plan.md` - stage-local TDD slice and red/green evidence.
- `.idea-to-ship/ITS-ROADMAP-009/tdd-log.md` - red-first fixture gate evidence.
- `.idea-to-ship/ITS-ROADMAP-009/implementation-log.md` - implementation evidence and verification record.
- `issue-evaluator/skills/evaluate-issue/SKILL.md` - replaced inline Round 2, Round 3, and final report blocks with extracted artifact references and missing/empty terminal stop rule.
- `issue-evaluator/prompts/evaluate-issue-round2-adversarial.md` - extracted Round 2 adversarial diagnosis prompt.
- `issue-evaluator/prompts/evaluate-issue-round3-synthesis.md` - extracted Round 3 final synthesis prompt.
- `issue-evaluator/templates/evaluate-issue-final-report.md` - extracted final issue evaluation report template.
- `tests/agent-playbook-eval-fixtures.py` - added contract and forbidden-pattern checks for the extracted artifacts.

### Decisions made during implementation
- Added the Round 2 required angle list to the extracted Round 2 prompt file because the original skill stored those angle names immediately above the fenced prompt; keeping them in the artifact makes the prompt contract self-contained and satisfies the reviewed fixture matrix.
- Kept the final report template free of the compact output/token/error contract because the reviewed architecture explicitly deferred output-contract changes.
- Used the existing `agent-playbook-eval-fixtures` command because release-gate routing already covers `issue-evaluator/` changes.
- Post-review fix: split the new fixture invariants into one required token per
  `InvariantGroup` because fixture groups are OR matches, added a forbidden
  inline final-report-wrapper check, tightened the GitHub read-only invariant
  to the full no-mutation sentence, and kept the artifact section under the
  workflow heading.

### Deviations from design artifacts
- None. The Round 2 prompt includes the adjacent required-angle list from the source skill so the extracted artifact preserves the full Round 2 contract, not only the fenced prompt body.

### Adjacent issues noticed (NOT fixed here)
- None.

### Verification
- tdd: `tdd-log.md` entry 2026-05-15 13:36, failing test then passed (`bash tests/agent-playbook-eval-fixtures.sh`).
- compile: `python3 -m py_compile tests/agent-playbook-eval-fixtures.py` passed.
- tests: `bash tests/agent-playbook-eval-fixtures.sh` passed.
- staged scope: all intended implementation files are staged, and no implementation path has unstaged remainder.
- release gate: `scripts/release-gate.sh --mode staged --strict` passed.
- full gate: `scripts/release-gate.sh --mode all --strict` passed.
- review-code: iteration 1 found fixture OR-match and heading-scope issues;
  iteration 2 found staged-scope evidence and GitHub mutation-guard issues;
  iteration 3 found workflow-site reference and Round 3 input-placeholder
  fixture gaps; fixes were applied before final staged/full strict gates.

### Cross-Skill Checks
- `secret-scanner:scan-secrets` - triggered by generated prompt/template files; covered by release gate `secret-scan` in staged and all strict modes.
- `harness-engineering:harness-audit` - not run; this stage extracts existing prompt text and does not implement new harness, retry, persistence, evaluator, or tool middleware behavior.
- `antifragile:antifragile-system` - not run; this stage does not add external calls, fallback paths, persistence, destructive operations, or recovery behavior.
