---
goal: "记录 roadmap 转外部项目管理工具 issue 列表能力到 idea-to-ship portfolio roadmap"
horizon: "candidate brief only until final priority and implementation horizon are approved"
generated_at: "2026-06-17 10:16 CST"
repo_head: "16bc4f6c5984aec8fbcd57141819d633c3375417"
dirty_worktree: "roadmap edit requested by user; existing workspace may contain unrelated changes"
mode: "portfolio"
source_scope: "current user request + multi-agent brainstorm + local roadmap/contract/template evidence; no live Linear/GitLab/GitHub access"
write_target: ".idea-to-ship/roadmap.md"
final_lanes_written: "no; candidate brief updated only"
priority_approval: "ITS-ROADMAP-023 intake approved by current user request; final lane priority and horizon still not provided"
---

# Roadmap - Workflow Router Intake And Prior Skill Work

## Human-Owned Sections

### Current Refresh Request - 2026-06-17

- User requested: support converting `idea-to-ship` roadmap output into
  external project-management tool issue lists, including Linear and GitLab,
  record the capability in the current roadmap, and use multi-agent
  brainstorming to think through best practices.
- Multi-agent conclusion: the safest first capability is export-only local
  issue-list generation with stable roadmap IDs, field mapping, loss/conflict
  reporting, and provider-specific import artifacts. Direct Linear/GitLab
  writes, sync, or write-back should be separate, explicit-authorization
  follow-up stages.
- Roadmap action: track this as `ITS-ROADMAP-023` in the candidate brief. Do
  not write final Now / Next / Later lanes until priority and implementation
  horizon are explicitly approved.

### Current Refresh Request - 2026-06-02

- User requested: sync the current workflow-router task into the
  `idea-to-ship` roadmap.
- Current task: add `$agent-playbook:workflow-router` as the Start Here route
  card for choosing and sequencing existing plugin workflows.
- Current implementation state: local diff adds the new skill, metadata,
  README / SKILLS catalog entries, marketplace descriptions, and
  agent-playbook fixture coverage.
- Review status: user-provided review found two P2 routing bugs that must be
  resolved before marking the roadmap item complete:
  route pre-commit hook installation to
  `$secret-scanner:install-precommit-hook`, and replace
  `$harness-engineering:*` with concrete harness-engineering skills.
- Roadmap action: track this as `ITS-ROADMAP-022` in the candidate brief. Do
  not write final Now / Next / Later lanes until priority and horizon are
  explicitly approved.

### Current Refresh Request - 2026-05-27

- User requested: add `https://github.com/steipete/agent-scripts/blob/main/skills/skill-cleaner/SKILL.md` as a roadmap reference and decide which existing skill/plugin boundary should absorb it.
- Explicit goal: evaluate `skill-cleaner` as a portable skill cleanup capability for this plugin marketplace.
- Horizon is not explicit in the request; final Now / Next / Later lanes remain blocked until a horizon and candidate priority are approved.
- User decision after intake: extend the existing `skill-stats` workflow rather than adding a separate public skill.
- User decision after intake: wrap the external analyzer rather than porting or rewriting it in the first pass.
- User decision after intake: support both report-only mode and an explicit confirmation-gated apply mode.
- Recommended integration target: `skill-stats`, expanded carefully so the default behavior remains report-only and any cleanup/write behavior is isolated behind an apply-confirm path.
- Secondary consumers: `agent-playbook:context-audit` and the repo release gate can consume its reports or reuse checks, but they should not own the user-facing cleanup workflow.

### Previous Refresh Request - Kagenti Intake

- User requested: understand the skills under `https://github.com/kagenti/kagenti/tree/main/.claude/skills`, find ideas worth absorbing into the subsequent roadmap, and think through how a visual-test skill should be defined for frontend projects.
- Explicit goal: absorb transferable skill-system patterns and define a frontend visual-testing workflow.
- Horizon is not explicit in the request; final Now / Next / Later lanes remain blocked until a horizon and candidate priorities are approved.
- Existing human-owned sections below are preserved from the previous roadmap refresh.

### Completion Snapshot - 2026-05-17

- Current committed head: `91618937a6f4d649c5b2b57d8b819f7178f7f7c4` (`feat(idea-to-ship): add visual-test workflow`).
- Completed with tracked idea-to-ship artifacts and clean review: `ITS-ROADMAP-009`, `ITS-ROADMAP-010`, `ITS-ROADMAP-012`, `ITS-ROADMAP-013`, `ITS-ROADMAP-014`, `ITS-ROADMAP-015`, and the grouped `ITS-ROADMAP-016-020` implementation.
- `ITS-ROADMAP-016` through `ITS-ROADMAP-019` are closed by the new `$idea-to-ship:visual-test` skill, visual-test templates, review-code handoff, visual matrix/fingerprint rules, and release-gate fixtures.
- `ITS-ROADMAP-020` is closed as a spike, not as a new broad orchestrator: `.idea-to-ship/ITS-ROADMAP-020/orchestration-spike.md` records "adapt narrow intake patterns; reject a broad repo orchestrator."
- `ITS-ROADMAP-008` is closed by the focused 2026-06-01 closure pass under `.idea-to-ship/ITS-ROADMAP-008/`; `ITS-ROADMAP-011` is closed by the focused 2026-06-01 shared-audit-checklist pass under `.idea-to-ship/ITS-ROADMAP-011/`.
- Latest verification recorded before this refresh: `scripts/release-gate.sh --mode staged`, `scripts/release-gate.sh --mode working --strict`, and `scripts/release-gate.sh --mode all --strict` passed for the visual-test implementation.

### Strategic Objective

在整个 `agent-plugins` repo 内，把接下来 3 个 commit 用于稳定性、token 消耗和重复维护的收敛：优先减少长 skill 中重复的路由、prompt、模板和检查清单，同时用 release gate / fixture 防止后续反弹。

### Manual Overrides

- Requested horizon: next 3 commits.
- Requested scope: entire `agent-plugins`.
- Requested optimization goal: stability, lower token use, and less repeated maintenance.
- Roadmap review policy: every roadmap-item review must be adversarial review,
  not a passive summary or rubber-stamp check.
- Priority approval for a new final Now/Next/Later plan is still pending; this file now records a completion snapshot for user-directed work already executed.

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

- Current user request: support roadmap conversion to external project
  management tools such as Linear and GitLab issue lists, record it in the
  current skill roadmap, think through best practices, and use multi-agent
  brainstorming.
- Multi-agent brainstorm outputs in this session:
  product/export mapping, skill-boundary analysis, and safety/idempotency
  analysis.
- Local roadmap ownership and gates:
  `idea-to-ship/skills/roadmap/SKILL.md:16-27`,
  `idea-to-ship/skills/roadmap/SKILL.md:51-59`,
  `idea-to-ship/skills/roadmap/SKILL.md:105-113`,
  `idea-to-ship/skills/roadmap/SKILL.md:221-249`,
  `idea-to-ship/skills/roadmap/SKILL.md:271-283`, and
  `idea-to-ship/skills/roadmap/SKILL.md:314-323`.
- Local external-mutation and read-only boundaries:
  `idea-to-ship/WORKFLOW-CONTRACTS.md:104-110`,
  `README.md:32-35`, and `SKILLS.md:7-10`.
- Local roadmap schema and fixture patterns:
  `idea-to-ship/templates/roadmap-item-schema.md:3-36`,
  `idea-to-ship/templates/roadmap-candidate-brief.md:6-23`,
  `tests/idea-to-ship-eval-fixtures.py:56-71`,
  `tests/idea-to-ship-eval-fixtures.py:825-837`, and
  `tests/idea-to-ship-eval-fixtures.py:1312-1372`.
- Current user request: sync the workflow-router task into the idea-to-ship
  portfolio roadmap.
- Current workflow-router diff: `agent-playbook/skills/workflow-router/SKILL.md:1-169`,
  `agent-playbook/skills/workflow-router/agents/openai.yaml:1-4`,
  `README.md:42-65`, `SKILLS.md:12-47`,
  `agent-playbook/README.md:36-40`,
  `.claude-plugin/marketplace.json:32-35`,
  `agent-playbook/.claude-plugin/plugin.json:1-7`, and
  `tests/agent-playbook-eval-fixtures.py:237-287`.
- User-provided review comments for the current workflow-router diff: P2 route
  hook-install requests to `$secret-scanner:install-precommit-hook`; P2 replace
  `$harness-engineering:*` with concrete harness-engineering skills so
  `next_prompt` remains copy-pasteable.
- Current user request: add steipete `skill-cleaner` as a roadmap reference and decide which existing skill/plugin boundary should absorb it.
- steipete `skill-cleaner` skill file: `https://github.com/steipete/agent-scripts/blob/main/skills/skill-cleaner/SKILL.md#L1-L56` for trigger scope, analyzer invocation, report categories, Codex-like skill rendering assumptions, usage-log heuristics, and output policy.
- Local `skill-stats` ownership and constraints: `skill-stats/skills/skill-stats/SKILL.md:11-47`, `skill-stats/WORKFLOW-CONTRACTS.md:7-24`, `skill-stats/scripts/track-skill.sh:1-25`, `README.md:106-110`, and `PORTFOLIO.md:55`.
- Local adjacent boundaries: `agent-playbook/skills/context-audit/SKILL.md:40-67` and `agent-playbook/skills/context-audit/SKILL.md:123-128` for context/tool-sprawl audit scope; `agent-playbook/skills/tool-review/SKILL.md:173-174` for suite-level tool sprawl routing; `scripts/skill-hygiene-check.py:224-259` and `RELEASE-GATE.md:56-63` for repo-local skill hygiene and topology checks.
- Current user request: analyze Kagenti `.claude/skills`, identify reusable ideas, update the future roadmap, and define a frontend visual-test skill.
- Kagenti skill tree from `https://github.com/kagenti/kagenti/tree/main/.claude/skills`; remote recursive tree snapshot downloaded to `/private/tmp/kagenti-tree.json`.
- Kagenti README: `.claude/skills/README.md:24-30` for parent-skill routing and sandbox/management boundaries; `.claude/skills/README.md:94-120` for the test workflow; `.claude/skills/README.md:311-410` for the complete skill tree, auto-approve policy, and generated README maintenance.
- Kagenti skill meta workflow: `.claude/skills/skills:scan/SKILL.md:103-180` for existing-skill validation, gap analysis, connection analysis, and usefulness scoring; `.claude/skills/skills:scan/SKILL.md:224-236` for regenerating skill tree diagrams and auto-approve docs.
- Kagenti skill authoring and validation: `.claude/skills/skills:write/SKILL.md:46-83`, `.claude/skills/skills:write/SKILL.md:85-146`, `.claude/skills/skills:write/SKILL.md:177-244`; `.claude/skills/skills:validate/SKILL.md:14-42` and `.claude/skills/skills:validate/SKILL.md:44-130`.
- Kagenti frontend / Playwright samples: `.claude/skills/test:ui/SKILL.md:1-11`, `.claude/skills/test:ui/SKILL.md:75-95`, `.claude/skills/test:ui/SKILL.md:138-155`; `.claude/skills/test:playwright/SKILL.md:42-56`, `.claude/skills/test:playwright/SKILL.md:103-154`; `.claude/skills/test:ui-sandbox/SKILL.md:36-50`, `.claude/skills/test:ui-sandbox/SKILL.md:72-120`.
- Kagenti testing and RCA patterns: `.claude/skills/test:review/SKILL.md:17-47`, `.claude/skills/tdd:ui-hypershift/SKILL.md:40-73`, `.claude/skills/rca:ci/SKILL.md:10-27`, `.claude/skills/rca:ci/SKILL.md:90-177`, `.claude/skills/rca:ci/SKILL.md:213-233`.
- Kagenti orchestration / matrix loop samples: `.claude/skills/orchestrate/SKILL.md:41-120`, `.claude/skills/orchestrate:plan/SKILL.md:39-76`, `.claude/skills/orchestrate:tests/SKILL.md:25-115`, `.claude/skills/graph-loop/SKILL.md:11-31`, `.claude/skills/graph-loop/SKILL.md:115-177`.
- Local skill contracts: `idea-to-ship/skills/ui-design/SKILL.md:168-189`, `idea-to-ship/skills/test/SKILL.md:122-124`, `idea-to-ship/skills/test/SKILL.md:214-217`, `idea-to-ship/skills/review-code/SKILL.md:40-42`, `idea-to-ship/skills/review-code/SKILL.md:109-112`, `idea-to-ship/skills/tdd/SKILL.md:125-130`, `idea-to-ship/skills/tdd/SKILL.md:195-196`.
- Current repo inventory and hygiene hooks: `README.md:42-115`; `scripts/skill-hygiene-check.py:19-25`, `scripts/skill-hygiene-check.py:181-243`.
- Previously approved local cleanup candidates are retained; this status refresh marks artifact-closed items complete, including `ITS-ROADMAP-008` and `ITS-ROADMAP-011`.

Excluded sources:

- Live Linear, GitLab, GitHub, Jira, or other project-management APIs.
- Current Linear/GitLab API documentation and provider-specific field limits;
  those belong in `ITS-ROADMAP-023` requirements/architecture before
  implementation.
- Existing external issue trackers, milestones, labels, assignees, or team
  configuration.
- External `skill-cleaner` analyzer implementation under `scripts/skill-cleaner.ts`; this run used only the user-provided `SKILL.md` reference, so implementation effort, license fit, and exact parser behavior remain open.
- GitHub issues, PRs, milestones, and discussions in both repos.
- TODO/FIXME scan and git-history mining.
- Full deep read of every Kagenti domain skill; sampled high-signal skills by category instead.
- Subagent exploration, because the current request did not explicitly authorize non-review delegation and the source scope was manageable sequentially.

### Candidate Work

| ID | Title | Status | Work Type | Evidence Class | Confidence | Source Anchors | Suggested Action |
|---|---|---|---|---|---|---|---|
| ITS-ROADMAP-008 | Collapse `idea-to-ship:implement` routing and log-template repetition into shared contracts/templates. | Completed | Maintenance | Repo | High | `idea-to-ship/skills/implement/SKILL.md`; `idea-to-ship/templates/implementation-log.md`; `idea-to-ship/WORKFLOW-CONTRACTS.md:98-136`; `.idea-to-ship/ITS-ROADMAP-008/code-review.md` | Closed with focused closure artifacts, template contract tightening, and passing idea-to-ship fixtures. |
| ITS-ROADMAP-009 | Extract `issue-evaluator:evaluate-issue` long adversarial prompts and report template. | Completed | Maintenance | Repo | High | `issue-evaluator/skills/evaluate-issue/SKILL.md:128-187`; `issue-evaluator/skills/evaluate-issue/SKILL.md:194-280`; `issue-evaluator/WORKFLOW-CONTRACTS.md:6-84`; `.idea-to-ship/ITS-ROADMAP-009/code-review.md` | Closed with clean multi-angle review. |
| ITS-ROADMAP-010 | Add hygiene checks for repeated inline prompts/templates and moderate skill bloat. | Completed | Maintenance | Repo | Medium | `scripts/skill-hygiene-check.py:19-25`; `scripts/skill-hygiene-check.py:181-243`; `RELEASE-GATE.md:42-51`; `.idea-to-ship/ITS-ROADMAP-010/code-review.md` | Closed with repeated-prompt/template, bloat, and release-gate fixture coverage. |
| ITS-ROADMAP-011 | Extract shared audit/safety checklist used by tool-review, context-audit, vibe health, and antifragile-agent. | Completed | Maintenance | Repo | Medium | `agent-playbook/WORKFLOW-CONTRACTS.md`; `tests/agent-playbook-eval-fixtures.py`; `.idea-to-ship/ITS-ROADMAP-011/code-review.md` | Closed with explicit shared-checklist citations, section-bounded fixture coverage, and clean adversarial review. |
| ITS-ROADMAP-012 | Normalize agent-playbook audit report templates into `templates/`. | Completed | Maintenance | Repo | Medium | `agent-playbook/skills/tool-review/SKILL.md:146-180`; `agent-playbook/skills/context-audit/SKILL.md:116-158`; `agent-playbook/skills/vibe-coding-health-check/SKILL.md:145-190`; `.idea-to-ship/ITS-ROADMAP-012/code-review.md` | Closed with template extraction and clean multi-angle review. |
| ITS-ROADMAP-013 | Strengthen skill frontmatter validation against real loader YAML semantics and installed-cache drift. | Completed | Maintenance | Repo | High | `worktree-cleaner/skills/clean-worktrees/SKILL.md:4`; `scripts/skill-hygiene-check.py:181-243`; `RELEASE-GATE.md:42-51`; `.idea-to-ship/ITS-ROADMAP-013/code-review.md` | Closed with YAML frontmatter gate and fixtures. |
| ITS-ROADMAP-014 | Add skill topology scan and connection analysis. | Completed | Maintenance | Repo | High | Kagenti `.claude/skills/skills:scan/SKILL.md:103-180`; Kagenti `.claude/skills/skills:scan/SKILL.md:224-236`; `scripts/skill-topology-scan.py`; `.idea-to-ship/ITS-ROADMAP-014/code-review.md` | Closed with read-only topology scanner, fixtures, and release-gate integration. |
| ITS-ROADMAP-015 | Import stronger skill authoring / validation standards. | Completed | Maintenance | Repo | High | Kagenti `.claude/skills/skills:write/SKILL.md:46-83`; Kagenti `.claude/skills/skills:validate/SKILL.md:14-42`; `.idea-to-ship/ITS-ROADMAP-015/code-review.md` | Closed with authoring-standard hygiene checks and tests. |
| ITS-ROADMAP-016 | Create a frontend visual-test skill. | Completed | Feature | Explicit | High | User request; `idea-to-ship/skills/visual-test/SKILL.md`; `.idea-to-ship/ITS-ROADMAP-016-020/code-review.md` | Closed by `$idea-to-ship:visual-test`. |
| ITS-ROADMAP-017 | Add a frontend selector and state recipe template. | Completed | Maintenance | Repo | Medium | `idea-to-ship/templates/visual-test-selectors.md`; `.idea-to-ship/ITS-ROADMAP-016-020/test-plan.md` | Closed by selector/state template and visual-test workflow references. |
| ITS-ROADMAP-018 | Add context-safe CI and Playwright artifact RCA guidance. | Completed | Maintenance | Repo | Medium | `idea-to-ship/templates/visual-artifact-rca.md`; `idea-to-ship/skills/visual-test/SKILL.md` | Closed by bounded artifact RCA template and visual-test gates. |
| ITS-ROADMAP-019 | Add matrix-driven verification loops for visual and multi-env checks. | Completed | Feature | Repo | Medium | `idea-to-ship/templates/visual-test-matrix.md`; `.idea-to-ship/ITS-ROADMAP-016-020/architecture.md` | Closed by visual matrix template, carry-forward rules, and fixture coverage. |
| ITS-ROADMAP-020 | Evaluate a repo orchestration / bootstrap skill. | Spike complete | Spike | Repo | Medium | `.idea-to-ship/ITS-ROADMAP-020/orchestration-spike.md`; `tests/agent-playbook-eval-fixtures.py` | Closed as "adapt narrow intake patterns; reject broad repo orchestrator." |
| ITS-ROADMAP-021 | Extend `skill-stats` with steipete `skill-cleaner` via an external-wrapper analyzer. | Completed | Feature | Explicit | High | User request; user decisions: expand existing, external wrapper, report-only plus confirmation-gated apply; `https://github.com/steipete/agent-scripts/blob/main/skills/skill-cleaner/SKILL.md#L8-L56`; `skill-stats/skills/skill-stats/SKILL.md`; `skill-stats/WORKFLOW-CONTRACTS.md`; `.idea-to-ship/ITS-ROADMAP-021/code-review.md` | Closed with local wrapper, report/preflight/apply fixtures, public contract/docs updates, release-gate wiring, and clean adversarial review. |
| ITS-ROADMAP-022 | Add `$agent-playbook:workflow-router` as a Start Here route card and fix review-discovered routing gaps. | In progress | Feature | Explicit | High | User request; `agent-playbook/skills/workflow-router/SKILL.md:1-169`; `README.md:42-65`; `SKILLS.md:12-47`; `tests/agent-playbook-eval-fixtures.py:237-287`; user-provided P2 review comments | Fix hook-install routing to `$secret-scanner:install-precommit-hook`, replace `$harness-engineering:*` with concrete harness skills, update fixture coverage, and rerun strict release gates. |
| ITS-ROADMAP-023 | Export `idea-to-ship` roadmaps to Linear/GitLab-ready issue lists. | Candidate | Feature | Explicit | High | User request; multi-agent brainstorm; `idea-to-ship/skills/roadmap/SKILL.md:16-27`; `idea-to-ship/skills/roadmap/SKILL.md:51-59`; `idea-to-ship/templates/roadmap-item-schema.md:3-36`; `idea-to-ship/WORKFLOW-CONTRACTS.md:104-110`; `tests/idea-to-ship-eval-fixtures.py:825-837` | Run `/brainstorm --slug ITS-ROADMAP-023` to define export-only MVP, provider field mapping, local artifact format, item eligibility rules, and post-MVP sync/write-back authorization gates. |

### ITS-ROADMAP-008 - Collapse idea-to-ship implement repetition

**Status:** Completed
**Work Type:** Maintenance
**Evidence Class:** Repo
**Confidence:** High
**Source Anchors:** `idea-to-ship/skills/implement/SKILL.md:199-229`; `idea-to-ship/skills/implement/SKILL.md:231-259`; `idea-to-ship/skills/implement/SKILL.md:293-317`; `idea-to-ship/WORKFLOW-CONTRACTS.md:98-136`
**Why Now / Why Next / Why Later:** Completed with a focused closure pass because `implement` is central and now explicitly delegates shared routing to `WORKFLOW-CONTRACTS.md` and implementation-log field shape to `templates/implementation-log.md`.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: current `implement` behavior and output contract are captured. Exit: repeated routing/log-field detail is represented by shared contract/template references, fixtures pass, and no public skill name changes. No-go: removing safety routing or weakening TDD/review gates for brevity.
**Evidence Required:** Satisfied by updated `idea-to-ship/skills/implement/SKILL.md`, updated `idea-to-ship/templates/implementation-log.md`, `tests/idea-to-ship-eval-fixtures.sh` passing, and `.idea-to-ship/ITS-ROADMAP-008/` closure artifacts. Full strict release gate remains environment-blocked locally by missing `PyYAML`.
**Dependencies:** Existing `idea-to-ship/WORKFLOW-CONTRACTS.md`.
**Risk:** medium - reducing prompt text can accidentally remove a behavioral gate unless the contract reference is explicit and fixture coverage remains green.

### ITS-ROADMAP-009 - Extract issue-evaluator evaluate prompts

**Status:** Completed
**Work Type:** Maintenance
**Evidence Class:** Repo
**Confidence:** High
**Source Anchors:** `issue-evaluator/skills/evaluate-issue/SKILL.md:128-187`; `issue-evaluator/skills/evaluate-issue/SKILL.md:194-263`; `issue-evaluator/skills/evaluate-issue/SKILL.md:267-280`; `issue-evaluator/WORKFLOW-CONTRACTS.md:6-84`
**Why Now / Why Next / Why Later:** Completed as part of the local cleanup sequence by extracting `evaluate-issue` prompts/templates while preserving the output contract and read-only GitHub behavior.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: current prompt phases and final report fields are preserved. Exit: skill body references prompt/template artifacts, output contract remains unchanged, and issue-evaluator fixtures pass. No-go: changing GitHub read-only behavior or silently dropping multi-angle review steps.
**Evidence Required:** Updated `issue-evaluator/skills/evaluate-issue/SKILL.md`; prompt/template files under `issue-evaluator/prompts/` and/or `issue-evaluator/templates/`; passing `tests/agent-playbook-eval-fixtures.sh` or the relevant issue-evaluator fixture if present; strict release gate result.
**Dependencies:** Existing `issue-evaluator/WORKFLOW-CONTRACTS.md`.
**Risk:** medium - prompt extraction reduces visible context in `SKILL.md`, so references must be exact and fixtures should check required phases still exist.

### ITS-ROADMAP-010 - Add repetition and bloat hygiene checks

**Status:** Completed
**Work Type:** Maintenance
**Evidence Class:** Repo
**Confidence:** Medium
**Source Anchors:** `scripts/skill-hygiene-check.py:19-25`; `scripts/skill-hygiene-check.py:181-243`; `RELEASE-GATE.md:42-51`
**Why Now / Why Next / Why Later:** Completed after extraction work so the release gate now enforces repeated-prompt/template and moderate-bloat hygiene instead of relying on manual review.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: define non-brittle signals for repeated inline prompts/templates and moderate-size skill bodies. Exit: hygiene check reports actionable advisory failures in `--strict` mode without punishing legitimate concise skills. No-go: exact prose golden-file checks that make normal wording edits noisy.
**Evidence Required:** Updated `scripts/skill-hygiene-check.py`; fixture/sample coverage for repeated prompt/template markers; `scripts/release-gate.sh --mode all --strict`.
**Dependencies:** Prefer after `ITS-ROADMAP-008` or `ITS-ROADMAP-009` so the rule can be tuned against real cleanup.
**Risk:** medium - too-strict thresholds create false positives; too-loose thresholds do not stop drift.

### ITS-ROADMAP-011 - Extract shared audit and safety checklist

**Status:** Completed
**Work Type:** Maintenance
**Evidence Class:** Repo
**Confidence:** Medium
**Source Anchors:** `agent-playbook/skills/tool-review/SKILL.md:89-138`; `agent-playbook/skills/context-audit/SKILL.md:68-115`; `agent-playbook/skills/vibe-coding-health-check/SKILL.md:108-130`; `README.md:48-59`
**Why Now / Why Next / Why Later:** Completed with a focused closure pass because audit skills overlap by design, but their shared safety and eval criteria should be maintained once instead of duplicated across several skill bodies.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: identify shared checklist items that are truly common and keep skill-specific criteria local. Exit: shared checklist file is cited from each audit skill, and each skill keeps a short boundary-focused local checklist. No-go: forcing all audit skills into one generic checklist that loses domain-specific judgment.
**Evidence Required:** Satisfied by `agent-playbook/WORKFLOW-CONTRACTS.md`, updated audit skill references, section-bounded `tests/agent-playbook-eval-fixtures.py` coverage, passing strict release gate, and `.idea-to-ship/ITS-ROADMAP-011/code-review.md`.
**Dependencies:** Can pair with `ITS-ROADMAP-010` if the hygiene check watches for duplicated checklist headings.
**Risk:** medium - over-extraction can hide the differences between context hygiene, tool review, vibe health, and antifragile audits.

### ITS-ROADMAP-012 - Normalize agent-playbook audit templates

**Status:** Completed
**Work Type:** Maintenance
**Evidence Class:** Repo
**Confidence:** Medium
**Source Anchors:** `agent-playbook/skills/tool-review/SKILL.md:146-180`; `agent-playbook/skills/context-audit/SKILL.md:116-158`; `agent-playbook/skills/vibe-coding-health-check/SKILL.md:145-190`; `.gitignore:2`
**Why Now / Why Next / Why Later:** Completed by moving agent-playbook audit report structure into templates while keeping `.agent-playbook/current/` ignored and local-only.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: current audit outputs and generated markers are known. Exit: templates live outside long skill bodies and report-writing rules still distinguish read-only analysis from local artifact writes. No-go: committing generated `.agent-playbook/current/` reports or changing read-only semantics.
**Evidence Required:** New or updated `agent-playbook/templates/` files; updated audit skills; passing `tests/agent-playbook-eval-fixtures.sh`; strict release gate result.
**Dependencies:** Strongly related to `ITS-ROADMAP-011`.
**Risk:** low - mostly documentation/template movement, but output contract wording must stay clear.

### ITS-ROADMAP-013 - Prevent invalid skill frontmatter from shipping

**Status:** Completed
**Work Type:** Maintenance
**Evidence Class:** Repo
**Confidence:** High
**Source Anchors:** `worktree-cleaner/skills/clean-worktrees/SKILL.md:4`; `scripts/skill-hygiene-check.py:181-243`; `RELEASE-GATE.md:42-51`
**Why Now / Why Next / Why Later:** Completed as a high-priority stability gate after the repo exposed a loader-visible YAML warning that needed real frontmatter parsing.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: reproduce the invalid unquoted bracket argument-hint case in a fixture or sample. Exit: release gate parses skill frontmatter with real YAML semantics, rejects invalid flow-style scalars, and optionally verifies installed-cache copies when a cache path is available. No-go: validator depends on network or mutates installed plugins during normal checks.
**Evidence Required:** Updated frontmatter validation in `scripts/skill-hygiene-check.py` or the release-gate frontmatter checker; fixture covering `argument-hint: [--apply] [--all] [--force]`; passing `scripts/release-gate.sh --mode all --strict`; documented cache-sync expectation if source and installed cache can diverge.
**Dependencies:** Can pair with `ITS-ROADMAP-010` because both strengthen hygiene enforcement.
**Risk:** low - the validation target is narrow, but the parser must remain compatible with existing quoted and unquoted scalar frontmatter fields.

## Preserved Local Cleanup Sequence

1. `ITS-ROADMAP-009`, `ITS-ROADMAP-010`, `ITS-ROADMAP-012`, and `ITS-ROADMAP-013` are complete and reviewed.
2. `ITS-ROADMAP-014` and `ITS-ROADMAP-015` are complete and reviewed.
3. `ITS-ROADMAP-016-020` is complete and reviewed, with `ITS-ROADMAP-020` closed as a spike decision rather than a new orchestrator skill.
4. `ITS-ROADMAP-008` is complete and reviewed with closure artifacts.
5. `ITS-ROADMAP-011` is complete and reviewed with closure artifacts.

Recommended next action is to resolve the `ITS-ROADMAP-022` review comments
before closing workflow-router work. For the new external-PM roadmap capability,
run `/brainstorm --slug ITS-ROADMAP-023` before design or implementation.

### ITS-ROADMAP-014 - Add skill topology scan and connection analysis

**Status:** Completed
**Work Type:** Maintenance
**Evidence Class:** Repo
**Confidence:** High
**Source Anchors:** Kagenti `.claude/skills/skills:scan/SKILL.md:103-180`; Kagenti `.claude/skills/skills:scan/SKILL.md:224-236`; `README.md:42-115`; `scripts/skill-hygiene-check.py:181-243`
**Why Now / Why Next / Why Later:** Completed by adding a read-only topology scanner that reports inventory, broken references, orphan skills, hubs, skill-tree output, and README coverage gaps.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: define local inventory schema for plugin, skill, parent/leaf, related links, and referenced skills. Exit: a deterministic scan produces a markdown report and optional README fragment without requiring network access. No-go: treating graph metrics as deletion authority without human review.
**Evidence Required:** Updated scan/hygiene script or a new read-only report command; fixture for broken refs and orphan skills; strict release gate or dedicated test result.
**Dependencies:** Existing `scripts/skill-hygiene-check.py`.
**Risk:** medium - graph reports can create noisy churn unless generated sections and stable ordering are enforced.

### ITS-ROADMAP-015 - Import stronger skill authoring / validation standards

**Status:** Completed
**Work Type:** Maintenance
**Evidence Class:** Repo
**Confidence:** High
**Source Anchors:** Kagenti `.claude/skills/skills:write/SKILL.md:46-83`; Kagenti `.claude/skills/skills:write/SKILL.md:85-146`; Kagenti `.claude/skills/skills:write/SKILL.md:177-244`; Kagenti `.claude/skills/skills:validate/SKILL.md:14-42`; `scripts/skill-hygiene-check.py:19-25`
**Why Now / Why Next / Why Later:** Completed after topology work by adding stronger authoring-standard checks for new or changed skills.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: choose which Kagenti standards map to this repo's runtime: command safety, task tracking, diagram-text match, related-skill links, and length budget. Exit: local validator catches missing required metadata, broken related links, unsafe command examples, and missing workflow diagrams where applicable. No-go: forcing Claude-specific auto-approve assumptions onto Codex/plugin runtimes without translation.
**Evidence Required:** Updated skill-creation guidance and validator fixtures; run local release gate.
**Dependencies:** `ITS-ROADMAP-014` improves the related-link and diagram coverage checks, but this can start independently.
**Risk:** medium - Kagenti's command rules are Claude Code-specific, so the local version must express runtime-neutral safety where possible.

### ITS-ROADMAP-016 - Create a frontend visual-test skill

**Status:** Completed
**Work Type:** Feature
**Evidence Class:** Explicit
**Confidence:** High
**Source Anchors:** User request; Kagenti `.claude/skills/test:ui/SKILL.md:1-11`; Kagenti `.claude/skills/test:ui/SKILL.md:75-95`; Kagenti `.claude/skills/test:ui/SKILL.md:138-155`; Kagenti `.claude/skills/test:playwright/SKILL.md:42-56`; Kagenti `.claude/skills/test:playwright/SKILL.md:143-154`; `idea-to-ship/skills/ui-design/SKILL.md:168-189`; `idea-to-ship/skills/test/SKILL.md:214-217`; `idea-to-ship/skills/review-code/SKILL.md:40-42`
**Why Now / Why Next / Why Later:** Completed by adding `$idea-to-ship:visual-test` as the dedicated workflow for collecting visual evidence, comparing baselines, and triaging visual regressions.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: decide whether the skill lives under `idea-to-ship` as `visual-test`, under a new frontend plugin, or as an agent-playbook frontend audit skill. Exit: the skill defines inputs, baseline policy, viewport/state matrix, Playwright commands, artifact paths, and hand-off report schema. No-go: visual screenshots with no functional assertions or no baseline update policy.
**Evidence Required:** New skill `SKILL.md` plus template(s), fixture/sample visual-test report, and a local acceptance test that checks required gates are present.
**Dependencies:** Existing `ui-design`, `test`, `tdd`, and `review-code` visual QA references.
**Risk:** medium - screenshot tests are brittle if fonts, time, animation, network, or seed data are not controlled.

#### Proposed Frontend Visual-Test Skill Definition

**Name:** `frontend:visual-test` if a frontend plugin is created; otherwise `idea-to-ship:visual-test` if it is scoped to idea-to-ship slugs.

**Trigger:** Use after frontend UI changes, when `interface-design.md` has a Visual QA Plan, when a user asks for visual regression / screenshot verification, or before `review-code` gives a UI/UX verdict on a UI diff.

**Inputs:** app root, dev-server command or URL, routes/screens, required auth/seed state, design source (`interface-design.md`, Figma, screenshot, or project `DESIGN.md`), baseline mode (`create`, `compare`, `update-requested`), browsers, viewports, themes, and states.

**Workflow:**
1. Discover existing UI tooling: Playwright, Storybook, Cypress, Vitest browser mode, screenshot baselines, package scripts, and CI artifacts.
2. Resolve the design contract: map `interface-design.md` Visual QA Plan to a matrix of screen x state x viewport x theme.
3. Stabilize the run: deterministic data, fixed time, disabled animations/reduced motion, loaded fonts/assets, mocked third-party APIs where appropriate, no console errors, and no failed network requests.
4. Assert before capture: visible route landmarks, required content, accessibility/role selectors, loading completion, and interaction-state preconditions. Screenshots must not be the only assertion.
5. Capture and compare: use Playwright screenshot assertions where available, store artifacts under a deterministic report directory, and require user/design approval before updating baselines.
6. Triage diffs: classify as product regression, intentional design change needing baseline update, environment flake, or out-of-scope. Record exact screenshot/report paths and the reason.
7. Write hand-off: update `test-plan.md` or write `visual-test-report.md` with matrix coverage, failed diffs, baseline decisions, manual checks, and remaining visual risks.

**Hard gates:** no happy-path-only screenshots; no baseline from a visibly broken screen; no silent baseline update; no viewport text overlap; no screenshot after unresolved loading; no ignored console/network failures unless explicitly justified.

### ITS-ROADMAP-017 - Add a frontend selector and state recipe template

**Status:** Completed
**Work Type:** Maintenance
**Evidence Class:** Repo
**Confidence:** Medium
**Source Anchors:** Kagenti `.claude/skills/test:ui/SKILL.md:75-95`; Kagenti `.claude/skills/test:ui-sandbox/SKILL.md:36-50`; Kagenti `.claude/skills/test:ui-sandbox/SKILL.md:72-120`; Kagenti `.claude/skills/test:playwright/SKILL.md:103-124`
**Why Now / Why Next / Why Later:** Completed with the selector/state recipe template so visual-test runs do not rediscover selectors, auth flows, route transitions, and async output states every time.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: define a template that is project-specific, not a universal selector doctrine. Exit: template captures stable selectors, user-visible states, auth/session notes, known flaky states, and preferred test IDs / roles. No-go: encouraging brittle CSS class selectors when semantic role/test-id selectors exist.
**Evidence Required:** New template file and an example section in the visual-test skill.
**Dependencies:** Best implemented with `ITS-ROADMAP-016`.
**Risk:** low - mostly documentation, but poor examples can normalize brittle selectors.

### ITS-ROADMAP-018 - Add context-safe CI and Playwright artifact RCA guidance

**Status:** Completed
**Work Type:** Maintenance
**Evidence Class:** Repo
**Confidence:** Medium
**Source Anchors:** Kagenti `.claude/skills/rca:ci/SKILL.md:10-27`; Kagenti `.claude/skills/rca:ci/SKILL.md:90-177`; Kagenti `.claude/skills/rca:ci/SKILL.md:213-233`; Kagenti `.claude/skills/test:ui/SKILL.md:147-155`
**Why Now / Why Next / Why Later:** Completed with bounded artifact RCA guidance for screenshot reports, traces, and CI logs so large artifacts are referenced by path/anchor instead of dumped inline.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: identify which local GitHub/CI skills read large logs or Playwright reports. Exit: they download artifacts to files, inspect bounded snippets, and report anchors/summaries instead of raw logs. No-go: adding GitHub write/comment behavior to read-only review workflows.
**Evidence Required:** Updated CI/debug skill guidance and fixture or reviewer checklist for large-artifact handling.
**Dependencies:** Could pair with `ITS-ROADMAP-016` or GitHub CI-fix improvements.
**Risk:** medium - too much indirection can hide key failure lines unless report summaries include precise file/line anchors.

### ITS-ROADMAP-019 - Add matrix-driven verification loops for visual and multi-env checks

**Status:** Completed
**Work Type:** Feature
**Evidence Class:** Repo
**Confidence:** Medium
**Source Anchors:** Kagenti `.claude/skills/graph-loop/SKILL.md:11-31`; Kagenti `.claude/skills/graph-loop/SKILL.md:115-177`; Kagenti `.claude/skills/tdd:ui-hypershift/SKILL.md:40-73`; `idea-to-ship/skills/tdd/SKILL.md:125-130`; `idea-to-ship/skills/tdd/SKILL.md:195-196`
**Why Now / Why Next / Why Later:** Completed with visual matrix fields and carry-forward rules for browser, viewport, route, state, and environment coverage.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: define the smallest matrix format and when carry-forward pass status is valid. Exit: visual-test reports mark PASS/FAIL/FLAKY/MISS/SKIP-with-reason and never treat missing coverage as success. No-go: auto-retry loops that hide real flakes.
**Evidence Required:** Report template plus acceptance fixture with missing, flaky, skipped, and failed cells.
**Dependencies:** Prefer after `ITS-ROADMAP-016`.
**Risk:** medium - matrix tooling can become process-heavy if it is required for small UI changes.

### ITS-ROADMAP-020 - Evaluate a repo orchestration / bootstrap skill

**Status:** Spike complete
**Work Type:** Spike
**Evidence Class:** Repo
**Confidence:** Medium
**Source Anchors:** Kagenti `.claude/skills/orchestrate/SKILL.md:41-120`; Kagenti `.claude/skills/orchestrate:plan/SKILL.md:39-76`; Kagenti `.claude/skills/orchestrate:tests/SKILL.md:25-115`
**Why Now / Why Next / Why Later:** Completed as a spike: narrow intake and handoff patterns were adapted, while a broad repo orchestrator was rejected.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: decide target plugin boundary: `agent-playbook` for repo bootstrap vs `idea-to-ship` for product feature work. Exit: one-page architecture note deciding adopt / reject / adapt, including conflict analysis with existing staged implementation. No-go: copying Kagenti's self-replication pattern wholesale without local plugin packaging and safety gates.
**Evidence Required:** Spike note under `.idea-to-ship/ITS-ROADMAP-020/` or a future requirements doc.
**Dependencies:** None.
**Risk:** medium - broad orchestration can become a backlog generator instead of a focused workflow.

### ITS-ROADMAP-021 - Extend skill-stats with steipete skill-cleaner

**Status:** Completed
**Work Type:** Feature
**Evidence Class:** Explicit
**Confidence:** High
**Source Anchors:** User request; user decisions: expand existing, external wrapper, report-only plus confirmation-gated apply; `https://github.com/steipete/agent-scripts/blob/main/skills/skill-cleaner/SKILL.md#L8-L56`; `skill-stats/skills/skill-stats/SKILL.md:11-47`; `skill-stats/WORKFLOW-CONTRACTS.md:7-24`; `skill-stats/scripts/track-skill.sh:1-25`; `README.md:106-110`; `PORTFOLIO.md:55`
**Why Now / Why Next / Why Later:** The external skill's core signals are installed skill roots, skill usage evidence, duplicates, prompt-budget pressure, description candidates, and cleanup recommendations. That is a direct extension of `skill-stats`, which already owns usage logs and unused-skill reporting. The approved shape is to expand the existing `skill-stats` workflow, wrap the external analyzer, keep report-only as the default path, and support cleanup only behind explicit confirmation. `agent-playbook:context-audit` should remain a repo-context and tool-sprawl audit that can cite this analyzer output, while `scripts/skill-hygiene-check.py` remains the repo release-gate checker for source-controlled skill files.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Closed with accepted requirements, architecture, red-first fixtures, implementation log, and clean adversarial code review. The external-wrapper analyzer/report covers skill budget, duplicates, stale/unused candidates, root summary, description candidates, bounded log/root scans, report-only default behavior, and confirmation-gated apply semantics. No-go items remain enforced: no default deletion/disable behavior, no unbounded personal-directory scans, no silent broad config rewrites, and no release blocker based on personal usage logs.
**Evidence Required:** Complete under `.idea-to-ship/ITS-ROADMAP-021/`: `requirements.md`, `architecture.md`, `design-review.md`, `test-plan.md`, `tdd-log.md`, `implementation-log.md`, and `code-review.md`; focused wrapper fixtures in `tests/skill-stats-cleaner-fixtures.py`; updated `skill-stats/WORKFLOW-CONTRACTS.md`, README, portfolio docs, plugin metadata, and release-gate wiring; passing `scripts/release-gate.sh --mode all --strict`.
**Dependencies:** Existing `skill-stats` usage log and current read-only output contract, which must be split into report-only mode and apply-confirm mode. External `skill-cleaner` script availability/version becomes a runtime dependency unless the architecture provides a vendored or fallback path.
**Risk:** medium - cleanup reports can create false confidence if usage evidence is heuristic, and scanning personal roots/logs can leak noisy local paths unless output is bounded and redacted where needed.

### ITS-ROADMAP-022 - Add agent-playbook workflow-router

**Status:** In progress
**Work Type:** Feature
**Evidence Class:** Explicit
**Confidence:** High
**Source Anchors:** User request to add a workflow-router Start Here entry; user request to sync the current task into roadmap; `agent-playbook/skills/workflow-router/SKILL.md:1-169`; `agent-playbook/skills/workflow-router/agents/openai.yaml:1-4`; `README.md:42-65`; `SKILLS.md:12-47`; `agent-playbook/README.md:36-40`; `.claude-plugin/marketplace.json:32-35`; `agent-playbook/.claude-plugin/plugin.json:1-7`; `tests/agent-playbook-eval-fixtures.py:237-287`; user-provided P2 review comments on hook-install routing and harness wildcard routing.
**Why Now / Why Next / Why Later:** The plugin suite now has many specialized owners, and users need a safe Start Here workflow that selects and sequences existing skills without becoming a broad autopilot. The first implementation adds the new route-card skill, catalog entries, metadata, marketplace text, and fixture coverage, but the user-provided review found two route bugs that affect supported workflows and must be fixed before closure.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: current diff introduces `agent-playbook:workflow-router` as a conversation-only route-card skill plus docs and fixtures. Exit: router outputs copy-pasteable route cards for feature, issue, PR, tool/context audit, resilience, secret scan, worktree cleanup, and commit-readiness requests; pre-commit hook installation routes to `$secret-scanner:install-precommit-hook`; secret scans continue to route to `$secret-scanner:scan-secrets`; harness requests route to concrete skills such as `$harness-engineering:harness-design`, `$harness-engineering:harness-audit`, `$harness-engineering:resilience-plan`, `$harness-engineering:goal-mode`, or `$harness-engineering:sprint-contract`; route-card fixtures cover those distinctions; `bash tests/agent-playbook-eval-fixtures.sh`, `python3 scripts/skill-hygiene-check.py --mode all .`, `python3 scripts/skill-topology-scan.py .`, and `scripts/release-gate.sh --mode all --strict` pass. No-go: wildcard skill names in `next_prompt`, sending mutating hook-install requests to read-only scan workflows, executing downstream skills from the router, or weakening the broad-orchestrator mutation guard.
**Evidence Required:** Updated `agent-playbook/skills/workflow-router/SKILL.md`, `tests/agent-playbook-eval-fixtures.py`, docs/catalog entries if wording changes, and fresh verification after fixing review findings. Prior verification passed before the P2 review comments, so closure requires rerunning gates after those comments are addressed.
**Dependencies:** Existing `agent-playbook` operator workflows, `secret-scanner:scan-secrets`, `secret-scanner:install-precommit-hook`, and concrete `harness-engineering` skills.
**Risk:** medium - the router is user-facing and low-code, so small wording mistakes can send users to the wrong owner or produce non-invocable prompts even when release fixtures pass.

### ITS-ROADMAP-023 - Export idea-to-ship roadmaps to external PM issue lists

**Status:** Candidate
**Work Type:** Feature
**Evidence Class:** Explicit
**Confidence:** High
**Source Anchors:** User request on 2026-06-17 to support roadmap conversion to external project management tools such as Linear and GitLab issue lists; multi-agent brainstorm results in the current session; `idea-to-ship/skills/roadmap/SKILL.md:16-27`; `idea-to-ship/skills/roadmap/SKILL.md:51-59`; `idea-to-ship/skills/roadmap/SKILL.md:105-113`; `idea-to-ship/skills/roadmap/SKILL.md:221-249`; `idea-to-ship/skills/roadmap/SKILL.md:271-283`; `idea-to-ship/templates/roadmap-item-schema.md:3-36`; `idea-to-ship/WORKFLOW-CONTRACTS.md:104-110`; `README.md:32-35`; `SKILLS.md:7-10`; `tests/idea-to-ship-eval-fixtures.py:56-71`; `tests/idea-to-ship-eval-fixtures.py:825-837`.
**Why Now / Why Next / Why Later:** The user explicitly asked for this capability and it has high leverage because `idea-to-ship` roadmaps already carry stable IDs, evidence, release gates, dependencies, and risk fields that map naturally to external issue trackers. Best practice is to start with deterministic export-only local artifacts and loss/conflict reports, then add explicit-authorized sync/write-back only after requirements, provider mapping, idempotency, and safety gates are designed. Because final priority and horizon were not approved, this stays in the Candidate Brief instead of entering Now.
**Owner:** Unassigned
**Decision Owner:** User/maintainer
**Release Gate:** Entry: run `/brainstorm --slug ITS-ROADMAP-023`; approve provider scope, export-only MVP, target field mapping, item eligibility, local artifact paths, and whether Linear/GitLab are first-class targets or examples of a generic provider contract. Exit: deterministic local export artifacts can produce Linear/GitLab-ready issue lists from sourced roadmap items; stable roadmap IDs are preserved as the primary key; exported bodies retain status, work type, evidence class, confidence, source anchors, lane rationale, release gate, evidence required, dependencies, and risk; missing provider mappings produce warnings instead of guessed assignees/projects; weak, unknown, inferred, or unverified items are blocked from executable issue output unless explicitly approved; fixtures cover schema loss, generated-marker preservation, rerun idempotency, duplicate prevention strategy, and provider-free export behavior. No-go: direct Linear/GitLab API writes from `/roadmap`, creating issues from Candidate Backlog or Unverified Signals by default, title-only duplicate detection, guessed assignees/projects/milestones, overwriting remote human content, live-provider tests in the release gate, or sync/write-back without two-phase plan/apply approval.
**Evidence Required:** `.idea-to-ship/ITS-ROADMAP-023/requirements.md`, `architecture.md`, `test-plan.md`, `tdd-log.md`, `implementation-log.md`, and `code-review.md`; focused provider-free export fixtures; fake-provider sync fixtures if sync is implemented; updated roadmap/export templates or skill docs if the public contract changes; `tests/idea-to-ship-eval-fixtures.sh`; and `scripts/release-gate.sh --mode all --strict`.
**Dependencies:** Existing roadmap item schema, generated-marker preservation, brainstorm requirements gate, and external-mutation authorization rules. Post-MVP sync depends on provider configuration, auth handling, stable remote markers/custom fields, and a local sidecar mapping.
**Risk:** high - direct external PM writes can duplicate or mutate team backlogs if stable IDs, search-before-create, conflict detection, and explicit approval gates are missing.

## Unverified Signals

- `ITS-ROADMAP-023` has no accepted requirements yet; this brief records
  direction and safety constraints, not an implementation design.
- No live Linear/GitLab provider access or current provider API documentation
  was used in this refresh; exact provider fields, limits, and auth flows need
  `ITS-ROADMAP-023` requirements and architecture.
- The multi-agent brainstorm recommended export-only first, but target artifact
  paths, formats, and provider matrix are not yet approved.
- The workflow-router implementation has not yet been updated after the
  user-provided P2 review comments in this refresh.
- The external `skill-cleaner` script implementation was not inspected in this roadmap refresh; only its `SKILL.md` contract was used as evidence.
- The user selected an external-wrapper strategy, but the external script implementation, versioning, dependency installation, and license/attribution details still need architecture review.
- The full Kagenti skill tree has roughly one hundred `SKILL.md` leaves; this brief sampled high-signal categories instead of reading every domain-specific Kubernetes/auth skill.
- Kagenti's session analytics skills may be relevant, but this repo already has `skill-stats`; no candidate is promoted until usage-data requirements are explicit.
- Kagenti's domain-specific HyperShift, OpenShift, Kind, Keycloak, and Kubernetes skills are mostly not portable as-is; only their routing, artifact, and test-matrix patterns are candidates here.
- No implementation effort estimate was produced; suggested sequencing should be approved before converting candidates to final lanes.
- No empirical visual-test flake analysis was run against a real frontend repo in this workspace.

## Conflicts

- The current `workflow-router` text groups "pre-commit secret concern" under
  `$secret-scanner:scan-secrets`, but hook installation and enforcement are
  mutating local hook/config work owned by
  `$secret-scanner:install-precommit-hook`. Keep scan/audit requests on
  `$secret-scanner:scan-secrets`; route install/enforce requests to the
  installer.
- The current route catalog emits `$harness-engineering:*` for harness work
  while the route-card contract promises copy-pasteable `next_prompt` values.
  Replace the wildcard with concrete routing to
  `$harness-engineering:harness-design`,
  `$harness-engineering:harness-audit`,
  `$harness-engineering:resilience-plan`, `$harness-engineering:goal-mode`,
  and `$harness-engineering:sprint-contract` by request intent.
- `skill-cleaner` includes cleanup application guidance when asked, including grouped commits and deletion/config-disable recommendations. Local `skill-stats` is currently explicitly read-only and conversation-only; the approved apply-confirm behavior requires a contract update that preserves report-only as the default non-mutating path and labels any apply path as mutating.
- Local `scripts/skill-hygiene-check.py` and skill-topology release-gate checks already cover source-controlled repo skill hygiene. `skill-cleaner` should not duplicate those as another release-gate blocker; it should cover local installed roots, personal roots, and usage-log-informed cleanup.
- The preserved human-owned section above still references the previous "next 3 commits" stability roadmap. This generated brief now keeps those prior candidates and appends Kagenti intake candidates, instead of treating the new scan as a replacement.
- Kagenti assumes Claude Code-specific skill invocation, TaskList, AskUserQuestion, and `.claude/settings.json` auto-approve behavior. Local adoption must translate those ideas to this Codex/plugin repo rather than copying host-specific mechanics.
- A dedicated visual-test skill overlaps with existing `ui-design`, `test`, `tdd`, and `review-code` UI gates. The new skill should execute visual verification, while the existing skills continue to own design contract, story test plan, red-first gates, and code review verdicts.
- External PM sync is valuable, but existing roadmap and cross-skill safety
  rules prevent default external mutation. `ITS-ROADMAP-023` resolves this by
  scoping the first stage to export-only local artifacts and keeping live sync
  or write-back behind explicit plan/apply authorization.

## Resolved And Open Decisions

| Decision | Options | Recommended Option | Decision Owner | Needed By | Impact If Delayed |
|---|---|---|---|---|---|
| How should `workflow-router` route pre-commit secret hook requests? | A: route every secret concern to `$secret-scanner:scan-secrets`; B: route scan/audit to `$secret-scanner:scan-secrets` and install/enforce to `$secret-scanner:install-precommit-hook` | B | User/maintainer | Before `ITS-ROADMAP-022` closure | Wrong owner sends users to a read-only workflow for hook installation. |
| How should `workflow-router` route harness-engineering requests? | A: emit `$harness-engineering:*`; B: select a concrete harness skill by intent | B | User/maintainer | Before `ITS-ROADMAP-022` closure | Wildcard output prevents copy-pasteable `next_prompt` handoff. |
| Does `ITS-ROADMAP-008` need a fresh closure artifact? | Resolved: focused ITS-008 closure pass completed | B was selected | User | Resolved 2026-06-01 | Closure artifacts now exist under `.idea-to-ship/ITS-ROADMAP-008/`. |
| Should `ITS-ROADMAP-011` be implemented? | Resolved: focused shared audit/safety checklist closure completed | A was selected | User | Resolved 2026-06-01 | Closure artifacts now exist under `.idea-to-ship/ITS-ROADMAP-011/`, with section-bounded fixture coverage and clean adversarial review. |
| Where should `skill-cleaner` be integrated? | A: new `skill-stats:skill-cleaner`; B: expand `skill-stats:skill-stats`; C: make it part of `agent-playbook:context-audit`; D: make it a release-gate check | Resolved: B | User | Resolved 2026-05-27 | Implementation should expand existing `skill-stats` while keeping the broadened responsibility explicit in the workflow contract. |
| Which implementation strategy should be used? | A: port/adapt external TypeScript; B: implement local analyzer in the repo's current language/tooling; C: shell out to an external checkout | Resolved: C | User/maintainer | Resolved 2026-05-27 | Architecture must define external script location, version pinning/update policy, missing-dependency fallback, and attribution/licensing expectations. |
| Can cleanup be applied automatically? | A: report-only first; B: optional apply mode later with explicit confirmation; C: immediate delete/disable support | Resolved: A plus B | User | Resolved 2026-05-27 | Default path must remain report-only; apply mode must require explicit confirmation and name every planned edit/delete/disable target first. |
| What should the first external-PM capability be? | A: export-only local issue lists and reports; B: live create/update sync; C: write-back from PM tools to roadmap | A | User/maintainer | Before `ITS-ROADMAP-023` requirements closure | Starting with live sync risks duplicate issues and unintended backlog mutation before the schema, mapping, and approval gates are proven. |
| Which providers and formats are in scope for `ITS-ROADMAP-023`? | A: Linear and GitLab-ready local Markdown/JSONL or CSV artifacts; B: add GitHub/Jira immediately; C: generic provider adapter first | A as the initial requirement candidate | User/maintainer | During `/brainstorm --slug ITS-ROADMAP-023` | Over-broad provider scope will turn a bounded export into a generic backlog orchestrator. |
| How should external writes be authorized after export-only works? | A: never write externally; B: two-phase plan/apply with exact provider scope, action list, and approval hash; C: direct sync from roadmap generation | B for a post-MVP stage | User/maintainer | Before any sync/write-back implementation | Without explicit approval and stable action identity, sync can overwrite remote human edits or create duplicate issues. |
| What remains the source of truth after external sync exists? | A: roadmap remains authoritative and external tools are execution views; B: external tools can write back automatically; C: bidirectional merge by latest timestamp | A, with drift reports first | User/maintainer | Before write-back design | Latest-timestamp merges can silently replace requirements-backed roadmap decisions with low-context PM edits. |
| Should visual baselines be generated automatically in downstream projects? | A: create only with explicit user/design approval; B: create on first run and flag for review; C: compare only, never create | A | User/design owner per project | Before each real visual-test run | Automatic baseline creation can bless broken UI and hide regressions. |
| Should Kagenti-style topology docs become generated README sections? | A: generated sections in root README; B: separate report command; C: release-gate-only output | B remains current | User | Future topology-doc cycle | Generated README churn can create noisy diffs if the schema is not stable. |

## Rejected / Not Roadmap-Relevant

- Making `agent-playbook:context-audit` the primary owner for `skill-cleaner`: rejected because context-audit owns repo agent-context hygiene and writes a repo punch-list, while `skill-cleaner` centers on local skill roots, usage logs, duplicates, and prompt-budget cleanup.
- Making `skill-cleaner` a release-gate blocker in the first pass: rejected because personal installed roots and usage logs are not source-controlled release state. Release-gate integration can come later only for repo-local deterministic checks.
- Copying the deletion/config-disable behavior without a confirmation gate: rejected. Local policy should support report-only output by default and require explicit user approval before any cleanup edits.
- Copying Kagenti's domain skills wholesale: rejected because many are platform-specific to Kagenti, HyperShift, OpenShift, Keycloak, and Kubernetes.
- Replacing local `idea-to-ship` with Kagenti `orchestrate`: rejected for now because their ownership differs. `idea-to-ship` owns product/feature artifacts; `orchestrate` is a repo enablement pipeline.
- Making screenshot diff approval a pure model judgment: rejected. Visual-test should produce deterministic artifacts, assertions, and user/design approval for baseline changes.
- Treating Playwright demo-video testing as equivalent to visual regression testing: rejected. Kagenti separates functional UI tests from demo recording; local visual-test should do the same.
- Adding Linear/GitLab write APIs directly to `/roadmap`: rejected because
  roadmap owns sequencing, evidence, release gates, and human decisions; live
  external mutation needs a separately authorized sync/apply stage.
- Treating Candidate Backlog or Unverified Signals as an import queue:
  rejected because weak, unknown, inferred, and unsourced work must not become
  executable external issues by default.
- Using title-only matching for external issue idempotency: rejected because
  titles drift and are not stable enough to prevent duplicate issue creation.
- Making live Linear/GitLab provider calls part of the release gate: rejected
  because release verification must remain deterministic and provider-free.

## Acceptance Checks

- Workflow-router intake: `ITS-ROADMAP-022` was added as an in-progress
  candidate with explicit source anchors, review-discovered P2 defects, and
  exit gates for fixture and release-gate verification.
- Review sync: hook-install routing and harness wildcard findings are recorded
  as `ITS-ROADMAP-022` release-gate exit conditions, not as closed work.
- Skill-cleaner intake: `ITS-ROADMAP-021` was added as a candidate with explicit source anchors, user-approved target shape (`skill-stats` expansion), external-wrapper strategy, and report-only plus confirmation-gated apply behavior.
- External-PM roadmap intake: `ITS-ROADMAP-023` was added as a candidate with
  multi-agent brainstorm evidence, export-only MVP guidance, explicit sync and
  write-back safety gates, and provider-free fixture expectations.
- Final-lane gate: no final Now/Next/Later lanes were written because horizon and implementation priority are not explicit in the current request.
- External mutation gate: no Linear, GitLab, GitHub, or other external PM API
  was called; this refresh only updates the local roadmap artifact.
- Boundary discipline: `agent-playbook:context-audit` and release-gate checks are recorded as consumers/adjacent checks, not the primary owner.
- Status-refresh run: final lanes were not rewritten; this update records completion state after user-directed implementation work.
- Preservation: `ITS-ROADMAP-008` and `ITS-ROADMAP-011` are now marked complete only with direct closure artifacts and clean review.
- Artifact safety: existing human-owned sections were preserved; generated content was replaced inside `idea-to-ship:roadmap` markers.
- Source discipline: Kagenti GitHub content is cited as remote path/line anchors; low-confidence domain-specific ideas stay in Unverified Signals or Rejected.
- Visual-test completion: `$idea-to-ship:visual-test`, selector/matrix/RCA/report templates, review-code handoff, and broad-orchestrator spike guards are committed in `91618937a6f4d649c5b2b57d8b819f7178f7f7c4`.
- ITS-ROADMAP-008 completion: focused closure artifacts, implementation-log template tightening, implement-skill shared contract references, and idea-to-ship fixture coverage were added on 2026-06-01.
- Next action: run `/brainstorm --slug ITS-ROADMAP-023` to turn the external
  PM export/sync direction into accepted requirements before architecture or
  implementation.

<!-- idea-to-ship:roadmap generated:end -->
