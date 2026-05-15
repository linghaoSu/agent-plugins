# Test Plan Template

```markdown
# Test Plan - <slug>

**Date:** <YYYY-MM-DD>
**Target:** <list of changed files>
**Framework:** <detected>
**Run command:** <`npm test` | `pytest` | ...>

## Scope
<One paragraph: what's covered, what's explicitly out.>

## User Stories
| Story ID | Actor | Goal | Preconditions | Trigger | Expected Outcome | Source |
|---|---|---|---|---|---|---|
| US-1 | ... | ... | ... | ... | ... | FR-1 |

## Acceptance Criteria
| AC ID | Story ID | Criterion | Verification Method | Source |
|---|---|---|---|---|
| AC-1 | US-1 | ... | test: ... | FR-1 |

## Scenario Matrix
| Scenario ID | Story ID | Type | Sequence | Inputs / Setup | Expected | Failure Signal | Source |
|---|---|---|---|---|---|---|---|
| S-1 | US-1 | happy | ... | ... | ... | none | AC-1 |
| S-2 | US-1 | invalid-input | ... | ... | ... | ... | AC-1 |

## Test Matrix

### Unit
| # | Scenario | Case | Input | Expected | Source |
|---|---|---|---|---|---|
| U1 | S-1 | ... | ... | ... | AC-1 |

### Integration
| # | Scenario | Case | Setup | Expected | Source |
|---|---|---|---|---|---|
| I1 | S-2 | ... | ... | ... | architecture section |

### E2E (if applicable)
| # | Scenario | Case | Flow | Expected | Source |
|---|---|---|---|---|---|
| E1 | S-1 | ... | ... | ... | AC-1 |

## Traceability
| Requirement | Story | Acceptance Criteria | Scenarios | Tests |
|---|---|---|---|---|
| FR-1 | US-1 | AC-1 | S-1, S-2 | U1, I1 |

## Out Of Scope
- <what we consciously are NOT testing and why>

## Fixtures & Test Data
<Any shared setup, factories, or data the cases need.>

## Risk Notes
<Anything flaky, slow, or requiring future attention.>

## Stage TDD Slices
<Optional: stage-local slices imported from `/implement --tdd`; each must map to
story/acceptance/scenario/test IDs or be marked provisional.>
```
