# Design Review - Extract Evaluate-Issue Prompts

**Slug:** ITS-ROADMAP-009
**Date:** 2026-05-15
**Reviewer:** multi-agent: architecture correctness -> runtime-native reviewer; implementation/testability -> runtime-native reviewer
**Iterations:** 3
**Result:** clean
**Mode:** multi-agent
**Degradation reason:** none

## Issues Raised & Resolution

| # | Severity | Issue | Resolution |
|---|---|---|---|
| 1 | critical | The design treated non-strict staged release gate as authoritative even though fixture checks are advisory unless strict, and the fixture helper reads the working tree rather than the staged index. | Fixed in `architecture.md` Data Flow and Test Strategy Hooks: require `scripts/release-gate.sh --mode staged --strict`, `scripts/release-gate.sh --mode all --strict`, explicit staged-name checks, and no unstaged remainder on implementation paths. |
| 2 | critical | The design added a compact output/token/error contract with `outputs_written: []`, contradicting the no-output-contract-change requirement and ignoring possible code-style guide writes. | Fixed in `architecture.md` Interfaces: remove that contract from this roadmap item and explicitly defer any output-contract change to a later item. |
| 3 | warning | FR-12 depended on fixture coverage, but the architecture did not specify exact contract checks, IDs, or invariant groups. | Fixed in `architecture.md` Test Strategy Hooks: added a concrete fixture contract matrix for skill references, Round 2 prompt, Round 3 prompt, and final template. |
| 4 | warning | The single implementation stage hid the red-first test gate and made fixture regression behavior less explicit. | Fixed in `architecture.md` Staged Implementation Plan: split Stage 1 into red fixture gate, verbatim extraction, and verification checkpoint substeps. |
| 5 | warning | The extraction procedure did not pin source block boundaries or require verbatim preservation, so semantic prompt drift could slip in during cleanup. | Fixed in `architecture.md` Extraction Procedure: require verbatim copying of the current Round 2, Round 3, and Step 4 blocks before replacing inline text; wording cleanup is out of scope. |
| 6 | warning | Runtime behavior was undefined if an installed plugin was missing an extracted prompt/template file. | Fixed in `architecture.md` Interfaces and Failure Modes: `evaluate-issue` must read each artifact before use and terminally stop if it is missing or empty; no reconstruction from memory. |
| 7 | warning | The final template contract required a description-mode line but did not explain that the line currently lives in Step 0, not the Step 4 wrapper. | Fixed in `architecture.md` Extraction Procedure: add the exact Step 0 description-mode line as an optional conditional line immediately after the issue heading. |
| 8 | warning | The final template fixture required only `## Issue Evaluation`, leaving the issue-title placeholder under-protected. | Fixed in `architecture.md` Interfaces and Test Strategy Hooks: require `## Issue Evaluation: <issue-title>`. |

## Review Rounds

| Round | Angle | Route | Verdict |
|---|---|---|---|
| 1 | architecture correctness | sub-agent | 1 critical, 2 warnings |
| 1 | implementation/testability | sub-agent | 1 critical, 4 warnings |
| 1 | UI/UX | not applicable | no `interface-design.md` |
| 2 | architecture correctness | sub-agent | 1 warning |
| 2 | implementation/testability | sub-agent | 1 warning |
| 2 | UI/UX | not applicable | no `interface-design.md` |
| 3 | architecture correctness | sub-agent | LGTM |
| 3 | implementation/testability | sub-agent | LGTM |
| 3 | UI/UX | not applicable | no `interface-design.md` |

## Residual Open Issues

None.

## Design Drift

No drift remains. The architecture still implements the requirements' prompt
extraction scope and explicitly avoids changing the public output contract.
`<issue-title>` appears in the architecture intentionally as a required final
template placeholder, not as unresolved content.

## Reviewer Final Verdicts

| Angle | Verdict |
|---|---|
| architecture correctness | LGTM |
| implementation/testability | LGTM |
| UI/UX | not applicable |

## Self-Review Notes

The chosen option still makes sense after revisions. The design now gives an
implementer enough detail to build the red-first fixture gate, preserve prompt
text verbatim, handle missing runtime artifacts loudly, and verify staged
content with strict release gates before implementation is considered done.
