# idea-to-ship

A plugin for taking a fuzzy idea all the way to shipped, tested code. Each stage
produces a markdown artifact on disk so you can stop, edit, and resume anywhere.

All skills that write or review code apply the four principles in
[`PRINCIPLES.md`](./PRINCIPLES.md): Think Before Coding · Simplicity First ·
Surgical Changes · Goal-Driven Execution.

All artifacts land under `.idea-to-ship/<slug>/` at the repo root:

```
.idea-to-ship/<slug>/
├── requirements.md       # from /brainstorm
├── architecture.md       # from /architect
├── design-review.md      # from /review-design
├── implementation-log.md # from /implement
├── code-review.md        # from /review-code
└── test-plan.md          # from /test
```

The default `<slug>` is `current`. Pass `--slug <name>` to any skill to switch,
or run `/brainstorm` to create a fresh one.

## Commands

### `/brainstorm [description]`
Turns a vague idea into a concrete requirements document via Socratic Q&A.
Asks clarifying questions in batches until the problem, users, constraints,
and success criteria are unambiguous. Writes `requirements.md`.

### `/architect [notes]`
Reads `requirements.md`, explores the codebase, and produces `architecture.md`:
goals, module breakdown, data flow, interfaces, tradeoffs of 2–3 alternatives,
and a recommendation. Does not write code.

### `/review-design [focus]`
Adversarial review of `architecture.md` via Codex (`codex:codex-rescue`).
Linus-style: blunt, skeptical, attacks weak assumptions. Iterates — each round
updates `architecture.md` with fixes until the reviewer returns LGTM (max 5
iterations). Final verdict goes to `design-review.md`.

### `/implement [stage]`
Reads `architecture.md` and implements it in staged commits. Logs each stage
(files touched, decisions, deviations from the design) to
`implementation-log.md`. Stops between stages for your review.

### `/review-code [focus]`
Adversarial code review of the current diff via Codex, looping fix→review
until clean. Similar to `issue-evaluator/review-fix` but scoped to this flow
and aware of the architecture document. Writes `code-review.md`.

### `/test [focus]`
Produces `test-plan.md` (strategy: unit/integration/e2e split, coverage goals,
edge cases derived from requirements), then implements the tests and runs
them until green.

## Typical flow

```bash
/brainstorm "I want to add an offline cache to the API client"
# answers questions, writes requirements.md
/architect
# writes architecture.md with 2 options + recommendation
/review-design
# Codex tears it apart, you fix, loops until LGTM
/implement
# staged implementation
/review-code
# adversarial review of the diff
/test
# test plan + implementation
```

Each step is independent — skip any, or hand-edit artifacts between steps.

## Conventions

- **Slug**: all skills accept `--slug <name>` as the first token of their
  arguments. If omitted, uses `current`.
- **Adversarial review is on by default** for `/review-design` and
  `/review-code`. Requires `codex:codex-rescue` agent to be available.
- **No auto-commit**: skills never commit or push. You control git.
- **Artifact-first**: skills prefer updating the artifact over chatting.
  Read the file to see what they did.
