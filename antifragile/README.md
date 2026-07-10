# Antifragile

`antifragile-audit --scope agent|system` provides one read-only entry point:

- `agent`: hooks, plugins, skills, dependency guards, state, and recovery.
- `system`: dependencies, errors, data safety, observability, and config.

The skill prints a ranked report and never mutates the target.
