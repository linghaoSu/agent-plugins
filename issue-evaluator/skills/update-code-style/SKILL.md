---
name: update-code-style
description: Regenerate the code style guide for the current repo by analyzing code and PR review comments
argument-hint: '[--force]'
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent]
---

# Update Code Style Guide

Regenerate the code style guide for the current repo. This runs the full analysis (static code analysis + reviewer preference mining) regardless of whether a guide already exists.

## Arguments

Raw arguments: `$ARGUMENTS`

- `--force`: Skip confirmation and overwrite directly.

## Runtime-Aware Agent Routing

Before launching analysis agents, read `../../PRINCIPLES.md` and
`../../WORKFLOW-CONTRACTS.md`. Apply the shared **Runtime-Aware Agent Routing**
contract and the **Code Style Guide Lifecycle** contract.

## Workflow

### Step 1: Determine Storage Path

```bash
# Get repo identifier
gh repo view --json owner,name --jq '"\(.owner.login)/\(.name)"'
```
If `gh` fails, fall back to the current directory name.

```bash
# Resolve this plugin's source data directory
MARKETPLACE_PATH=$(cat ~/.claude/settings.local.json | jq -r '.extraKnownMarketplaces["claude-skills"].source.path // empty')
[ -z "$MARKETPLACE_PATH" ] && MARKETPLACE_PATH=$(cat ~/.claude/settings.json | jq -r '.extraKnownMarketplaces["claude-skills"].source.path // empty')
DATA_DIR="$MARKETPLACE_PATH/issue-evaluator/data"
```

The file is at `<data-dir>/<owner>/<repo>/code-style.md`.

### Step 2: Confirm Overwrite

If the file already exists and `--force` is not specified, show the user:
- File path
- Last modified date (`stat` the file)
- Ask: "Code style guide already exists (last updated: <date>). Overwrite? [Y/n]"

If user declines, abort.

### Step 3: Run Full Analysis

Apply `../../WORKFLOW-CONTRACTS.md` § Code Style Guide Lifecycle / Full
Regeneration. Launch the Static Code Analysis and Reviewer Preference Mining
roles in parallel, then synthesize their outputs into the guide with the
required metadata header.

### Step 4: Synthesize and Write

Create the directory if needed (`mkdir -p`) and write the regenerated guide to
`<data-dir>/<owner>/<repo>/code-style.md`.

### Step 5: Report

Tell the user:
```
Code style guide updated: ~/.claude/issue-evaluator/<owner>/<repo>/code-style.md
- Static analysis: <N> config files, <M> source files sampled
- Reviewer preferences: <K> preferences from <P> PRs
```

## Notes

- This is the same analysis that `/evaluate-issue` runs on first use, extracted as a standalone command for manual re-generation.
- The metadata comment at the top of the doc is used by `/evaluate-issue` and PR review skills to cheaply check staleness.
