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
├── roadmap.md            # from /roadmap --slug <name>
├── design-review.md      # from /review-design
├── implementation-log.md # from /implement
├── code-review.md        # from /review-code
└── test-plan.md          # from /test
```

Portfolio roadmaps land at `.idea-to-ship/roadmap.md`.

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

### `/roadmap [options]`
Builds or refreshes an evidence-backed roadmap. Defaults to the portfolio
roadmap at `.idea-to-ship/roadmap.md`; pass `--slug <name>` for a feature-level
roadmap at `.idea-to-ship/<slug>/roadmap.md`.

The skill first produces a sourced Candidate Brief, then writes final
Now/Next/Later lanes only after goal, horizon, source scope, citations,
priority approval, and overwrite safety gates are satisfied. Optional
`--include-git`, `--include-todos`, and `--include-github` inputs are
quarantined as lower-authority signals unless confirmed.

### `/review-design [focus]`
Runtime-aware adversarial review of `architecture.md`. In Claude Code it uses
Codex (`codex:codex-rescue`) when available; in other runtimes it uses the
host's native adversarial reviewer role. Linus-style: blunt, skeptical, attacks
weak assumptions. Iterates — each round updates `architecture.md` with fixes
until the reviewer returns LGTM (max 5 iterations). Final verdict goes to
`design-review.md`.

### `/implement [--tdd] [stage]`
Reads `architecture.md` and implements it in staged commits. Logs each stage
(files touched, decisions, deviations from the design) to
`implementation-log.md`. Stops between stages for your review. With `--tdd`,
behavior-changing stages write failing story/acceptance tests before
production code, then implement until those tests pass.

### `/review-code [focus]`
Runtime-aware adversarial code review of the current diff, looping fix→review
until clean. Similar to `issue-evaluator/review-fix` but scoped to this flow
and aware of requirements, architecture, implementation logs, and test-plan
traceability. Writes `code-review.md`.

### `/test [focus]`
Produces `test-plan.md` from user stories, acceptance criteria, scenario
sequences, and unit/integration/e2e matrices. Every core story should cover a
happy path plus at least one edge/corner, invalid-input, alternate, or
failure-mode scenario unless explicitly out of scope. Then implements the
tests and runs them until green.

## Typical flow

```bash
/brainstorm "I want to add an offline cache to the API client"
# answers questions, writes requirements.md
/architect
# writes architecture.md with 2 options + recommendation
/roadmap --goal "ship offline cache safely" --horizon "next 4 weeks"
# writes a sourced roadmap brief/final roadmap depending on gates
/review-design
# runtime-aware adversarial reviewer tears it apart, you fix, loops until LGTM
/implement
# staged implementation
/implement --tdd 1
# optional test-first implementation for one behavior-changing stage
/review-code
# adversarial review of the diff + test traceability
/test
# story-driven test plan + implementation
```

Each step is independent — skip any, or hand-edit artifacts between steps.

## Conventions

- **Slug**: all skills accept `--slug <name>` as the first token of their
  arguments. If omitted, uses `current`.
- **Roadmap scope**: `/roadmap` defaults to portfolio mode
  (`.idea-to-ship/roadmap.md`). With `--slug <name>`, it writes the feature
  roadmap for that slug.
- **Roadmap safety**: final Now/Next/Later lanes require explicit goal,
  horizon, sourced candidate items, and overwrite safety. Weak signals such as
  TODOs and mined issues never enter `Now` automatically.
- **Test traceability**: `/test` derives user stories, acceptance criteria,
  scenario matrices, and test cases before implementation. `/review-code`
  flags behavior changes without requirement/story/scenario/test evidence.
- **TDD mode**: `/implement --tdd` is opt-in. It is required to write a
  failing test before production code for behavior-changing stages, or document
  why the stage has no meaningful runtime behavior.
- **Adversarial review is on by default** for `/review-design` and
  `/review-code`. Claude Code uses `codex:codex-rescue` when available;
  non-Claude runtimes use their native sub-agent review mechanism, with a
  recorded self-review fallback if no sub-agent mechanism exists.
- **No auto-commit**: skills never commit or push. You control git.
- **Artifact-first**: skills prefer updating the artifact over chatting.
  Read the file to see what they did.
