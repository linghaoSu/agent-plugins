---
name: install-precommit-hook
description: Install secret-scanner as a repo-local git pre-commit hook, with overwrite confirmation and native or pre-commit framework modes.
argument-hint: '[--framework native|pre-commit] [--abort-on-findings|--warn-only]'
allowed-tools: [Read, Write, Edit, Bash, Glob]
---

# Install Pre-commit Hook

Wire `secret-scanner/scripts/scan.py` into the current repo's git hooks so
every `git commit` is checked for leaked secrets before the commit lands.

**Changes the user's repo.** This skill writes files inside the repo and
inside `.git/hooks/`. Always show the diff before writing, and always ask
before overwriting an existing hook.

## Arguments

Raw: `$ARGUMENTS`

Parse:
- `--framework native` (default) → classic `.git/hooks/pre-commit` shell
  script. Not version-controlled; each developer runs this skill once.
- `--framework pre-commit` → appends a local hook entry to
  `.pre-commit-config.yaml` for the [pre-commit](https://pre-commit.com)
  framework. Version-controlled; each dev runs `pre-commit install` once.
- `--abort-on-findings` (default) → hook exits non-zero when findings
  are present, blocking the commit.
- `--warn-only` → hook prints findings but always exits 0 (does not
  block). Useful while the team rolls this out.

## Workflow

### Step 1: Sanity check the repo

```bash
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "not a git repo"; exit 2; }
GIT_DIR=$(git rev-parse --git-dir)
REPO_ROOT=$(git rev-parse --show-toplevel)
```

Work from `$REPO_ROOT`. If the working tree is dirty, tell the user —
you're about to add files, which will show up in their next commit.

### Step 2: Copy the scanner into the repo

Self-sufficiency matters: the hook should not depend on a magic Claude
plugin path that other developers may not have. Copy `scan.py` into
`$REPO_ROOT/.secret-scanner/scan.py`.

```bash
mkdir -p "$REPO_ROOT/.secret-scanner"
cp "${CLAUDE_PLUGIN_ROOT}/scripts/scan.py" "$REPO_ROOT/.secret-scanner/scan.py"
chmod +x "$REPO_ROOT/.secret-scanner/scan.py"
```

Tell the user what you did and whether to commit `.secret-scanner/`:
- **Commit it** if the team should share the same scanner version.
- **Gitignore it** (`echo '.secret-scanner/' >> .gitignore`) if each dev
  should manage their own copy.

### Step 3a: Native git hook

Target: `$GIT_DIR/hooks/pre-commit`.

1. If the file does **not** exist: write the template below, `chmod +x`,
   and tell the user.
2. If it **does** exist: read it, show it to the user, and offer:
   a. **Abort** — do nothing, user will merge manually.
   b. **Append** — add the scanner invocation to the existing script.
      Only do this if the existing script is a plain shell script with
      a shebang.
   c. **Back up and replace** — rename the existing hook to
      `pre-commit.bak` and install a fresh one.
   Never silently overwrite.

Template (abort-on-findings variant):

```bash
#!/bin/sh
# Installed by secret-scanner/install-precommit-hook
# See .secret-scanner/scan.py
set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
SCAN="$REPO_ROOT/.secret-scanner/scan.py"

if [ ! -x "$SCAN" ]; then
    echo "secret-scanner: $SCAN missing or not executable — skipping"
    exit 0
fi

if ! python3 "$SCAN" --mode staged; then
    echo ""
    echo "secret-scanner: findings in staged changes. Review above."
    echo "  • rotate any real credentials before anything else"
    echo "  • unstage the file: git restore --staged <file>"
    echo "  • re-scan: python3 $SCAN --mode staged --reveal"
    echo "  • bypass (NOT RECOMMENDED): git commit --no-verify"
    exit 1
fi
```

For the warn-only variant, replace the `if ! python3 …` block with:

```bash
python3 "$SCAN" --mode staged || true
```

### Step 3b: pre-commit framework hook

Target: `$REPO_ROOT/.pre-commit-config.yaml`.

1. Check whether the file exists. If not, ask before creating it — a new
   `.pre-commit-config.yaml` commits the whole team to the pre-commit
   workflow.
2. Append a local hook entry (do not modify existing repos/hooks):

```yaml
repos:
  # … existing entries …
  - repo: local
    hooks:
      - id: secret-scanner
        name: secret-scanner (staged)
        entry: python3 .secret-scanner/scan.py --mode staged
        language: system
        pass_filenames: false
        stages: [commit]
```

3. Tell the user to run `pre-commit install` so the hook is registered.
4. If `.secret-scanner/` is gitignored, the pre-commit framework runs in
   a clean clone (CI) and will not find the script. Recommend committing
   `.secret-scanner/scan.py` in this setup.

### Step 4: Smoke test

After installing, run a dry-run to make sure the wiring works:

```bash
python3 "$REPO_ROOT/.secret-scanner/scan.py" --mode staged
```

If it exits cleanly with "no findings" or "0 findings", you're good.
Then simulate the hook:

```bash
"$GIT_DIR/hooks/pre-commit"
```

(For pre-commit framework: `pre-commit run --all-files secret-scanner`.)

### Step 5: Tell the user what was installed

One-line summary:

```
installed: .secret-scanner/scan.py, .git/hooks/pre-commit
mode:      abort-on-findings | warn-only
framework: native | pre-commit
next:      (if pre-commit) run `pre-commit install`
           (always) optionally commit .secret-scanner/ for the team
           to `git commit --no-verify` bypasses this hook, by design
```

## Uninstall

Not automated. To remove:

```bash
rm -f "$(git rev-parse --git-dir)/hooks/pre-commit"      # native
# or edit .pre-commit-config.yaml to drop the entry       # framework
rm -rf .secret-scanner
```

## Notes

- **Never `--no-verify` silently.** If you're adding noise, fix the
  regex or the false positive; don't route around the hook.
- **Redaction is on.** The hook output uses the default redacted preview
  so terminal scrollback doesn't get a plaintext secret.
- **Not a CI replacement.** A local hook is easily bypassed. For CI,
  run `gitleaks` / `trufflehog` with a tuned config in addition to this.
- This skill does not configure the scanner itself (add custom patterns,
  extend skip lists). Edit `.secret-scanner/scan.py` directly for that.
