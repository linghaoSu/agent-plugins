---
name: review
description: Risk-scaled review of idea-to-ship architecture or implementation. Use --target design|code and optional --review-depth quick|standard|deep; preserves existing review artifacts and approval gates.
---

# Review

Review one idea-to-ship artifact or diff, apply only approved critical/high
repairs, and independently re-check the result.

## Arguments

- `--slug <name>`: artifact root; default `current`.
- `--target design|code`: required unless exactly one target is discoverable.
- `--review-depth quick|standard|deep`: optional forced intensity.
- Remaining text: focus notes.

Read `../../PRINCIPLES.md` and `../../WORKFLOW-CONTRACTS.md`. Use their
capability routing, severity, approval, artifact ownership, output, and review
loop contracts. Never name a model or execution product.

## Inputs

Always read `requirements.md`. For `design`, require `architecture.md` and read
`interface-design.md` when present. For `code`, collect the complete current
diff including untracked files and read architecture, interface, implementation
log, test plan, TDD log, and visual evidence when present. Fingerprint inputs
before review and again before edits; stop on drift.

## Intensity

- `quick`: small, low-risk target; same-context checklist.
- `standard`: independent reviewers for required angles, then synthesis.
- `deep`: multiple independent angles, adversarial challenge, synthesis, and
  final sanity review.

Escalate when review discovers auth, secrets, data migration, destructive
behavior, broad public contracts, or unclear ownership. If independent
execution is unavailable, preserve angles sequentially and record `degraded`.

## Review axes

Keep findings separated so one axis cannot mask another:

- **Spec:** missing/partial requirements, wrong behavior, scope creep.
- **Standards:** documented repo rules and evidence-backed design smells.
- **Correctness:** causal behavior, failure modes, security, regressions.
- **Verification:** public seams, non-tautological tests, traceability.
- **UI/UX:** required only when interface artifacts or UI changes exist.

Reviewers return finding ID, severity, axis, evidence, consequence, and minimal
repair—or `LGTM`. Do not report style that tooling enforces.

## Repair loop

1. Select intensity and run required angles independently where supported.
2. Deduplicate by root cause without merging axes or dropping evidence.
3. If critical/high findings require edits, create the documented modification
   plan and obtain approval before changing architecture or code.
4. Apply only approved repairs. Do not fix medium/low findings opportunistically.
5. Run objective checks, then re-run every required affected angle. Permit one
   repair round; unresolved severe findings end as open issues, not success.

## Artifacts

- `design`: preserve `.idea-to-ship/<slug>/design-review.md`.
- `code`: preserve `.idea-to-ship/<slug>/code-review.md`.

Record intensity, mode/degradation, fingerprint, findings and resolution,
checks, deferred/out-of-scope items, residual risk, and verdict. A clean verdict
requires all required angles to return `LGTM` on current inputs.

Design findings return to `$idea-to-ship:architect`; code findings return to
`$idea-to-ship:implement` and verification to `$idea-to-ship:test`.
