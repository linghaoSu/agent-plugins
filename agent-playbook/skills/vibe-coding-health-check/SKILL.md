---
name: vibe-coding-health-check
description: Audit a repo or current diff after fast AI-assisted coding for drift, fragility, missing verification, and context/tool hygiene. Writes .agent-playbook/<slug>/vibe-health-check.md.
argument-hint: '[--slug <name>] [--scope diff|repo|agent|all] [--deep] [focus notes]'
allowed-tools: [Read, Write, Glob, Grep, Bash]
---

# Vibe Coding Health Check

Run a lightweight control check after fast AI-assisted coding. The goal is not
to prove the code is perfect; it is to decide whether to keep shipping, slow
down for tests/review, or stop and run a deeper audit.

This is a router plus scorecard. Do not duplicate the full audits from
`idea-to-ship`, `antifragile`, `harness-engineering`, or `context-audit`; use
this skill to collect the first signals and route to the right deeper workflow.

Before scoring, read `../../PRINCIPLES.md` and
`../../WORKFLOW-CONTRACTS.md`. In particular, apply "Verify over vibe" and
"Explore -> Plan -> Code -> Verify": every green decision needs a runnable
check or cited evidence, not confidence from the same model that made the
change. Also apply the local 12-rule execution contract: name assumptions,
conflicts, skipped checks, token-budget pressure, and residual risk instead of
smoothing them over. If the user asks to fix the findings after this diagnosis,
hand off to the Vibe Health To Fix Contract via `agent-playbook:vibe-coding-fix`.

## Arguments

Raw: `$ARGUMENTS`

Parse:

- `--slug <name>` -> artifact directory `.agent-playbook/<slug>/`. Default:
  `current`.
- `--scope diff` -> current staged/unstaged changes only. Default when a diff
  exists.
- `--scope repo` -> whole target project health.
- `--scope agent` -> agent/plugin/hook/harness health.
- `--scope all` -> diff + repo + agent workflow.
- `--deep` -> after the lightweight scorecard, run the relevant deeper local
  checks that are safe and non-mutating. This health-check does not launch its
  own subagents unless the user explicitly authorizes delegation. If it routes
  to a review skill, invoking that review skill is standing authorization for
  its reviewer sub-agents unless the user explicitly forbids delegation, the
  runtime explicitly does not support reviewer sub-agents, or the selected
  reviewer/model is explicitly unavailable or at capacity; in that case the
  review skill may fall back to recorded same-context review.
- Remaining text -> focus notes.

## Workflow

### Step 1: Bootstrap

1. Create `.agent-playbook/<slug>/`.
2. Capture basic state:
   ```bash
   git status --short
   git diff --shortstat HEAD
   git diff --cached --shortstat
   git diff --name-only HEAD
   git diff --cached --name-only
   git ls-files --others --exclude-standard
   ```
3. Detect available checks:
   - `scripts/release-gate.sh`
   - package/test commands in `package.json`, `Makefile`, `justfile`,
     `pyproject.toml`, `go.mod`, `Cargo.toml`, or similar
   - existing idea-to-ship artifacts under `.idea-to-ship/`
   - agent/plugin files: `*/skills/*/SKILL.md`, `hooks.json`, hook scripts,
     `.claude-plugin/plugin.json`
4. If there is no diff and scope is `diff`, switch to `repo` and state why.
5. Build a changed-file union from tracked, staged, and untracked files. Use
   this union for scope, size, and touched-file routing. Untracked files must
   count as changed files; for rough size, use `wc -l` on text files or mark
   binary/unknown files as new untracked risk.

### Step 2: Fast Signals

Score each dimension as `green`, `yellow`, or `red`. Cite concrete file paths,
commands, or artifact headings. If evidence is absent, say "not found" rather
than guessing.

| Dimension | Green | Yellow | Red |
|---|---|---|---|
| Change size | Small, cohesive diff | More than 15 files or 800 changed lines | More than 30 files or 2000 changed lines without staged plan |
| Scope control | Every changed file maps to one goal | Mixed docs/code/tests but still explainable | Unrelated refactors, drive-by cleanup, or unclear goal |
| Requirement traceability | Requirements or issue are clear | Intent only exists in chat or commit text | Behavior change with no requirement/story/acceptance source |
| Test/verification | Focused tests or release gate pass | Only smoke/manual checks | Behavior change with no runnable verification path |
| Error/resilience | Boundaries handle failures | Some IO/network/state paths lack clear failure behavior | Critical path lacks timeout, retry, validation, or rollback |
| State/recovery | State is durable and resumable where needed | Logs/state exist but recovery is manual | Agent/pipeline loop has no state, schema, retry, or resume path |
| Context/tool hygiene | Rules are short, tools bounded | Some overlap or context bloat | Conflicting agent rules, noisy tools, or unbounded outputs |

### Step 3: Run Safe Checks

Run checks that are documented and non-mutating:

1. If `scripts/release-gate.sh` exists:
   - `scripts/release-gate.sh --mode working` when reviewing uncommitted work.
   - `scripts/release-gate.sh --mode all` when scope is `repo`, `agent`, or
     `all`, or when the user asked for a release-ready check.
2. If touched files include `idea-to-ship` skills and
   `tests/idea-to-ship-eval-fixtures.sh` exists, run it.
3. Run obvious focused tests only when the command is local and known from repo
   docs or manifests. Do not invent an expensive full-suite command.
4. If a check fails, mark the relevant dimension `red` and stop before
   recommending "ship".

### Step 4: Route To Deep Audits

Use this table to decide the next action. With `--deep`, perform only safe
read-only audits directly if the corresponding skill is available. Mutating
workflows must be recommended, not executed, unless the user explicitly gives
that additional authorization in the current request.

| Signal | Next action | Auto-run with `--deep`? |
|---|---|---|
| Requirement, design, test, or review traceability is weak | Recommend `idea-to-ship:test` then `idea-to-ship:review-code` | No, may write tests or fixes |
| Runtime code has dependency, error handling, data safety, or observability risk | Run or recommend `antifragile:antifragile-system` | Yes, read-only |
| Plugin hooks, skill infrastructure, state files, or scripts look fragile | Run or recommend `antifragile:antifragile-agent` | Yes, read-only |
| Agent/pipeline work lacks state, schemas, retries, resumability, or independent evaluation | Run or recommend `harness-engineering:harness-audit` | Yes, audit artifact only |
| Agent rules, tools, MCPs, memory files, or context are bloated/conflicting | Run or recommend `agent-playbook:context-audit` or `agent-playbook:tool-review` | Yes, read-only/artifact-only |
| Commit or release readiness is the question | Recommend `agent-playbook:commit-changes` after staged release gate passes | No, mutates git and may create PRs |

Do not run subagents as part of this health-check unless the user explicitly
asked for delegation. Main-context audits are acceptable here. Do not convert a
routed review workflow into same-context review because of this health-check's
local delegation gate; review skills own their multi-agent routing and should
fall back to recorded same-context review only when required reviewer agents are
explicitly unsupported by the host/runtime, explicitly forbidden by the user,
or explicitly unavailable / at capacity.

### Step 5: Decision

Choose one:

- **Continue:** only green/yellow findings, all required checks pass, and
  yellow items have clear follow-up.
- **Slow down:** no blocking failure, but traceability, test coverage,
  resilience, or context hygiene is weak. Run the routed deep audit before
  more feature work.
- **Stop:** any red finding that can cause data loss, broken release gates,
  unverifiable behavior, unbounded agent loops, or unclear ownership. Do not
  keep coding until the red item has a fix plan.

### Step 6: Write Artifact

Write `.agent-playbook/<slug>/vibe-health-check.md` with artifact ownership
protection:

1. If no previous file exists, create it.
2. If a previous file exists and has the expected headings, append a new
   dated `## Run - <YYYY-MM-DD HH:MM>` section rather than replacing history.
3. Preserve human notes and any content outside expected headings.
4. If the file cannot be safely appended or merged, write
   `vibe-health-check.draft.md` or ask before replacing the canonical file.

```markdown
# Vibe Coding Health Check - <repo or target>

**Date:** <YYYY-MM-DD>
**Scope:** <diff|repo|agent|all>
**Decision:** <Continue|Slow down|Stop>
**Overall:** <A|B|C|D|F>

## Summary
<2-4 sentences. Name the main risk and next action.>

## Scorecard
| Dimension | Status | Evidence | Why It Matters |
|---|---|---|---|

## Checks Run
| Command | Result | Notes |
|---|---|---|

## Routed Audits
| Trigger | Recommended Skill | Run Now? | Reason |
|---|---|---|---|

## Red / Yellow Findings
- [ ] <severity> - <finding> - <evidence> - <fix or next skill>

## Passed
- <signals that looked healthy>

## Next Steps
1. <highest payoff action>
2. <second action>
3. <third action>
```

### Step 7: Hand-off

Report the decision, top 3 risks, checks run, and the next skill or command.
If the decision is `Stop`, do not soften it; name the first fix needed to get
back to `Slow down` or `Continue`.

## Stop Rules

Stop and mark `red` when any of these are true:

- Release gate or required verification command fails.
- A behavior-changing diff lacks both test coverage and documented reason.
- The diff mixes unrelated goals and cannot be reviewed as one coherent unit.
- Critical state is only in memory without a recovery story.
- External IO on a critical path has no timeout or failure behavior.
- An agent loop has no persisted state, no schema validation, and no retry or
  resume path.
- The repo's agent instructions are contradictory enough that future agents are
  likely to ignore important rules.
