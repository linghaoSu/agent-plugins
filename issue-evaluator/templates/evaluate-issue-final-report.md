# Evaluate Issue Final Report Template

```markdown
## Issue Evaluation: <issue-title>
<!-- Description mode only: include the next line. -->
**Mode**: description-based evaluation (no GitHub issue)

**Issue**: #<number>
**Review mode**: <multi-agent | degraded-same-context-review>
**Degradation reason**: <none | explicit unsupported runtime | user forbade reviewer sub-agents | reviewer/model unavailable or at capacity>
**Diagnosis pipeline**: Round 1 (primary analysis + independent check + IDE Diagnostics) → Round 2 (adversarial review + evaluation) → Round 3 (final synthesis)

<Round 3 structured output follows>
```
