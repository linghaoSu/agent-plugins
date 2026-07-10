# Idea to Ship

Composable stages from vague idea to verified implementation. Artifacts remain
under `.idea-to-ship/<slug>/` with their existing filenames.

| Skill | Purpose |
|---|---|
| `brainstorm` | Batch-discover testable requirements |
| `grill` | Stress-test one dependent decision at a time |
| `architect` | Compare alternatives and stage a design |
| `roadmap [--commercial]` | Prioritize evidence and commercial scenarios |
| `ui-design` | Define an interface contract |
| `test --mode gate|full|backfill` | Red gate, full story suite, or backfill |
| `implement` | Build one approved vertical stage |
| `review --target design|code` | Risk-scaled review and approved repair |
| `visual-test` | Assert, capture, compare, and diagnose UI states |

```text
brainstorm -> optional grill -> architect -> review design
           -> optional ui-design -> test gate -> implement
           -> test full -> optional visual-test -> review code
```

`WORKFLOW-CONTRACTS.md` owns intensity, capability routing, artifact ownership,
approval, and output rules. Planning stages do not write production code;
implementation never commits or pushes.
