# TDD Log - ITS-ROADMAP-008

**Date:** 2026-06-01
**Mode:** stage-tdd

## Stage 1 - Close implement shared-contract cleanup

### Red

Command:

```bash
tests/idea-to-ship-eval-fixtures.sh
```

Result:

- Failed as expected after adding fixture invariants.
- Missing invariant groups:
  - `implement-template-reference-contract`: `template owns log details`
  - `implementation-log-template-contract`: `success criteria`

### Green

Command:

```bash
tests/idea-to-ship-eval-fixtures.sh
```

Result:

- Passed after updating `implement/SKILL.md`,
  `templates/implementation-log.md`, and the fixture contract.
