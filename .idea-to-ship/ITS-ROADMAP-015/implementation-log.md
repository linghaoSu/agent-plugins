# Implementation Log - ITS-ROADMAP-015

**Architecture:** architecture.md
**Started:** 2026-05-16

## Stage Status

- [x] Stage 1A - Baseline and target selection
- [x] Stage 1B - Fixture helper migration and section/workflow checks
- [x] Stage 1C - Related-skill validation
- [x] Stage 1D - Command-fence checks
- [x] Stage 1E - Release-gate docs and evidence

## Stage 1 - Authoring-standard hygiene checks

**Completed:** 2026-05-16 19:34

### Files touched

- `scripts/skill-hygiene-check.py` - added authoring-standard checks, baseline target selection, related-skill inventory, and command-fence validation.
- `scripts/skill-authoring-baseline.txt` - recorded current legacy skill hashes for authoring-check compatibility.
- `scripts/release-gate.sh` - added baseline file to skill-hygiene infrastructure drift scope.
- `tests/skill-hygiene-check-fixtures.py` - added authoring, baseline, related-skill, and staged-index fixtures; migrated affected old fixtures to authoring-compliant examples.
- `tests/skill-hygiene-release-gate-fixtures.sh` - added authoring strict all-mode evidence and baseline infra target mirroring.
- `RELEASE-GATE.md` - documented authoring-standard checks and baseline behavior.
- `.idea-to-ship/ITS-ROADMAP-015/*` - added requirements, architecture, design review, test plan, TDD log, and implementation evidence.

### Decisions made during implementation

- Baseline applies only to new authoring-standard checks; existing hygiene checks keep their original target behavior.
- Staged/working modes always check touched skills, even if the baseline contains their current hash.
- `--mode all` catches unbaselined committed weak skills, but staged/working remains the enforceable gate for baseline edits.
- Single-skill fixture repos may satisfy related-skill coverage only with a self-reference plus the exact fixture note.

### Deviations from design artifacts

- None.

### Adjacent issues noticed (NOT fixed here)

- No runtime helper exists to regenerate `scripts/skill-authoring-baseline.txt`; this is acceptable for the current static baseline but could be a future convenience command.

### Verification

- 2026-05-16 21:15 code-review fix: `has_workflow_diagram(...)` now preserves
  four-space-indented Mermaid content inside fenced diagrams, and related-skill
  reference extraction no longer carries an unused plugin parameter.
- 2026-05-16 21:19 final verification: full strict release gate, release-gate
  fixtures, topology fixtures, working hygiene check, secret scan, no local
  `skill-creator` source search, and baseline hash audit all passed.
- tdd: `tdd-log.md` entry 2026-05-16 19:22, failing fixture then passed (`bash tests/skill-hygiene-check-fixtures.sh`).
- `python3 -m py_compile scripts/skill-hygiene-check.py tests/skill-hygiene-check-fixtures.py`: ok after review fixes.
- `bash tests/skill-hygiene-check-fixtures.sh`: ok after review fixes.
- `bash tests/skill-hygiene-release-gate-fixtures.sh --self-check`: ok.
- `bash tests/skill-hygiene-release-gate-fixtures.sh`: ok.
- `bash tests/skill-topology-scan-fixtures.sh`: ok.
- `python3 scripts/skill-hygiene-check.py --mode working .`: ok.
- `python3 scripts/skill-topology-scan.py .`: ok; report shows 0 broken references and 0 README coverage gaps.
- `python3 secret-scanner/scripts/scan.py --mode working --format json`: ok; `[]`.
- `scripts/release-gate.sh --mode all --strict`: ok after review fixes; all blocking/advisory checks passed.

### Cross-Skill Checks

- `secret-scanner:scan-secrets --mode working` - triggered by command/example fixture edits; clean JSON result `[]`.
