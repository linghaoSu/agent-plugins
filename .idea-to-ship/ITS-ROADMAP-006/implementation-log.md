# Implementation Log - ITS-ROADMAP-006

**Architecture:** architecture.md
**Started:** 2026-05-09

## Stage Status

- [x] Stage 1 - Contract fixture command
- [x] Stage 2 - Artifact safety fixtures
- [x] Stage 3 - Release-gate integration
- [x] Stage 4 - Delegation authorization hardening
- [x] Stage 5 - Requirements and architecture ownership safety
- [x] Stage 6 - Capacity fallback hardening

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

## Stage 2 - Artifact safety fixtures

**Completed:** 2026-05-12

### Files touched

- `idea-to-ship/README.md` - moved `/test` before final `/review-code` in the
  typical flow and replaced misleading staged-commit wording with local staged
  implementation wording.
- `idea-to-ship/skills/implement/SKILL.md` - aligned the frontmatter
  description and hand-off guidance with non-committing staged local edits.
- `tests/idea-to-ship-eval-fixtures.py` - added executable artifact checks for
  roadmap generated markers, lane item schema, write-target preservation,
  human-only draft fallback, generated-marker preservation, and test-plan
  traceability sections.
- `RELEASE-GATE.md` - documented that the manual idea-to-ship fixture command
  now includes artifact safety checks as well as instruction contract checks.
- `.idea-to-ship/ITS-ROADMAP-006/test-plan.md` - expanded traceability and
  results for Stage 2 artifact fixtures.

### Decisions made during implementation

- Kept the artifact checks inside the existing eval helper so operators still
  run one command: `bash tests/idea-to-ship-eval-fixtures.sh`.
- Encoded a small executable write-target rule for roadmap artifacts: valid
  generated markers allow updating the same file; human-only or malformed
  roadmap content resolves to `roadmap.draft.md`.
- Checked actual repo artifacts (`.idea-to-ship/roadmap.md` and this slug's
  `test-plan.md`) plus temporary roadmap fixtures for draft fallback and marker
  preservation.

### Deviations from architecture.md

- Stage 2 became executable without a live model by validating the artifact
  safety rules directly in the Python helper. This preserves the architecture's
  no-live-agent constraint.

### Adjacent issues noticed (NOT fixed here)

- The fixture helper now owns a small copy of roadmap write-target logic. If a
  future executable roadmap renderer exists, this logic should move there and
  the fixture should call the shared implementation.

### Verification

- python compile: ok (`python3 -m py_compile tests/idea-to-ship-eval-fixtures.py`)
- eval fixtures: ok (`bash tests/idea-to-ship-eval-fixtures.sh`, 13 contract
  checks and 6 artifact checks)
- diff whitespace: ok (`git diff --check`)
- release gate working: ok (`scripts/release-gate.sh --mode working`)
- release gate all: ok (`scripts/release-gate.sh --mode all`)

## Stage 3 - Release-gate integration

**Completed:** 2026-05-12

### Files touched

- `scripts/release-gate.sh` - added `idea-to-ship-fixtures` as a non-blocking
  advisory check in `--mode all`, with staged/working modes recorded as skipped.
- `tests/release-gate-stage1.sh` - added fixture coverage for staged-mode skip
  output and all-mode non-blocking advisory behavior when the idea-to-ship
  fixture command is absent.
- `RELEASE-GATE.md` - documented advisory checks, JSON output coverage, and the
  `--mode all` idea-to-ship fixture integration.
- `.idea-to-ship/roadmap.md` - updated roadmap evidence for Stage 2/3 fixture
  completion.

### Decisions made during implementation

- Kept `idea-to-ship-fixtures` advisory rather than blocking because it checks
  skill contracts and current artifacts, not live model obedience.
- Limited the advisory to `--mode all` so staged and working checks stay fast
  and focused on the user's immediate diff.
- Preserved exit semantics: advisory `WARN` results do not change exit code;
  missing or failing blocking checks still return `1` or `2`.

### Deviations from architecture.md

- Stage 3 used release-gate advisory integration, not blocking integration.
  This follows the architecture's false-confidence guardrail and keeps the
  command safe for full-repo release hardening.

### Adjacent issues noticed (NOT fixed here)

- `--strict` still does not promote advisories to blocking failures. That can
  be revisited after the advisory signal proves stable.

### Verification

- syntax: ok (`bash -n scripts/release-gate.sh`; `bash -n tests/release-gate-stage1.sh`)
- release gate fixture tests: ok (`bash tests/release-gate-stage1.sh`)
- eval fixtures: ok (`bash tests/idea-to-ship-eval-fixtures.sh`)
- staged gate: ok (`scripts/release-gate.sh --mode staged`)
- all gate: ok (`scripts/release-gate.sh --mode all`, advisory pass)
- json smoke: ok (`scripts/release-gate.sh --mode all --json`, advisory check included)
- diff whitespace: ok (`git diff --check`)

## Stage 4 - Delegation authorization hardening

**Completed:** 2026-05-12

### Files touched

- `idea-to-ship/PRINCIPLES.md` - changed runtime-aware routing from
  "sub-agent by default" to a delegation gate requiring host support and
  current user/host authorization.
- `idea-to-ship/README.md` - changed adversarial review guidance to say
  sub-agents are used only when authorized.
- `idea-to-ship/skills/architect/SKILL.md` - made explorer delegation
  conditional and required main-context fallback recording.
- `idea-to-ship/skills/review-code/SKILL.md` - made adversarial reviewer
  delegation conditional and required fallback reason recording.
- `idea-to-ship/skills/review-design/SKILL.md` - applied the same conditional
  delegation rule to design review.
- `idea-to-ship/skills/roadmap/SKILL.md` - made collection subagents
  conditional and defined sequential collection fallback.
- `idea-to-ship/skills/brainstorm/SKILL.md` - made two-context critique
  conditional on delegation authorization.
- `tests/idea-to-ship-eval-fixtures.py` - extended the runtime-aware review
  contract fixture to require delegation authorization wording.

### Decisions made during implementation

- Preserved runtime-native sub-agent support for hosts that allow it, but made
  authorization explicit so the plugin does not conflict with runtimes that
  require user opt-in before delegation.
- Kept fallback behavior as an active adversarial/exploration pass, not a
  weaker "skip review" path.

### Deviations from architecture.md

- None. This extends FR-8's runtime-aware routing contract without changing the
  fixture command shape.

### Adjacent issues noticed (NOT fixed here)

- Runtime-specific adapters remain described in prose. A future executable
  runner could make these routing choices machine-checkable.

### Verification

- eval fixtures: ok (`bash tests/idea-to-ship-eval-fixtures.sh`)
- release gate all: ok (`scripts/release-gate.sh --mode all`)
- diff whitespace: ok (`git diff --check`)

## Stage 5 - Requirements and architecture ownership safety

**Completed:** 2026-05-12

### Files touched

- `idea-to-ship/skills/brainstorm/SKILL.md` - added Requirements Ownership
  rerun rules for stable `FR-*` IDs, heading-level merges, human-note
  preservation, `requirements.draft.md` fallback, and explicit replacement
  approval.
- `idea-to-ship/skills/architect/SKILL.md` - added Architecture Ownership
  rerun rules for option/stage identity, decision history, human-note
  preservation, `architecture.draft.md` fallback, and explicit replacement
  approval.
- `tests/idea-to-ship-eval-fixtures.py` - added contract checks for
  brainstorm/architect rerun preservation and artifact checks for
  requirements/architecture draft fallback plus current structured artifact
  safety.
- `.idea-to-ship/ITS-ROADMAP-006/requirements.md` and
  `.idea-to-ship/ITS-ROADMAP-006/architecture.md` - recorded the expanded
  Stage 5 fixture scope.

### Decisions made during implementation

- Used the same preservation model as `/test`: update by stable identity where
  possible, preserve human edits, and write a draft when a safe merge cannot be
  proven.
- Kept these as contract/artifact fixtures rather than live agent evals, so the
  release-gate advisory stays deterministic and offline.

### Deviations from architecture.md

- Stage 5 extends the original eval fixture scope from roadmap/test/review-code
  into brainstorm/architect ownership safety. The architecture artifact was
  updated to record this extension.

### Adjacent issues noticed (NOT fixed here)

- The ownership rules are still prose contracts. A future executable artifact
  writer could centralize merge/draft behavior and let the fixtures call shared
  code instead of mirrored helper logic.

### Verification

- python compile: ok (`python3 -m py_compile tests/idea-to-ship-eval-fixtures.py`)
- eval fixtures: ok (`bash tests/idea-to-ship-eval-fixtures.sh`, 15 contract
  checks and 10 artifact checks)
- release gate fixture tests: ok (`bash tests/release-gate-stage1.sh`)
- staged gate: ok (`scripts/release-gate.sh --mode staged`)
- working gate: ok (`scripts/release-gate.sh --mode working`)
- all gate: ok (`scripts/release-gate.sh --mode all`)
- json smoke: ok (`scripts/release-gate.sh --mode all --json`)
- diff whitespace: ok (`git diff --check`)

## Stage 6 - Capacity fallback hardening

**Completed:** 2026-05-12

### Files touched

- `idea-to-ship/PRINCIPLES.md` - classified model-selection and capacity
  errors, including "Selected model is at capacity", as sub-agent
  unavailability that must fall back to the main context.
- `idea-to-ship/skills/review-code/SKILL.md` - required `/review-code` to stop
  retrying the same selected model after capacity errors and record a capacity
  fallback in `code-review.md`.
- `idea-to-ship/skills/review-design/SKILL.md` - applied the same capacity
  fallback rule to design review.
- `tests/idea-to-ship-eval-fixtures.py` - extended the runtime-aware review
  contract fixture to require capacity fallback wording.

### Decisions made during implementation

- Treated capacity errors as an availability problem, not as a review failure
  or a reason to retry the same unavailable selected model.
- Kept fallback behavior equivalent: run the same adversarial prompt in the
  main context and record the reason.

### Deviations from architecture.md

- Stage 6 extends runtime-aware routing coverage based on a Codex-specific
  failure mode reported during use.

### Adjacent issues noticed (NOT fixed here)

- Installed plugin caches may still contain older skill text until the plugin
  is reinstalled or refreshed from this source repo.

### Verification

- python compile: ok (`python3 -m py_compile tests/idea-to-ship-eval-fixtures.py`)
- eval fixtures: ok (`bash tests/idea-to-ship-eval-fixtures.sh`, capacity
  fallback covered by `review-code-runtime-aware-routing-contract`)
- release gate fixture tests: ok (`bash tests/release-gate-stage1.sh`)
- staged gate: ok (`scripts/release-gate.sh --mode staged`)
- working gate: ok (`scripts/release-gate.sh --mode working`)
- all gate: ok (`scripts/release-gate.sh --mode all`)
- json smoke: ok (`scripts/release-gate.sh --mode all --json`)
- diff whitespace: ok (`git diff --check`)
