# Code Review - ITS-ROADMAP-015

**Date:** 2026-05-16
**Reviewer:** multi-agent round 1; same-context fallback round 2
**Iterations:** 2
**Result:** clean
**Mode:** multi-agent + degraded-same-context-review
**Degradation reason:** round-2 reviewer sub-agents were unavailable due usage-limit/capacity errors, so the same correctness/security, traceability/testability, and maintainability/repo-fit prompts were rerun in the main context.
**Diff size:** tracked diff: 5 files, 825 insertions, 10 deletions; plus new `scripts/skill-authoring-baseline.txt` and `.idea-to-ship/ITS-ROADMAP-015/*` artifacts.

## Issues Raised & Resolution

| # | Severity | File:line | Issue | Resolution |
|---|---|---|---|---|
| 1 | warning | `scripts/skill-hygiene-check.py:141` | Unsafe-command detection missed `git checkout -- .` and `curl ... | bash`. | Added explicit destructive checkout and curl-pipe patterns plus fixture coverage. |
| 2 | warning | `scripts/skill-hygiene-check.py:579` | Non-dollar `plugin:skill` refs and unknown plugin-qualified refs were not fully validated. | Related-skill extraction now validates all plugin-qualified and path refs against the mode-aware local inventory. |
| 3 | warning | `scripts/skill-hygiene-check.py:607` | Hidden Mermaid inside HTML comments could satisfy the workflow-diagram rule. | Diagram scan now strips HTML comments and fixtures assert hidden Mermaid does not pass. |
| 4 | warning | `scripts/skill-hygiene-check.py:128` | Bare `plan` / `status` made task-tracking detection too permissive. | Tightened task-tracking signals to concrete tracking/status-update language. |
| 5 | warning | `scripts/skill-hygiene-check.py:687` | Placeholder explanation could be satisfied by words inside the command itself. | Placeholder explanations now come only from nearby context, with fixture coverage. |
| 6 | warning | `tests/skill-hygiene-check-fixtures.py:2298` | Baseline bypass evidence covered working mode but not dirty all-mode. | Added dirty all-mode baseline-bypass assertion. |
| 7 | warning | `tests/skill-hygiene-release-gate-fixtures.sh:500` | Release-gate strict fixture asserted only partial authoring evidence. | Added JSON evidence assertions for all seven new authoring IDs. |
| 8 | warning | `tests/skill-hygiene-check-fixtures.py:2333` | Related-skill tests covered dollar refs but not non-dollar or path refs. | Added non-dollar `plugin:skill` and `plugin/skills/skill/SKILL.md` variants. |
| 9 | warning | `scripts/skill-authoring-baseline.txt` | New required baseline file was untracked during review. | File exists in the working tree and is documented as a required new file; no commit/staging was requested. |
| 10 | warning | `scripts/skill-hygiene-check.py:607` | Mermaid edge lines with common four-space indentation inside a fenced diagram were skipped, causing false positives. | Moved indented-code skipping outside active fences and changed compliant fixtures to use four-space-indented Mermaid edges. |
| 11 | nit | `scripts/skill-hygiene-check.py:579` | `known_plugins` parameter became unused after validating all qualified refs. | Removed the parameter and updated the caller. |

## Review Rounds

| Round | Angle | Route | Verdict |
|---|---|---|---|
| 1 | correctness/security | sub-agent | 4 warnings |
| 1 | traceability/testability | sub-agent | 5 warnings |
| 1 | maintainability/repo-fit | sub-agent | 2 warnings |
| 2 | correctness/security | degraded same-context | 1 warning, then LGTM after fix |
| 2 | traceability/testability | degraded same-context | LGTM |
| 2 | maintainability/repo-fit | degraded same-context | 1 nit, then LGTM after fix |

## Final Holistic Pass

- Requirements match: FR-1..FR-7 map to checker findings and fixtures; FR-8 maps to `RELEASE-GATE.md`; FR-9 maps to Python/Bash fixtures; FR-10 maps to strict release-gate verification.
- Design drift: none. The implementation follows the baseline-based Option A and artifacts were updated after review fixes.
- Test traceability: every new check ID has positive evidence; compliant skills, baseline target selection, staged inventory, command safety, placeholders, hidden Mermaid comments, and indented Mermaid content are covered.
- UI/UX angle: not applicable; no `interface-design.md` exists and the diff does not touch UI.
- Residual open issues: none. `scripts/skill-authoring-baseline.txt` remains a new untracked file because no commit or staging operation was requested.

## Final Verdict

All required review angles are clean after fixes. The second iteration used the documented same-context fallback because reviewer sub-agents were at capacity, not because multi-angle review was skipped.
