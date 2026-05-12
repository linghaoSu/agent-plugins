# Issue Evaluator Workflow Contracts

Shared contracts for issue-evaluator skills. Individual skills should cite this
file instead of duplicating the full lifecycle text.

## Runtime-Aware Agent Routing

Before launching analysis, review, executor, or synthesis agents:

1. Read `PRINCIPLES.md` and apply its runtime-aware routing guidance.
2. In Claude Code, keep the existing role split only when the host supports it.
3. Outside Claude Code, use the host runtime's native sub-agent mechanism for
   the same roles and do not request Claude-only model names or subagent types.
4. If no sub-agent mechanism is available, run a separate main-context pass
   with the same prompt and record the fallback.
5. If a selected model or sub-agent is unavailable or at capacity, stop retrying
   that same route, use the fallback, and record the reason.

The invariant is role separation and independent validation, not a specific
model brand.

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

## Adversarial Review Loop

For `review-fix`-style loops:

1. Collect a fresh diff at the start of every iteration.
2. Review only changed lines and behavior introduced by the current diff.
3. Drop pure style findings in unchanged code.
4. Fix criticals and warnings that are in scope; skip or record nits unless
   they are trivially co-located.
5. Treat `LGTM` as the clean sentinel.
6. Cap loops at five iterations unless the user explicitly asks to continue.
7. Run one final holistic pass over the full diff after the incremental loop.
