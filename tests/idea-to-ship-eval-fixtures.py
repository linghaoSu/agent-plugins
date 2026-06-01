#!/usr/bin/env python3
"""Offline contract fixtures for critical idea-to-ship skill workflows."""

from __future__ import annotations

import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable


@dataclass(frozen=True)
class InvariantGroup:
    name: str
    patterns: tuple[str, ...]


@dataclass(frozen=True)
class ContractCheck:
    check_id: str
    skill_path: str
    groups: tuple[InvariantGroup, ...]


@dataclass(frozen=True)
class UntrackedManifestEntry:
    path: str
    classification: str
    content: bytes = b""
    rationale: str = ""


@dataclass(frozen=True)
class VisualVerdictScenario:
    name: str
    required_statuses: tuple[str, ...]
    fingerprint_fresh: bool = True
    baseline_approved: bool = True
    console_status: str = "PASS"
    network_status: str = "PASS"
    ignored_complete: bool = True
    artifact_blocker: bool = False
    unclassified_untracked: bool = False
    carry_forward: bool = False
    carry_forward_prior_evidence: bool = True
    carry_forward_relevant_changed: bool = False
    descoped_required: bool = False
    descoped_has_approver: bool = True
    descoped_has_rationale: bool = True
    expected: str = ""


GENERATED_START = "<!-- idea-to-ship:roadmap generated:start -->"
GENERATED_END = "<!-- idea-to-ship:roadmap generated:end -->"
ROADMAP_LANE_FIELDS = (
    "**Status:**",
    "**Work Type:**",
    "**Evidence Class:**",
    "**Confidence:**",
    "**Source Anchors:**",
    "**Why Now / Why Next / Why Later:**",
    "**Owner:**",
    "**Decision Owner:**",
    "**Release Gate:**",
    "**Evidence Required:**",
    "**Dependencies:**",
    "**Risk:**",
)
REQUIREMENTS_CORE_HEADINGS = (
    "## Problem",
    "## Functional Requirements",
    "## Success Criteria",
    "## Open Questions",
)
ARCHITECTURE_CORE_HEADINGS = (
    "## Summary",
    "## Codebase Context",
    "## Alternatives Considered",
    "## Recommendation",
    "## Chosen Design",
    "## Staged Implementation Plan",
)
INTERFACE_DESIGN_CORE_HEADINGS = (
    "## Summary",
    "## UX Brief",
    "## Existing UI / Design System Map",
    "## Visual Contract",
    "## Interaction Spec",
    "## Component Spec",
    "## Responsive Spec",
    "## Accessibility Contract",
    "## Visual QA Plan",
)


CHECKS: tuple[ContractCheck, ...] = (
    ContractCheck(
        "brainstorm-mandatory-readme-contract",
        "idea-to-ship/README.md",
        (
            InvariantGroup("mandatory brainstorm", (r"mandatory brainstorm", r"do not skip `/brainstorm`")),
            InvariantGroup("downstream stop", (r"requirements\.md` is missing.{0,160}downstream skills stop",)),
            InvariantGroup("roadmap boundary", (r"Roadmaps can sequence work.{0,180}do not replace",)),
        ),
    ),
    ContractCheck(
        "brainstorm-mandatory-skill-contract",
        "idea-to-ship/skills/brainstorm/SKILL.md",
        (
            InvariantGroup("mandatory first stage", (r"mandatory first stage",)),
            InvariantGroup("downstream skills stop", (r"Downstream skills.{0,160}must stop",)),
            InvariantGroup("roadmap does not replace", (r"roadmap.{0,80}does not replace",)),
        ),
    ),
    ContractCheck(
        "brainstorm-rerun-preservation-contract",
        "idea-to-ship/skills/brainstorm/SKILL.md",
        (
            InvariantGroup("requirements ownership", (r"Requirements Ownership",)),
            InvariantGroup("stable requirement ids", (r"stable requirement IDs",)),
            InvariantGroup("requirement id examples", (r"FR-\*", r"FR-1")),
            InvariantGroup(
                "human content preservation",
                (r"human notes", r"manual exclusions", r"human edits"),
            ),
            InvariantGroup("draft fallback", (r"requirements\.draft\.md",)),
            InvariantGroup("replacement approval", (r"explicit approval",)),
        ),
    ),
    ContractCheck(
        "commercialize-artifact-contract",
        "idea-to-ship/skills/commercialize/SKILL.md",
        (
            InvariantGroup("commercialization artifact", (r"commercialization\.md",)),
            InvariantGroup("pre requirements mode", (r"pre-requirements",)),
            InvariantGroup("scenario expansion", (r"Commercial Scenario Expansion", r"CS-001", r"fuzzy idea")),
            InvariantGroup("commercial analysis", (r"ICP", r"Monetization Model", r"Feature-To-Business Impact")),
            InvariantGroup("multi angle review", (r"Multi-Angle Commercial Review", r"Review Rounds")),
            InvariantGroup("roadmap handoff", (r"Handoff To Roadmap", r"/roadmap --slug <slug>")),
        ),
    ),
    ContractCheck(
        "commercialize-requirements-boundary",
        "idea-to-ship/skills/commercialize/SKILL.md",
        (
            InvariantGroup("requirements boundary", (r"cannot replace\s+`requirements\.md`",)),
            InvariantGroup("brainstorm next when missing", (r"/brainstorm --slug <slug>",)),
            InvariantGroup("no weak now", (r"Weak`, `Unknown`, and `Speculative` items cannot be recommended as `Now`",)),
            InvariantGroup("reject costly low return", (r"Rejected / Costly Low-Return Ideas", r"High-cost low-return")),
            InvariantGroup("no user pleasing", (r"Do not flatter the user", r"User-pleasing summaries")),
            InvariantGroup("scenario disqualifier", (r"Disqualifier", r"One-scenario anchoring")),
        ),
    ),
    ContractCheck(
        "commercialize-template-reference-contract",
        "idea-to-ship/skills/commercialize/SKILL.md",
        (
            InvariantGroup("scenario template reference", (r"commercial-scenario\.md",)),
            InvariantGroup("review hypothesis template reference", (r"commercial-review-and-hypothesis\.md",)),
            InvariantGroup("artifact template reference", (r"commercialization\.md", r"templates/commercialization")),
            InvariantGroup("generated marker policy retained", (r"idea-to-ship:commercialize generated:start",)),
        ),
    ),
    ContractCheck(
        "commercial-scenario-template-contract",
        "idea-to-ship/templates/commercial-scenario.md",
        (
            InvariantGroup("scenario id", (r"CS-001",)),
            InvariantGroup("target segment", (r"Target segment",)),
            InvariantGroup("buyer blocker", (r"User / buyer / blocker",)),
            InvariantGroup("trigger event", (r"Trigger event",)),
            InvariantGroup("current alternative", (r"Current alternative",)),
            InvariantGroup("monetizable pain", (r"Monetizable pain",)),
            InvariantGroup("value metric", (r"Value metric",)),
            InvariantGroup("paid boundary", (r"First paid boundary",)),
            InvariantGroup("disqualifier", (r"Disqualifier",)),
        ),
    ),
    ContractCheck(
        "commercial-review-hypothesis-template-contract",
        "idea-to-ship/templates/commercial-review-and-hypothesis.md",
        (
            InvariantGroup("reviewer table", (r"Keep / Change / Reject", r"Cost Concern", r"Roadmap Implication")),
            InvariantGroup("hypothesis ids", (r"CH-001", r"CH-002")),
            InvariantGroup("hypothesis table", (r"Hypothesis", r"Revenue Lever", r"Validation Check", r"Stop Condition")),
        ),
    ),
    ContractCheck(
        "commercialization-template-contract",
        "idea-to-ship/templates/commercialization.md",
        (
            InvariantGroup("human owned sections", (r"Human-Owned Sections",)),
            InvariantGroup("generated markers", (r"idea-to-ship:commercialize generated:start", r"idea-to-ship:commercialize generated:end")),
            InvariantGroup("review rounds", (r"Review Rounds", r"Round 0", r"Round 3")),
            InvariantGroup("commercial hypotheses", (r"Commercial Hypotheses",)),
            InvariantGroup("feature impact", (r"Feature-To-Business Impact",)),
            InvariantGroup("rejected ideas", (r"Rejected / Costly Low-Return Ideas",)),
            InvariantGroup("handoff", (r"Handoff To Roadmap",)),
        ),
    ),
    ContractCheck(
        "architect-requires-brainstorm-contract",
        "idea-to-ship/skills/architect/SKILL.md",
        (
            InvariantGroup("requires requirements", (r"Require `requirements\.md`",)),
            InvariantGroup("run brainstorm when missing", (r"/brainstorm --slug <slug>",)),
            InvariantGroup("thin requirements return to brainstorm", (r"thin.{0,160}/brainstorm --slug <slug>",)),
        ),
    ),
    ContractCheck(
        "architect-rerun-preservation-contract",
        "idea-to-ship/skills/architect/SKILL.md",
        (
            InvariantGroup("architecture ownership", (r"Architecture Ownership",)),
            InvariantGroup("option identity preservation", (r"option names",)),
            InvariantGroup("stage identity preservation", (r"stage names",)),
            InvariantGroup("decision history preservation", (r"decision history",)),
            InvariantGroup(
                "human content preservation",
                (r"human notes", r"unresolved risks", r"human edits"),
            ),
            InvariantGroup("draft fallback", (r"architecture\.draft\.md",)),
            InvariantGroup("replacement approval", (r"explicit approval",)),
        ),
    ),
    ContractCheck(
        "ui-design-artifact-contract",
        "idea-to-ship/skills/ui-design/SKILL.md",
        (
            InvariantGroup("requires requirements", (r"Require `requirements\.md`",)),
            InvariantGroup("interface design artifact", (r"interface-design\.md",)),
            InvariantGroup("project design md boundary", (r"--write-design-md", r"DESIGN\.md")),
            InvariantGroup("design system map", (r"Design System Map",)),
            InvariantGroup("do dont constraints", (r"Do / Don't",)),
            InvariantGroup("accessibility contract", (r"Accessibility Contract",)),
            InvariantGroup("visual qa", (r"Visual QA Plan",)),
            InvariantGroup("visual reference intake", (r"Visual Reference Intake", r"Visual References", r"Image-Derived Constraints")),
            InvariantGroup("image reference roles", (r"target", r"inspiration", r"competitor", r"avoid")),
            InvariantGroup("mood board anti pattern", (r"Mood-board averaging",)),
            InvariantGroup("known gaps", (r"Known gaps",)),
            InvariantGroup("decision rationale", (r"Design Decisions", r"Tradeoff")),
            InvariantGroup("phase gates", (r"Phase Gates", r"Design System Map", r"Verification Plan")),
        ),
    ),
    ContractCheck(
        "ui-design-rerun-preservation-contract",
        "idea-to-ship/skills/ui-design/SKILL.md",
        (
            InvariantGroup("interface design ownership", (r"Interface Design Ownership",)),
            InvariantGroup("human content preservation", (r"human notes", r"human-owned")),
            InvariantGroup("draft fallback", (r"interface-design\.draft\.md",)),
            InvariantGroup("replacement approval", (r"explicit approval",)),
        ),
    ),
    ContractCheck(
        "ui-design-runtime-metadata-contract",
        "idea-to-ship/skills/ui-design/agents/openai.yaml",
        (
            InvariantGroup("plugin qualified default prompt", (r"\$idea-to-ship:ui-design",)),
        ),
    ),
    ContractCheck(
        "ui-design-figma-routing-contract",
        "idea-to-ship/skills/ui-design/SKILL.md",
        (
            InvariantGroup("figma route", (r"route through the available Figma skill",)),
            InvariantGroup("figma fallback", (r"tooling is unavailable", r"Known Gaps")),
        ),
    ),
    ContractCheck(
        "ui-design-template-reference-contract",
        "idea-to-ship/skills/ui-design/SKILL.md",
        (
            InvariantGroup("visual reference template", (r"visual-reference-inventory\.md",)),
            InvariantGroup("interface template", (r"interface-design\.md", r"templates/interface-design")),
            InvariantGroup("visual references retained", (r"Visual References", r"Image-Derived Constraints")),
            InvariantGroup("verification sections retained", (r"Accessibility Contract", r"Visual QA Plan")),
        ),
    ),
    ContractCheck(
        "visual-reference-template-contract",
        "idea-to-ship/templates/visual-reference-inventory.md",
        (
            InvariantGroup("inventory columns", (r"Source", r"Intended Role", r"Extracted Constraints", r"Conflicts / Limits")),
            InvariantGroup("roles", (r"target", r"inspiration", r"competitor", r"current-ui", r"avoid")),
            InvariantGroup("role actions", (r"must-match", r"borrow", r"avoid", r"reuse")),
        ),
    ),
    ContractCheck(
        "interface-design-template-contract",
        "idea-to-ship/templates/interface-design.md",
        (
            InvariantGroup("core headings", (r"## Summary", r"## UX Brief", r"## Existing UI / Design System Map")),
            InvariantGroup("visual references", (r"## Visual References", r"## Image-Derived Constraints")),
            InvariantGroup("visual contract", (r"## Visual Contract", r"Do / Don't")),
            InvariantGroup("interaction component responsive", (r"## Interaction Spec", r"## Component Spec", r"## Responsive Spec")),
            InvariantGroup("accessibility visual qa", (r"## Accessibility Contract", r"## Visual QA Plan")),
            InvariantGroup("decisions questions", (r"## Design Decisions", r"## Open Questions")),
        ),
    ),
    ContractCheck(
        "tdd-skill-contract",
        "idea-to-ship/skills/tdd/SKILL.md",
        (
            InvariantGroup("stage tdd mode", (r"stage-tdd", r"--stage <N>")),
            InvariantGroup("backfill mode", (r"test-backfill", r"--backfill")),
            InvariantGroup("backfill standalone authority", (r"concrete user focus", r"current diff", r"lower-authority")),
            InvariantGroup("no production code", (r"does not edit\s+production code", r"never writes production code")),
            InvariantGroup("stage tdd slices", (r"Stage TDD Slices",)),
            InvariantGroup("red first gate", (r"expected failing test", r"before `/implement` writes production code")),
            InvariantGroup("tdd log", (r"tdd-log\.md",)),
            InvariantGroup("backfill not tdd", (r"Backfill pretending to be TDD",)),
        ),
    ),
    ContractCheck(
        "tdd-runtime-metadata-contract",
        "idea-to-ship/skills/tdd/agents/openai.yaml",
        (
            InvariantGroup("plugin qualified default prompt", (r"\$idea-to-ship:tdd",)),
        ),
    ),
    ContractCheck(
        "test-requires-brainstorm-contract",
        "idea-to-ship/skills/test/SKILL.md",
        (
            InvariantGroup("requires requirements", (r"Require `requirements\.md`",)),
            InvariantGroup("run brainstorm when missing", (r"/brainstorm --slug <slug>",)),
            InvariantGroup("no diff substitute", (r"not substitutes for brainstormed requirements", r"not.*substitute.*requirements")),
        ),
    ),
    ContractCheck(
        "review-code-requires-brainstorm-contract",
        "idea-to-ship/skills/review-code/SKILL.md",
        (
            InvariantGroup("requires requirements", (r"Require `requirements\.md`",)),
            InvariantGroup("run brainstorm when missing", (r"/brainstorm --slug <slug>",)),
            InvariantGroup("required context", (r"Requirements \(required context\)",)),
        ),
    ),
    ContractCheck(
        "downstream-interface-design-contract",
        "idea-to-ship/skills/implement/SKILL.md",
        (
            InvariantGroup("implement reads interface design", (r"interface-design\.md",)),
            InvariantGroup("implement reads project design", (r"DESIGN\.md",)),
            InvariantGroup("ui stage missing contract stops", (r"touches UI", r"/ui-design --slug <slug>", r"stop before coding")),
            InvariantGroup("implicit ui design anti pattern", (r"Implicit UI design",)),
            InvariantGroup("ui contract drift", (r"design drift", r"document the deviation")),
        ),
    ),
    ContractCheck(
        "implement-delegates-tdd-contract",
        "idea-to-ship/skills/implement/SKILL.md",
        (
            InvariantGroup("delegates to tdd skill", (r"\$idea-to-ship:tdd",)),
            InvariantGroup("requires tdd evidence", (r"Stage TDD Slices", r"tdd-log\.md")),
            InvariantGroup("no inline substitute", (r"Do not inline a\s+weaker same-context TDD substitute",)),
            InvariantGroup("tdd gate before code", (r"before production code is\s+written",)),
        ),
    ),
    ContractCheck(
        "implement-optional-tournament-contract",
        "idea-to-ship/skills/implement/SKILL.md",
        (
            InvariantGroup("compete flag", (r"--compete", r"--tournament")),
            InvariantGroup("routes to tournament", (r"\$agent-playbook:implementation-tournament",)),
            InvariantGroup("artifact path", (r"implementation-tournament\.md",)),
            InvariantGroup("no winner stops", (r"No Winner", r"fallback")),
        ),
    ),
    ContractCheck(
        "implement-template-reference-contract",
        "idea-to-ship/skills/implement/SKILL.md",
        (
            InvariantGroup("implementation log template", (r"implementation-log\.md", r"templates/implementation-log")),
            InvariantGroup("cross skill contract reference", (r"WORKFLOW-CONTRACTS\.md", r"implementation-stage route table")),
            InvariantGroup("template owns stage status", (r"Use the template for stage status",)),
            InvariantGroup("template owns cross-skill check fields", (r"cross-skill check fields",)),
            InvariantGroup("stage status retained", (r"Stage Status",)),
        ),
    ),
    ContractCheck(
        "implementation-log-template-contract",
        "idea-to-ship/templates/implementation-log.md",
        (
            InvariantGroup("stage status heading", (r"## Stage Status",)),
            InvariantGroup("stage status row", (r"Stage 1",)),
            InvariantGroup("stage entry heading", (r"## Stage <N>",)),
            InvariantGroup("files touched field", (r"Files touched",)),
            InvariantGroup("pre-stage assumptions heading", (r"### Pre-Stage Assumptions",)),
            InvariantGroup("architecture assumption field", (r"architecture\.md:",)),
            InvariantGroup("interface design assumption field", (r"interface-design\.md:",)),
            InvariantGroup("codebase assumption field", (r"codebase:",)),
            InvariantGroup("success criteria heading", (r"### Success Criteria",)),
            InvariantGroup("success criteria verification wording", (r"command, test, or observable behavior",)),
            InvariantGroup("verification heading", (r"### Verification",)),
            InvariantGroup("tdd evidence field", (r"tdd-log\.md",)),
            InvariantGroup("cross skill checks heading", (r"### Cross-Skill Checks",)),
            InvariantGroup("cross skill trigger column", (r"Trigger",)),
            InvariantGroup("cross skill result column", (r"Result",)),
            InvariantGroup("cross skill impact column", (r"Impact",)),
        ),
    ),
    ContractCheck(
        "review-design-interface-design-contract",
        "idea-to-ship/skills/review-design/SKILL.md",
        (
            InvariantGroup("review reads interface design", (r"interface-design\.md",)),
            InvariantGroup("architecture ui contradiction", (r"contradicts `interface-design\.md`", r"design drift")),
            InvariantGroup("prompt includes interface design", (r"## Interface Design",)),
            InvariantGroup("drift output", (r"## Design Drift",)),
        ),
    ),
    ContractCheck(
        "review-code-interface-design-contract",
        "idea-to-ship/skills/review-code/SKILL.md",
        (
            InvariantGroup("review reads interface design", (r"interface-design\.md",)),
            InvariantGroup("component visual responsive a11y", (r"component.{0,80}visual.{0,120}responsive.{0,120}accessibility",)),
            InvariantGroup("drift artifact", (r"departed from architecture\.md or\s+interface-design\.md",)),
        ),
    ),
    ContractCheck(
        "test-interface-design-contract",
        "idea-to-ship/skills/test/SKILL.md",
        (
            InvariantGroup("test reads interface design", (r"interface-design\.md",)),
            InvariantGroup("ui contract test mapping", (r"UI Contracts", r"scenario/test", r"Out Of Scope")),
        ),
    ),
    ContractCheck(
        "roadmap-does-not-replace-brainstorm-contract",
        "idea-to-ship/skills/roadmap/SKILL.md",
        (
            InvariantGroup("roadmap boundary", (r"Roadmap does not replace `/brainstorm`",)),
            InvariantGroup("slug mode requirements", (r"In slug mode.{0,180}requirements\.md",)),
            InvariantGroup("portfolio next action", (r"portfolio mode.{0,260}/brainstorm --slug <slug>",)),
        ),
    ),
    ContractCheck(
        "roadmap-first-run-contract",
        "idea-to-ship/skills/roadmap/SKILL.md",
        (
            InvariantGroup(
                "first-run candidate brief target",
                (r"first run.{0,240}candidate brief.{0,240}write_target",),
            ),
        ),
    ),
    ContractCheck(
        "roadmap-rerun-preservation-contract",
        "idea-to-ship/skills/roadmap/SKILL.md",
        (
            InvariantGroup("rerun or refresh", (r"\brerun\b", r"\brefresh\b")),
            InvariantGroup(
                "human content preservation",
                (r"human content", r"human-owned content", r"human edits"),
            ),
            InvariantGroup(
                "marker merge or draft fallback",
                (r"generated markers", r"roadmap\.draft\.md", r"\bdraft\.md\b"),
            ),
        ),
    ),
    ContractCheck(
        "roadmap-final-without-approval-contract",
        "idea-to-ship/skills/roadmap/SKILL.md",
        (
            InvariantGroup("final mode", (r"--final",)),
            InvariantGroup("priority approval", (r"priority approval",)),
            InvariantGroup(
                "blocked final lanes",
                (r"final .*lanes are not\s+written", r"without .*approval", r"ask .*approval"),
            ),
        ),
    ),
    ContractCheck(
        "roadmap-template-reference-contract",
        "idea-to-ship/skills/roadmap/SKILL.md",
        (
            InvariantGroup("item schema template reference", (r"roadmap-item-schema\.md",)),
            InvariantGroup("candidate brief template reference", (r"roadmap-candidate-brief\.md",)),
            InvariantGroup("final template reference", (r"roadmap-final\.md",)),
            InvariantGroup("generated marker policy retained", (r"idea-to-ship:roadmap generated:start",)),
        ),
    ),
    ContractCheck(
        "roadmap-item-schema-template-contract",
        "idea-to-ship/templates/roadmap-item-schema.md",
        (
            InvariantGroup("stable ids", (r"ITS-ROADMAP-001", r"ITS-<slug>-001")),
            InvariantGroup("candidate table", (r"Status", r"Work Type", r"Evidence Class", r"Source Anchors")),
            InvariantGroup("lane fields", (r"\*\*Release Gate:\*\*", r"\*\*Evidence Required:\*\*", r"\*\*Dependencies:\*\*", r"\*\*Risk:\*\*")),
            InvariantGroup("no loose substitutes", (r"Do not substitute looser fields",)),
        ),
    ),
    ContractCheck(
        "roadmap-candidate-brief-template-contract",
        "idea-to-ship/templates/roadmap-candidate-brief.md",
        (
            InvariantGroup("candidate brief", (r"Candidate Brief",)),
            InvariantGroup("source plan", (r"Source Plan",)),
            InvariantGroup("candidate work", (r"Candidate Work",)),
            InvariantGroup("unverified signals", (r"Unverified Signals",)),
            InvariantGroup("conflicts", (r"Conflicts",)),
            InvariantGroup("open decisions", (r"Open Decisions",)),
            InvariantGroup("rejected", (r"Rejected / Not Roadmap-Relevant",)),
        ),
    ),
    ContractCheck(
        "roadmap-final-template-contract",
        "idea-to-ship/templates/roadmap-final.md",
        (
            InvariantGroup("frontmatter", (r"goal:", r"horizon:", r"repo_head:", r"source_scope:")),
            InvariantGroup("human owned sections", (r"Human-Owned Sections",)),
            InvariantGroup("generated markers", (r"idea-to-ship:roadmap generated:start", r"idea-to-ship:roadmap generated:end")),
            InvariantGroup("lanes", (r"## Now", r"## Next", r"## Later")),
            InvariantGroup("milestones", (r"## Milestones", r"Release Gate", r"Risk Level")),
            InvariantGroup("open decisions", (r"## Open Decisions",)),
        ),
    ),
    ContractCheck(
        "test-story-traceability-contract",
        "idea-to-ship/skills/test/SKILL.md",
        (
            InvariantGroup("user stories", (r"user stories",)),
            InvariantGroup("acceptance criteria", (r"acceptance criteria",)),
            InvariantGroup("scenario matrix", (r"scenario matrix",)),
            InvariantGroup("test matrix", (r"test matrix",)),
            InvariantGroup("test layer split", (r"unit\s*/\s*integration\s*/\s*e2e",)),
        ),
    ),
    ContractCheck(
        "test-negative-scenarios-contract",
        "idea-to-ship/skills/test/SKILL.md",
        (
            InvariantGroup("happy path", (r"happy path",)),
            InvariantGroup("edge or corner cases", (r"edge/corner", r"corner / boundary", r"edge cases")),
            InvariantGroup(
                "invalid or abnormal input",
                (r"invalid / abnormal input", r"invalid-input", r"malformed input"),
            ),
            InvariantGroup("failure modes", (r"failure modes", r"failure-mode")),
        ),
    ),
    ContractCheck(
        "test-template-reference-contract",
        "idea-to-ship/skills/test/SKILL.md",
        (
            InvariantGroup("test plan template", (r"test-plan\.md", r"templates/test-plan")),
            InvariantGroup("results template", (r"test-results-summary\.md",)),
            InvariantGroup("traceability retained", (r"user stories", r"acceptance\s+criteria", r"scenario matrix", r"test matrix")),
            InvariantGroup("test layer retained", (r"unit / integration / e2e",)),
        ),
    ),
    ContractCheck(
        "test-plan-template-contract",
        "idea-to-ship/templates/test-plan.md",
        (
            InvariantGroup("user stories", (r"## User Stories", r"Story ID", r"Actor", r"Expected Outcome")),
            InvariantGroup("acceptance criteria", (r"## Acceptance Criteria", r"Verification Method")),
            InvariantGroup("scenario matrix", (r"## Scenario Matrix", r"invalid-input", r"Failure Signal")),
            InvariantGroup("test layers", (r"### Unit", r"### Integration", r"### E2E")),
            InvariantGroup("traceability", (r"## Traceability", r"Requirement", r"Scenarios", r"Tests")),
            InvariantGroup("stage tdd slices", (r"## Stage TDD Slices",)),
        ),
    ),
    ContractCheck(
        "test-results-template-contract",
        "idea-to-ship/templates/test-results-summary.md",
        (
            InvariantGroup("results heading", (r"## Results",)),
            InvariantGroup("completed timestamp", (r"\*\*Completed:\*\* <YYYY-MM-DD HH:MM>",)),
            InvariantGroup("pass status", (r"All pass: yes / no",)),
            InvariantGroup("coverage", (r"Changed-file line coverage",)),
            InvariantGroup("production fixes", (r"Production fixes triggered by tests",)),
        ),
    ),
    ContractCheck(
        "review-code-missing-test-plan-contract",
        "idea-to-ship/skills/review-code/SKILL.md",
        (
            InvariantGroup("missing test plan", (r"test-plan\.md`? is absent", r"test-plan\.md`? if absent")),
            InvariantGroup("observable behavior change", (r"diff changes observable behavior", r"behavior-changing")),
            InvariantGroup("verification gap", (r"verification gap",)),
            InvariantGroup("warning severity", (r"\bwarning\b",)),
        ),
    ),
    ContractCheck(
        "workflow-multi-agent-review-contract",
        "idea-to-ship/WORKFLOW-CONTRACTS.md",
        (
            InvariantGroup("multi-agent routing", (r"Multi-Agent Review Routing",)),
            InvariantGroup("multiple angles", (r"multiple independent", r"at least two angles")),
            InvariantGroup("multiple rounds", (r"multiple rounds", r"Run multiple rounds")),
            InvariantGroup("explicit fallback only", (r"explicitly unsupported by the host/runtime", r"explicitly unavailable\s+or at capacity")),
            InvariantGroup("degraded mode recorded", (r"degraded-same-context-review",)),
            InvariantGroup("degraded preserves angles", (r"Degraded mode.{0,140}same angles and rounds",)),
        ),
    ),
    ContractCheck(
        "review-design-multi-agent-contract",
        "idea-to-ship/skills/review-design/SKILL.md",
        (
            InvariantGroup("multi-agent review", (r"multiple independent", r"reviewer agents")),
            InvariantGroup("required angles", (r"Architecture correctness angle", r"Implementation/testability angle")),
            InvariantGroup("explicit fallback only", (r"explicitly unsupported by the host/runtime", r"selected reviewer/model is\s+explicitly unavailable")),
            InvariantGroup("degraded mode recorded", (r"degraded-same-context-review",)),
            InvariantGroup("degraded preserves rounds", (r"preserves multi-angle and multi-round",)),
        ),
    ),
    ContractCheck(
        "review-code-multi-agent-contract",
        "idea-to-ship/skills/review-code/SKILL.md",
        (
            InvariantGroup("multi-agent review", (r"multiple independent", r"reviewer agents")),
            InvariantGroup("required angles", (r"Correctness/security angle", r"Traceability/testability angle", r"Maintainability/repo-fit angle")),
            InvariantGroup("explicit fallback only", (r"explicitly unsupported by the host/runtime", r"selected reviewer/model is\s+explicitly unavailable")),
            InvariantGroup("degraded mode recorded", (r"degraded-same-context-review",)),
            InvariantGroup("rerun all angles", (r"re-run every required reviewer angle",)),
        ),
    ),
    ContractCheck(
        "visual-test-skill-contract",
        "idea-to-ship/skills/visual-test/SKILL.md",
        (
            InvariantGroup("report artifact", (r"visual-test-report\.md",)),
            InvariantGroup("matrix artifact", (r"visual-test-matrix\.md",)),
            InvariantGroup("selector artifact", (r"visual-test-selectors\.md",)),
            InvariantGroup("artifact rca artifact", (r"visual-artifact-rca\.md",)),
            InvariantGroup("requires requirements", (r"Require `requirements\.md`", r"/brainstorm --slug <slug>")),
            InvariantGroup("required inputs", (r"requirements\.md", r"interface-design\.md", r"test-plan\.md")),
            InvariantGroup("usage trigger", (r"after UI implementation", r"before `?\$idea-to-ship:review-code`?")),
            InvariantGroup("visual qa mapping", (r"Visual QA", r"assertions", r"screenshots", r"baselines", r"reports")),
            InvariantGroup("gate 1", (r"Gate 1 - Input Contract",)),
            InvariantGroup("gate 2", (r"Gate 2 - Tooling Discovery",)),
            InvariantGroup("gate 3", (r"Gate 3 - Selector/State Readiness",)),
            InvariantGroup("gate 4", (r"Gate 4 - Matrix Derivation",)),
            InvariantGroup("gate 5", (r"Gate 5 - Assert Before Capture",)),
            InvariantGroup("gate 6", (r"Gate 6 - Capture And Compare",)),
            InvariantGroup("gate 7", (r"Gate 7 - Artifact RCA",)),
            InvariantGroup("gate 8", (r"Gate 8 - Matrix Closure",)),
            InvariantGroup("gate 9", (r"Gate 9 - Report Handoff",)),
            InvariantGroup("status vocabulary", (r"(?=.*PASS)(?=.*FAIL)(?=.*FLAKY)(?=.*MISS)(?=.*NEEDS-RUN)(?=.*SKIP-with-reason)",)),
            InvariantGroup("aggregate verdict vocabulary", (r"(?=.*aggregate_verdict)(?=.*NEEDS_USER)",)),
            InvariantGroup("workspace fingerprint", (r"workspace_diff_fingerprint",)),
            InvariantGroup("untracked enumeration command", (r"git ls-files --others --exclude-standard -z",)),
            InvariantGroup("untracked manifest", (r"untracked_files_manifest",)),
            InvariantGroup("self evidence fingerprint exclusion", (r"self evidence artifact", r"visual evidence artifacts")),
            InvariantGroup("console network statuses", (r"(?=.*console_status)(?=.*network_status)(?=.*NOT_COLLECTED)(?=.*IGNORED-with-justification)",)),
            InvariantGroup("baseline approval", (r"baseline.{0,80}approval",)),
            InvariantGroup("baseline self approval block", (r"cannot self-approve",)),
            InvariantGroup("related skills heading", (r"Related Skills",)),
            InvariantGroup("review-code handoff", (r"\$idea-to-ship:review-code",)),
        ),
    ),
    ContractCheck(
        "visual-test-runtime-metadata-contract",
        "idea-to-ship/skills/visual-test/agents/openai.yaml",
        (
            InvariantGroup("plugin qualified default prompt", (r"\$idea-to-ship:visual-test",)),
        ),
    ),
    ContractCheck(
        "visual-test-report-template-contract",
        "idea-to-ship/templates/visual-test-report.md",
        (
            InvariantGroup("aggregate verdict field", (r"aggregate_verdict",)),
            InvariantGroup("blocking reasons field", (r"blocking_reasons",)),
            InvariantGroup("status counts", (r"matrix_status_counts", r"required_cell_status_counts")),
            InvariantGroup("fingerprint field", (r"workspace_diff_fingerprint",)),
            InvariantGroup("untracked manifest", (r"untracked_files_manifest",)),
            InvariantGroup("baseline summary", (r"baseline_approval_summary",)),
            InvariantGroup("console network summary", (r"console_status", r"network_status", r"console_network_summary")),
            InvariantGroup("console ignored justification field", (r"console_ignored_justification",)),
            InvariantGroup("console ignored owner field", (r"console_ignored_owner_or_source",)),
            InvariantGroup("console ignored rca field", (r"console_ignored_rca_link",)),
            InvariantGroup("network ignored justification field", (r"network_ignored_justification",)),
            InvariantGroup("network ignored owner field", (r"network_ignored_owner_or_source",)),
            InvariantGroup("network ignored rca field", (r"network_ignored_rca_link",)),
            InvariantGroup("residual risk", (r"residual_risk",)),
            InvariantGroup("artifact rca summary", (r"artifact_rca_summary",)),
            InvariantGroup("baseline approver field", (r"approver/source",)),
            InvariantGroup("baseline path field", (r"baseline path",)),
            InvariantGroup("baseline diff summary field", (r"diff summary",)),
            InvariantGroup("baseline before artifact field", (r"before artifact",)),
            InvariantGroup("baseline after artifact field", (r"after artifact",)),
            InvariantGroup("baseline linked cells field", (r"linked matrix cells",)),
            InvariantGroup("baseline rationale field", (r"rationale",)),
        ),
    ),
    ContractCheck(
        "visual-test-selectors-template-contract",
        "idea-to-ship/templates/visual-test-selectors.md",
        (
            InvariantGroup("route or screen", (r"route", r"screen")),
            InvariantGroup("stable selectors", (r"stable selectors", r"role", r"test-id")),
            InvariantGroup("auth session", (r"auth", r"session")),
            InvariantGroup("preconditions", (r"precondition", r"seed data")),
            InvariantGroup("loading completion", (r"loading completion", r"ready state")),
            InvariantGroup("flaky states", (r"flaky",)),
            InvariantGroup("rejected brittle selectors", (r"Rejected Brittle Selectors",)),
        ),
    ),
    ContractCheck(
        "visual-test-matrix-template-contract",
        "idea-to-ship/templates/visual-test-matrix.md",
        (
            InvariantGroup("status vocabulary", (r"(?=.*PASS)(?=.*FAIL)(?=.*FLAKY)(?=.*MISS)(?=.*NEEDS-RUN)(?=.*SKIP-with-reason)",)),
            InvariantGroup("source ids", (r"source_ids",)),
            InvariantGroup("required field", (r"required",)),
            InvariantGroup("assertion command", (r"assertion_command",)),
            InvariantGroup("screenshot path", (r"screenshot_path",)),
            InvariantGroup("baseline path", (r"baseline_path",)),
            InvariantGroup("artifact rca link", (r"artifact_rca_link",)),
            InvariantGroup("workspace fingerprint field", (r"workspace_diff_fingerprint",)),
            InvariantGroup("git status snapshot field", (r"git_status_snapshot",)),
            InvariantGroup("untracked manifest field", (r"untracked_files_manifest",)),
            InvariantGroup("carry forward allowed field", (r"carry_forward_allowed",)),
            InvariantGroup("carry forward rationale field", (r"carry_forward_rationale",)),
            InvariantGroup("de scope approver field", (r"de_scope_approver_source",)),
            InvariantGroup("de scope rationale field", (r"de_scope_rationale",)),
            InvariantGroup("prior report field", (r"prior_report_path",)),
            InvariantGroup("prior cell field", (r"prior_cell_id",)),
            InvariantGroup("previous source commit field", (r"previous_source_commit",)),
            InvariantGroup("relevant paths unchanged evidence field", (r"relevant_paths_unchanged_evidence",)),
            InvariantGroup("console status field", (r"console_status",)),
            InvariantGroup("network status field", (r"network_status",)),
            InvariantGroup("ignored console network justification field", (r"ignored_console_network_justification",)),
        ),
    ),
    ContractCheck(
        "visual-artifact-rca-template-contract",
        "idea-to-ship/templates/visual-artifact-rca.md",
        (
            InvariantGroup("artifact path", (r"artifact path", r"artifact_path")),
            InvariantGroup("redacted url", (r"redacted URL", r"redacted_url")),
            InvariantGroup("source command field", (r"source command",)),
            InvariantGroup("ci job field", (r"CI job",)),
            InvariantGroup("test id field", (r"test id",)),
            InvariantGroup("test title field", (r"test title",)),
            InvariantGroup("project browser field", (r"project/browser",)),
            InvariantGroup("retry index field", (r"retry index",)),
            InvariantGroup("trace step field", (r"trace step",)),
            InvariantGroup("screenshot video field", (r"screenshot/video filename",)),
            InvariantGroup("inspected anchor field", (r"inspected anchor",)),
            InvariantGroup("line range field", (r"line range",)),
            InvariantGroup("byte range field", (r"byte range",)),
            InvariantGroup("snippet cap", (r"snippet cap",)),
            InvariantGroup("redaction notes", (r"redaction",)),
            InvariantGroup("linked cells", (r"linked matrix cell",)),
            InvariantGroup("failure classification", (r"failure classification",)),
        ),
    ),
    ContractCheck(
        "review-code-visual-test-evidence-contract",
        "idea-to-ship/skills/review-code/SKILL.md",
        (
            InvariantGroup("reads report", (r"visual-test-report\.md",)),
            InvariantGroup("reads matrix", (r"visual-test-matrix\.md",)),
            InvariantGroup("reads rca", (r"visual-artifact-rca\.md",)),
            InvariantGroup("reads selectors", (r"visual-test-selectors\.md",)),
            InvariantGroup("ui touched no report", (r"UI-touching diff", r"no `visual-test-report\.md`")),
            InvariantGroup("ui touched no report flag", (r"VISUAL_TEST_REPORT_MISSING",)),
            InvariantGroup("ui touched no matrix flag", (r"VISUAL_TEST_MATRIX_MISSING",)),
            InvariantGroup("stale fingerprint", (r"workspace_diff_fingerprint", r"stale fingerprint")),
            InvariantGroup("self evidence fingerprint exclusion", (r"visual evidence artifacts", r"fingerprint hash input")),
            InvariantGroup("sensitive untracked redaction", (r"auth/session/cookie/token/log/env-like", r"path \+ SHA-256 \+ redacted summary")),
            InvariantGroup("missing matrix evidence", (r"missing matrix evidence",)),
            InvariantGroup("weak artifact anchors", (r"weak artifact anchors",)),
            InvariantGroup("baseline approval", (r"missing baseline approval",)),
            InvariantGroup("console network", (r"unjustified console/network",)),
        ),
    ),
    ContractCheck(
        "visual-test-readme-contract",
        "idea-to-ship/README.md",
        (
            InvariantGroup("command documented", (r"/visual-test",)),
            InvariantGroup("report artifact", (r"visual-test-report\.md",)),
            InvariantGroup("matrix artifact", (r"visual-test-matrix\.md",)),
        ),
    ),
    ContractCheck(
        "root-readme-visual-test-catalog-contract",
        "README.md",
        (
            InvariantGroup("visual-test catalog row", (r"\[`visual-test`\]\(idea-to-ship/skills/visual-test/SKILL\.md\)",)),
        ),
    ),
)


def has_valid_generated_markers(text: str) -> bool:
    start = text.find(GENERATED_START)
    end = text.find(GENERATED_END)
    if start == -1 or end == -1:
        return False
    if start >= end:
        return False
    return text.count(GENERATED_START) == 1 and text.count(GENERATED_END) == 1


def has_required_headings(text: str, headings: tuple[str, ...]) -> bool:
    return all(heading in text for heading in headings)


def resolve_structured_artifact_write_target(
    artifact_path: Path, draft_name: str, required_headings: tuple[str, ...]
) -> Path:
    if not artifact_path.exists():
        return artifact_path

    text = artifact_path.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        return artifact_path
    if has_required_headings(text, required_headings):
        return artifact_path
    return artifact_path.with_name(draft_name)


def resolve_roadmap_write_target(roadmap_path: Path) -> Path:
    if not roadmap_path.exists():
        return roadmap_path

    text = roadmap_path.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        return roadmap_path
    if has_valid_generated_markers(text):
        return roadmap_path
    return roadmap_path.with_name("roadmap.draft.md")


def roadmap_lane_items_are_structured(text: str) -> bool:
    matches = list(re.finditer(r"^### ITS-[^\n]+", text, flags=re.MULTILINE))
    if not matches:
        return False

    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[match.start():end]
        if not all(field in block for field in ROADMAP_LANE_FIELDS):
            return False
    return True


def test_plan_has_traceability_sections(text: str) -> bool:
    required_headings = (
        "## User Stories",
        "## Acceptance Criteria",
        "## Scenario Matrix",
        "## Test Matrix",
        "### Unit",
        "### Integration",
        "## Results",
    )
    return all(heading in text for heading in required_headings)


def parse_untracked_ls_files(raw: bytes) -> tuple[str, ...]:
    paths = sorted(chunk for chunk in raw.split(b"\0") if chunk)
    return tuple(path.decode("utf-8", "surrogateescape") for path in paths)


def filter_visual_evidence_artifact_status(payload: bytes, excluded_paths: tuple[str, ...]) -> bytes:
    if not excluded_paths:
        return payload
    excluded = set(excluded_paths)
    kept = []
    for record in payload.split(b"\0"):
        if not record:
            continue
        path = record[3:].decode("utf-8", "surrogateescape") if len(record) > 3 else ""
        if path not in excluded:
            kept.append(record)
    return b"\0".join(kept) + (b"\0" if kept else b"")


def filter_visual_evidence_artifact_diff(payload: bytes, excluded_paths: tuple[str, ...]) -> bytes:
    if not excluded_paths:
        return payload
    excluded = set(excluded_paths)
    chunks: list[bytes] = []
    current: list[bytes] = []
    for line in payload.splitlines(keepends=True):
        if line.startswith(b"diff --git "):
            if current:
                chunks.append(b"".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        chunks.append(b"".join(current))

    kept = []
    for chunk in chunks:
        if not chunk.startswith(b"diff --git "):
            kept.append(chunk)
            continue
        header = chunk.split(b"\n", 1)[0][len(b"diff --git "):]
        match = re.match(rb"a/(.+?) b/(.+)$", header)
        old_path = match.group(1).decode("utf-8", "surrogateescape") if match else ""
        new_path = match.group(2).decode("utf-8", "surrogateescape") if match else ""
        if old_path in excluded or new_path in excluded:
            continue
        kept.append(chunk)
    return b"".join(kept)


def compute_visual_workspace_fingerprint(
    tracked_status: bytes,
    unstaged_diff: bytes,
    staged_diff: bytes,
    untracked_entries: tuple[UntrackedManifestEntry, ...],
    excluded_evidence_artifact_paths: tuple[str, ...] = (),
) -> tuple[str | None, str | None]:
    tracked_status = filter_visual_evidence_artifact_status(tracked_status, excluded_evidence_artifact_paths)
    unstaged_diff = filter_visual_evidence_artifact_diff(unstaged_diff, excluded_evidence_artifact_paths)
    staged_diff = filter_visual_evidence_artifact_diff(staged_diff, excluded_evidence_artifact_paths)
    untracked_entries = tuple(
        entry for entry in untracked_entries if entry.path not in excluded_evidence_artifact_paths
    )
    unclassified = [entry.path for entry in untracked_entries if entry.classification == "unclassified"]
    if unclassified:
        return None, f"unclassified untracked files: {', '.join(sorted(unclassified))}"

    digest = hashlib.sha256()
    digest.update(b"tracked-status\0")
    digest.update(tracked_status)
    digest.update(b"\0unstaged-diff\0")
    digest.update(unstaged_diff)
    digest.update(b"\0staged-diff\0")
    digest.update(staged_diff)

    for entry in sorted(untracked_entries, key=lambda item: item.path.encode("utf-8", "surrogateescape")):
        digest.update(b"\0untracked\0")
        digest.update(entry.path.encode("utf-8", "surrogateescape"))
        digest.update(b"\0")
        digest.update(entry.classification.encode("utf-8"))
        if entry.classification == "relevant":
            digest.update(b"\0sha256\0")
            digest.update(hashlib.sha256(entry.content).hexdigest().encode("ascii"))
        elif entry.classification == "excluded":
            if not entry.rationale:
                return None, f"excluded untracked file lacks rationale: {entry.path}"
            digest.update(b"\0rationale\0")
            digest.update(entry.rationale.encode("utf-8"))
        else:
            return None, f"unknown untracked classification: {entry.classification}"

    return digest.hexdigest(), None


def review_code_visual_fingerprint_status(current: str | None, reported: str | None) -> str:
    if not current or not reported:
        return "VISUAL_EVIDENCE_GAP"
    if current != reported:
        return "NEEDS_USER"
    return "PASS"


def review_code_visual_evidence_status(ui_diff: bool, has_report: bool, has_matrix: bool) -> str:
    if not ui_diff:
        return "PASS"
    missing: list[str] = []
    if not has_report:
        missing.append("VISUAL_TEST_REPORT_MISSING")
    if not has_matrix:
        missing.append("VISUAL_TEST_MATRIX_MISSING")
    return "+".join(missing) if missing else "PASS"


VISUAL_VERDICT_SCENARIOS: tuple[VisualVerdictScenario, ...] = (
    VisualVerdictScenario("all fresh pass", ("PASS",), expected="PASS"),
    VisualVerdictScenario("valid carried forward pass", ("PASS",), carry_forward=True, expected="PASS"),
    VisualVerdictScenario(
        "carry forward missing prior evidence",
        ("PASS",),
        carry_forward=True,
        carry_forward_prior_evidence=False,
        expected="NEEDS_USER",
    ),
    VisualVerdictScenario(
        "carry forward relevant path changed",
        ("PASS",),
        carry_forward=True,
        carry_forward_relevant_changed=True,
        expected="NEEDS_USER",
    ),
    VisualVerdictScenario("required fail", ("FAIL",), expected="FAIL"),
    VisualVerdictScenario("required flaky", ("FLAKY",), expected="FAIL"),
    VisualVerdictScenario("required miss", ("MISS",), expected="NEEDS_USER"),
    VisualVerdictScenario("needs run", ("NEEDS-RUN",), expected="NEEDS_USER"),
    VisualVerdictScenario("required skip is not success", ("SKIP-with-reason",), expected="NEEDS_USER"),
    VisualVerdictScenario(
        "explicit descoped required skip can pass",
        ("SKIP-with-reason",),
        descoped_required=True,
        expected="PASS",
    ),
    VisualVerdictScenario(
        "descoped required skip missing approver",
        ("SKIP-with-reason",),
        descoped_required=True,
        descoped_has_approver=False,
        expected="NEEDS_USER",
    ),
    VisualVerdictScenario(
        "descoped required skip missing rationale",
        ("SKIP-with-reason",),
        descoped_required=True,
        descoped_has_rationale=False,
        expected="NEEDS_USER",
    ),
    VisualVerdictScenario("stale fingerprint", ("PASS",), fingerprint_fresh=False, expected="NEEDS_USER"),
    VisualVerdictScenario("unapproved baseline", ("PASS",), baseline_approved=False, expected="NEEDS_USER"),
    VisualVerdictScenario("console fail", ("PASS",), console_status="FAIL", expected="FAIL"),
    VisualVerdictScenario("console unknown", ("PASS",), console_status="UNKNOWN", expected="NEEDS_USER"),
    VisualVerdictScenario("console blank", ("PASS",), console_status="", expected="NEEDS_USER"),
    VisualVerdictScenario("network fail", ("PASS",), network_status="FAIL", expected="FAIL"),
    VisualVerdictScenario("network not collected", ("PASS",), network_status="NOT_COLLECTED", expected="NEEDS_USER"),
    VisualVerdictScenario("network unknown", ("PASS",), network_status="UNKNOWN", expected="NEEDS_USER"),
    VisualVerdictScenario("network blank", ("PASS",), network_status="", expected="NEEDS_USER"),
    VisualVerdictScenario(
        "ignored incomplete",
        ("PASS",),
        console_status="IGNORED-with-justification",
        ignored_complete=False,
        expected="NEEDS_USER",
    ),
    VisualVerdictScenario("artifact blocker", ("PASS",), artifact_blocker=True, expected="FAIL"),
    VisualVerdictScenario("unclassified untracked", ("PASS",), unclassified_untracked=True, expected="NEEDS_USER"),
    VisualVerdictScenario("unknown status", ("PASSED",), expected="NEEDS_USER"),
    VisualVerdictScenario("blank status", ("",), expected="NEEDS_USER"),
    VisualVerdictScenario("no required status evidence", (), expected="NEEDS_USER"),
)


ALLOWED_VISUAL_CELL_STATUSES = {"PASS", "FAIL", "FLAKY", "MISS", "NEEDS-RUN", "SKIP-with-reason"}
ALLOWED_CONSOLE_NETWORK_STATUSES = {"PASS", "FAIL", "NOT_COLLECTED", "IGNORED-with-justification"}


def aggregate_visual_verdict(scenario: VisualVerdictScenario) -> str:
    if not scenario.required_statuses:
        return "NEEDS_USER"
    if any(status not in ALLOWED_VISUAL_CELL_STATUSES for status in scenario.required_statuses):
        return "NEEDS_USER"
    required_statuses = tuple(
        "PASS"
        if (
            status == "SKIP-with-reason"
            and scenario.descoped_required
            and scenario.descoped_has_approver
            and scenario.descoped_has_rationale
        )
        else status
        for status in scenario.required_statuses
    )
    if (
        scenario.console_status not in ALLOWED_CONSOLE_NETWORK_STATUSES
        or scenario.network_status not in ALLOWED_CONSOLE_NETWORK_STATUSES
    ):
        return "NEEDS_USER"
    if (
        any(status in {"FAIL", "FLAKY"} for status in required_statuses)
        or scenario.console_status == "FAIL"
        or scenario.network_status == "FAIL"
        or scenario.artifact_blocker
    ):
        return "FAIL"
    if (
        any(status in {"MISS", "NEEDS-RUN", "SKIP-with-reason"} for status in required_statuses)
        or not scenario.fingerprint_fresh
        or not scenario.baseline_approved
        or scenario.unclassified_untracked
        or (scenario.carry_forward and not scenario.carry_forward_prior_evidence)
        or (scenario.carry_forward and scenario.carry_forward_relevant_changed)
        or scenario.console_status == "NOT_COLLECTED"
        or scenario.network_status == "NOT_COLLECTED"
        or (scenario.console_status == "IGNORED-with-justification" and not scenario.ignored_complete)
        or (scenario.network_status == "IGNORED-with-justification" and not scenario.ignored_complete)
    ):
        return "NEEDS_USER"
    return "PASS"


def run_visual_scenario_fixtures(root: Path) -> list[tuple[str, str | None]]:
    results: list[tuple[str, str | None]] = []

    base_entries = (
        UntrackedManifestEntry("docs/manual-note.md", "excluded", rationale="non-visual planning note"),
    )
    base, failure = compute_visual_workspace_fingerprint(b"", b"", b"", base_entries)
    staged, _ = compute_visual_workspace_fingerprint(b"", b"", b"diff --git a/ui.css b/ui.css\n+color: red\n", base_entries)
    unstaged, _ = compute_visual_workspace_fingerprint(b"", b"diff --git a/ui.css b/ui.css\n+color: blue\n", b"", base_entries)
    relevant_untracked, _ = compute_visual_workspace_fingerprint(
        b"",
        b"",
        b"",
        (
            UntrackedManifestEntry("src/new-widget.css", "relevant", content=b".widget { color: red; }"),
        ),
    )
    relevant_untracked_changed, _ = compute_visual_workspace_fingerprint(
        b"",
        b"",
        b"",
        (
            UntrackedManifestEntry("src/new-widget.css", "relevant", content=b".widget { color: blue; }"),
        ),
    )
    unclassified, unclassified_failure = compute_visual_workspace_fingerprint(
        b"",
        b"",
        b"",
        (
            UntrackedManifestEntry("src/new-widget.css", "unclassified"),
        ),
    )

    fingerprint_expectations = (
        ("visual-fingerprint-base-valid", base is not None and failure is None, failure or "invalid base fingerprint"),
        ("visual-fingerprint-staged-content-change", staged != base, "staged content did not change fingerprint"),
        ("visual-fingerprint-unstaged-content-change", unstaged != base, "unstaged content did not change fingerprint"),
        (
            "visual-fingerprint-relevant-untracked-content-change",
            relevant_untracked != relevant_untracked_changed,
            "relevant untracked content did not change fingerprint",
        ),
        (
            "visual-fingerprint-unclassified-untracked-blocks-pass",
            unclassified is None and bool(unclassified_failure),
            "unclassified untracked file did not block fingerprint",
        ),
    )
    for check_id, passed, message in fingerprint_expectations:
        results.append((check_id, None if passed else message))

    parsed_untracked = parse_untracked_ls_files(b"nested/untracked/component.css\0top-level.md\0")
    if parsed_untracked == ("nested/untracked/component.css", "top-level.md"):
        results.append(("visual-fingerprint-nested-untracked-enumeration", None))
    else:
        results.append(
            (
                "visual-fingerprint-nested-untracked-enumeration",
                f"unexpected parsed paths: {parsed_untracked}",
            )
        )

    invalid_utf8_path = b"\xff-auth-state.json".decode("utf-8", "surrogateescape")
    invalid_utf8_fingerprint, invalid_utf8_failure = compute_visual_workspace_fingerprint(
        b"",
        b"",
        b"",
        (UntrackedManifestEntry(invalid_utf8_path, "relevant", content=b"\xff\x00{}"),),
    )
    if invalid_utf8_fingerprint and invalid_utf8_failure is None:
        results.append(("visual-fingerprint-invalid-utf8-untracked-path", None))
    else:
        results.append(
            (
                "visual-fingerprint-invalid-utf8-untracked-path",
                invalid_utf8_failure or "invalid UTF-8 path did not fingerprint",
            )
        )

    evidence_artifact_path = ".idea-to-ship/demo/visual-test-report.md"
    evidence_artifact_base, _ = compute_visual_workspace_fingerprint(
        b"",
        b"",
        b"",
        (),
        excluded_evidence_artifact_paths=(evidence_artifact_path,),
    )
    evidence_artifact_changed, _ = compute_visual_workspace_fingerprint(
        f" M {evidence_artifact_path}\0".encode("utf-8"),
        f"diff --git a/{evidence_artifact_path} b/{evidence_artifact_path}\n+aggregate_verdict: PASS\n".encode("utf-8"),
        b"",
        (UntrackedManifestEntry(".idea-to-ship/demo/visual-test-matrix.md", "relevant", content=b"PASS"),),
        excluded_evidence_artifact_paths=(
            evidence_artifact_path,
            ".idea-to-ship/demo/visual-test-matrix.md",
        ),
    )
    if evidence_artifact_changed == evidence_artifact_base:
        results.append(("visual-fingerprint-excludes-self-evidence-artifacts", None))
    else:
        results.append(
            (
                "visual-fingerprint-excludes-self-evidence-artifacts",
                "visual evidence artifact updates changed fingerprint",
            )
        )

    adjacent_artifact, _ = compute_visual_workspace_fingerprint(
        b" M .idea-to-ship/demo/visual-test-report.md.backup\0",
        b"diff --git a/.idea-to-ship/demo/visual-test-report.md.backup b/.idea-to-ship/demo/visual-test-report.md.backup\n+relevant backup\n",
        b"",
        (),
        excluded_evidence_artifact_paths=(evidence_artifact_path,),
    )
    if adjacent_artifact != evidence_artifact_base:
        results.append(("visual-fingerprint-keeps-adjacent-non-evidence-artifacts", None))
    else:
        results.append(
            (
                "visual-fingerprint-keeps-adjacent-non-evidence-artifacts",
                "adjacent non-evidence artifact was excluded from fingerprint",
            )
        )

    embedded_fake_header_red, _ = compute_visual_workspace_fingerprint(
        b"",
        (
            b"diff --git a/src/widget.css b/src/widget.css\n"
            b"@@\n"
            + f"+diff --git a/{evidence_artifact_path} b/{evidence_artifact_path}\n".encode("utf-8")
            + b"+changed visual-affecting content: red\n"
        ),
        b"",
        (),
        excluded_evidence_artifact_paths=(evidence_artifact_path,),
    )
    embedded_fake_header_blue, _ = compute_visual_workspace_fingerprint(
        b"",
        (
            b"diff --git a/src/widget.css b/src/widget.css\n"
            b"@@\n"
            + f"+diff --git a/{evidence_artifact_path} b/{evidence_artifact_path}\n".encode("utf-8")
            + b"+changed visual-affecting content: blue\n"
        ),
        b"",
        (),
        excluded_evidence_artifact_paths=(evidence_artifact_path,),
    )
    if embedded_fake_header_red != embedded_fake_header_blue:
        results.append(("visual-fingerprint-keeps-embedded-fake-diff-header", None))
    else:
        results.append(
            (
                "visual-fingerprint-keeps-embedded-fake-diff-header",
                "embedded fake evidence-artifact diff header was excluded from relevant diff content",
            )
        )

    for scenario in VISUAL_VERDICT_SCENARIOS:
        actual = aggregate_visual_verdict(scenario)
        check_id = f"visual-aggregate-verdict-{scenario.name.replace(' ', '-')}"
        if actual == scenario.expected:
            results.append((check_id, None))
        else:
            results.append((check_id, f"expected {scenario.expected}, got {actual}"))

    review_code = read_skill(root, "idea-to-ship/skills/review-code/SKILL.md")
    ui_no_report = (
        re.search(r"UI-touching diff", review_code, flags=re.IGNORECASE)
        and re.search(r"VISUAL_TEST_REPORT_MISSING", review_code, flags=re.IGNORECASE)
        and re.search(r"missing visual evidence", review_code, flags=re.IGNORECASE)
    )
    if ui_no_report:
        results.append(("review-code-ui-no-visual-report-scenario", None))
    else:
        results.append(
            (
                "review-code-ui-no-visual-report-scenario",
                "review-code does not surface UI-touching diffs without visual report",
            )
        )

    fingerprint_scenarios = (
        ("review-code-fingerprint-match", "abc", "abc", "PASS"),
        ("review-code-fingerprint-stale", "abc", "def", "NEEDS_USER"),
        ("review-code-fingerprint-not-computed", None, "def", "VISUAL_EVIDENCE_GAP"),
        ("review-code-fingerprint-missing-report", "abc", None, "VISUAL_EVIDENCE_GAP"),
    )
    for check_id, current, reported, expected in fingerprint_scenarios:
        actual = review_code_visual_fingerprint_status(current, reported)
        if actual == expected:
            results.append((check_id, None))
        else:
            results.append((check_id, f"expected {expected}, got {actual}"))

    evidence_scenarios = (
        ("review-code-visual-evidence-complete", True, True, True, "PASS"),
        ("review-code-visual-evidence-report-missing", True, False, True, "VISUAL_TEST_REPORT_MISSING"),
        ("review-code-visual-evidence-matrix-missing", True, True, False, "VISUAL_TEST_MATRIX_MISSING"),
        (
            "review-code-visual-evidence-both-missing",
            True,
            False,
            False,
            "VISUAL_TEST_REPORT_MISSING+VISUAL_TEST_MATRIX_MISSING",
        ),
        ("review-code-visual-evidence-not-ui", False, False, False, "PASS"),
    )
    for check_id, ui_diff, has_report, has_matrix, expected in evidence_scenarios:
        actual = review_code_visual_evidence_status(ui_diff, has_report, has_matrix)
        if actual == expected:
            results.append((check_id, None))
        else:
            results.append((check_id, f"expected {expected}, got {actual}"))

    return results


def run_artifact_fixtures(root: Path) -> list[tuple[str, str | None]]:
    results: list[tuple[str, str | None]] = []

    roadmap_path = root / ".idea-to-ship" / "roadmap.md"
    roadmap_text = read_skill(root, ".idea-to-ship/roadmap.md")
    if has_valid_generated_markers(roadmap_text):
        results.append(("roadmap-generated-marker-artifact", None))
    else:
        results.append(
            ("roadmap-generated-marker-artifact", "invalid or missing generated marker pair")
        )

    if roadmap_lane_items_are_structured(roadmap_text):
        results.append(("roadmap-lane-schema-artifact", None))
    else:
        results.append(
            ("roadmap-lane-schema-artifact", "lane item missing required template fields")
        )

    if has_valid_generated_markers(roadmap_text):
        expected_target = roadmap_path
    else:
        expected_target = roadmap_path.with_name("roadmap.draft.md")
    actual_target = resolve_roadmap_write_target(roadmap_path)
    if actual_target == expected_target:
        results.append(("roadmap-write-target-artifact", None))
    else:
        results.append(
            (
                "roadmap-write-target-artifact",
                f"expected {expected_target.name}, got {actual_target.name}",
            )
        )

    with TemporaryDirectory(prefix="idea-to-ship-artifacts-") as tmp:
        temp_root = Path(tmp)
        artifact_dir = temp_root / ".idea-to-ship"
        artifact_dir.mkdir()
        human_only = artifact_dir / "roadmap.md"
        human_only.write_text("# Human Roadmap\n\nManual planning notes.\n", encoding="utf-8")
        draft_target = resolve_roadmap_write_target(human_only)
        if draft_target.name == "roadmap.draft.md":
            results.append(("roadmap-draft-fallback-artifact", None))
        else:
            results.append(
                (
                    "roadmap-draft-fallback-artifact",
                    f"expected roadmap.draft.md, got {draft_target.name}",
                )
            )

        generated = artifact_dir / "generated.md"
        generated.write_text(
            "# Roadmap\n\nHuman note.\n\n"
            f"{GENERATED_START}\n\n## Now\n\nagent content\n\n{GENERATED_END}\n",
            encoding="utf-8",
        )
        generated_target = resolve_roadmap_write_target(generated)
        if generated_target == generated:
            results.append(("roadmap-marker-preservation-artifact", None))
        else:
            results.append(
                (
                    "roadmap-marker-preservation-artifact",
                    f"expected generated.md, got {generated_target.name}",
                )
            )

        malformed_requirements = artifact_dir / "requirements.md"
        malformed_requirements.write_text(
            "# Human Requirements\n\nManual product notes.\n", encoding="utf-8"
        )
        requirements_target = resolve_structured_artifact_write_target(
            malformed_requirements,
            "requirements.draft.md",
            REQUIREMENTS_CORE_HEADINGS,
        )
        if requirements_target.name == "requirements.draft.md":
            results.append(("requirements-draft-fallback-artifact", None))
        else:
            results.append(
                (
                    "requirements-draft-fallback-artifact",
                    f"expected requirements.draft.md, got {requirements_target.name}",
                )
            )

        malformed_architecture = artifact_dir / "architecture.md"
        malformed_architecture.write_text(
            "# Human Architecture\n\nManual design notes.\n", encoding="utf-8"
        )
        architecture_target = resolve_structured_artifact_write_target(
            malformed_architecture,
            "architecture.draft.md",
            ARCHITECTURE_CORE_HEADINGS,
        )
        if architecture_target.name == "architecture.draft.md":
            results.append(("architecture-draft-fallback-artifact", None))
        else:
            results.append(
                (
                    "architecture-draft-fallback-artifact",
                    f"expected architecture.draft.md, got {architecture_target.name}",
                )
            )

        malformed_interface_design = artifact_dir / "interface-design.md"
        malformed_interface_design.write_text(
            "# Human Interface Notes\n\nManual visual notes.\n", encoding="utf-8"
        )
        interface_design_target = resolve_structured_artifact_write_target(
            malformed_interface_design,
            "interface-design.draft.md",
            INTERFACE_DESIGN_CORE_HEADINGS,
        )
        if interface_design_target.name == "interface-design.draft.md":
            results.append(("interface-design-draft-fallback-artifact", None))
        else:
            results.append(
                (
                    "interface-design-draft-fallback-artifact",
                    f"expected interface-design.draft.md, got {interface_design_target.name}",
                )
            )

    requirements_path = root / ".idea-to-ship" / "ITS-ROADMAP-006" / "requirements.md"
    requirements_text = read_skill(
        root, ".idea-to-ship/ITS-ROADMAP-006/requirements.md"
    )
    requirements_target = resolve_structured_artifact_write_target(
        requirements_path,
        "requirements.draft.md",
        REQUIREMENTS_CORE_HEADINGS,
    )
    if (
        has_required_headings(requirements_text, REQUIREMENTS_CORE_HEADINGS)
        and requirements_target == requirements_path
    ):
        results.append(("requirements-structured-artifact", None))
    else:
        results.append(
            (
                "requirements-structured-artifact",
                "missing core headings or unsafe write target",
            )
        )

    architecture_path = root / ".idea-to-ship" / "ITS-ROADMAP-006" / "architecture.md"
    architecture_text = read_skill(
        root, ".idea-to-ship/ITS-ROADMAP-006/architecture.md"
    )
    architecture_target = resolve_structured_artifact_write_target(
        architecture_path,
        "architecture.draft.md",
        ARCHITECTURE_CORE_HEADINGS,
    )
    if (
        has_required_headings(architecture_text, ARCHITECTURE_CORE_HEADINGS)
        and architecture_target == architecture_path
    ):
        results.append(("architecture-structured-artifact", None))
    else:
        results.append(
            (
                "architecture-structured-artifact",
                "missing core headings or unsafe write target",
            )
        )

    test_plan_text = read_skill(root, ".idea-to-ship/ITS-ROADMAP-006/test-plan.md")
    if test_plan_has_traceability_sections(test_plan_text):
        results.append(("test-plan-traceability-artifact", None))
    else:
        results.append(
            ("test-plan-traceability-artifact", "missing required traceability sections")
        )

    return results


def usage() -> None:
    print("Usage: idea-to-ship-eval-fixtures.py <repo-root>", file=sys.stderr)


def read_skill(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        print(f"Missing skill file: {relative_path}", file=sys.stderr)
        raise SystemExit(2)
    return path.read_text(encoding="utf-8", errors="replace")


def group_matches(text: str, group: InvariantGroup) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL) for pattern in group.patterns)


def run_check(root: Path, check: ContractCheck) -> list[str]:
    text = read_skill(root, check.skill_path)
    failures: list[str] = []
    for group in check.groups:
        if not group_matches(text, group):
            failures.append(group.name)
    return failures


def run_all(root: Path, checks: Iterable[ContractCheck]) -> int:
    failures = 0
    print("Idea-to-ship contract fixtures")
    for check in checks:
        missing = run_check(root, check)
        if missing:
            failures += 1
            print(f"FAIL {check.check_id}: missing invariant group(s): {', '.join(missing)}")
        else:
            print(f"PASS {check.check_id}: contract fixture coverage present")
    print("Idea-to-ship visual scenario fixtures")
    for check_id, failure in run_visual_scenario_fixtures(root):
        if failure:
            failures += 1
            print(f"FAIL {check_id}: {failure}")
        else:
            print(f"PASS {check_id}: visual scenario passed")
    print("Idea-to-ship artifact fixtures")
    for check_id, failure in run_artifact_fixtures(root):
        if failure:
            failures += 1
            print(f"FAIL {check_id}: {failure}")
        else:
            print(f"PASS {check_id}: artifact safety coverage present")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        usage()
        return 2

    root = Path(argv[1]).resolve()
    if not root.is_dir():
        print(f"Repo root is not a directory: {root}", file=sys.stderr)
        return 2

    return run_all(root, CHECKS)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
