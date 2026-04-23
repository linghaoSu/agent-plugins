---
name: scan-secrets
description: Scan git-changed files or the whole project for leaked secrets - AWS/GitHub/Stripe/OpenAI/Anthropic/Slack/Google/Twilio/SendGrid keys, private keys, JWTs, DB connection strings, and password/token assignments. Deterministic regex scanner plus LLM-assisted false-positive triage. Read-only; never modifies your repo.
argument-hint: '[--mode staged|working|head|range|all] [--base <ref>] [--reveal] [paths...]'
allowed-tools: [Read, Bash, Grep, Glob]
---

# Scan Secrets

Catch credential leaks **before** they land in `git log` forever. Runs a
deterministic Python scanner first, then uses context to demote false
positives. Read-only: this skill never rewrites files or rewrites history.

## Arguments

Raw: `$ARGUMENTS`

Parse:
- `--mode <staged|working|head|range|all>` → what to scan. Default `staged`
  (the files you're about to commit).
  - `staged` — `git diff --cached` (index vs HEAD)
  - `working` — `git diff` **plus untracked files** (catches brand-new
    `.env` that hasn't been `git add`ed yet)
  - `head` — last commit (`HEAD~1..HEAD`)
  - `range` — requires `--base <ref>`, optional `--head <ref>` (default `HEAD`)
  - `all` — every tracked + untracked file in the project (first-time
    audit; slower, bigger output)
- `--reveal` → print full matched secrets *and* unredacted context.
  **Default is redacted** (`abcd…wxyz` in both preview and context) so
  the secret doesn't get pasted into chat logs, JSON output, or screenshots.
- `--full-file` → scan entire files, not only added lines. For
  `staged`/`head`/`range`, content is read from the git object (`git show`)
  so post-`git add` worktree edits cannot hide a staged secret. For
  `working`/`all` the worktree is the source of truth, as expected.
- Remaining tokens → optional path filters.

## Workflow

### Step 1: Sanity check the repo

```bash
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
  echo "not a git repo"; exit 2;
}
```

If the user asked for `head` mode but only one commit exists, say so and
offer to scan the working tree instead.

### Step 2: Run the scanner

Use the bundled Python scanner — it's deterministic and its regexes are
tuned for a low false-positive rate on diff-only scans.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/scan.py" \
    --mode <mode> \
    [--base <ref>] [--head <ref>] \
    [--full-file] [--reveal] \
    --format json \
    [-- path ...]
```

If the script isn't runnable (non-POSIX env, no Python 3), fall back to
Grep-based scanning with the pattern table in the "Pattern reference"
section below — but say so, so the user knows the coverage is reduced.

### Step 3: Triage findings

The scanner already flags `likely_false_positive: true` for lines that
contain words like `example`, `dummy`, `placeholder`, `change-me`,
`your-key-here`. That's a coarse filter. Apply a finer one:

For each finding, read 5–10 lines of surrounding context (use Read with
line offsets) and classify:

| Verdict | Meaning | Action |
|---------|---------|--------|
| **CONFIRMED_LEAK** | Looks like a real live credential | Block; escalate to rotation |
| **TEST_FIXTURE** | Test/spec file, clearly synthetic | Allow; optionally add to ignore |
| **PLACEHOLDER** | Matches a known placeholder pattern (`xxx`, `AKIAIOSFODNN7EXAMPLE`, `ghp_<fill-me-in>`) | Allow |
| **AMBIGUOUS** | Cannot tell without asking | Ask the user |

Rules of thumb:
- `AKIAIOSFODNN7EXAMPLE` is the AWS docs example key → **PLACEHOLDER**.
- `sk_test_*` is a Stripe test key → still report, but lower severity
  (test keys can still be rate-limit-abused).
- A secret in a file under `test/`, `tests/`, `spec/`, `__tests__/`,
  `fixtures/`, `examples/`, or `docs/` with a synthetic look → **TEST_FIXTURE**.
- A secret in a `.env`, `config.yaml`, `settings.json`, or similar that
  *isn't* gitignored → **CONFIRMED_LEAK** until proven otherwise.
- Generic `password = "hunter2"` in application code → **CONFIRMED_LEAK**.
- Generic `PASSWORD = os.environ["PASSWORD"]` → **PLACEHOLDER** (it's
  reading, not assigning a literal).

### Step 4: Report

Print a table to stdout (do not write a file unless asked):

```
# Secret scan — <N> finding(s), <K> after triage

## Confirmed leaks (K)
<file>:<line>  <pattern>  <redacted-preview>
  context: <trimmed line>
  ↳ why real: <1-line reasoning — why this isn't a fixture>
  ↳ action:  rotate + remove from history (see git filter-repo / BFG)

## Test fixtures / placeholders (N - K)
(collapsed by default; list only if user asks or if count < 5)

## Ambiguous — needs you to look
<file>:<line>  <pattern>  <redacted-preview>
  context: <trimmed line>
  ↳ question: <specific thing blocking classification>
```

### Step 5: Next steps — ask, don't act

If there are confirmed leaks, tell the user what to do, but **do not do
it**:

1. **Rotate first.** Even if you never push, assume compromise once the
   secret hits disk.
2. **Remove from the upcoming commit.** `git restore --staged <file>` +
   edit + re-stage, or use `git commit --amend` if already committed.
3. **Scrub history** if already pushed. Recommend `git filter-repo` or
   BFG; warn that force-pushing rewrites shared history.
4. **Move to a secret store.** `.env` (gitignored), `direnv`, Doppler,
   1Password, Vault, AWS Secrets Manager — pick one.

Never offer to run `git filter-repo`, force-push, or delete files —
these are destructive and the user must drive them.

## Pattern reference

The script catches:

| Name | Pattern summary |
|------|-----------------|
| `aws-access-key` | `AKIA…` / `ASIA…` + 16 chars |
| `github-pat` | `ghp_` / `gho_` / `ghs_` / `ghu_` / `ghr_` + 36+ chars |
| `gitlab-pat` | `glpat-` + 20 chars |
| `stripe-live-key` | `sk_live_` / `rk_live_` + 24+ chars |
| `stripe-test-key` | `sk_test_` + 24+ chars |
| `slack-token` | `xoxb-` / `xoxp-` / `xoxa-` / `xoxr-` / `xoxs-` |
| `openai-key` | `sk-` or `sk-proj-` + 20+ chars (excludes `sk-ant-`) |
| `anthropic-key` | `sk-ant-` + 20+ chars |
| `sendgrid-key` | `SG.` + 22 chars + `.` + 43 chars |
| `twilio-sid` | `AC` / `AK` / `AS` + 32 hex |
| `google-api-key` | `AIza` + 35 chars |
| `jwt` | three base64-url segments separated by `.`, starting `eyJ` |
| `private-key-header` | `-----BEGIN [TYPE ]PRIVATE KEY-----` |
| `basic-auth-url` | `https://user:pass@host` |
| `db-conn-string` | `{mongodb,postgres,mysql,redis,amqp}://user:pass@host` |
| `generic-secret` | `password\|secret\|api_key\|token = "…"` with 16+ char value |

Skipped paths (too noisy): `node_modules`, `vendor`, `dist`, `build`,
`.next`, `.turbo`, `coverage`, `__pycache__`, `.venv`, etc. Skipped
extensions: `.lock`, `.min.js`, `.map`, images, archives, binaries.

## Notes

- **Redaction is on by default** precisely so we don't echo secrets into
  chat, logs, or screenshots. `--reveal` exists for when the user
  explicitly wants to copy a match.
- **Diff-only scanning is the default** because it matches the question
  "is my next commit safe?" For a whole-repo audit, run with
  `--full-file` and an intentionally broader `--mode`.
- The scanner is **not a replacement for** trufflehog or gitleaks in CI.
  It's designed for the human-in-the-loop pre-commit moment. For CI,
  install gitleaks with a tuned config.
- If the same secret appears multiple times across files, treat it as
  one incident — rotating once fixes all copies.
- To install this as a git pre-commit hook, run `/install-precommit-hook`.
  That skill copies `scan.py` into `.secret-scanner/` in the repo and
  wires `.git/hooks/pre-commit` (or a `.pre-commit-config.yaml` entry).
