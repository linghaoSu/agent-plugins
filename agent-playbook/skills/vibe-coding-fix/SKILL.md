---
name: vibe-coding-fix
description: Apply bounded local fixes from a vibe-coding health-check report, then verify. Routes unsafe or domain-specific fixes to the owning skill.
argument-hint: '[--slug <name>] [--dry-run] [--apply] [focus notes]'
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash]
---

# Vibe Coding Fix

Consume `.agent-playbook/<slug>/vibe-health-check.md` and stabilize the work
without turning the health check into an unbounded autopilot.

Before editing, read `../../PRINCIPLES.md` and
`../../WORKFLOW-CONTRACTS.md`, especially the **Vibe Health To Fix Contract**,
**Fix Classification**, and **Artifact Ownership** sections. Apply "Verify over
vibe": every applied fix needs a concrete check or a recorded reason why only
static verification was possible.

## Arguments

Raw: `$ARGUMENTS`

Parse:

- `--slug <name>` -> artifact directory `.agent-playbook/<slug>/`. Default:
  `current`.
- `--dry-run` -> classify findings and write the fix plan, but do not edit
  files.
- `--apply` -> explicit authorization to apply safe local cleanup findings.
- Remaining text -> focus notes.

If the current user request clearly says to fix the health-check findings, that
counts as apply authorization for **safe local cleanup only**. It does not
authorize commits, pushes, destructive cleanup, global plugin/runtime changes,
or domain-specific feature work.

## Workflow

### Step 1: Bootstrap

1. Resolve `ARTIFACT_DIR=".agent-playbook/<slug>"`.
2. Require `vibe-health-check.md` to exist. If missing, stop and tell the user
   to run `agent-playbook:vibe-coding-health-check --slug <slug>` first.
3. Read the full health-check artifact and capture:
   - `Decision`
   - `Overall`
   - `Red / Yellow Findings`
   - `Routed Audits`
   - `Next Steps`
4. Capture baseline state:
   ```bash
   git status --short
   git diff --shortstat HEAD
   git diff --cached --shortstat
   ```

### Step 2: Classify Findings

For each red/yellow finding, assign exactly one class from
`../../WORKFLOW-CONTRACTS.md` § Fix Classification:

- **Safe local cleanup** — bounded repo-local docs, skill descriptions, small
  fixture updates, missing artifact links, or documented local checks.
- **Routed workflow** — belongs to another skill such as `idea-to-ship:test`,
  `idea-to-ship:review-code`, `antifragile:*`, `harness-engineering:*`,
  `agent-playbook:context-audit`, `agent-playbook:tool-review`, or
  `agent-playbook:commit-changes`.
- **User-owned decision** — product behavior, public API, deleting tools,
  changing global plugin/runtime installs, or any destructive action.
- **Stop item** — failed release gate, mixed unrelated goals, behavior change
  with no verification path, critical in-memory state, or unclear ownership.

If there are any stop items, do not edit until the first stop item has a fix
plan. If a finding is ambiguous, classify it as user-owned rather than guessing.

### Step 3: Write The Fix Plan

Write or append `.agent-playbook/<slug>/vibe-fix-log.md`.

If no previous file exists, create it. If it exists and has expected headings,
append a dated `## Run - <YYYY-MM-DD HH:MM>` section. Preserve human notes and
write `vibe-fix-log.draft.md` if merge safety is unclear.

Plan template:

```markdown
# Vibe Coding Fix Log - <repo or target>

**Source health check:** vibe-health-check.md
**Date:** <YYYY-MM-DD>
**Mode:** <dry-run|apply>

## Classification
| Finding | Class | Planned Action | Reason |
|---|---|---|---|

## Applied Fixes
| File | Change | Evidence |
|---|---|---|

## Routed / Deferred
| Finding | Target Skill Or Owner | Reason |
|---|---|---|

## Checks Run
| Command | Result | Notes |
|---|---|---|

## Residual Risk
- <risk or "none">
```

### Step 4: Apply Safe Local Cleanup

Proceed only if `--apply` is present or the current request explicitly asks to
fix the health-check findings.

Rules:

1. Apply only findings classified as **Safe local cleanup**.
2. Keep edits minimal and trace each changed line to a health-check finding.
3. Do not run routed workflows unless the current request explicitly asks for
   that workflow too.
4. Do not commit, push, post to GitHub, delete worktrees, or change global
   plugin/runtime installations.
5. If a safe cleanup turns out to require a user-owned decision, stop and move
   it to `Routed / Deferred`.

Examples that are safe in this skill:

- Shorten frontmatter descriptions that duplicate body workflow details.
- Add or update shared skill-contract references.
- Add small fixture checks for the new safety contract.
- Run local release gates and record the results.

Examples that are not safe in this skill:

- Implement product behavior without requirements.
- Add tests for a feature without running `idea-to-ship:test` when traceability
  is missing.
- Delete duplicate plugins from a global runtime install.
- Create commits or PRs.

### Step 5: Verify

Run the safest documented local checks that cover the applied fixes:

1. If `scripts/release-gate.sh` exists, run:
   ```bash
   scripts/release-gate.sh --mode all
   ```
2. If touched files include `agent-playbook`, and
   `tests/agent-playbook-eval-fixtures.sh` exists, run it directly if the
   release gate did not already cover it.
3. If a check fails, stop and mark the fix log result as blocked. Do not claim
   the health-check findings are fixed.

### Step 6: Hand-off

Report:

1. What was applied.
2. What was routed or deferred.
3. Checks run and their result.
4. Whether another health check should be run.

If the remaining work is only routed workflows, name the next skill. If the
remaining work is a user-owned decision, ask that decision plainly.

## Stop Rules

Stop without editing when:

- The source health check has `Decision: Stop` and the first stop item lacks a
  fix plan.
- A release gate or required verification command fails.
- The requested fix requires deleting files, changing global runtime
  installation state, committing, pushing, or posting externally.
- A behavior-changing fix lacks requirements and a runnable verification path.
- Findings cannot be traced back to concrete files, commands, or artifacts.
