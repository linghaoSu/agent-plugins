# Implementation Log - ITS-ROADMAP-001

**Architecture:** architecture.md
**Started:** 2026-05-09

## Stage Status

- [x] Stage 1 - Release gate contract
- [ ] Stage 2 - Advisory scans
- [ ] Stage 3 - Machine-readable output
- [ ] Stage 4 - Promotion decisions

## Pre-Stage Assumptions

- Stage 1 is behavior-changing, so it uses TDD with shell fixture tests before
  production code.
- The repo has no package manager, CI config, or existing test runner; Stage 1
  tests will live in `tests/release-gate-stage1.sh`.
- The release gate will use `jq` for manifest JSON because architecture marks
  missing `jq` as usage exit `2`.
- The release gate will use `python3` for structural skill frontmatter checks
  and for invoking the existing secret scanner.
- Stage 1 will implement `--mode staged|working|all` and accept `--strict` as a
  no-op until advisory checks exist.
- Full advisory scans, hook installation, and CI wiring remain out of scope.

## Stage 1 - Release gate contract

**Completed:** 2026-05-09 15:02 CST

### Files touched

- `scripts/release-gate.sh` - added the local release gate entry point with
  manifest, skill frontmatter, diff whitespace, and secret-scan blocking
  checks.
- `RELEASE-GATE.md` - documented modes, blocking checks, output, and Stage 1
  boundaries.
- `tests/release-gate-stage1.sh` - added shell fixture coverage for Stage 1
  happy path, failure modes, and usage errors.
- `.idea-to-ship/ITS-ROADMAP-001/test-plan.md` - recorded story, acceptance,
  scenario, and test traceability for Stage 1.
- `secret-scanner/README.md` - rewrote example connection-string wording so
  full-repo secret scanning does not match documentation examples.
- `secret-scanner/skills/scan-secrets/SKILL.md` - rewrote example credential
  patterns so full-repo secret scanning does not match documentation examples.

### Decisions made during implementation

- Used shell fixture tests because the repo has no existing test framework or
  package runner.
- Kept the release gate as a Bash script that shells out to existing local
  deterministic tools: `git`, `jq`, `python3`, and
  `secret-scanner/scripts/scan.py`.
- Implemented structural frontmatter validation with `python3` instead of a
  full YAML parser, matching the reviewed architecture.
- Accepted `--strict` as a no-op in Stage 1 because advisory checks are not
  implemented yet.
- Removed function-local `trap` overrides during code review so temporary-file
  cleanup does not overwrite the script's global cleanup trap.
- Fixed staged-mode manifest and skill validation to read the staged index
  snapshot instead of the worktree. This prevents a bad staged file from
  passing after the worktree has been repaired but not re-staged.

### Deviations from architecture.md

- Minimal `--json` output was implemented in Stage 1 even though the staged
  plan listed machine-readable output in Stage 3. Reason: the reviewed command
  interface already exposed `--json`, `jq` is already a required blocking tool,
  and adding JSON over the Stage 1 result file avoided leaving a documented
  flag unimplemented. Stage 3 still owns dedicated JSON fixture assertions and
  advisory-check JSON coverage.

### Adjacent issues noticed (NOT fixed here)

- The full-repo secret scan exposed documentation examples that matched the
  scanner's real credential patterns. The examples were rewritten because they
  would otherwise make the new release gate unusable for `--mode all`.

### Verification

- syntax: ok (`bash -n scripts/release-gate.sh tests/release-gate-stage1.sh`)
- tests: ok (`bash tests/release-gate-stage1.sh`, 10 fixture cases)
- release gate staged: ok (`scripts/release-gate.sh --mode staged`)
- release gate working: ok (`scripts/release-gate.sh --mode working`)
- release gate all: ok (`scripts/release-gate.sh --mode all`)
- json smoke: ok (`scripts/release-gate.sh --mode staged --json`)
- whitespace: ok (`git diff --check` and trailing-whitespace scan)
- tdd: failing test written first, then passed after implementation
