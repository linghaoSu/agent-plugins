---
name: bootstrap-project-memory
description: Create or refine CLAUDE.md (and optionally AGENTS.md) for the current repo via Socratic Q&A. Targets under 200 lines, only captures what agents cannot discover by reading code. Writes to repo root; never overwrites without diff confirmation.
argument-hint: '[--agents-md] [free-form notes about the project]'
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash]
---

# Bootstrap Project Memory

Produce a tight `CLAUDE.md` (and optionally `AGENTS.md`) for the current
repo. The goal is **persistent, agent-specific context that every session
needs** — not architecture docs, not style guides the agent already knows.

Read `../../PRINCIPLES.md` first; apply the local 12-rule execution contract
when drafting or pruning memory files, and cite Principle 3 when pushing back
on bloat.

## Arguments

Raw: `$ARGUMENTS`

Parse:
- `--agents-md` → also produce `AGENTS.md` (or `AGENTS.md` import stub)
  for tools that read it (Codex, other agents).
- Remaining text → optional project notes (stack, team conventions,
  known quirks). May be empty.

## Workflow

### Step 1: Inventory what already exists

1. Check for existing memory files and note sizes:
   ```bash
   for f in CLAUDE.md .claude/CLAUDE.md AGENTS.md CLAUDE.local.md \
            .claude/rules/*.md 2>/dev/null; do
     [ -f "$f" ] && wc -l "$f"
   done
   ```
2. Read any existing memory file fully.
3. If a CLAUDE.md over 200 lines exists, **the job is pruning, not
   writing.** Jump to the Prune workflow at the bottom.

### Step 2: Probe the repo

Run these in parallel; the goal is to find the 5–10 facts the agent
cannot infer:

- `package.json` / `pyproject.toml` / `Cargo.toml` / `go.mod` → build
  tool, test command, node version, package manager (npm vs pnpm vs yarn).
- `.github/workflows/*.yml` → what CI runs and in what order.
- `README.md` → user-facing intent; often the pitch but rarely the
  conventions.
- `Makefile` / `justfile` / `scripts/` → the commands contributors
  actually run.
- `.editorconfig` / `.prettierrc` / `eslint.config.*` / `ruff.toml` →
  style tooling that agents should *defer to*, not reimplement.
- Test layout: `tests/`, `*_test.go`, `__tests__/` — single-file test
  runner commands beat full-suite commands.
- `.env.example` — env vars agents must set but cannot discover.

### Step 3: Socratic Q&A

Ask in **one batch of 4–7 questions**, only those you cannot answer from
Step 2. Typical questions:

1. What's the single command to run the full test suite? A single test?
2. Before committing, what *must* run (typecheck, lint, format)?
3. Are there env vars/ports/services required for local dev?
4. Any PR/branch conventions (commit prefix, branch naming, CI must-be-green)?
5. Any "don't touch without asking" files or folders?
6. Any non-obvious gotchas — migrations, codegen, generated files?
7. Package manager and node/python version if relevant?

If the user says "use defaults", pick a reasonable choice and note it as
`# assumption: <choice>` inline.

### Step 4: Draft CLAUDE.md

Target: **under 200 lines** ([Claude Code memory docs](https://code.claude.com/docs/en/memory#write-effective-instructions)).
Every line must pass: *"Would removing this cause the agent to make
mistakes?"* If not, cut it.

Template:

```markdown
# <repo-name>

## Commands
- Install: `<pkg manager> install`
- Dev server: `<cmd>`
- Test (full): `<cmd>`
- Test (single): `<cmd --filter X>` (prefer this; full suite is slow)
- Typecheck: `<cmd>`
- Lint: `<cmd>`
- Build: `<cmd>`

## Code style
<Only rules that differ from language defaults. Skip "use clean code".>
- Use <ES modules / CommonJS / …>
- Destructure imports when possible
- <project-specific convention that burned someone>

## Workflow
- Run typecheck after a series of edits, not after every edit.
- Prefer single-test runs over the full suite.
- Before commit: <pre-commit chain>
- Branch naming / PR title: <pattern>
- Local execution rules: <only project-specific rules that agents cannot infer;
  keep broad behavior rules concise and avoid duplicating tooling>

## Environment
- Node: <version>  (or Python: <version>, …)
- Required env vars: <list — see .env.example>
- External services: <docker compose up? redis? postgres?>

## Gotchas
<Non-obvious behaviors. One line each.>
- <gotcha>

## Out of scope for agents
<Things we've decided agents shouldn't touch without human review.>
- <path or pattern>
```

### Step 5: Optional AGENTS.md

If `--agents-md` was passed, prefer the one-file approach from the
[Claude Code docs](https://code.claude.com/docs/en/memory#agents-md):
write the real content to `AGENTS.md` and make `CLAUDE.md` a one-line
import:

```markdown
@AGENTS.md

## Claude Code specifics
<Anything truly Claude-only. Often nothing.>
```

If both files already exist with drifting content, *flag the drift* and
ask which one to make canonical — do not auto-merge.

### Step 6: Show diff and confirm

1. If the target file exists, show `diff -u <old> <draft>` and ask for
   approval before writing.
2. If new, write it and print:
   - Line count (target: <200)
   - Top 5 rules by "would an agent fail without this?"
3. Remind the user: `/memory` in Claude Code lists what's loaded; if a
   rule doesn't show up, the file isn't being found.

## Prune workflow (existing oversized memory)

Triggered when Step 1 finds CLAUDE.md > 200 lines.

1. Read the full file.
2. For each bullet, classify:
   - **Keep** — fact the agent cannot infer (command, env var, gotcha).
   - **Cut** — self-evident ("write clean code"), standard language
     convention, or duplicates `.editorconfig`/lint config.
   - **Move** — sometimes-relevant; target is `.claude/rules/<topic>.md`
     with `paths:` frontmatter if it's path-scoped, or a skill if it's
     a workflow.
3. Produce the pruned file; show before/after line count and sample
   cuts. Require approval before writing.

## Notes

- **Never put architecture in CLAUDE.md.** Architecture changes; the
  file will rot. Link to an `architecture.md` if needed.
- **Never duplicate what tooling already enforces.** If `eslint.config.js`
  forbids `var`, the CLAUDE.md line "don't use var" is noise.
- **Never add "IMPORTANT:" or "YOU MUST" unless adherence is actually
  failing.** They work by being rare. Overuse nullifies them.
- This skill does not run `/init` for you — `/init` is a Claude Code
  built-in that does codebase scanning. Use it first if the repo is
  large and unfamiliar, then run this skill to prune/refine the result.
