# Vibe Coding Health Check - agent-plugins-linghao skills

**Date:** 2026-05-12
**Scope:** agent
**Decision:** Slow down
**Overall:** B-

## Summary
The repository contains 29 `SKILL.md` files and the release gate passes, so
there is no blocking structural failure. The main risk is context/tool hygiene:
the runtime skill registry contains duplicate plugin copies, and several repo
skills duplicate routing, artifact ownership, code-style-guide, and review-loop
instructions. Consolidating those common contracts would reduce routing
ambiguity and prompt bloat without changing skill behavior.

## Scorecard
| Dimension | Status | Evidence | Why It Matters |
|---|---|---|---|
| Change size | green | `git status --short` clean; no diff before artifact write | No feature diff is being mixed into this audit. |
| Scope control | green | Audited `*/skills/*/SKILL.md`, plugin manifests, and release gate only | The work maps to the user's skill-duplication question. |
| Requirement traceability | yellow | User request: "当前 skills 里有哪些重复定义的，哪些是可以被复用的，哪些描述是冗余的" | The request is clear enough for an audit but not a standing repo policy yet. |
| Test/verification | green | `scripts/release-gate.sh --mode all` passed | Frontmatter, manifests, fixture checks, whitespace, and secret scan are healthy. |
| Error/resilience | yellow | `antifragile-agent`, `harness-audit`, and `context-audit` overlap but have different boundaries | Duplicate resilience language can make future agents route to the broadest skill. |
| State/recovery | yellow | Repeated artifact ownership rules in `brainstorm`, `architect`, `test`, `roadmap`, `vibe` | Copy-pasted preservation rules can drift. |
| Context/tool hygiene | yellow | Runtime registry duplicate entries across `agent-playbook`, `harness-engineering`, `idea-to-ship`, `issue-evaluator`, `react-doctor` | Duplicate loaded skills increase routing ambiguity and context noise. |

## Checks Run
| Command | Result | Notes |
|---|---|---|
| `rg --files -g 'SKILL.md'` | pass | Found 29 skill files. |
| `rg -n "^(name|description|argument-hint|allowed-tools):" -g 'SKILL.md'` | pass | No duplicate `name:` values inside the repo. |
| `scripts/release-gate.sh --mode all` | pass | Validated 10 manifests, 29 skill frontmatters, 2 metadata files; fixture checks passed. |
| `wc -l */skills/*/SKILL.md` | pass | 6,498 total lines; largest files are `fix-pr-comments` and `review-pr`. |

## Routed Audits
| Trigger | Recommended Skill | Run Now? | Reason |
|---|---|---|---|
| Duplicate runtime skill registrations | `agent-playbook:context-audit` | No | This audit already covered the focused skill list; deeper context audit would inspect runtime config sources. |
| Shared review-loop and tool-contract duplication | `agent-playbook:tool-review` | No | Useful if extracting shared helper tools or schemas. |
| Plugin/hook/skill operational overlap | `antifragile:antifragile-agent` | No | Recommended before changing hooks or shared skill-loading behavior. |

## Duplicate Definitions
- Runtime registry duplicates, not repo file duplicates: the current session's available skill list contains duplicate entries from `agent-plugins-linghao` and `claude-skills` cache roots. Duplicated groups include `agent-playbook:bootstrap-project-memory`, `agent-playbook:context-audit`, `agent-playbook:tool-review`, all four `harness-engineering` skills, most `idea-to-ship` skills, most `issue-evaluator` skills, and `react-doctor`.
- Repo-local exact duplicates: not found. The 29 local `SKILL.md` files have unique `name:` values and pass structural validation.
- Near-duplicate skill roles: `issue-evaluator/review-fix` and `idea-to-ship/review-code` both review current diffs with an adversarial loop; the real boundary is "GitHub issue fix with repo style guide" vs "idea-to-ship implementation with requirements/design/test traceability".
- Near-duplicate PR workflows: `issue-evaluator/review-pr` and `issue-evaluator/fix-pr-comments` both fetch PR metadata/diff/comments, enforce GitHub read-only behavior, load a code style guide, and run multi-role review. Their distinct boundary is "review a PR" vs "triage existing reviewer comments and apply local edits".
- Near-duplicate issue workflows: `issue-evaluator/evaluate-issue`, `fix-issue`, and `update-code-style` repeat the same code-style-guide generation contract and runtime-aware routing language.
- Near-duplicate agent audit roles: `agent-playbook/context-audit`, `agent-playbook/tool-review`, `antifragile/antifragile-agent`, and `harness-engineering/harness-audit` overlap on MCP/tool sprawl, bounded outputs, state, retry, and verification. They are reusable as a ladder, not interchangeable.

## Reuse Candidates
- Code style guide lifecycle: extract from `evaluate-issue`, `fix-issue`, `review-pr`, `fix-pr-comments`, and `update-code-style`. Shared contract should cover storage path, staleness rule, two-agent generation, compact checklist extraction, and metadata header.
- Runtime-aware agent routing: extract from `review-code`, `review-design`, `evaluate-issue`, `fix-issue`, `review-pr`, `fix-pr-comments`, `review-fix`, and `update-code-style`. Shared contract should say "use host-native subagents only when authorized; fall back in main context; do not request Claude-only model names outside Claude Code".
- Artifact ownership: extract from `brainstorm`, `architect`, `implement --tdd`, `test`, `roadmap`, and `vibe-coding-health-check`. Shared rule should cover stable IDs, heading-based merge, preserving human notes, and `.draft.md` fallback.
- GitHub read-only safety: extract for `review-pr`, `fix-pr-comments`, `scan-issues`, and `roadmap --include-github`. Shared rule should define allowed `gh` commands and forbidden write operations.
- Adversarial review loop: extract for `review-design`, `review-code`, and `review-fix`. Shared rule should cover iteration cap, scope filtering, LGTM sentinel, fallback reviewer, and final holistic pass.
- Harness primitives: extract `state.json`, retry wrapper, schema validator, tool-output truncation, context reset, and memory consolidation terminology from `harness-design`, `harness-audit`, `resilience-plan`, and `sprint-contract`.
- Router skill pattern: keep `vibe-coding-health-check` as a thin scorecard/router and reuse deeper audits instead of embedding downstream trigger logic in its frontmatter description.

## Red / Yellow Findings
- [ ] yellow - Runtime duplicate skill registrations - available skill list includes duplicated plugin copies from separate cache roots - pick one canonical root per plugin or adjust installed plugin source precedence.
- [ ] yellow - Code-style-guide workflow is duplicated across five issue-evaluator skills - repeated blocks can drift on path/staleness/metadata behavior - extract a shared reference and have skills cite it.
- [ ] yellow - Runtime-aware routing text is repeated across eight skills - model/runtime instructions are likely to diverge - extract one shared routing contract.
- [ ] yellow - Artifact ownership rules are repeated in several idea-to-ship skills - merge/preserve/draft semantics can drift - extract a shared "Artifact Ownership" section.
- [ ] yellow - `vibe-coding-health-check` frontmatter is broad enough to compete with deeper skills - description names multiple downstream audits - shorten description and keep routing table in body.
- [ ] yellow - `commit-changes`, `roadmap`, `fix-pr-comments`, and `review-pr` descriptions carry too much workflow detail - frontmatter should optimize routing, not encode the whole procedure - move details to body/shared references.

## Passed
- No duplicate local `name:` values in repo skill frontmatter.
- Release gate passes in `--mode all`.
- The overlapping audit skills have defensible boundaries when read in full.
- The repo already has fixture tests for `idea-to-ship` and `agent-playbook`.

## Next Steps
1. Decide canonical runtime roots for duplicated plugin families; prefer this repo's local plugin copies when actively developing them.
2. Extract shared references for code-style-guide lifecycle, runtime-aware routing, artifact ownership, GitHub read-only safety, and adversarial review loops.
3. Shorten broad frontmatter descriptions so routing is based on task intent, while detailed safety and workflow rules stay in the skill body or shared references.
