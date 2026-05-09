# Design Review - Repo-Wide Plugin Release Gates

**Slug:** ITS-ROADMAP-001
**Date:** 2026-05-09
**Reviewer:** main-context runtime-aware adversarial reviewer fallback + self-review
**Iterations:** 2
**Result:** clean

## Issues Raised & Resolution

| # | Severity | Issue | Resolution |
|---|---|---|---|
| 1 | critical | `--mode staged` specified `git diff --check`, which would miss staged whitespace errors because it checks the unstaged diff by default. | Fixed in `architecture.md` by making `diff-whitespace` mode-specific: staged uses `git diff --cached --check`, working uses `git diff --check`, and all uses `git diff --check HEAD`. |
| 2 | critical | Push/release usage was ambiguous. A default staged gate can pass after commit while scanning no committed secret changes. | Fixed by documenting default `staged`, explicit `working` and `all` usage, and the limitation that a future `--range <base..head>` mode may be needed for unpushed commits. |
| 3 | warning | Skill frontmatter validation contradicted itself: it required a local parser, then later recommended only structural validation. | Fixed by making first-stage blocking validation structural only: frontmatter delimiters plus non-empty `name` and `description`; full YAML parsing is deferred until a parser dependency is chosen deliberately. |
| 4 | warning | `secret-scan` was described as a shell command, but not as a captured check. With `set -e`, findings could terminate before the gate prints its grouped report. | Fixed by requiring the release gate to capture scanner stdout/stderr and translate scanner exit code into a blocking result with redacted evidence. |
| 5 | warning | `--json` output was too underspecified for future eval fixtures. | Fixed by defining a stable `checks[]` schema with `id`, `category`, `status`, `message`, `evidence`, `command`, and `exit_code`, plus allowed statuses. |
| 6 | warning | Runtime wording and hook robustness advisories were broad enough to become noisy. | Fixed by narrowing runtime wording to targeted stale phrases and scoping hook robustness to selected changed hook files, with full `antifragile-agent` as a manual handoff. |

## Residual Open Issues

None blocking. Product decisions remain documented in `architecture.md` with recommendations:

- Whether `secret-scan` should stay blocking for staged changes from the first implementation.
- Whether `--mode all` should be used before every push or only release hardening.
- Whether full YAML parsing should become blocking later.

## Reviewer's Final Verdict

LGTM

## Self-Review Notes

The chosen Option B still fits the requirements after revision. The design now
has concrete mode semantics, deterministic blocking/advisory boundaries, and a
JSON contract that can support the future ITS-ROADMAP-006 fixtures. The staged
implementation remains design-only and does not introduce hooks, CI, or
production scripts in this step.
