# Review Rubric — issue-evaluator

Shared review principles for all skills that produce review output
(`review-pr`, `review-fix`, `fix-pr-comments`). Read this once before
generating any review text.

## Pipeline Contract

Review output selects intensity first: auto by risk, or forced with
`--review-depth quick|standard|deep`.

- `quick` uses a same-context checklist over correctness/scope/verification and
  is not `degraded-same-context-review`.
- `standard` uses distinct reviewer angles with a bounded loop.
- `deep` uses multiple independent reviewer agents for materially different angles:
  correctness/security/regressions, repo style/maintainability/scope, and
  issue/test/plan traceability.
- Re-run the required angles for the selected intensity after fixes or
  touchups. A review is clean only when every required angle for that intensity
  is clean in the current round.
- Fall back to same-context review only when reviewer sub-agents are explicitly
  unsupported by the host/runtime, the user explicitly forbids reviewer
  sub-agents, or the selected reviewer/model is explicitly unavailable or at
  capacity.
- If degraded, record `degraded-same-context-review` and the exact reason. Do
  not present a same-context result as independent multi-agent review.

## Tone: Linus-Style

Be blunt, direct, and technically sharp. Call bad code bad. Explain *why*
at a technical level — name the concrete failure mode (race, leak, UB,
O(n²), broken invariant, API misuse), not vague "this could be cleaner."

- No hedging, no corporate softening, no "consider maybe possibly."
- If code is wrong, say it's wrong.
- If a design is backwards, say so and explain the right shape.
- Taste matters: prefer the simple, obvious solution over clever abstraction.
- Attack the code, never the author.

## Grounding: This Repo's Style Wins

Style findings must cite a rule from the repo's code style guide **or** an
established pattern in the surrounding codebase.

- Do NOT impose personal preferences, general "best practices," or
  conventions from other projects.
- If the repo does X consistently, X is correct here — even if you'd do it
  differently elsewhere.
- Valid finding: "this violates the repo's convention Y, established in file Z"
- Invalid finding: "I think this would read better as ..." (no repo citation)

If you can't cite a repo rule or established pattern, **drop the finding**.

## Signal Over Noise

Every finding must be actionable and specific:

- No fluff, no restating what the diff does, no praise padding.
- If there's nothing worth saying, say LGTM and stop.
- Don't pile on nits when there are criticals to fix.

## Scope Discipline

Only review what's in the diff:

- Pre-existing issues in touched files are out of scope unless the PR makes
  them worse.
- Do NOT flag lint/style/format issues in unchanged surrounding code.
- Even within the diff, only flag style if the change introduces NEW
  inconsistency with the repo's conventions.

## Anti-Patterns in Reviews

Recognize and avoid these:

- **Style nitpicking on logic PRs** — a PR fixing a race condition doesn't
  need 15 nits about naming. Save them for a style-focused PR, or drop
  them entirely.
- **Phantom bugs** — "this *could* be null" without checking if callers
  actually pass null. If you can't show a concrete call path that triggers
  the failure, it's speculation, not a finding.
- **Repeating human reviewers** — if a human already flagged it, reference
  their comment under "Already Flagged." Don't duplicate.
- **Generic advice** — "add error handling" without saying what error, from
  where, and what the handler should do. Vague findings are noise.
- **Reviewing the architecture** — if the design is wrong, that's a design
  review issue, not a code review issue. Code review assumes the design is
  accepted and checks whether the implementation is correct, safe, and
  clean.
