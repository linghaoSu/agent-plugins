# Implementation Log - ITS-ROADMAP-006

**Architecture:** architecture.md
**Started:** 2026-05-09

## Stage Status

- [x] Stage 1 - Contract fixture command
- [ ] Stage 2 - Artifact safety fixtures
- [ ] Stage 3 - Release-gate integration

## Stage 1 - Contract fixture command

**Completed:** 2026-05-09

### Files touched

- `tests/idea-to-ship-eval-fixtures.sh` - added the executable shell entry
  point for offline contract fixtures.
- `tests/idea-to-ship-eval-fixtures.py` - added grouped invariant assertions
  for `/roadmap`, `/test`, and `/review-code` skill contracts.
- `RELEASE-GATE.md` - documented the manual fixture command and its limitation.
- `.idea-to-ship/ITS-ROADMAP-006/test-plan.md` - recorded story, scenario,
  and result traceability for the fixture command.
- `.idea-to-ship/roadmap.md` - marked `ITS-ROADMAP-006` complete after Stage 1
  satisfied the roadmap exit criteria.

### Decisions made during implementation

- Used a separate Python helper instead of inline Python so named contract
  checks stay reviewable.
- Kept Stage 1 manually runnable instead of wiring it into
  `scripts/release-gate.sh`, matching the architecture's false-confidence
  guardrail.
- Asserted semantic groups rather than exact paragraphs to avoid brittle
  golden-file behavior.

### Deviations from architecture.md

- None.

### Adjacent issues noticed (NOT fixed here)

- These fixtures still do not exercise actual generated artifacts. Stage 2 owns
  that if skill behavior becomes executable outside the model prompt.

### Verification

- syntax: ok (`bash -n tests/idea-to-ship-eval-fixtures.sh`; `bash -n tests/release-gate-stage1.sh`; `bash -n scripts/release-gate.sh`)
- python compile: ok (`python3 -m py_compile tests/idea-to-ship-eval-fixtures.py`)
- eval fixtures: ok (`bash tests/idea-to-ship-eval-fixtures.sh`, 13 contract checks)
- negative smoke: ok (temporary root with removed roadmap Candidate Brief fails `roadmap-first-run-contract`)
- usage errors: ok (`python3 tests/idea-to-ship-eval-fixtures.py`; `python3 tests/idea-to-ship-eval-fixtures.py /tmp/agent-plugins-nonexistent-root-006` both exit `2`)
- release gate stage 1 tests: ok (`bash tests/release-gate-stage1.sh`)
- release gate working: ok (`scripts/release-gate.sh --mode working`)
- release gate all: ok (`scripts/release-gate.sh --mode all`)
- diff whitespace: ok (`git diff --check`)
