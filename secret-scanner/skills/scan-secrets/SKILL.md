---
name: scan-secrets
description: Deterministically scan staged, working, recent, ranged, or full-repo content for leaked credentials, then classify likely fixtures and false positives. Read-only.
---

# Scan Secrets

Run the bundled `../../scripts/scan.py`; never print full secret values, edit
files, clean history, commit, push, revoke, or rotate credentials.

## Workflow

1. Resolve exactly one mode: staged default, working, recent, range, or all.
   Verify repo and scanner availability. Treat full-repo/history scans as
   explicit only because they are slower and noisier.
2. Run the deterministic scanner with bounded output. Preserve its redaction;
   never re-open matching values merely to display them.
3. Classify findings as confirmed leak, documented placeholder/test fixture, or
   ambiguous. Use path, variable name, entropy, format, comments, and known
   fixture directories; do not dismiss a valid-format secret solely because it
   appears in a test.
4. Report type, redacted prefix, path/line, tracked/staged status, confidence,
   and containment advice. For confirmed exposure, recommend revoke/rotate,
   remove from current content, assess history, and notify the owner through
   approved channels.

Exit nonzero scanner results are findings, not tool failure. Distinguish parse,
permission, and execution errors. Ask before any remediation; this skill is
strictly read-only.

Use `$secret-scanner:install-precommit-hook` only when prevention is explicitly requested.
