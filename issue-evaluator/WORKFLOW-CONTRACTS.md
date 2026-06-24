# Issue Evaluator Workflow Contracts

Shared contracts for issue-evaluator skills. Individual skills should cite this
file instead of duplicating the full lifecycle text.

## Review Intensity Selection

Before launching reviewers, select a review intensity. Parse optional
`--review-depth quick|standard|deep`; when present, it is a user-forced
override. Record the selected intensity, whether it was auto or forced, and the
reason in the final report. A forced lower depth is allowed, but never claim
deep assurance for it and never skip read-only safety, changed-line scope, or
required deterministic verification gates.

Auto-select the smallest tier that covers the risk:

| Intensity | Use when | Review shape |
|---|---|---|
| `quick` | Docs-only, tests-only, fixture-only, or a small non-behavior diff/PR with no public API/schema, auth, external IO, persistence, destructive action, concurrency, or security-sensitive path. | One same-context checklist over correctness/scope/verification. If it finds issues in a review workflow that would normally modify files, generate a Plannotator modification plan instead of editing. This is selected intensity, not `degraded-same-context-review`. |
| `standard` | Normal bug fixes, reviewer-comment fixes, or PRs with bounded blast radius, clear intent, and runnable verification. | One multi-angle review round. Capture material findings in a Plannotator modification plan instead of applying fixes. After a user-approved plan is applied in a later modification pass, re-review only angles touched by the change unless it changes public contract, security, data flow, or broad scope. |
| `deep` | Security/auth/secrets, data loss, persistence/migrations, external IO, destructive operations, concurrency, public APIs/schemas, large or mixed diffs, many unresolved review comments, unclear issue coverage, failed checks, or user-forced `--review-depth deep`. | Full multi-agent, multi-angle review. Capture material findings in a Plannotator modification plan instead of applying fixes. After a user-approved plan is applied in a later modification pass, re-run every required angle, then run a holistic/synthesis pass. |

Escalate during review if a lower tier discovers higher-risk behavior. Do not
de-escalate a forced `deep` request.

## Multi-Agent Review Routing

Before launching analysis, review, executor, or synthesis agents:

1. Read `PRINCIPLES.md` and apply its runtime-aware routing guidance.
2. Treat invocation of a review workflow as standing authorization to launch
   reviewer and synthesis sub-agents. Do not ask for new multi-agent
   authorization and do not use missing fresh authorization as a fallback
   reason.
3. Select review intensity using the contract above. Use independent reviewer
   agents for `standard` and `deep`; use same-context review only for selected
   `quick` or for recorded degraded fallback.
4. For reviewer-agent rounds, cover at least these angles:
   - correctness / security / regressions
   - repo style / maintainability / scope control
   - requirements, issue, test, or plan traceability
5. A round is clean only when every required angle returns `LGTM` in that
   round. If material findings remain in a review workflow with a modification
   phase, generate a Plannotator modification plan and stop instead of editing
   files. After a user-approved plan, including one approved by
   `bypassed-current-conversation`, is applied in a later modification pass,
   re-run the required angles for the selected intensity.
6. In Claude Code, keep the existing role split only when the host supports it.
7. Outside Claude Code, use the host runtime's native sub-agent mechanism for
   the same roles and do not request Claude-only model names or subagent types.
8. Fall back to same-context review only when reviewer sub-agents are explicitly
   unsupported by the host/runtime, the user explicitly forbids reviewer
   sub-agents, or the selected reviewer/model is explicitly unavailable or at
   capacity. Record `degraded-same-context-review` and the exact reason. Do not
   present the result as independent multi-agent review. Degraded mode still
   preserves the same angles and rounds; it only loses independent agents.
9. For non-review analysis or executor roles, a skill may define a degraded
   main-context fallback, but it must record that the pipeline lost independent
   validation.

The deep-review invariant is independent skeptical review from multiple agents,
multiple angles, and multiple rounds. Same-context review is either selected
`quick` intensity or the recorded degradation path for the explicit unsupported
cases above.

## Output, Token, And Error Contract

Every issue-evaluator skill that reads GitHub metadata, PR diffs, review
comments, logs, or repo-wide data must end with a compact contract block:

```yaml
status: success | needs_user | terminal | degraded
mode: <id | description | read-only-review | comment-triage | scan>
inputs_resolved:
  repo: <owner/repo or local path>
  target: <issue, PR, or scan window>
outputs_written:
  - <local file or worktree path, empty when conversation-only>
skipped:
  - <item>: <reason>
errors:
  - type: retryable | terminal | needs_user | degraded
    message: <actionable sentence>
next_action: <one command or user decision>
truncated: true | false
```

Error categories:

| Type | Meaning |
|---|---|
| `retryable` | A transient command, network, auth-refresh, or rate-limit problem where rerunning may succeed. |
| `terminal` | The workflow cannot safely continue without a different repo state, target, or command result. |
| `needs_user` | The next step requires a user decision, confirmation, or missing business/product context. |
| `degraded` | The workflow continued with a weaker path, such as diff-only review after worktree setup failed. |

Token and size budgets are explicit safety rules, not hints:

- PR diff: default cap 25 changed files and 400 diff lines per file.
- Review comments: default cap 100 inline comments, 100 review summaries, and
  100 issue conversation comments. Prefer unresolved human comments first.
- Issue scan: default cap 100 issues per window and top 15 results in the
  final table.
- Repo search: default cap 20 hits per query and 80 surrounding lines per file.
- Logs and command output: default cap 240 rendered characters per evidence
  item unless a skill-specific fixture needs more.

If a budget is exceeded, set `truncated: true`, state exactly what was omitted,
and provide the continuation query, command, page, or narrower filter in
`next_action`. Never silently truncate data that affects a verdict.

## Review Modification Plan Gate

When a review workflow has a modification phase and material findings remain,
write a concrete Plannotator modification plan before any edits. The plan must
include finding ids, severity, affected files, planned edits, tests or
verification to run after applying the plan, skipped out-of-scope findings, and
any user-owned decisions.

Use this approval order:

1. If the user explicitly enabled current-conversation approval bypass, do not
   run Plannotator. Record `bypassed-current-conversation` as the approval
   source, keep the plan artifact, and continue only through the planned edit
   path.
2. If the `plannotator` CLI is on `PATH`, run
   `plannotator annotate <plan-artifact> --render-html --gate`.
3. Otherwise, use the runtime's Plannotator planning/visual-explainer workflow
   if available.
4. If Plannotator is unavailable, record `Plannotator unavailable`, leave the
   plan artifact in place, and stop without editing.

Bypass is an approval bypass, not a plan bypass. Do not edit before the plan is
written and recorded.

## Code Style Guide Lifecycle

The repo-specific code style guide is the shared context for issue evaluation,
PR review, fix implementation, and review-comment triage.

### Storage Path

Resolve the repo identifier:

```bash
gh repo view --json owner,name --jq '"\(.owner.login)/\(.name)"'
```

If `gh` fails, fall back to the current directory name.

Resolve the plugin data directory:

```bash
MARKETPLACE_PATH=$(cat ~/.claude/settings.local.json | jq -r '.extraKnownMarketplaces["claude-skills"].source.path // empty')
[ -z "$MARKETPLACE_PATH" ] && MARKETPLACE_PATH=$(cat ~/.claude/settings.json | jq -r '.extraKnownMarketplaces["claude-skills"].source.path // empty')
DATA_DIR="$MARKETPLACE_PATH/issue-evaluator/data"
```

The guide path is:

```text
<data-dir>/<owner>/<repo>/code-style.md
```

### Freshness Check

The first line should be:

```markdown
<!-- generated: YYYY-MM-DD | commits-analyzed: <sha> -->
```

Treat the guide as stale if the metadata is missing, the sha is not found,
400+ commits have landed since that sha, or the guide is 30+ days old.

### Full Regeneration

Run two analysis roles in parallel:

1. **Static Code Analysis** reads config files and samples representative
   source files. It records language/framework, naming, imports, error
   handling, testing, organization, comments/docs, type-system usage, and local
   idioms.
2. **Reviewer Preference Mining** reads recent PR review comments and reviews
   via read-only `gh api` calls. It extracts recurring style/convention
   preferences such as naming, preferred patterns, structure, error handling,
   testing expectations, and import ordering. It ignores pure logic, bug, or
   feature-design feedback.

Synthesize the outputs into one guide:

- Static analysis is the base structure.
- Reviewer preferences go in `## Reviewer Preferences` with PR citations.
- If reviewer practice conflicts with unconfigured defaults, note the conflict;
  reviewer practice wins.
- Add the metadata header above.
- Create parent directories before writing.

### Use In Skills

- First-use skills generate the guide if absent.
- Review skills extract a compact checklist of at most 15 rules before
  launching style reviewers.
- Stale guides may be regenerated in the background when the current workflow
  can proceed safely with the old guide.
- `update-code-style` always runs full regeneration, asking before overwrite
  unless `--force` is provided.

## GitHub Read-Only Safety

Read-only workflows may use `gh issue view`, `gh issue list`, `gh pr view`,
`gh pr diff`, and `gh api` GET/GraphQL queries to fetch metadata, diffs,
comments, reviews, and thread state.

They must not run commands or API calls that post comments, submit reviews,
change labels, resolve threads, merge, close, push, commit, or otherwise alter
GitHub state unless the skill explicitly owns that mutation and the user asked
for it in the current request.

## Multi-Round Adversarial Review Loop

For `review-fix`-style loops:

1. Collect a fresh diff at the start of every iteration.
2. Select and record `review_intensity` before reviewer launch. Honor
   `--review-depth quick|standard|deep` when provided.
3. Review only changed lines and behavior introduced by the current diff.
4. Drop pure style findings in unchanged code.
5. Run every required review angle for the selected intensity. Do not collapse angles into
   one generic review.
6. Do not fix findings inside the review workflow. Filter kept criticals and
   warnings into a Plannotator modification plan; skip or record nits unless
   they are part of the same necessary change.
7. Treat `LGTM` as the clean sentinel per angle. The iteration is clean only
   when all required angles are clean.
8. Stop after presenting the plan and approval status. Only a later
   user-approved modification pass, including one approved by
   `bypassed-current-conversation`, may apply the planned edits.
9. After an approved plan is applied, run a fresh review. For `deep`, re-run
   every required angle; for `standard`, re-run affected angles unless risk
   escalated; for `quick`, run targeted confirmation.
