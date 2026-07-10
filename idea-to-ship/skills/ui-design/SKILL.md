---
name: ui-design
description: Produce an implementation-ready UI/UX contract from requirements, architecture, existing design systems, and visual evidence. Writes interface-design.md without production code.
---

# UI Design

Design task flow and system-consistent states, not decorative mock prose.

## Workflow

1. Resolve `--slug`; require requirements and read architecture when present.
   Inspect current UI, components, tokens, accessibility patterns, responsive
   behavior, and supplied visual references. Apply artifact ownership rules.
2. Define users, jobs, primary/secondary flows, information hierarchy, density,
   navigation, and state transitions. Challenge UI that does not serve a task.
3. Build a design-system map: reuse, extend, or explicitly introduce tokens
   and components. Record source/license for external visual assets.
4. Specify layout, content, interaction, loading/empty/error/success/disabled
   states, keyboard/focus behavior, accessibility semantics, breakpoints, and
   motion only where it explains state or hierarchy.
5. Define visual QA routes, selectors/states, viewport matrix, invariants, and
   evidence needed by `visual-test`.
6. Write `.idea-to-ship/<slug>/interface-design.md` using the existing template.
   Update project `DESIGN.md` only with explicit approval and reusable system
   knowledge—not feature-specific detail.

## Completion

Every requirement touching UI maps to a screen/state and a verifiable
interaction. Name unresolved product decisions, preserve human edits, and stop
before production code.

Use `$idea-to-ship:visual-test` for evidence and `$idea-to-ship:review` for review.
