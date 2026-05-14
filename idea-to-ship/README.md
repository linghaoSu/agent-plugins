# idea-to-ship

A plugin for taking a fuzzy idea all the way to shipped, tested code. Each stage
produces a markdown artifact on disk so you can stop, edit, and resume anywhere.
Every new idea-to-ship slug starts with `/brainstorm`; downstream stages require
the resulting `requirements.md`. Commercialization planning can run before or
after `/brainstorm`, but it does not replace requirements for build stages.

All skills that write or review code apply the four principles in
[`PRINCIPLES.md`](./PRINCIPLES.md): Think Before Coding · Simplicity First ·
Surgical Changes · Goal-Driven Execution.

All artifacts land under `.idea-to-ship/<slug>/` at the repo root:

```
.idea-to-ship/<slug>/
├── requirements.md       # from /brainstorm
├── commercialization.md  # from /commercialize
├── interface-design.md   # from /ui-design for UI/UX-heavy work
├── architecture.md       # from /architect
├── roadmap.md            # from /roadmap --slug <name>
├── design-review.md      # from /review-design
├── tdd-log.md            # from /tdd for stage gates or backfill tests
├── implementation-log.md # from /implement
├── code-review.md        # from /review-code
└── test-plan.md          # from /test
```

Portfolio roadmaps land at `.idea-to-ship/roadmap.md`.

The default `<slug>` is `current`. Pass `--slug <name>` to any skill to switch.
For a fresh slug, run `/brainstorm --slug <name>` first.

## Commands

### `/brainstorm [description]`
Mandatory first stage. Turns a vague idea into a concrete requirements document
via Socratic Q&A. Asks clarifying questions in batches until the problem, users,
constraints, and success criteria are unambiguous. Writes `requirements.md`.

### `/commercialize [options]`
Expands fuzzy product ideas into concrete commercialization scenarios, then
turns business-model conclusions into roadmap inputs. Covers ICP, buyer/user
split, monetization model, pricing/packaging hypotheses, paid/free boundaries,
commercial blockers, feature-to-business impact, validation metrics,
adversarial multi-angle review, explicit rejection of impractical or costly
low-return ideas, and open commercial decisions. Writes `commercialization.md`.

This can run before `/brainstorm` for a rough commercial thesis, but the result
is marked `pre-requirements` until `requirements.md` exists. `/roadmap` treats
`commercialization.md` as prioritization evidence, not as a replacement for
requirements.

### `/architect [notes]`
Reads `requirements.md`, explores the codebase, and produces `architecture.md`:
goals, module breakdown, data flow, interfaces, tradeoffs of 2–3 alternatives,
and a recommendation. Routes to harness / antifragile / secret-handling skills
when the requirements signal agent, resilience, or credential risk. Does not
write code.

### `/ui-design [notes]`
Reads `requirements.md`, `architecture.md` if present, existing UI code, and
project `DESIGN.md` if present. Produces `interface-design.md`: UX brief,
design-system map, visual contract, interaction spec, component states,
responsive behavior, accessibility contract, and visual QA plan. With
`--write-design-md`, creates or updates project-level `DESIGN.md` as a reusable
visual-system contract. Does not write production code.

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
Multi-agent, multi-angle, multi-round adversarial review of `architecture.md`. Independent
reviewer agents check architecture correctness, implementation/testability, and
UI/UX when `interface-design.md` exists. Iterates until every angle returns
LGTM (max 5 rounds). Same-context review is only the recorded fallback when
reviewer sub-agents are explicitly unsupported by the host/runtime, explicitly
forbidden by the user, or the selected reviewer/model is explicitly unavailable
or at capacity.

### `/implement [stage]`
Reads `architecture.md` and implements it as stage-by-stage local edits. Logs each stage
(files touched, decisions, deviations from the design) to
`implementation-log.md`. Stops between stages for your review. Production-code
and behavior-changing stages must call `/tdd` first: failing story/acceptance
tests come before production code, then implementation continues until those
tests pass. Stage verification includes signal-driven cross-skill checks such
as secret scanning, harness audit, antifragile audit, and React checks when the
diff warrants them.

### `/tdd [--stage <N> | --backfill] [focus]`
Creates the test gate for a stage before production code, writing stage-local
evidence to `test-plan.md` and `tdd-log.md`. In `--backfill` mode, supplements
missing tests for existing code or the current diff without pretending those
passing tests are TDD. Does not write production code.

### `/review-code [focus]`
Multi-agent, multi-angle, multi-round adversarial code review of the current diff, looping
fix→review until every required angle is clean. Similar to
`issue-evaluator/review-fix` but scoped to this flow and aware of requirements,
architecture, interface design, implementation logs, and test-plan traceability.
Same-context review is only the recorded fallback when reviewer sub-agents are
explicitly unsupported by the host/runtime, explicitly forbidden by the user, or
the selected reviewer/model is explicitly unavailable or at capacity. Writes
`code-review.md`.

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
/commercialize --goal "find the first paid path" --horizon "next 6 weeks"
# writes commercialization.md with ICP, pricing/packaging hypotheses, commercial gates
/ui-design
# optional for UI-heavy work, writes interface-design.md
/architect
# writes architecture.md with 2 options + recommendation
/roadmap --goal "ship offline cache safely" --horizon "next 4 weeks"
# writes a sourced roadmap brief/final roadmap depending on gates
/review-design
# multi-agent reviewers tear it apart, you fix, loops until every angle is LGTM
/tdd --stage 1
# writes the failing stage test gate
/implement
# staged TDD-first implementation for code-producing stages
/test
# story-driven test plan + implementation
/review-code
# adversarial review of the diff + test traceability
```

You may hand-edit artifacts between stages, but do not skip `/brainstorm`.
If `requirements.md` is missing, downstream skills stop and send you back to
`/brainstorm --slug <name>`.

## Conventions

- **Slug**: all skills accept `--slug <name>` as the first token of their
  arguments. If omitted, uses `current`.
- **Mandatory brainstorm**: every new slug begins with `/brainstorm`, which
  owns `requirements.md`. Roadmaps can sequence work, but they do not replace
  brainstormed requirements for design, implementation, test, or review.
- **Commercialization input**: `/commercialize` owns `commercialization.md`.
  It can run before `/brainstorm` as a business hypothesis, but downstream
  build stages still require `requirements.md`. `/roadmap` may use
  `commercialization.md` to prioritize commercial gates, packaging work, and
  validation experiments.
- **Roadmap scope**: `/roadmap` defaults to portfolio mode
  (`.idea-to-ship/roadmap.md`). With `--slug <name>`, it writes the feature
  roadmap for that slug.
- **UI design contract**: `/ui-design` is optional for backend-only work and
  expected for UI-heavy work. `interface-design.md` is the slug-level contract;
  project `DESIGN.md` is only written when explicitly requested.
- **Roadmap safety**: final Now/Next/Later lanes require explicit goal,
  horizon, sourced candidate items, and overwrite safety. Weak signals such as
  TODOs and mined issues never enter `Now` automatically.
- **Test traceability**: `/test` derives user stories, acceptance criteria,
  scenario matrices, and test cases before final review. `/review-code`
  flags behavior changes without requirement/story/scenario/test evidence.
- **TDD-first implementation**: `/implement` defaults to TDD for production-code
  and behavior-changing stages by calling `/tdd`. The TDD skill must write a
  failing test before production code, or document why the stage has no
  meaningful runtime behavior. `/tdd --backfill` is available for projects that
  need missing tests added after code already exists.
- **Multi-agent review**: `/review-design` and `/review-code` require multiple
  independent reviewer agents, multiple angles, and multiple rounds by default.
  Same-context adversarial passes are supported only when reviewer sub-agents
  are explicitly unsupported by the host/runtime, explicitly forbidden by the
  user, or the selected reviewer/model is explicitly unavailable or at
  capacity; the artifact must record `degraded-same-context-review` and must
  not present the result as independent multi-agent review.
- **Cross-skill routing**: `/architect` and `/implement` may route to other
  repo skills when their risk signal is present. Read-only or artifact-only
  routes can run automatically; code/git/GitHub/deployment/credential mutations
  require explicit user authorization. Routes and outcomes are recorded in
  `architecture.md` or `implementation-log.md`.
- **No auto-commit**: skills never commit or push. You control git.
- **Artifact-first**: skills prefer updating the artifact over chatting.
  Read the file to see what they did.
