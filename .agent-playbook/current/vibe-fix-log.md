# Vibe Coding Fix Log - agent-plugins-linghao skills

**Source health check:** vibe-health-check.md
**Date:** 2026-05-12
**Mode:** apply

## Classification
| Finding | Class | Planned Action | Reason |
|---|---|---|---|
| Runtime duplicate skill registrations | User-owned decision | Defer global runtime cleanup | Duplicates come from installed cache roots outside this repo; deleting or re-prioritizing them changes the user's global setup. |
| Code-style-guide workflow duplication | Safe local cleanup | Extract shared `issue-evaluator/WORKFLOW-CONTRACTS.md` and replace repeated long blocks with references | This is repo-local documentation/skill contract cleanup. |
| Runtime-aware routing duplication | Safe local cleanup | Move shared routing language into `issue-evaluator/WORKFLOW-CONTRACTS.md` and cite it from issue-evaluator skills | This reduces repeated model/runtime instructions without changing workflow roles. |
| Artifact ownership and health-to-fix gap | Safe local cleanup | Add `agent-playbook/WORKFLOW-CONTRACTS.md` and new `vibe-coding-fix` skill | The health check now has a bounded fix handoff rather than embedding fix behavior in diagnosis. |
| Broad frontmatter descriptions | Safe local cleanup | Shorten high-noise descriptions in `vibe-coding-health-check`, `commit-changes`, `review-pr`, `fix-pr-comments`, and `roadmap` | Frontmatter should route; detailed safety rules belong in bodies/shared contracts. |

## Applied Fixes
| File | Change | Evidence |
|---|---|---|
| `agent-playbook/WORKFLOW-CONTRACTS.md` | Added shared health-to-fix, classification, artifact, and frontmatter contracts | Supports `vibe-coding-health-check` and `vibe-coding-fix`. |
| `agent-playbook/skills/vibe-coding-fix/SKILL.md` | Added bounded fix workflow for health-check findings | New skill classifies safe/routed/user-owned/stop findings and writes this log. |
| `agent-playbook/skills/vibe-coding-fix/agents/openai.yaml` | Added OpenAI interface metadata | Release gate validated 3 metadata files. |
| `agent-playbook/skills/vibe-coding-health-check/SKILL.md` | Shortened description and added fix handoff | Fixture `vibe-health-fix-handoff-contract` passed. |
| `issue-evaluator/WORKFLOW-CONTRACTS.md` | Added shared routing, code-style-guide lifecycle, GitHub read-only, and adversarial-loop contracts | Referenced by five issue-evaluator skills. |
| `issue-evaluator/skills/evaluate-issue/SKILL.md` | Replaced duplicated routing/code-style lifecycle text with shared contract references | Release gate and fixtures passed. |
| `issue-evaluator/skills/fix-issue/SKILL.md` | Replaced duplicated code-style guide generation and path logic with shared contract references | Release gate passed. |
| `issue-evaluator/skills/review-pr/SKILL.md` | Replaced duplicated routing/code-style lifecycle text with shared contract references | Release gate passed. |
| `issue-evaluator/skills/fix-pr-comments/SKILL.md` | Replaced duplicated routing/code-style lifecycle text with shared contract references | Release gate passed. |
| `issue-evaluator/skills/review-fix/SKILL.md` | Replaced duplicated routing/path guidance with shared contract references | Release gate passed. |
| `issue-evaluator/skills/update-code-style/SKILL.md` | Replaced duplicated full regeneration procedure with shared lifecycle reference | Release gate passed. |
| `agent-playbook/README.md`, `.claude-plugin/marketplace.json`, `agent-playbook/.claude-plugin/plugin.json` | Documented `vibe-coding-fix` | Manifest JSON validation passed. |
| `tests/agent-playbook-eval-fixtures.py` | Added contracts for health-to-fix handoff and fix safety | `bash tests/agent-playbook-eval-fixtures.sh` passed. |

## Routed / Deferred
| Finding | Target Skill Or Owner | Reason |
|---|---|---|
| Runtime duplicate skill registrations across installed cache roots | User/runtime configuration | This repo's marketplace has no duplicate local plugin entries. Cleanup requires choosing a canonical installed plugin source outside the repo. |
| Broader `idea-to-ship` artifact ownership duplication | Future local cleanup | Existing fixture coverage is strict; this pass changed only the highest-noise descriptions and issue-evaluator duplication. |
| Agent/harness audit overlap | `agent-playbook:context-audit`, `agent-playbook:tool-review`, or `antifragile:antifragile-agent` | The skills have distinct boundaries when read in full; deeper consolidation should be designed separately. |

## Checks Run
| Command | Result | Notes |
|---|---|---|
| `bash tests/agent-playbook-eval-fixtures.sh` | pass | New `vibe-coding-fix` contract fixtures passed. |
| `bash tests/idea-to-ship-eval-fixtures.sh` | pass | Roadmap description change did not break idea-to-ship fixtures. |
| `scripts/release-gate.sh --mode all` | pass | Validated 10 manifests, 30 skill frontmatters, 3 metadata files, whitespace, secret scan, and advisory fixtures. |

## Residual Risk
- Runtime duplicate registrations remain outside this repo. Fixing that should be an explicit user-owned runtime cleanup, not an automatic skill edit.
- Further body-size reduction is possible in `review-pr` and `fix-pr-comments`, but the largest repeated code-style lifecycle blocks were already extracted.
