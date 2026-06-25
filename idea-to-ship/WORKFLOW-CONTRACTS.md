# Idea-To-Ship Workflow Contracts

Shared contracts for idea-to-ship skills. Skills should cite this file for
cross-cutting runtime behavior while preserving their stage-specific gates.

## Review Intensity Selection

Before launching reviewers, select a review intensity. Parse optional
`--review-depth quick|standard|deep`; when present, it is a user-forced
override. Record the selected intensity, whether it was auto or forced, and the
reason in the review artifact. A forced lower depth is allowed, but never claim
deep assurance for it and never skip required deterministic verification gates.

Auto-select the smallest tier that covers the risk:

| Intensity | Use when | Review shape |
|---|---|---|
| `quick` | Docs-only, tests-only, fixture-only, generated artifact updates, or a small non-behavior diff with no public API/schema, UI, auth, external IO, persistence, destructive action, agent loop, or release-critical change. | One same-context checklist over correctness/scope/verification. If it finds issues in a review workflow that would normally modify files, generate a Plannotator modification plan before editing. This is selected intensity, not `degraded-same-context-review`. |
| `standard` | Normal behavior changes with bounded blast radius, clear requirements, and runnable verification. | One multi-angle review round. Capture material findings in a Plannotator modification plan before fixes. After approval, apply only planned critical/high fixes and re-review only angles touched by the change unless it changes architecture, public contract, security, data flow, or broad scope. |
| `deep` | Security/auth/secrets, data loss, persistence/migrations, external IO, destructive operations, concurrency, agent/harness loops, public APIs/schemas, large or mixed diffs, UI requiring visual evidence, failed release gates, unclear requirements, or user-forced `--review-depth deep`. | Full multi-agent, multi-angle review. Capture material findings in a Plannotator modification plan before fixes. After approval, apply only planned critical/high fixes, re-run every required angle, then run a holistic pass. |

Escalate during review if a lower tier discovers higher-risk behavior. Do not
de-escalate a forced `deep` request.

## Review Finding Severity And Fix Policy

Use exactly five severity labels in review workflows:

| Severity | Meaning | Default handling |
|---|---|---|
| `critical` | A confirmed blocker: data loss/corruption, security exposure, crash, irreversible side effect, broken primary flow, invalid architecture recommendation, or release gate failure with a concrete path. | Must be in the modification plan and must be fixed after approval. Never defer as low ROI. |
| `high` | A real bug or design defect likely to affect a normal user path, public contract, persistence, security posture, or required verification, but not immediately catastrophic. | Must be in the modification plan and fixed after approval unless the Known Issue deferral rule below applies. |
| `medium` | A real but bounded defect, missing edge-case handling, or verification gap that does not block the main path. | Plan only when it is part of the same necessary change or the user asks; otherwise record or defer. |
| `low` | Minor correctness, clarity, or maintainability risk with limited impact. | Usually record only. |
| `nit` | Cosmetic style, naming, prose, formatting, or preference feedback. | Do not plan unless bundled into an already-approved necessary edit. |

Only true bugs, verification blockers, or technical design defects can be
must-fix. Style, preference, generalized best-practice advice, speculative
cleanup, and broad nice-to-have suggestions do not enter the must-fix set even
if a reviewer uses strong language. Reclassify or drop them.

### Approved Critical/High Fix Loop

Review workflows with a modification phase still write a concrete Plannotator
modification plan before edits. Once Plannotator approves the plan, or once a
current-conversation bypass records `bypassed-current-conversation`, treat that
approval as the user's authorization that the planned solution is the correct
solution to apply.

After approval:

1. Apply only the plan's in-scope `critical`/`high` bug, verification-blocker,
   or design-defect fixes. Do not apply medium/low/nit cleanup unless it is
   necessary to complete an approved critical/high fix.
2. Re-run the review angles required by the selected intensity and touched
   area. For `deep`, re-run every required angle and the holistic pass.
3. If fresh review finds new in-scope `critical`/`high` bugs or design defects,
   add them to the modification plan. Require Plannotator approval before
   applying them, unless the current-conversation bypass is active; with bypass,
   record that it covers the new plan entries and continue.
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

For design and code review loops:

1. Read `PRINCIPLES.md` before launching a reviewer.
2. Select review intensity using the contract above. Use runtime-native
   reviewer agents for `standard` and `deep`; use same-context review only for
   selected `quick` or for recorded degraded fallback.
3. Cover at least two angles whenever reviewer agents run:
   - correctness / failure modes / security
   - traceability / testability / implementation fit
   Add a UI/UX/accessibility angle when `interface-design.md` is present or the
   diff touches UI.
4. Treat invocation of a design or code review workflow as standing
   authorization to launch reviewer sub-agents. Use sub-agents when the host
   supports them unless the user explicitly forbids delegation. In Claude Code,
   keep the Codex adversarial reviewer (`subagent_type: "codex:codex-rescue"`)
   when available. Outside Claude Code, do not request Claude-only subagent
   types; use the host runtime's native reviewer agents for the same roles.
5. Fall back to same-context review only when reviewer sub-agents are
   explicitly unsupported by the host/runtime, the user explicitly forbids
   reviewer sub-agents, or a selected reviewer/model is explicitly unavailable
   or at capacity. Record `degraded-same-context-review` and the exact reason
   in the review artifact. Do not present the result as independent multi-agent
   review. Degraded mode still preserves the same angles and rounds; it only
   loses independent agents.
6. A review can return clean only after every required reviewer angle for the
   selected intensity has returned `LGTM`. If material findings remain in a
   review workflow with a modification phase, generate a Plannotator
   modification plan before editing. Do not edit before Plannotator approval
   or `bypassed-current-conversation` approval is recorded.

The deep-review invariant is independent skeptical review from multiple agents,
multiple angles, and multiple rounds. Same-context review is either selected
`quick` intensity or the recorded degradation path for the explicit unsupported
cases above.

## Output, Token, And Error Contract

Idea-to-ship skills that read requirements, architecture, diffs, test output,
commercial evidence, roadmap candidates, UI references, or review transcripts
must end with a compact contract block:

```yaml
status: success | needs_user | terminal | degraded
mode: <brainstorm | architecture | roadmap | tdd | test | review | implement>
inputs_resolved:
  slug: <slug>
  artifacts: <requirements/architecture/test-plan/etc.>
outputs_written:
  - <artifact or source file path>
skipped:
  - <item>: <reason>
errors:
  - type: retryable | terminal | needs_user | degraded
    message: <actionable sentence>
next_action: <one command, skill, or decision>
truncated: true | false
```

Error categories:

| Type | Meaning |
|---|---|
| `retryable` | A transient command, render, test, network, or evidence-fetch failure. |
| `terminal` | A required upstream artifact is missing or the stage cannot continue safely. |
| `needs_user` | Product intent, priority approval, destructive overwrite, or scope needs a human decision. Route through Human Approval Routing when available. |
| `degraded` | The workflow continued with partial evidence, missing optional tools, or same-context review fallback. |

Default token budget unless a skill declares a stricter one:

- Artifact reads: summarize after 300 lines per artifact unless exact text is
  needed for an edit.
- Diff/source reads: 25 files and 400 changed lines per file.
- Roadmap/commercial evidence: 30 candidates, 10 sources per candidate, and a
  one-sentence source anchor in the final artifact.
- Review transcripts: 5 rounds and 100 findings/comments per round.
- Test output: include failing test names and first actionable stack frame;
  omit repetitive logs.

If data exceeds the budget, set `truncated: true`, name omitted artifacts,
files, candidates, or logs, and put the continuation command or next skill in
`next_action`.

## Review Loop Shape

1. Verify required artifacts first. Missing `requirements.md` sends the user
   back to `/brainstorm --slug <slug>`.
2. Select and record `review_intensity` before reviewer launch. Honor
   `--review-depth quick|standard|deep` when provided.
3. Collect the current target (`architecture.md` or diff) fresh each iteration.
4. Treat `LGTM` as the clean sentinel only per reviewer angle; the round is
   clean only when all required angles are clean.
5. Do not fix findings before the plan gate. Filter true `critical`/`high`
   bugs, verification blockers, and design defects into a Plannotator
   modification plan; record eligible deferred `high`/`medium` findings as
   Known Issues; skip or record `low`/`nit` issues unless they are part of the
   same necessary change.
6. Stop before edits unless Plannotator approval or
   `bypassed-current-conversation` approval is recorded. Approval authorizes
   only the planned critical/high fix path.
7. After an approved plan is applied, run a fresh review. For `deep`, re-run
   every required reviewer angle; for `standard`, re-run affected angles unless
   risk escalated; for `quick`, run targeted confirmation. Continue the
   approved critical/high fix loop until no `critical`/`high` bugs or design
   defects remain.

## Human Approval Routing

When a phase gate needs human confirmation, approval, or a user-owned decision,
route the decision through Plannotator first when a Plannotator gate is
available in the current runtime, unless the user has enabled the
current-conversation bypass. This includes architecture/design approval,
roadmap priority approval, overwrite approval, residual-risk acceptance, visual
baseline approval, scope/deviation decisions, and continue/stop decisions
between implementation stages.

### Current-Conversation Bypass

Support a fast approval bypass for the current conversation only. If the user
explicitly says to skip approvals for this conversation/thread/session (for
example, "skip all approvals in this conversation" or "本对话跳过所有审批"),
do not run Plannotator gates or stop for Human Approval Routing decisions for
the rest of this conversation unless the user revokes the bypass.

Bypass rules:

- Treat the bypass as user approval for Human Approval Routing gates only.
- For review workflows with a modification phase, bypass skips the
  Plannotator approval gate only. It does not skip writing the modification
  plan before edits.
- Record every skipped gate as `bypassed-current-conversation`, with the
  decision source `user requested approval bypass in current conversation`.
- Do not persist the bypass to repo files, config, goals, or future
  conversations.
- Do not infer bypass from vague urgency such as "go fast" or "don't ask too
  much"; require an explicit skip-approval instruction.
- Do not use the bypass to override required upstream artifacts, deterministic
  verification, review loops, policy constraints, or the Cross-Skill Routing
  safety boundary for code/git/GitHub/GitLab/deployment/credential/external
  system mutations.

Use this order:

1. Check whether current-conversation bypass is active. If active, record the
   bypass and continue without Plannotator or a direct user question.
2. Check availability: a Plannotator skill/workflow that supports gated
   annotation is present, or the `plannotator` CLI is available on `PATH`.
3. Prepare a concrete approval artifact instead of an open-ended prompt. Use
   the stage artifact itself when it contains the decision context; otherwise
   write a short sibling `*.approval.md` artifact. Include: decision needed,
   options, recommended option, tradeoffs/risks, affected artifact paths, and
   the exact next action if approved.
4. Run Plannotator as the approval gate:
   - Plain markdown: `plannotator annotate <artifact> --gate`
   - Rendered design/proposal review when supported:
     `plannotator annotate <artifact> --render-html --gate`
5. Wait up to 30 minutes (1800 seconds) for a usable Plannotator decision. Do
   not treat a one-minute delay as a timeout. If no usable decision is returned
   within 30 minutes, interrupt the specific Plannotator gate process when
   possible, record `Plannotator attempted, no decision returned`, and fall
   back to direct user confirmation only when the approval decision is still
   required before continuing.
6. If denied, revise from the feedback and re-gate. Stop with `needs_user` if
   the denial changes product scope or requires a decision the artifact cannot
   settle.
7. Record the approval source, date, decision, and artifact path in the
   relevant stage artifact or log before continuing.
8. If Plannotator is unavailable, ask the user directly and record the
   response. Do not block only because Plannotator is absent.

Never self-approve. Reviewer `LGTM`, passing tests, or a generated
Plannotator preview is evidence, not human approval. A current-conversation
bypass is user-provided approval, not agent self-approval.

## Cross-Skill Routing

`idea-to-ship` owns the product flow. Other repo skills may be invoked only
when their domain signal is present and their output strengthens the current
stage. Do not turn `/architect` or `/implement` into a generic orchestrator.

### Safety boundary

- Read-only or artifact-only skills may be run automatically when their trigger
  is met and the current request is already in the relevant stage.
- Skills that modify production code, git history, GitHub/GitLab state,
  deployment state, credentials, or external systems require explicit user
  authorization in the current request.
- If a routed skill is unavailable in the host runtime, continue with the
  nearest local check and record the missing route.
- Always record routed skills and results:
  - `/architect` records them in `architecture.md` under
    `## Cross-Skill Routing`.
  - `/implement` records them in `implementation-log.md` under the current
    stage's `### Cross-Skill Checks`.

### Architecture-stage routes

| Signal in requirements / design | Route | Expected output |
|---|---|---|
| Agent, pipeline, autonomous loop, evaluator, state machine, retry, tool middleware, or structured model output | `harness-engineering:harness-design` or `harness-engineering:sprint-contract` | Harness constraints, state schema, evaluator contract, or a reason the feature is too small for a harness |
| Multi-context / long-horizon work, checkpointing, resumability, memory consolidation, or handoff risk | `harness-engineering:resilience-plan` or `harness-engineering:goal-mode` | Reset/checkpoint/resume requirements to cite in the design |
| External dependencies, network calls, persistence, irreversible side effects, data safety, observability, or degraded mode | `antifragile:antifragile-system` | Failure-mode and recovery requirements to fold into architecture |
| Secrets, credentials, tokens, webhooks, signing keys, auth config, or generated examples that might include secrets | `secret-scanner:scan-secrets` guidance, not a scan unless files already changed | Secret storage/redaction/no-hardcoded-secret constraints in architecture |

### Implementation-stage routes

| Signal in current stage / diff | Route | Expected output |
|---|---|---|
| Stage writes auth, credentials, `.env`, config, CI, deployment files, webhook/signing code, examples, fixtures, or generated files | `secret-scanner:scan-secrets --mode working` | Clean scan or triaged findings before marking the stage complete |
| Stage implements agent/pipeline/harness behavior, state persistence, retry, evaluator, or tool middleware | `harness-engineering:harness-audit` | State/schema/retry/evaluation gaps recorded before review |
| Stage touches external APIs, data consistency, destructive operations, retries, fallback paths, observability, or recovery | `antifragile:antifragile-system` | Resilience findings recorded as fixes, follow-ups, or accepted risk |
| Stage changes React/UI code | `react-doctor` when available, plus the relevant UI verification from `interface-design.md` | React-specific risks and visual/interaction evidence |
| Stage changes long-running goal/pipeline state | `harness-engineering:goal-mode` only when the implementation itself needs persistent execution state | Goal/checkpoint artifact path or explicit non-applicability |
