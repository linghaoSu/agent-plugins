# secret-scanner

Catch leaked credentials **before** they land in `git log` forever. Runs a
deterministic regex scanner over the diff of your upcoming commit (or any
range you specify), then applies LLM judgment to demote obvious false
positives — test fixtures, placeholders, env-var references.

Read-only. Never modifies your repo, never runs destructive git commands.

## Commands

### `/scan-secrets [--mode <scope>] [--reveal] [paths...]`

Scans files for secrets and reports findings grouped by severity.

Modes:
- `staged` (default) — `git diff --cached`; what your next commit contains
- `working` — `git diff` **plus untracked files**; uncommitted work (catches
  brand-new `.env` before `git add`)
- `head` — last commit (`HEAD~1..HEAD`)
- `range` — arbitrary range, requires `--base <ref>` and optional `--head <ref>`
- `all` — every tracked + untracked file in the project (first-time audit)

Flags:
- `--reveal` — print full matched secrets and unredacted context (default:
  both redacted)
- `--full-file` — scan entire changed files, not only added lines. For
  `staged`/`head`/`range` this reads from the git object (index / commit
  blob) so post-`git add` worktree edits cannot hide a staged secret.

### `/install-precommit-hook [--framework native|pre-commit] [--warn-only]`

Install the scanner as a git pre-commit hook. Copies `scan.py` into
`.secret-scanner/` in the repo so the hook is self-sufficient, then wires
either `.git/hooks/pre-commit` (native) or a `.pre-commit-config.yaml`
entry (pre-commit framework). Never overwrites an existing hook without
asking.

## What it catches

Deterministic regex for:
- **Cloud provider keys** — AWS (`AKIA…`, `ASIA…`), Google (`AIza…`)
- **VCS tokens** — GitHub (`ghp_/gho_/ghs_/ghu_/ghr_`), GitLab (`glpat-`)
- **Payment / messaging** — Stripe (`sk_live_`, `sk_test_`, `rk_live_`),
  Slack (`xox[baprs]-`), Twilio (`AC…`, `AK…`, `AS…`), SendGrid (`SG.…`)
- **AI API keys** — OpenAI (`sk-…`, `sk-proj-…`), Anthropic (`sk-ant-…`)
- **JWTs** — `eyJ...eyJ....`
- **Private keys** — `-----BEGIN [RSA|EC|…] PRIVATE KEY-----`
- **Connection strings** — `postgres://user:pass@host`, `mongodb+srv://…`,
  basic-auth URLs
- **Generic** — `password`/`secret`/`api_key`/`token` = "…" with 16+ char
  literal value

## Why this plugin instead of just `gitleaks` / `trufflehog`

This is the **human-in-the-loop pre-commit** tool. It's for the moment
when you're about to `git commit` and want a fast check that understands
*your* context — "this is a test fixture", "that's documented placeholder
key". It's **not** a replacement for `gitleaks` in CI; run both.

Key differences from raw `grep` / vanilla `gitleaks`:

- **Diff-only by default.** Scans *added* lines in the current change,
  not the whole repo. Long-standing legacy matches don't swamp output.
- **Redacted by default.** Findings are truncated to `abcd…wxyz` so the
  secret isn't pasted back into chat or logs. Use `--reveal` when needed.
- **LLM-assisted triage.** After the deterministic scan, the skill reads
  surrounding context and classifies each match as CONFIRMED_LEAK,
  TEST_FIXTURE, PLACEHOLDER, or AMBIGUOUS.
- **Read-only.** Never runs `git filter-repo`, never force-pushes, never
  deletes files. Recommends those steps for the user to execute.

## Layout

```
secret-scanner/
├── .claude-plugin/plugin.json
├── README.md
├── scripts/scan.py                              # deterministic scanner, runnable standalone
├── skills/scan-secrets/SKILL.md                 # /scan-secrets
└── skills/install-precommit-hook/SKILL.md       # /install-precommit-hook
```

The script is self-contained and usable without Claude Code:

```bash
python3 secret-scanner/scripts/scan.py --mode staged --format json
```

Exit codes: `0` no findings, `1` findings present, `2` usage error.

## Wiring as a pre-commit hook

Run `/install-precommit-hook` to do it safely. The skill:

1. Copies `scan.py` to `.secret-scanner/scan.py` in the repo (so the hook
   is not tied to a Claude plugin path).
2. Writes `.git/hooks/pre-commit` (or appends to `.pre-commit-config.yaml`
   with `--framework pre-commit`).
3. Refuses to overwrite an existing hook without asking.

Uninstall: delete `.git/hooks/pre-commit` and `.secret-scanner/`.

## Limitations

- Does not detect entropy-based secrets without a known prefix (e.g., a
  random 40-char string with no keyword nearby won't trigger).
- Does not reach into encrypted archives, binary files, or minified JS.
- The `generic-secret` pattern is opinionated and may miss custom
  naming (`SECRET_FOO_BAR`) — add patterns by editing `scripts/scan.py`
  if you need broader coverage.
- No built-in allowlist file yet; false positives are handled per-run
  via LLM triage. For CI, use `gitleaks` with a `.gitleaksignore`.
