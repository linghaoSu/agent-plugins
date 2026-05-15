---
goal: "吸收 Kagenti .claude/skills 中可迁移的技能组织模式，并定义前端 visual test skill"
horizon: "not explicit; candidate brief only until user approves horizon and priorities"
generated_at: "2026-05-15 14:35 CST"
repo_head: "255dcfdb9038a2de38bca6c37f4ce4d95bd27d20"
dirty_worktree: "clean before roadmap refresh"
mode: "portfolio"
source_scope: "current user request + Kagenti GitHub skills tree + local idea-to-ship UI/test contracts; no GitHub issues, TODO, or git-history scan"
write_target: ".idea-to-ship/roadmap.md"
final_lanes_written: "no"
priority_approval: "pending"
---

# Roadmap - Kagenti Skills Intake And Frontend Visual Testing

## Human-Owned Sections

### Current Refresh Request

- User requested: understand the skills under `https://github.com/kagenti/kagenti/tree/main/.claude/skills`, find ideas worth absorbing into the subsequent roadmap, and think through how a visual-test skill should be defined for frontend projects.
- Explicit goal: absorb transferable skill-system patterns and define a frontend visual-testing workflow.
- Horizon is not explicit in the request; final Now / Next / Later lanes remain blocked until a horizon and candidate priorities are approved.
- Existing human-owned sections below are preserved from the previous roadmap refresh.

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
- Previously approved local cleanup candidates are retained, not marked done: `ITS-ROADMAP-008` through `ITS-ROADMAP-013` from the prior generated candidate brief.

Excluded sources:

- GitHub issues, PRs, milestones, and discussions in both repos.
- TODO/FIXME scan and git-history mining.
- Full deep read of every Kagenti domain skill; sampled high-signal skills by category instead.
- Subagent exploration, because the current request did not explicitly authorize non-review delegation and the source scope was manageable sequentially.

### Candidate Work

| ID | Title | Status | Work Type | Evidence Class | Confidence | Source Anchors | Suggested Action |
|---|---|---|---|---|---|---|---|
| ITS-ROADMAP-008 | Collapse `idea-to-ship:implement` routing and log-template repetition into shared contracts/templates. | Candidate | Maintenance | Repo | High | `idea-to-ship/skills/implement/SKILL.md:199-229`; `idea-to-ship/WORKFLOW-CONTRACTS.md:98-136` | Keep as first local cleanup candidate unless the user reprioritizes. |
| ITS-ROADMAP-009 | Extract `issue-evaluator:evaluate-issue` long adversarial prompts and report template. | Candidate | Maintenance | Repo | High | `issue-evaluator/skills/evaluate-issue/SKILL.md:128-187`; `issue-evaluator/skills/evaluate-issue/SKILL.md:194-280`; `issue-evaluator/WORKFLOW-CONTRACTS.md:6-84` | Keep as second local cleanup candidate after `ITS-ROADMAP-008`. |
| ITS-ROADMAP-010 | Add hygiene checks for repeated inline prompts/templates and moderate skill bloat. | Candidate | Maintenance | Repo | Medium | `scripts/skill-hygiene-check.py:19-25`; `scripts/skill-hygiene-check.py:181-243`; `RELEASE-GATE.md:42-51` | Pair with `ITS-ROADMAP-013` after at least one extraction commit. |
| ITS-ROADMAP-011 | Extract shared audit/safety checklist used by tool-review, context-audit, vibe health, and antifragile-agent. | Candidate | Maintenance | Repo | Medium | `agent-playbook/skills/tool-review/SKILL.md:89-138`; `agent-playbook/skills/context-audit/SKILL.md:68-115`; `agent-playbook/skills/vibe-coding-health-check/SKILL.md:108-130` | Keep as follow-up cleanup; do not let it displace higher-confidence 008/009/013 unless requested. |
| ITS-ROADMAP-012 | Normalize agent-playbook audit report templates into `templates/`. | Candidate | Maintenance | Repo | Medium | `agent-playbook/skills/tool-review/SKILL.md:146-180`; `agent-playbook/skills/context-audit/SKILL.md:116-158`; `agent-playbook/skills/vibe-coding-health-check/SKILL.md:145-190`; `.gitignore:2` | Pair with `ITS-ROADMAP-011` if the diff stays small. |
| ITS-ROADMAP-013 | Strengthen skill frontmatter validation against real loader YAML semantics and installed-cache drift. | Candidate | Maintenance | Repo | High | `worktree-cleaner/skills/clean-worktrees/SKILL.md:4`; `scripts/skill-hygiene-check.py:181-243`; `RELEASE-GATE.md:42-51` | Keep as a high-confidence stability gate, likely paired with `ITS-ROADMAP-010`. |
| ITS-ROADMAP-014 | Add skill topology scan and connection analysis. | Candidate | Maintenance | Repo | High | Kagenti `.claude/skills/skills:scan/SKILL.md:103-180`; Kagenti `.claude/skills/skills:scan/SKILL.md:224-236`; `README.md:42-115` | Extend local hygiene/reporting to inventory parent/leaf skills, broken references, orphan skills, hub skills, missing category coverage, and generated skill-tree docs. |
| ITS-ROADMAP-015 | Import stronger skill authoring / validation standards. | Candidate | Maintenance | Repo | High | Kagenti `.claude/skills/skills:write/SKILL.md:46-83`; Kagenti `.claude/skills/skills:write/SKILL.md:85-146`; Kagenti `.claude/skills/skills:write/SKILL.md:177-244`; Kagenti `.claude/skills/skills:validate/SKILL.md:14-42`; `scripts/skill-hygiene-check.py:19-25` | Upgrade local `skill-creator` / release-gate guidance around actionability, command safety, task tracking, diagram/text match, and moderate skill-size budgets. |
| ITS-ROADMAP-016 | Create a frontend visual-test skill. | Candidate | Feature | Explicit | High | User request; Kagenti `.claude/skills/test:ui/SKILL.md:1-11`; Kagenti `.claude/skills/test:playwright/SKILL.md:42-56`; `idea-to-ship/skills/ui-design/SKILL.md:168-189`; `idea-to-ship/skills/test/SKILL.md:122-124`; `idea-to-ship/skills/test/SKILL.md:214-217` | Define and implement a reusable skill for visual QA / screenshot regression tied to `interface-design.md`, Playwright screenshots, responsive/state matrices, baseline policy, and report artifacts. |
| ITS-ROADMAP-017 | Add a frontend selector and state recipe template. | Candidate | Maintenance | Repo | Medium | Kagenti `.claude/skills/test:ui/SKILL.md:75-95`; Kagenti `.claude/skills/test:ui-sandbox/SKILL.md:36-50`; Kagenti `.claude/skills/test:ui-sandbox/SKILL.md:72-120`; Kagenti `.claude/skills/test:playwright/SKILL.md:103-124` | Provide a project-local `visual-test-selectors.md` / template that records proven selectors, auth/session workarounds, loading/error/empty states, and flaky-state notes. |
| ITS-ROADMAP-018 | Add context-safe CI and Playwright artifact RCA guidance. | Candidate | Maintenance | Repo | Medium | Kagenti `.claude/skills/rca:ci/SKILL.md:10-27`; Kagenti `.claude/skills/rca:ci/SKILL.md:90-177`; Kagenti `.claude/skills/rca:ci/SKILL.md:213-233`; Kagenti `.claude/skills/test:ui/SKILL.md:147-155` | Reuse the "download large logs/artifacts to files, summarize only anchors" pattern in GitHub CI-fix and visual-test failure triage. |
| ITS-ROADMAP-019 | Add matrix-driven verification loops for visual and multi-env checks. | Candidate | Feature | Repo | Medium | Kagenti `.claude/skills/graph-loop/SKILL.md:11-31`; Kagenti `.claude/skills/graph-loop/SKILL.md:115-177`; Kagenti `.claude/skills/tdd:ui-hypershift/SKILL.md:40-73`; `idea-to-ship/skills/tdd/SKILL.md:125-130` | Define a compact matrix format for browser x viewport x route x UI state, with carry-forward pass rules, flaky marking, and no silent E2E omissions. |
| ITS-ROADMAP-020 | Evaluate a repo orchestration / bootstrap skill. | Candidate | Spike | Repo | Medium | Kagenti `.claude/skills/orchestrate/SKILL.md:41-120`; Kagenti `.claude/skills/orchestrate:plan/SKILL.md:39-76`; Kagenti `.claude/skills/orchestrate:tests/SKILL.md:25-115` | Spike whether `agent-playbook` should gain an orchestrated repo-bootstrap workflow for precommit, tests, CI, security, and skill replication, without conflicting with idea-to-ship staged implementation. |

### ITS-ROADMAP-008 - Collapse idea-to-ship implement repetition

**Status:** Candidate
**Work Type:** Maintenance
**Evidence Class:** Repo
**Confidence:** High
**Source Anchors:** `idea-to-ship/skills/implement/SKILL.md:199-229`; `idea-to-ship/skills/implement/SKILL.md:231-259`; `idea-to-ship/skills/implement/SKILL.md:293-317`; `idea-to-ship/WORKFLOW-CONTRACTS.md:98-136`
**Why Now / Why Next / Why Later:** This remains the strongest first local cleanup because `implement` is central, currently carries repeated cross-skill routing and inline log/report structure, and already has shared contracts it can cite instead.
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
**Why Now / Why Next / Why Later:** This remains the strongest second local cleanup because `evaluate-issue` has large inline adversarial prompts and final report text that are expensive to load and hard to diff-review inside the skill body.
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
**Why Now / Why Next / Why Later:** This remains useful because audit skills overlap by design, but their shared safety and eval criteria should be maintained once instead of duplicated across several skill bodies.
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
**Why Now / Why Next / Why Later:** This is a good companion to `ITS-ROADMAP-011`: shared report templates reduce boilerplate while `.agent-playbook/current/` remains ignored and local-only.
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
**Why Now / Why Next / Why Later:** This remains a high-priority stability gate because the repo produced a loader-visible YAML warning that current checks did not make obvious early enough. Preventing invalid `SKILL.md` frontmatter is a direct stability gate for every installed plugin.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: reproduce the invalid unquoted bracket argument-hint case in a fixture or sample. Exit: release gate parses skill frontmatter with real YAML semantics, rejects invalid flow-style scalars, and optionally verifies installed-cache copies when a cache path is available. No-go: validator depends on network or mutates installed plugins during normal checks.
**Evidence Required:** Updated frontmatter validation in `scripts/skill-hygiene-check.py` or the release-gate frontmatter checker; fixture covering `argument-hint: [--apply] [--all] [--force]`; passing `scripts/release-gate.sh --mode all --strict`; documented cache-sync expectation if source and installed cache can diverge.
**Dependencies:** Can pair with `ITS-ROADMAP-010` because both strengthen hygiene enforcement.
**Risk:** low - the validation target is narrow, but the parser must remain compatible with existing quoted and unquoted scalar frontmatter fields.

## Preserved Local Cleanup Sequence

1. Commit 1: `ITS-ROADMAP-008` - refactor `idea-to-ship:implement` around existing workflow contracts and templates.
2. Commit 2: `ITS-ROADMAP-009` - extract `issue-evaluator:evaluate-issue` prompts/templates and keep its output contract stable.
3. Commit 3: `ITS-ROADMAP-010` + `ITS-ROADMAP-013`, with `ITS-ROADMAP-011` or `ITS-ROADMAP-012` only if the diff stays small - enforce the cleanup pattern and prevent invalid skill frontmatter from reaching installed plugin load.

Recommended priority order remains `ITS-ROADMAP-008`, `ITS-ROADMAP-009`, then `ITS-ROADMAP-010` + `ITS-ROADMAP-013` unless the user explicitly reprioritizes `ITS-ROADMAP-016` visual testing ahead of local cleanup.

### ITS-ROADMAP-014 - Add skill topology scan and connection analysis

**Status:** Candidate
**Work Type:** Maintenance
**Evidence Class:** Repo
**Confidence:** High
**Source Anchors:** Kagenti `.claude/skills/skills:scan/SKILL.md:103-180`; Kagenti `.claude/skills/skills:scan/SKILL.md:224-236`; `README.md:42-115`; `scripts/skill-hygiene-check.py:181-243`
**Why Now / Why Next / Why Later:** This is the most directly reusable Kagenti pattern for this repo: the current hygiene script checks individual files, but it does not yet produce a skill graph, orphan/broken-reference report, usefulness score, or generated skill-tree docs.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: define local inventory schema for plugin, skill, parent/leaf, related links, and referenced skills. Exit: a deterministic scan produces a markdown report and optional README fragment without requiring network access. No-go: treating graph metrics as deletion authority without human review.
**Evidence Required:** Updated scan/hygiene script or a new read-only report command; fixture for broken refs and orphan skills; strict release gate or dedicated test result.
**Dependencies:** Existing `scripts/skill-hygiene-check.py`.
**Risk:** medium - graph reports can create noisy churn unless generated sections and stable ordering are enforced.

### ITS-ROADMAP-015 - Import stronger skill authoring / validation standards

**Status:** Candidate
**Work Type:** Maintenance
**Evidence Class:** Repo
**Confidence:** High
**Source Anchors:** Kagenti `.claude/skills/skills:write/SKILL.md:46-83`; Kagenti `.claude/skills/skills:write/SKILL.md:85-146`; Kagenti `.claude/skills/skills:write/SKILL.md:177-244`; Kagenti `.claude/skills/skills:validate/SKILL.md:14-42`; `scripts/skill-hygiene-check.py:19-25`
**Why Now / Why Next / Why Later:** This should pair with or follow `ITS-ROADMAP-014`: topology tells us where the skill system drifts, while stronger authoring/validation standards make new skills cheaper to review.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: choose which Kagenti standards map to this repo's runtime: command safety, task tracking, diagram-text match, related-skill links, and length budget. Exit: local validator catches missing required metadata, broken related links, unsafe command examples, and missing workflow diagrams where applicable. No-go: forcing Claude-specific auto-approve assumptions onto Codex/plugin runtimes without translation.
**Evidence Required:** Updated skill-creation guidance and validator fixtures; run local release gate.
**Dependencies:** `ITS-ROADMAP-014` improves the related-link and diagram coverage checks, but this can start independently.
**Risk:** medium - Kagenti's command rules are Claude Code-specific, so the local version must express runtime-neutral safety where possible.

### ITS-ROADMAP-016 - Create a frontend visual-test skill

**Status:** Candidate
**Work Type:** Feature
**Evidence Class:** Explicit
**Confidence:** High
**Source Anchors:** User request; Kagenti `.claude/skills/test:ui/SKILL.md:1-11`; Kagenti `.claude/skills/test:ui/SKILL.md:75-95`; Kagenti `.claude/skills/test:ui/SKILL.md:138-155`; Kagenti `.claude/skills/test:playwright/SKILL.md:42-56`; Kagenti `.claude/skills/test:playwright/SKILL.md:143-154`; `idea-to-ship/skills/ui-design/SKILL.md:168-189`; `idea-to-ship/skills/test/SKILL.md:214-217`; `idea-to-ship/skills/review-code/SKILL.md:40-42`
**Why Now / Why Next / Why Later:** The local idea-to-ship flow already requires visual QA in UI design, test planning, TDD, and code review, but it lacks a dedicated executable workflow for collecting screenshots, comparing baselines, and triaging visual regressions.
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

**Status:** Candidate
**Work Type:** Maintenance
**Evidence Class:** Repo
**Confidence:** Medium
**Source Anchors:** Kagenti `.claude/skills/test:ui/SKILL.md:75-95`; Kagenti `.claude/skills/test:ui-sandbox/SKILL.md:36-50`; Kagenti `.claude/skills/test:ui-sandbox/SKILL.md:72-120`; Kagenti `.claude/skills/test:playwright/SKILL.md:103-124`
**Why Now / Why Next / Why Later:** This is a useful companion to `ITS-ROADMAP-016`: visual testing fails in practice when selectors, auth flows, route transitions, and async output states are rediscovered every run.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: define a template that is project-specific, not a universal selector doctrine. Exit: template captures stable selectors, user-visible states, auth/session notes, known flaky states, and preferred test IDs / roles. No-go: encouraging brittle CSS class selectors when semantic role/test-id selectors exist.
**Evidence Required:** New template file and an example section in the visual-test skill.
**Dependencies:** Best implemented with `ITS-ROADMAP-016`.
**Risk:** low - mostly documentation, but poor examples can normalize brittle selectors.

### ITS-ROADMAP-018 - Add context-safe CI and Playwright artifact RCA guidance

**Status:** Candidate
**Work Type:** Maintenance
**Evidence Class:** Repo
**Confidence:** Medium
**Source Anchors:** Kagenti `.claude/skills/rca:ci/SKILL.md:10-27`; Kagenti `.claude/skills/rca:ci/SKILL.md:90-177`; Kagenti `.claude/skills/rca:ci/SKILL.md:213-233`; Kagenti `.claude/skills/test:ui/SKILL.md:147-155`
**Why Now / Why Next / Why Later:** This belongs near the visual-test work because screenshot reports, trace zips, and CI logs are high-volume artifacts that can pollute context if dumped inline.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: identify which local GitHub/CI skills read large logs or Playwright reports. Exit: they download artifacts to files, inspect bounded snippets, and report anchors/summaries instead of raw logs. No-go: adding GitHub write/comment behavior to read-only review workflows.
**Evidence Required:** Updated CI/debug skill guidance and fixture or reviewer checklist for large-artifact handling.
**Dependencies:** Could pair with `ITS-ROADMAP-016` or GitHub CI-fix improvements.
**Risk:** medium - too much indirection can hide key failure lines unless report summaries include precise file/line anchors.

### ITS-ROADMAP-019 - Add matrix-driven verification loops for visual and multi-env checks

**Status:** Candidate
**Work Type:** Feature
**Evidence Class:** Repo
**Confidence:** Medium
**Source Anchors:** Kagenti `.claude/skills/graph-loop/SKILL.md:11-31`; Kagenti `.claude/skills/graph-loop/SKILL.md:115-177`; Kagenti `.claude/skills/tdd:ui-hypershift/SKILL.md:40-73`; `idea-to-ship/skills/tdd/SKILL.md:125-130`; `idea-to-ship/skills/tdd/SKILL.md:195-196`
**Why Now / Why Next / Why Later:** This is valuable after the first visual-test skill exists: the matrix should track browser, viewport, route, state, and environment instead of rerunning everything or silently dropping missing E2E coverage.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: define the smallest matrix format and when carry-forward pass status is valid. Exit: visual-test reports mark PASS/FAIL/FLAKY/MISS/SKIP-with-reason and never treat missing coverage as success. No-go: auto-retry loops that hide real flakes.
**Evidence Required:** Report template plus acceptance fixture with missing, flaky, skipped, and failed cells.
**Dependencies:** Prefer after `ITS-ROADMAP-016`.
**Risk:** medium - matrix tooling can become process-heavy if it is required for small UI changes.

### ITS-ROADMAP-020 - Evaluate a repo orchestration / bootstrap skill

**Status:** Candidate
**Work Type:** Spike
**Evidence Class:** Repo
**Confidence:** Medium
**Source Anchors:** Kagenti `.claude/skills/orchestrate/SKILL.md:41-120`; Kagenti `.claude/skills/orchestrate:plan/SKILL.md:39-76`; Kagenti `.claude/skills/orchestrate:tests/SKILL.md:25-115`
**Why Now / Why Next / Why Later:** Kagenti's orchestrate flow is useful for repo enablement, but it may overlap with `idea-to-ship` and `agent-playbook`; it should be a spike, not immediate implementation.
**Owner:** Unassigned
**Decision Owner:** User
**Release Gate:** Entry: decide target plugin boundary: `agent-playbook` for repo bootstrap vs `idea-to-ship` for product feature work. Exit: one-page architecture note deciding adopt / reject / adapt, including conflict analysis with existing staged implementation. No-go: copying Kagenti's self-replication pattern wholesale without local plugin packaging and safety gates.
**Evidence Required:** Spike note under `.idea-to-ship/ITS-ROADMAP-020/` or a future requirements doc.
**Dependencies:** None.
**Risk:** medium - broad orchestration can become a backlog generator instead of a focused workflow.

## Unverified Signals

- The full Kagenti skill tree has roughly one hundred `SKILL.md` leaves; this brief sampled high-signal categories instead of reading every domain-specific Kubernetes/auth skill.
- Kagenti's session analytics skills may be relevant, but this repo already has `skill-stats`; no candidate is promoted until usage-data requirements are explicit.
- Kagenti's domain-specific HyperShift, OpenShift, Kind, Keycloak, and Kubernetes skills are mostly not portable as-is; only their routing, artifact, and test-matrix patterns are candidates here.
- No implementation effort estimate was produced; suggested sequencing should be approved before converting candidates to final lanes.
- No empirical visual-test flake analysis was run against a real frontend repo in this workspace.

## Conflicts

- The preserved human-owned section above still references the previous "next 3 commits" stability roadmap. This generated brief now keeps those prior candidates and appends Kagenti intake candidates, instead of treating the new scan as a replacement.
- Kagenti assumes Claude Code-specific skill invocation, TaskList, AskUserQuestion, and `.claude/settings.json` auto-approve behavior. Local adoption must translate those ideas to this Codex/plugin repo rather than copying host-specific mechanics.
- A dedicated visual-test skill overlaps with existing `ui-design`, `test`, `tdd`, and `review-code` UI gates. The new skill should execute visual verification, while the existing skills continue to own design contract, story test plan, red-first gates, and code review verdicts.

## Open Decisions

| Decision | Options | Recommended Option | Decision Owner | Needed By | Impact If Delayed |
|---|---|---|---|---|---|
| Should 008-013 remain ahead of Kagenti intake work? | A: keep 008, 009, then 010+013 first; B: put visual-test 016 first; C: mix 014/015 with 010/013 | A unless visual-test is urgent | User | Before final Now/Next/Later lanes | Without this, local cleanup and new visual-test work compete for the same next commits. |
| What is the horizon for this intake? | A: next 3 commits; B: next roadmap cycle; C: visual-test first only | C for focus | User | Before final Now/Next/Later lanes | Without a horizon, this file must remain a Candidate Brief. |
| Where should the visual-test skill live? | A: new `frontend` plugin; B: `idea-to-ship:visual-test`; C: `agent-playbook` audit/check skill | B if tied to `interface-design.md`; A if meant for all frontend repos | User | Before `ITS-ROADMAP-016` implementation | Wrong placement causes either too much coupling to idea-to-ship or too little integration with UI contracts. |
| Should visual baselines be generated automatically? | A: create only with explicit user/design approval; B: create on first run and flag for review; C: compare only, never create | A | User | Before visual-test skill design | Automatic baseline creation can bless broken UI and hide regressions. |
| Should Kagenti-style topology docs become generated README sections? | A: generated sections in root README; B: separate `.agent-playbook` report; C: release-gate-only output | B first, then A if stable | User | Before `ITS-ROADMAP-014` finalization | Generated README churn can create noisy diffs if the schema is not stable. |

## Rejected / Not Roadmap-Relevant

- Copying Kagenti's domain skills wholesale: rejected because many are platform-specific to Kagenti, HyperShift, OpenShift, Keycloak, and Kubernetes.
- Replacing local `idea-to-ship` with Kagenti `orchestrate`: rejected for now because their ownership differs. `idea-to-ship` owns product/feature artifacts; `orchestrate` is a repo enablement pipeline.
- Making screenshot diff approval a pure model judgment: rejected. Visual-test should produce deterministic artifacts, assertions, and user/design approval for baseline changes.
- Treating Playwright demo-video testing as equivalent to visual regression testing: rejected. Kagenti separates functional UI tests from demo recording; local visual-test should do the same.

## Acceptance Checks

- Candidate-only run: final lanes were not written because horizon and priority approval are missing.
- Preservation: previous unfinished candidates `ITS-ROADMAP-008` through `ITS-ROADMAP-013` are retained as Candidate items and are not marked done.
- Artifact safety: existing human-owned sections were preserved; generated content was replaced inside `idea-to-ship:roadmap` markers.
- Source discipline: Kagenti GitHub content is cited as remote path/line anchors; low-confidence domain-specific ideas stay in Unverified Signals or Rejected.
- Visual-test definition: a concrete proposed skill trigger, inputs, workflow, and hard gates are included under `ITS-ROADMAP-016`.
- Next action: approve a horizon, pick the visual-test skill location, and approve/edit candidate priority order before running `/roadmap --final`.

<!-- idea-to-ship:roadmap generated:end -->
