---
name: bootstrap-project-memory
description: Create or prune concise repo instructions such as CLAUDE.md and optional AGENTS.md. Use when agents lack project-specific commands, environment facts, gotchas, or boundaries.
---

# Bootstrap Project Memory

Write only facts an agent cannot cheaply infer from the repo. Target fewer than
200 lines and never replace human instructions without a reviewed diff.

## Arguments

- `--agents-md`: also create/update `AGENTS.md`.
- Remaining text: project notes or focus.

## Workflow

1. Read existing instruction files and repo rules. Inventory manifests,
   scripts, CI, editor config, env examples, generated-code markers, and tests.
2. Run safe discovery for exact build/test/lint commands and non-obvious
   environment constraints. Do not copy architecture or style already enforced
   by code/tooling.
3. Ask one batch only for facts the repo cannot answer: required services,
   must-run checks, hidden gotchas, and work agents must not perform.
4. Draft or merge concise sections for commands, environment, gotchas, and
   out-of-scope work. Prefer links over duplicated documentation.
5. Show the diff. Write only after approval when replacing or materially
   restructuring human content.

## Pruning

For an oversized file, classify each line as keep, move/link, or delete. Keep
project-specific facts whose removal would predictably cause failure. Delete
generic advice, architecture dumps, duplicated formatter rules, stale commands,
and tool tutorials.

## Completion

Verify commands and links, report assumptions, and confirm no unrelated file
changed. This skill does not initialize tools, install dependencies, or modify
global configuration.

Use `$agent-playbook:context-audit` when the question is diagnosis rather than editing.
