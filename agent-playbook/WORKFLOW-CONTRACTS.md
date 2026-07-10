# Agent-Playbook Workflow Contracts

These contracts are shared by agent-playbook skills. Skills should cite this
file instead of copying the same safety and artifact rules into every
frontmatter description.

## Capability Routing

Describe delegated work without naming a model, vendor, coding agent, or
host-specific agent type:

```yaml
role: coordinator | executor | reviewer | arbiter
capability: routine | reasoning | critical
independent_context: true | false
parallelizable: true | false
```

- Prefer deterministic verification over model judgment.
- Give `routine` executors only bounded task packets with runnable acceptance.
- Use `reasoning` for exploration and independent review.
- Use `critical` only for high-impact decisions, reviewer conflict, or final
  arbitration.
- Executors never accept their own work. Allow one revision, then repartition
  or raise the requested capability.
- Let the host map capabilities to available execution units. If it cannot,
  use the best available route and report `degraded`.

## Artifact Ownership

For `.agent-playbook/<slug>/` artifacts:

1. Append dated runs when the existing artifact has the expected headings.
2. Preserve human notes and content outside expected headings.
3. If merge safety is unclear, write `*.draft.md` instead of replacing the
   canonical artifact.
4. A fix log must link the source health-check artifact and record each finding
   as `applied`, `routed`, `deferred`, or `blocked`.

## External Contribution Quality Gate

Before any skill creates an externally visible PR, protect the user's
reputation and the target maintainers' time:

1. Read the target repo's PR template and contributor instructions before
   preparing the PR body.
2. Search open and closed PRs for duplicates using issue numbers, title
   keywords, and touched scope. Stop if a duplicate exists, and report the
   links plus what would need to differ.
3. Confirm the change solves one real, specific problem. Stop on speculative
   cleanup, broad "best practice" changes, or bundled unrelated fixes.
4. Show or summarize the complete diff and require explicit human approval
   before pushing a branch or creating the PR.
5. Fill every required PR template section with concrete diff, check, issue,
   and limitation evidence. Do not delete headings or use placeholders.
6. Follow the target repo's authorship/disclosure policy. Disclose AI/tool
   involvement only when the target repo requires it; never add AI attribution
   to commits unless the human explicitly asks and the repo policy allows it.

## Frontmatter Descriptions

Frontmatter descriptions are routing hints, not manuals. Keep them short:

- State the task intent.
- Name the artifact written, if any.
- Include one or two disambiguating trigger phrases.
- Keep long safety rules, workflow steps, and implementation details in the
  skill body or this shared contract.

## Output, Token, And Error Contract

Agent-playbook skills that read diffs, comments, logs, repo-wide data, hook
state, or external tool output must end with a compact result contract:

```yaml
status: success | needs_user | terminal | degraded
mode: <read-only | apply | audit | review>
inputs_resolved:
  target: <path, repo, PR, or artifact>
outputs_written:
  - <local artifact path, empty when conversation-only>
skipped:
  - <item>: <reason>
errors:
  - type: retryable | terminal | needs_user | degraded
    message: <actionable sentence>
next_action: <one command or decision>
truncated: true | false
```

Error categories:

| Type | Meaning |
|---|---|
| `retryable` | A transient command, filesystem, auth, or network failure where rerunning may succeed. |
| `terminal` | Continuing would violate the skill boundary or produce untrustworthy output. |
| `needs_user` | A destructive action, ownership question, or missing requirement needs user confirmation. |
| `degraded` | The workflow continued with weaker evidence, fewer reviewers, or partial data. |

Default token budget unless a skill sets a stricter one:

- Diff or patch reads: 25 files and 400 changed lines per file.
- Repo-wide scans: 100 files, 20 hits per query, and 80 surrounding lines per
  file.
- Comments/review threads/logs: 100 items, with each item summarized to the
  smallest actionable sentence.
- Command output evidence: 240 rendered characters per item in release-gate
  style summaries.

If a budget is exceeded, do not silently truncate. Set `truncated: true`, name
what was omitted, and put the continuation command, narrowed query, or next
artifact path in `next_action`.

## Shared Safety And Evaluation Checklist

Use this checklist from `tool-review`, `context-audit`, and
`antifragile:antifragile-audit --scope agent` instead of copying slightly
different rules into each skill. This section owns only shared audit fields;
tool design, context hygiene, vibe-health routing, and antifragile
hook/state/recovery criteria stay in their owning skills:

- **Boundary truth:** distinguish read-only-on-target, local artifact writes,
  git mutations, GitHub mutations, and external-system mutations.
- **Human gate:** require explicit current-turn authorization before
  destructive cleanup, force removal, commits, pushes, publishing, or global
  installation changes.
- **Token honesty:** declare input caps, set `truncated: true` when caps are
  hit, and provide a continuation path.
- **Error shape:** classify every failure as `retryable`, `terminal`,
  `needs_user`, or `degraded`.
- **Evaluation realism:** keep regex fixtures as contract smoke tests, but do
  not call them sufficient behavioral evaluation. Add scenario fixtures for
  safety gates that can cause writes, deletes, or misleading reviews.
- **Local report ownership:** read-only audit/review skills may write only
  their documented local artifact path. Conversation-only skills must set
  `outputs_written: []`.

## Review Intensity Selection

For agent-playbook review skills such as `tool-review`, select a review
intensity before launching reviewers. Parse optional
`--review-depth quick|standard|deep`; when present, it is a user-forced
override. Record the selected intensity, whether it was auto or forced, and the
reason in the local artifact.

Auto-select the smallest tier that covers the risk:

| Intensity | Use when | Review shape |
|---|---|---|
| `quick` | Small, read-only review of docs, one schema, one command surface, or one low-risk tool with no external mutation, auth, destructive behavior, or large output risk. | One same-context checklist and a ranked punch-list. This is selected intensity, not `degraded-same-context-review`. |
| `standard` | Normal tool/CLI/MCP review with bounded surface area and clear source/schema. | One multi-angle reviewer round plus synthesis. Re-check only material findings after edits to the review artifact. |
| `deep` | Tool suites, overlapping tools, auth/secrets, destructive or external-system tools, high token/output risk, unclear boundaries, or user-forced `--review-depth deep`. | Full multi-agent, multi-angle, multi-round review with final sanity pass. |

Escalate during review if a lower tier discovers higher-risk behavior. A forced
lower depth is allowed, but never claim deep assurance for it and never skip the
skill's documented safety boundary.
