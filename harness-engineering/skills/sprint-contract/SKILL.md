---
name: sprint-contract
description: Draft a Sprint Contract between a Generator agent and an independent Evaluator — concrete, testable success criteria agreed before work begins. Forces objective verification (compilers, tests, schema checks) over LLM-as-judge for anything non-subjective. Writes .harness-engineering/<slug>/sprint-contract.md.
argument-hint: '[--slug <name>] [what the Generator is supposed to produce]'
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash]
---

# Sprint Contract — agree on "done" before starting

Self-grading agents approve their own mediocre work. The fix is an independent
Evaluator operating on clean context, armed with a contract written *before*
the Generator starts. This skill writes that contract.

The contract is the Evaluator's checklist. If a criterion can't be checked by
running something (compiler, test, schema validator, browser automation), it
probably shouldn't be on the list.

## Arguments

Raw: `$ARGUMENTS`

Parse:
- Optional leading `--slug <name>` → slug. Default: `current`.
- Remaining text → description of what the Generator produces. If empty, ask.

## Workflow

### Step 1: Bootstrap

1. Resolve `<slug>` and artifact dir:
   ```bash
   ARTIFACT_DIR=".harness-engineering/<slug>"
   mkdir -p "$ARTIFACT_DIR"
   ```
2. If `harness-design.md` exists, read it — the contract should align with
   the Generator/Evaluator split already declared there.
3. If the task description is empty, ask in one batch:
   - What is the Generator supposed to produce (artifact type + location)?
   - What's the input it receives?
   - What counts as "done" from the user's perspective?
   - What's the worst failure mode we're guarding against?

### Step 2: Enumerate criteria, objective first

For every criterion, decide which tier of verification it belongs in. Push
criteria down the list (toward objective) whenever possible.

**Tier 1 — Machine-checkable (preferred, required when possible)**
- Compiles / type-checks
- Tests pass (name the tests)
- Schema validates (name the schema)
- Lint / format clean
- Browser automation assertion passes (name the selector + expected state)
- HTTP status / response shape matches

**Tier 2 — Structural but not semantic**
- File exists at expected path
- Required sections present in the artifact
- Links / references resolve
- Output size within expected bounds

**Tier 3 — LLM-as-judge (use sparingly, only for genuinely subjective output)**
- Tone / style for user-facing copy
- Summary faithfulness for long-form summaries
- Design taste for UX-only artifacts
- *Must* run on clean context (fresh model instance, only sees the artifact
  and the criteria)

If every criterion lands in Tier 3, that's a smell — push back and try to
define objective proxies first.

### Step 3: Define the failure protocol

What happens when the Evaluator rejects? Options:

- **Retry with feedback** — Generator receives the Evaluator's concrete
  errors (not vibes) and tries again. Cap the retries.
- **Escalate to human** — after N failed rounds, surface the artifact + all
  Evaluator feedback to the user.
- **Rollback** — revert any side effects and mark the step failed.

Pick one per criterion class; specify retry caps.

### Step 4: Write `sprint-contract.md`

Template:

```markdown
# Sprint Contract — <task name>

**Slug:** <slug>
**Date:** <YYYY-MM-DD>
**Generator role:** <who/what>
**Evaluator role:** <who/what, must be independent instance on clean context>

## Deliverable
<Exactly what the Generator produces: artifact type, path, shape.>

## Inputs
<What the Generator is given. Everything not listed here is out of scope.>

## Acceptance criteria

### Tier 1 — Machine-checkable (MUST pass)
| # | Criterion | How the Evaluator checks |
|---|-----------|--------------------------|
| 1 | ...       | `make test TEST=...` must exit 0 |
| 2 | ...       | Output validates against `schemas/foo.json` |
| 3 | ...       | ... |

### Tier 2 — Structural (MUST pass)
| # | Criterion | How checked |
|---|-----------|-------------|
| 1 | ...       | ... |

### Tier 3 — LLM-as-judge (only where listed, clean-context required)
| # | Criterion | Rubric |
|---|-----------|--------|
| 1 | ...       | ... |

## Feedback contract
The Evaluator returns structured output only:

```json
{
  "verdict": "accept | reject",
  "failed_criteria": [{"id": "T1-2", "evidence": "test X failed: ..."}],
  "notes": "string, objective only — no 'try harder' language"
}
```

Emotional / evaluative prose is forbidden. Evidence must cite a specific
check (command output, schema error, selector, rubric line).

## Failure protocol
- **Tier 1 reject**: retry with failed_criteria as feedback. Cap: N retries.
- **Tier 2 reject**: ...
- **Tier 3 reject**: ...
- **After cap**: escalate to human with full history.

## Out of scope
<What the Evaluator is NOT checking — prevents scope creep during review.>

## Open questions
<Anything deferred.>
```

### Step 5: Hand-off

1. Print the contract's headline: number of criteria per tier, retry caps.
2. If Tier 3 dominates, flag it and ask the user whether the task is genuinely
   subjective or whether objective proxies are possible.
3. Suggest: "Run the Generator; when it claims done, hand the artifact +
   this contract to a fresh Evaluator."

## Notes

- The contract is written *before* the Generator starts. Writing it after
  biases the criteria toward what was produced.
- "The Evaluator is another call to the same model" is fine — what matters
  is *clean context* and *objective criteria*, not a different model weight.
- If the user insists on subjective-only criteria, honor it but record in
  Open Questions that this contract has no machine-checkable floor.
