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

Launch **two Sonnet agents in parallel**:

**Agent 1 — Static Code Analysis:**
1. Read the project's config files (e.g. `.editorconfig`, `eslint*`, `prettier*`, `tsconfig*`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Makefile`, `package.json`, etc.)
2. Sample 5-8 representative source files from the main directories
3. Analyze and document:
   - Language(s) and framework(s) used
   - Naming conventions (variables, functions, classes, files)
   - Import/module organization patterns
   - Error handling patterns
   - Testing patterns and framework
   - Code organization and directory structure conventions
   - Comment style and documentation conventions
   - Type system usage (if applicable)
   - Common idioms and patterns specific to this codebase

**Agent 2 — Reviewer Preference Mining:**
Extract code style preferences from PR review comments on the last 100 commits:
1. Get the last 100 merge commit PR numbers:
   ```bash
   git log --oneline -100 | grep -oP '#\K[0-9]+' | head -30
   ```
2. For each PR with a number (batch with `gh api` to stay within rate limits), fetch review comments:
   ```bash
   gh api "repos/{owner}/{repo}/pulls/<number>/comments" --jq '.[].body' 2>/dev/null
   gh api "repos/{owner}/{repo}/pulls/<number>/reviews" --jq '.[] | select(.body != "") | .body' 2>/dev/null
   ```
3. Focus on comments that express **style preferences or code conventions**, such as:
   - Requests to rename variables/functions
   - Preferred patterns (e.g. "use X instead of Y", "we prefer...", "nit:")
   - Structural feedback (e.g. "extract this into...", "this should be in...")
   - Error handling preferences
   - Testing expectations
   - Import ordering or grouping requests
4. Ignore comments that are purely about logic, bugs, or feature design
5. Aggregate recurring themes into a ranked list of **Reviewer Preferences** (most frequent first)

### Step 4: Synthesize and Write

After both agents complete, **synthesize** their outputs into a single code style document:
- The static analysis forms the base structure
- The reviewer preferences are added as a dedicated `## Reviewer Preferences` section, with each preference citing the PR(s) where it appeared
- If a reviewer preference contradicts a config file rule, note the conflict — reviewer practice takes precedence over unconfigured defaults
- Add a metadata header to the document:
  ```markdown
  <!-- generated: YYYY-MM-DD | commits-analyzed: <latest-commit-sha> -->
  ```

Create the directory if needed (`mkdir -p`) and write to `<data-dir>/<owner>/<repo>/code-style.md`.

### Step 5: Report

Tell the user:
```
Code style guide updated: ~/.claude/issue-evaluator/<owner>/<repo>/code-style.md
- Static analysis: <N> config files, <M> source files sampled
- Reviewer preferences: <K> preferences from <P> PRs
```

## Notes

- This is the same analysis that `/evaluate-issue` runs on first use, extracted as a standalone command for manual re-generation.
- The metadata comment at the top of the doc is used by `/evaluate-issue` to cheaply check staleness.
