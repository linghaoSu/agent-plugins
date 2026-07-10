---
name: install-precommit-hook
description: Install the bundled secret scanner as a repo-local native Git pre-commit hook or pre-commit framework entry, with overwrite safety, smoke testing, and uninstall instructions.
---

# Install Pre-commit Hook

This mutates repo-local hook/config files. Require explicit installation intent;
never change global Git config or overwrite an existing hook silently.

## Workflow

1. Confirm Git root, clean understanding of current changes, bundled scanner,
   Python availability, and requested mode: native or pre-commit framework.
2. Inspect `.git/hooks/pre-commit`, `.pre-commit-config.yaml`, existing scanner
   copies, and repo instructions. If a target exists, show the conflict and ask
   whether to integrate, replace, or stop.
3. Copy the deterministic scanner into `.secret-scanner/scan.py` and preserve
   executable permissions. Do not copy caches or environment files.
4. Native mode: create a small hook that invokes the copied scanner in staged
   mode and propagates its exit code. Integrate with an existing hook only after
   approval and preserve its behavior.
5. Framework mode: add one local hook entry without reformatting or reordering
   unrelated configuration. Preserve existing stages and language settings.
6. Smoke-test scanner help and a safe staged-fixture path without committing.
   If the hook blocks on pre-existing staged content, report the findings rather
   than weakening it.
7. Show the exact installed files, how to run manually, and precise uninstall
   steps. Do not stage or commit the installation.

Stop on ownership ambiguity, unsupported framework shape, missing runtime, or
an existing hook the user has not authorized changing.

The installed hook runs the same engine as `$secret-scanner:scan-secrets`.
