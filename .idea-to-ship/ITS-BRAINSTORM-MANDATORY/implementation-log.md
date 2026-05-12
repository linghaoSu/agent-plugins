# Implementation Log - Mandatory Brainstorm Gate

**Architecture:** architecture.md
**Started:** 2026-05-09

## Stage Status

- [x] Stage 1 - Mandatory brainstorm contract

## Stage 1 - Mandatory brainstorm contract

**Completed:** 2026-05-09

### Files touched

- `idea-to-ship/README.md` - documented brainstorm as mandatory and removed
  skip guidance.
- `idea-to-ship/skills/brainstorm/SKILL.md` - marked brainstorm as the
  mandatory first stage.
- `idea-to-ship/skills/architect/SKILL.md` - strengthened requirements gate.
- `idea-to-ship/skills/review-design/SKILL.md` - requires requirements before
  design review.
- `idea-to-ship/skills/implement/SKILL.md` - requires requirements before
  implementation.
- `idea-to-ship/skills/test/SKILL.md` - requires requirements and rejects diff
  as a substitute for brainstorm.
- `idea-to-ship/skills/review-code/SKILL.md` - requires requirements before
  code review.
- `idea-to-ship/skills/roadmap/SKILL.md` - clarifies roadmap does not replace
  brainstorm.
- `tests/idea-to-ship-eval-fixtures.py` - added mandatory brainstorm contract
  checks.
- `.idea-to-ship/ITS-ROADMAP-006/*` - refreshed fixture docs that had stale
  "7 checks" wording.

### Decisions made during implementation

- Did not add artifact metadata to prove `requirements.md` origin. That would
  invalidate existing artifacts and create unnecessary schema churn.
- Kept portfolio roadmap planning possible, but required brainstorm before
  slug-level design/implementation/test/review work.

### Deviations from architecture.md

- None.

### Verification

- eval fixtures: ok (`bash tests/idea-to-ship-eval-fixtures.sh`, 13 contract checks)
- negative smoke: ok (temporary root with removed mandatory brainstorm wording fails `brainstorm-mandatory-skill-contract`)
- python compile: ok (`python3 -m py_compile tests/idea-to-ship-eval-fixtures.py`)
- diff whitespace: ok (`git diff --check`)
- release gate working: ok (`scripts/release-gate.sh --mode working`)
- release gate all: ok (`scripts/release-gate.sh --mode all`)
