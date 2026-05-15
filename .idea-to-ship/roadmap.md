---
goal: "提高 agent-plugins 稳定性，降低 token 消耗，减少重复维护"
horizon: "next 3 commits"
generated_at: "2026-05-15 12:52 CST"
repo_head: "2d23196de91a05804c2c101618b7ac18d62b787a"
dirty_worktree: "clean before roadmap refresh"
mode: "portfolio"
source_scope: "local artifacts + repo docs/manifests; no GitHub, TODO, or git-history scan"
write_target: ".idea-to-ship/roadmap.md"
final_lanes_written: "no"
priority_approval: "pending"
---

# Roadmap - 提高 agent-plugins 稳定性，降低 token 消耗，减少重复维护

## Human-Owned Sections

### Strategic Objective

在整个 `agent-plugins` repo 内，把接下来 3 个 commit 用于稳定性、token 消耗和重复维护的收敛：优先减少长 skill 中重复的路由、prompt、模板和检查清单，同时用 release gate / fixture 防止后续反弹。

### Manual Overrides

- Requested horizon: next 3 commits.
- Requested scope: entire `agent-plugins`.
- Requested optimization goal: stability, lower token use, and less repeated maintenance.
- Priority approval is pending; this file currently records candidates, not final Now/Next/Later lanes.

### Out of Scope / Non-Goals

- No GitHub issue, PR, or milestone scan in this run.
- No TODO/FIXME mining in this run.
- No broad renaming or removal of public skill entry points.
- No production code edits in this roadmap refresh.
- No final Now/Next/Later lanes until the candidate ordering is approved or edited.

<!-- idea-to-ship:roadmap generated:start -->

## Candidate Brief

### Source Plan

Included sources:

- Current user request: `$idea-to-ship:roadmap`, goal of stability / lower token use / less repetition, horizon of next 3 commits, scope of entire `agent-plugins`.
- `README.md:23-35` for repo naming, read-only, and token-budget expectations.
- `README.md:42-120` for current plugin and skill catalog boundaries.
- `PORTFOLIO.md:8-13` for sources of truth and roadmap ownership.
- `PORTFOLIO.md:46-56` for portfolio responsibility boundaries.
- `RELEASE-GATE.md:42-51` for advisory release-gate checks and fixture expectations.
- `idea-to-ship/WORKFLOW-CONTRACTS.md:38-83` for shared output, token, and error contracts.
- `idea-to-ship/WORKFLOW-CONTRACTS.md:98-136` for cross-skill routing already available to individual skills.
- `issue-evaluator/WORKFLOW-CONTRACTS.md:40-84` for shared output, token, and error contracts.
- `issue-evaluator/WORKFLOW-CONTRACTS.md:86-168` for code-style lifecycle and GitHub read-only safety contracts.
- `scripts/skill-hygiene-check.py:19-25` and `scripts/skill-hygiene-check.py:181-243` for current hygiene thresholds and missing repetition checks.
- `worktree-cleaner/skills/clean-worktrees/SKILL.md:4` for the invalid unquoted `argument-hint` pattern that triggered loader YAML warnings.
- Long / repetitive skill bodies inspected locally: `idea-to-ship/skills/implement/SKILL.md`, `idea-to-ship/skills/review-code/SKILL.md`, `issue-evaluator/skills/evaluate-issue/SKILL.md`, `issue-evaluator/skills/fix-issue/SKILL.md`, `agent-playbook/skills/tool-review/SKILL.md`, `agent-playbook/skills/context-audit/SKILL.md`, and `agent-playbook/skills/vibe-coding-health-check/SKILL.md`.

Excluded sources:

- GitHub issues, PRs, milestones, and discussions.
- TODO/FIXME scan.
- Full git-history mining beyond the current repo head.
- Subagent exploration, because the current request did not explicitly authorize parallel agent delegation.

### Candidate Work

| ID | Candidate | Suggested Commit | Evidence Class | Confidence | Primary Impact |
|---|---|---:|---|---|---|
| ITS-ROADMAP-008 | Collapse `idea-to-ship:implement` routing and log-template repetition into shared contracts/templates. | 1 | Repo | High | Lower token load in a central high-traffic skill; less duplicated routing maintenance. |
| ITS-ROADMAP-009 | Extract `issue-evaluator:evaluate-issue` long adversarial prompts and report template into reusable prompt/template files. | 2 | Repo | High | Lower per-invocation prompt bulk; clearer skill body; easier prompt review. |
| ITS-ROADMAP-010 | Add hygiene checks for repeated inline prompts/templates and moderate skill bloat. | 3 | Repo | Medium | Prevents repeated text from creeping back after manual cleanup. |
| ITS-ROADMAP-011 | Extract shared audit/safety checklist used by tool-review, context-audit, vibe health, and antifragile-agent. | 3 | Repo | Medium | Reduces four-way maintenance drift across overlapping audit skills. |
| ITS-ROADMAP-012 | Normalize agent-playbook audit report templates into `templates/`. | 3 | Repo | Medium | Cuts inline artifact boilerplate and improves report consistency. |
| ITS-ROADMAP-013 | Strengthen skill frontmatter validation against real loader YAML semantics and installed-cache drift. | 3 | Repo | High | Prevents invalid `SKILL.md` YAML from shipping or only surfacing after plugin load. |

### ITS-ROADMAP-008 - Collapse idea-to-ship implement repetition

**Status:** Candidate
**Work Type:** Maintenance
**Evidence Class:** Repo
**Confidence:** High
**Source Anchors:** `idea-to-ship/skills/implement/SKILL.md:199-229`; `idea-to-ship/skills/implement/SKILL.md:231-259`; `idea-to-ship/skills/implement/SKILL.md:293-317`; `idea-to-ship/WORKFLOW-CONTRACTS.md:98-136`
**Why Now / Why Next / Why Later:** This is the best first commit because `implement` is central, currently carries repeated cross-skill routing and inline log/report structure, and already has shared contracts it can cite instead.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: current `implement` behavior and output contract are captured. Exit: repeated routing text is replaced by references to shared contracts/templates, fixtures still pass, and no public skill name changes. No-go: removing safety routing or weakening TDD/review gates for brevity.
**Evidence Required:** Updated `idea-to-ship/skills/implement/SKILL.md`; new or reused template files under `idea-to-ship/templates/`; passing `tests/idea-to-ship-eval-fixtures.sh`; passing strict release gate if touched files require it.
**Dependencies:** Existing `idea-to-ship/WORKFLOW-CONTRACTS.md`.
**Risk:** medium - reducing prompt text can accidentally remove a behavioral gate unless the contract reference is explicit and fixture coverage remains green.

### ITS-ROADMAP-009 - Extract issue-evaluator evaluate prompts

**Status:** Candidate
**Work Type:** Maintenance
**Evidence Class:** Repo
**Confidence:** High
**Source Anchors:** `issue-evaluator/skills/evaluate-issue/SKILL.md:128-187`; `issue-evaluator/skills/evaluate-issue/SKILL.md:194-263`; `issue-evaluator/skills/evaluate-issue/SKILL.md:267-280`; `issue-evaluator/WORKFLOW-CONTRACTS.md:6-84`
**Why Now / Why Next / Why Later:** This is the strongest second commit because `evaluate-issue` has large inline adversarial prompts and final report text that are expensive to load and hard to diff-review inside the skill body.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: current prompt phases and final report fields are preserved. Exit: skill body references prompt/template artifacts, output contract remains unchanged, and issue-evaluator fixtures pass. No-go: changing GitHub read-only behavior or silently dropping multi-angle review steps.
**Evidence Required:** Updated `issue-evaluator/skills/evaluate-issue/SKILL.md`; prompt/template files under `issue-evaluator/prompts/` and/or `issue-evaluator/templates/`; passing `tests/agent-playbook-eval-fixtures.sh` or the relevant issue-evaluator fixture if present; strict release gate result.
**Dependencies:** Existing `issue-evaluator/WORKFLOW-CONTRACTS.md`.
**Risk:** medium - prompt extraction reduces visible context in `SKILL.md`, so references must be exact and fixtures should check required phases still exist.

### ITS-ROADMAP-010 - Add repetition and bloat hygiene checks

**Status:** Candidate
**Work Type:** Maintenance
**Evidence Class:** Repo
**Confidence:** Medium
**Source Anchors:** `scripts/skill-hygiene-check.py:19-25`; `scripts/skill-hygiene-check.py:181-243`; `RELEASE-GATE.md:42-51`
**Why Now / Why Next / Why Later:** This should land with or after the first extraction commits so the release gate enforces the new expectation instead of relying on manual review.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: define non-brittle signals for repeated inline prompts/templates and moderate-size skill bodies. Exit: hygiene check reports actionable advisory failures in `--strict` mode without punishing legitimate concise skills. No-go: exact prose golden-file checks that make normal wording edits noisy.
**Evidence Required:** Updated `scripts/skill-hygiene-check.py`; fixture/sample coverage for repeated prompt/template markers; `scripts/release-gate.sh --mode all --strict`.
**Dependencies:** Prefer after `ITS-ROADMAP-008` or `ITS-ROADMAP-009` so the rule can be tuned against real cleanup.
**Risk:** medium - too-strict thresholds create false positives; too-loose thresholds do not stop drift.

### ITS-ROADMAP-011 - Extract shared audit and safety checklist

**Status:** Candidate
**Work Type:** Maintenance
**Evidence Class:** Repo
**Confidence:** Medium
**Source Anchors:** `agent-playbook/skills/tool-review/SKILL.md:89-138`; `agent-playbook/skills/context-audit/SKILL.md:68-115`; `agent-playbook/skills/vibe-coding-health-check/SKILL.md:108-130`; `README.md:48-59`
**Why Now / Why Next / Why Later:** This belongs in the third commit because audit skills overlap by design, but their shared safety and eval criteria should be maintained once instead of duplicated across several skill bodies.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: identify shared checklist items that are truly common and keep skill-specific criteria local. Exit: shared checklist file is cited from each audit skill, and each skill keeps a short boundary-focused local checklist. No-go: forcing all audit skills into one generic checklist that loses domain-specific judgment.
**Evidence Required:** Shared checklist under `agent-playbook/` or a repo-wide contracts location; updated audit skill references; passing agent-playbook fixtures and strict release gate.
**Dependencies:** Can pair with `ITS-ROADMAP-010` if the hygiene check watches for duplicated checklist headings.
**Risk:** medium - over-extraction can hide the differences between context hygiene, tool review, vibe health, and antifragile audits.

### ITS-ROADMAP-012 - Normalize agent-playbook audit templates

**Status:** Candidate
**Work Type:** Maintenance
**Evidence Class:** Repo
**Confidence:** Medium
**Source Anchors:** `agent-playbook/skills/tool-review/SKILL.md:146-180`; `agent-playbook/skills/context-audit/SKILL.md:116-158`; `agent-playbook/skills/vibe-coding-health-check/SKILL.md:145-190`; `.gitignore:2`
**Why Now / Why Next / Why Later:** This is a good third-commit companion to `ITS-ROADMAP-011`: shared report templates reduce boilerplate while `.agent-playbook/current/` remains ignored and local-only.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: current audit outputs and generated markers are known. Exit: templates live outside long skill bodies and report-writing rules still distinguish read-only analysis from local artifact writes. No-go: committing generated `.agent-playbook/current/` reports or changing read-only semantics.
**Evidence Required:** New or updated `agent-playbook/templates/` files; updated audit skills; passing `tests/agent-playbook-eval-fixtures.sh`; strict release gate result.
**Dependencies:** Strongly related to `ITS-ROADMAP-011`.
**Risk:** low - mostly documentation/template movement, but output contract wording must stay clear.

### ITS-ROADMAP-013 - Prevent invalid skill frontmatter from shipping

**Status:** Candidate
**Work Type:** Maintenance
**Evidence Class:** Repo
**Confidence:** High
**Source Anchors:** `worktree-cleaner/skills/clean-worktrees/SKILL.md:4`; `scripts/skill-hygiene-check.py:181-243`; `RELEASE-GATE.md:42-51`
**Why Now / Why Next / Why Later:** This should be part of the third commit because the repo just produced a loader-visible YAML warning that the current checks did not make obvious early enough. Preventing invalid `SKILL.md` frontmatter is a direct stability gate for every installed plugin.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: reproduce the invalid unquoted bracket argument-hint case in a fixture or sample. Exit: release gate parses skill frontmatter with real YAML semantics, rejects invalid flow-style scalars, and optionally verifies installed-cache copies when a cache path is available. No-go: validator depends on network or mutates installed plugins during normal checks.
**Evidence Required:** Updated frontmatter validation in `scripts/skill-hygiene-check.py` or the release-gate frontmatter checker; fixture covering `argument-hint: [--apply] [--all] [--force]`; passing `scripts/release-gate.sh --mode all --strict`; documented cache-sync expectation if source and installed cache can diverge.
**Dependencies:** Can pair with `ITS-ROADMAP-010` because both strengthen hygiene enforcement.
**Risk:** low - the validation target is narrow, but the parser must remain compatible with existing quoted and unquoted scalar frontmatter fields.

## Recommended Three-Commit Shape

1. Commit 1: `ITS-ROADMAP-008` - refactor `idea-to-ship:implement` around existing workflow contracts and templates.
2. Commit 2: `ITS-ROADMAP-009` - extract `issue-evaluator:evaluate-issue` prompts/templates and keep its output contract stable.
3. Commit 3: `ITS-ROADMAP-010` + `ITS-ROADMAP-013`, with `ITS-ROADMAP-011` or `ITS-ROADMAP-012` only if the diff stays small - enforce the cleanup pattern and prevent invalid skill frontmatter from reaching installed plugin load.

Recommended priority order: `ITS-ROADMAP-008`, `ITS-ROADMAP-009`, then `ITS-ROADMAP-010` + `ITS-ROADMAP-013`. If the third commit remains small enough, include `ITS-ROADMAP-011` or `ITS-ROADMAP-012`; otherwise keep agent-playbook extraction for the next roadmap slice.

## Unverified Signals

- No empirical token measurements were taken; expected token savings are inferred from line counts and inline prompt/template repetition.
- GitHub and TODO signals were intentionally excluded, so external priorities may override this local-only view.
- The old `.agent-playbook/current/skill-complexity-audit.md` is ignored and was not treated as source of truth.
- Existing roadmap fixture behavior still expects structured `ITS-*` items; this candidate brief keeps that structure while avoiding final lanes.
- The cache warning was observed from the installed plugin cache; source validation should prevent recurrence, but cache drift may still need an explicit sync/check step.

## Conflicts And Tradeoffs

- The previous roadmap is complete and targeted a four-week sustainability horizon; the current request supersedes it for the next three commits.
- Extracting templates lowers repeated prompt bulk but can make behavior harder to inspect from a single file. Each extraction should keep exact template paths and output fields in the skill body.
- Strict hygiene should catch repeated text without making normal skill editing noisy.

## Open Decisions

| Decision | Options | Recommended Option | Decision Owner | Needed By | Impact If Delayed |
|---|---|---|---|---|---|
| Approve candidate ordering for final lanes? | A: 008, 009, then 010+013; B: 013 first, then cleanup; C: focus on one plugin only | A | User | Before writing final Now/Next/Later lanes or starting implementation | Work can begin from the recommendation, but the roadmap should not claim final priority approval. |
| How strict should moderate-bloat hygiene be? | A: advisory only over 300 lines; B: strict over 400 lines; C: keep only current 750-line limit | A to start | User | Before `ITS-ROADMAP-010` implementation | Too strict creates noise; too loose lets token-heavy skills keep growing. |
| Should token savings be measured before and after? | A: estimate by lines only; B: add a lightweight prompt-size/token budget script; C: defer measurement | B | User | Before or during commit 3 | Without measurement, improvements remain qualitative. |

## Rejected / Not Roadmap-Relevant

- Broadly renaming existing skills for nicer taxonomy: rejected for compatibility risk.
- Removing safety gates to shorten text: rejected because stability is part of the goal.
- Making GitHub/TODO scans mandatory for this refresh: rejected because the current request asked for a local next-3-commit plan.
- Committing ignored `.agent-playbook/current/` generated reports: rejected because the repo now intentionally ignores that local scratch path.

## Acceptance Checks

- Candidate-only run: this refresh writes a Candidate Brief and keeps `final_lanes_written: "no"`.
- Artifact safety: generated content remains inside `idea-to-ship:roadmap` markers, with human-owned sections explicit above the marker.
- Structure: candidate items use the same `ITS-*` fields required by the existing roadmap artifact fixture.
- Next action: approve or edit the recommended three-commit ordering before converting candidates into final lanes.

<!-- idea-to-ship:roadmap generated:end -->
