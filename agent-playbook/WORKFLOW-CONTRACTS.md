# Agent-Playbook Workflow Contracts

These contracts are shared by agent-playbook skills. Skills should cite this
file instead of copying the same safety and artifact rules into every
frontmatter description.

## Vibe Health To Fix Contract

`vibe-coding-health-check` is the diagnostic router. It scores current work and
writes `.agent-playbook/<slug>/vibe-health-check.md`.

`vibe-coding-fix` is the bounded stabilizer. It consumes the health-check
artifact, classifies findings, applies only fixes that are safe in the current
request, and writes `.agent-playbook/<slug>/vibe-fix-log.md`.

The fix skill must not become a generic autopilot:

- It may apply local edits only when the user explicitly asked to fix the
  health-check findings in the current request, or when an explicit `--apply`
  flag is present.
- It may run documented local verification commands such as
  `scripts/release-gate.sh`.
- It must route mutating feature work to the owning skill instead of doing it
  itself. Examples: `idea-to-ship:test`, `idea-to-ship:review-code`,
  `antifragile:*`, `harness-engineering:*`, `agent-playbook:commit-changes`.
- It must not commit, push, post to GitHub, remove worktrees, delete tools, or
  change global plugin/runtime installations unless the user asks for that
  exact action.
- It must stop on red findings involving data loss, unverifiable behavior,
  external IO without failure behavior, or unclear ownership.

## Fix Classification

Classify every health-check finding before editing:

| Class | Action |
|---|---|
| Safe local cleanup | Apply directly if explicitly authorized: docs, skill descriptions, small tests, release-gate fixture updates, bounded config fixes. |
| Routed workflow | Recommend or invoke the owning skill only if the current user request authorizes that workflow. |
| User-owned decision | Ask before editing: product behavior, public API, destructive cleanup, tool removal, global runtime config. |
| Stop item | Do not continue until there is a fix plan: failed release gate, mixed goals, missing verification for behavior change, critical in-memory state. |

## Artifact Ownership

For `.agent-playbook/<slug>/` artifacts:

1. Append dated runs when the existing artifact has the expected headings.
2. Preserve human notes and content outside expected headings.
3. If merge safety is unclear, write `*.draft.md` instead of replacing the
   canonical artifact.
4. A fix log must link the source health-check artifact and record each finding
   as `applied`, `routed`, `deferred`, or `blocked`.

## Frontmatter Descriptions

Frontmatter descriptions are routing hints, not manuals. Keep them short:

- State the task intent.
- Name the artifact written, if any.
- Include one or two disambiguating trigger phrases.
- Keep long safety rules, workflow steps, and implementation details in the
  skill body or this shared contract.
