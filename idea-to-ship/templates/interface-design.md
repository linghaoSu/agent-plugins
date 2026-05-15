# Interface Design Template

```markdown
# Interface Design - <short title>

**Slug:** <slug>
**Date:** <YYYY-MM-DD>
**Status:** draft
**References:** requirements.md, architecture.md (if present), DESIGN.md (if present)

## Summary
<One paragraph. What interface or flow is being designed and the chosen direction.>

## UX Brief
**Users:** ...
**Primary tasks:** ...
**Success criteria:** ...
**Context of use:** ...
**Non-goals:** ...

## Existing UI / Design System Map
**Relevant files:** <paths>
**Tokens:** <roles and source paths>
**Components to reuse:** <component -> role>
**States available:** <state inventory>
**Known gaps:** <uncertain or missing design-system evidence>

## Visual References
<table from visual-reference-inventory.md>

## Image-Derived Constraints
**Must match:** <constraints from target/current-ui references>
**May borrow:** <constraints from inspiration/brand/competitor references>
**Must avoid:** <negative references or rejected image patterns>
**Unusable / unclear references:** <images that could not be inspected or mapped>

## Visual Contract
**Style archetype:** <quiet SaaS / dense ops / editorial / commerce / etc.>
**Hierarchy:** <how attention is directed>
**Color roles:** <token roles, not decorative palette notes>
**Typography:** <scale and usage>
**Spacing / layout:** <grid, density, rhythm>
**Depth / motion:** <when used and limits>
**Do / Don't:** <concrete positive and negative constraints>

## Interaction Spec
### Flow 1 - <name>
**Entry:** ...
**Main path:** ...
**Alternate paths:** ...
**Exit / undo:** ...
**Validation / errors:** ...

## Component Spec
| Surface | Component | Source | States | Notes |
|---|---|---|---|---|
| ... | ... | `path` | default/hover/focus/error | ... |

## Responsive Spec
| Viewport | Layout | Navigation | Data density | Notes |
|---|---|---|---|---|
| desktop | ... | ... | ... | ... |
| tablet | ... | ... | ... | ... |
| mobile | ... | ... | ... | ... |

## Accessibility Contract
<Keyboard, focus, labels, contrast, semantics, announcements, reduced motion.>

## Visual QA Plan
<Screens, states, viewports, screenshot or visual-regression checks.>

## UX Measurement
<Task success or HEART-style metric mapping if this needs post-release validation.>

## Design Decisions
| Decision | Rationale | Tradeoff | Source |
|---|---|---|---|
| ... | ... | ... | FR-1 / `path` |

## Open Questions
<User-owned decisions or missing evidence. Empty is fine.>
```
