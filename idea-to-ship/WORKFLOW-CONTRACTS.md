# Idea-To-Ship Workflow Contracts

Shared contracts for idea-to-ship skills. Skills should cite this file for
cross-cutting runtime behavior while preserving their stage-specific gates.

## Multi-Agent Review Routing

For design and code review loops:

1. Read `PRINCIPLES.md` before launching a reviewer.
2. Launch multiple independent runtime-native reviewer agents by default. Use
   at least two angles per round:
   - correctness / failure modes / security
   - traceability / testability / implementation fit
   Add a UI/UX/accessibility angle when `interface-design.md` is present or the
   diff touches UI.
3. Treat invocation of a design or code review workflow as standing
   authorization to launch reviewer sub-agents. Use sub-agents when the host
   supports them unless the user explicitly forbids delegation. In Claude Code,
   keep the Codex adversarial reviewer (`subagent_type: "codex:codex-rescue"`)
   when available. Outside Claude Code, do not request Claude-only subagent
   types; use the host runtime's native reviewer agents for the same roles.
4. Fall back to same-context review only when reviewer sub-agents are
   explicitly unsupported by the host/runtime, the user explicitly forbids
   reviewer sub-agents, or a selected reviewer/model is explicitly unavailable
   or at capacity. Record `degraded-same-context-review` and the exact reason
   in the review artifact. Do not present the result as independent multi-agent
   review. Degraded mode still preserves the same angles and rounds; it only
   loses independent agents.
5. A review can return clean only after every required reviewer angle has
   either returned `LGTM` or all material findings from that angle have been
   fixed and re-reviewed.

The invariant is independent skeptical review from multiple agents, multiple
angles, and multiple rounds. Same-context review is only the recorded
degradation path for the explicit unsupported cases above.

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
| `needs_user` | Product intent, priority approval, destructive overwrite, or scope needs a human decision. |
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
2. Collect the current target (`architecture.md` or diff) fresh each iteration.
3. Treat `LGTM` as the clean sentinel only per reviewer angle; the round is
   clean only when all required angles are clean.
4. Fix critical and warning findings in scope; skip or record nits unless they
   are trivially co-located.
5. Run multiple rounds until clean, with a default cap of five rounds unless
   the user explicitly asks to continue.
6. Run one holistic pass after the incremental loop.

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
