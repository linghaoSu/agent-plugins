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
| `quick` | Docs-only, tests-only, fixture-only, or a small non-behavior diff/PR with no public API/schema, auth, external IO, persistence, destructive action, concurrency, or security-sensitive path. | One same-context checklist over correctness/scope/verification. If it finds issues in a review workflow that would normally modify files, generate a Plannotator modification plan before editing. This is selected intensity, not `degraded-same-context-review`. |
| `standard` | Normal bug fixes, reviewer-comment fixes, or PRs with bounded blast radius, clear intent, and runnable verification. | One multi-angle review round. Capture material findings in a Plannotator modification plan before fixes. After approval, apply only planned critical/high fixes and re-review only angles touched by the change unless it changes public contract, security, data flow, or broad scope. |
| `deep` | Security/auth/secrets, data loss, persistence/migrations, external IO, destructive operations, concurrency, public APIs/schemas, large or mixed diffs, many unresolved review comments, unclear issue coverage, failed checks, or user-forced `--review-depth deep`. | Full multi-agent, multi-angle review. Capture material findings in a Plannotator modification plan before fixes. After approval, apply only planned critical/high fixes, re-run every required angle, then run a holistic/synthesis pass. |

Escalate during review if a lower tier discovers higher-risk behavior. Do not
de-escalate a forced `deep` request.

## Review Finding Severity And Fix Policy

Use exactly five severity labels in review workflows:

| Severity | Meaning | Default handling |
|---|---|---|
| `critical` | A confirmed blocker: data loss/corruption, security exposure, crash, broken primary flow, irreversible side effect, public-contract break, or release gate failure with a concrete path. | Must be in the modification plan and must be fixed after approval. Never defer as low ROI. |
| `high` | A real bug likely to affect a normal user path, public contract, persistence, security posture, or required verification, but not immediately catastrophic. | Must be in the modification plan and fixed after approval unless the Known Issue deferral rule below applies. |
| `medium` | A real but bounded defect, missing edge-case handling, or verification gap that does not block the main path. | Plan only when it is part of the same necessary change or the user asks; otherwise record or defer. |
| `low` | Minor correctness, clarity, or maintainability risk with limited impact. | Usually record only. |
| `nit` | Cosmetic style, naming, formatting, or preference feedback. | Do not plan unless bundled into an already-approved necessary edit. |

Only true bugs, verification blockers, or technical defects can be must-fix.
Style, preference, generalized best-practice advice, speculative cleanup, and
broad nice-to-have suggestions do not enter the must-fix set even if a reviewer
uses strong language. Reclassify or drop them.

### Approved Critical/High Fix Loop

Review workflows with a modification phase still write a concrete Plannotator
modification plan before edits. Once Plannotator approves the plan, or once a
current-conversation bypass records `bypassed-current-conversation`, treat that
approval as the user's authorization that the planned solution is the correct
solution to apply.

After approval:

1. Apply only the plan's in-scope `critical`/`high` bug or
   verification-blocker fixes. Do not apply medium/low/nit cleanup unless it
   is necessary to complete an approved critical/high fix.
2. Re-run the review angles required by the selected intensity and touched
   area. For `deep`, re-run every required angle and the holistic/synthesis
   pass.
3. If fresh review finds new in-scope `critical`/`high` bugs, add them to the
   modification plan. Require Plannotator approval before applying them, unless
   the current-conversation bypass is active; with bypass, record that it
   covers the new plan entries and continue.
4. Repeat until `Remaining critical/high bugs: none` can be recorded.

### Known Issue Deferral Rule

`high` or `medium` findings may be recorded as Known Issues instead of fixed
only when they do not affect the primary path, are extreme or rare edge cases,
or the fix has clearly disproportionate blast radius, regression risk, or
scope for the current task. Each deferral must record severity, ROI rationale,
primary-path impact, and the condition that should trigger a future fix.

Never defer `critical` findings, security exposure, data loss/corruption,
primary-flow regressions, or `high` bugs that affect the main user path.

## Multi-Agent Review Routing

Before launching analysis, review, executor, or synthesis agents:

```yaml
role: coordinator | executor | reviewer | arbiter
capability: routine | reasoning | critical
independent_context: true | false
parallelizable: true | false
```

Never prescribe a model, vendor, coding agent, or host-specific agent type.
Prefer deterministic checks. A `routine` executor requires bounded scope and
runnable acceptance; `reasoning` owns exploration and independent review;
`critical` is reserved for high-risk decisions, conflicts, and arbitration.
Executors do not accept their own work. Permit one revision, then repartition
or raise capability. If the host cannot honor a route, use its best available
mechanism and record `degraded`.

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
   phase, generate a Plannotator modification plan before editing. Do not edit
   before Plannotator approval or `bypassed-current-conversation` approval is
   recorded. After an approved plan is applied, re-run the required angles for
   the selected intensity and continue until no `critical`/`high` bugs remain.
6. Preserve role independence whenever the host supports it.
7. Treat implementation details of the execution mechanism as host-owned.
8. Fall back to same-context review only when reviewer sub-agents are explicitly
   unsupported by the host/runtime, the user explicitly forbids reviewer
   roles, or the selected execution route is explicitly unavailable or at
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
verification to run after applying the plan, deferred Known Issues with ROI
rationale, skipped out-of-scope findings, and any user-owned decisions.

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
- Explicit style-cache refresh always runs full regeneration, asking before overwrite
  unless `--force` is provided.

## GitHub Read-Only Safety

Read-only workflows may use `gh issue view`, `gh issue list`, `gh pr view`,
`gh pr diff`, and `gh api` GET/GraphQL queries to fetch metadata, diffs,
comments, reviews, and thread state.

They must not run commands or API calls that post comments, submit reviews,
change labels, resolve threads, merge, close, push, commit, or otherwise alter
GitHub state unless the skill explicitly owns that mutation and the user asked
for it in the current request.

## Issue Contribution Gate

Issue workflows must separate "worth investigating" from "ready to fix":

1. Scan results rank candidates for human investigation; they do not imply PR
   readiness or permission to edit.
2. A fix-ready issue needs a concrete observed behavior, trigger or repro path,
   expected behavior, and code-path evidence that the bug is present in the
   current checkout.
3. Stop before a fix plan when the issue is vague, already fixed, actively
   claimed, duplicated by an open or closed PR, maintainer-deprioritized, or
   too broad for one narrow change.
4. Recent public claims to work on an issue and duplicate PRs are blockers for
   `fix-issue` handoff unless the user explicitly accepts that risk.
5. Description-mode evaluations that cannot meet the fix-ready bar must return
   `needs_user` with the missing evidence, not a speculative implementation
   plan.

## Multi-Round Adversarial Review Loop

For `review-fix`-style loops:

1. Collect a fresh diff at the start of every iteration.
2. Select and record `review_intensity` before reviewer launch. Honor
   `--review-depth quick|standard|deep` when provided.
3. Review only changed lines and behavior introduced by the current diff.
4. Drop pure style findings in unchanged code.
5. Run every required review angle for the selected intensity. Do not collapse angles into
   one generic review.
6. Do not fix findings before the plan gate. Filter true `critical`/`high`
   bugs and verification blockers into a Plannotator modification plan; record
   eligible deferred `high`/`medium` findings as Known Issues; skip or record
   `low`/`nit` issues unless they are part of the same necessary change.
7. Treat `LGTM` as the clean sentinel per angle. The iteration is clean only
   when all required angles are clean.
8. Stop before edits unless Plannotator approval or
   `bypassed-current-conversation` approval is recorded. Approval authorizes
   only the planned critical/high fix path.
9. After an approved plan is applied, run a fresh review. For `deep`, re-run
   every required angle; for `standard`, re-run affected angles unless risk
   escalated; for `quick`, run targeted confirmation. Continue the approved
   critical/high fix loop until no `critical`/`high` bugs remain.
