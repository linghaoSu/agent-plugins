# Issue Evaluator Workflow Contracts

Shared contracts for issue-evaluator skills. Individual skills should cite this
file instead of duplicating the full lifecycle text.

## Multi-Agent Review Routing

Before launching analysis, review, executor, or synthesis agents:

1. Read `PRINCIPLES.md` and apply its runtime-aware routing guidance.
2. Treat invocation of a review workflow as standing authorization to launch
   reviewer and synthesis sub-agents. Do not ask for new multi-agent
   authorization and do not use missing fresh authorization as a fallback
   reason.
3. For review workflows, launch multiple independent reviewer agents by
   default and cover at least these angles every review round:
   - correctness / security / regressions
   - repo style / maintainability / scope control
   - requirements, issue, test, or plan traceability
4. Re-run every required angle after fixes or touchups. A round is clean only
   when every required angle returns `LGTM` in that round, or all material
   findings from that angle have been fixed and re-reviewed.
5. In Claude Code, keep the existing role split only when the host supports it.
6. Outside Claude Code, use the host runtime's native sub-agent mechanism for
   the same roles and do not request Claude-only model names or subagent types.
7. Fall back to same-context review only when reviewer sub-agents are explicitly
   unsupported by the host/runtime, the user explicitly forbids reviewer
   sub-agents, or the selected reviewer/model is explicitly unavailable or at
   capacity. Record `degraded-same-context-review` and the exact reason. Do not
   present the result as independent multi-agent review. Degraded mode still
   preserves the same angles and rounds; it only loses independent agents.
8. For non-review analysis or executor roles, a skill may define a degraded
   main-context fallback, but it must record that the pipeline lost independent
   validation.

The invariant is independent skeptical review from multiple agents, multiple
angles, and multiple rounds. Same-context review is only the recorded
degradation path for the explicit unsupported cases above.

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
2. Review only changed lines and behavior introduced by the current diff.
3. Drop pure style findings in unchanged code.
4. Run every required review angle each iteration. Do not collapse angles into
   one generic review.
5. Fix criticals and warnings that are in scope; skip or record nits unless
   they are trivially co-located.
6. Treat `LGTM` as the clean sentinel per angle. The iteration is clean only
   when all required angles are clean.
7. Cap loops at five iterations unless the user explicitly asks to continue.
8. Run one final holistic pass over the full diff after the incremental loop.
