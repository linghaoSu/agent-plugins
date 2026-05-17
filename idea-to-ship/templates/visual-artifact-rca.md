# Visual Artifact RCA - <slug>

## Artifact Manifest

| Field | Value |
|---|---|
| artifact_path_or_redacted_url | <local path or redacted URL> |
| source command / CI job | <command or job> |
| test id / test title | <id / title> |
| project/browser | <project/browser> |
| retry index | <retry> |
| trace step/action or screenshot/video filename | <anchor> |
| timestamp | <timestamp> |
| inspected anchor range / line range / byte range | <bounded range> |
| snippet cap used | <cap> |
| redaction notes | <notes> |
| linked matrix cell IDs | <cell IDs> |

## Failure Analysis

| Field | Value |
|---|---|
| failure classification | product / test / environment / known-non-blocking / unknown |
| suspected cause | <cause> |
| next action/status | <next action> |

## Context-Safe Summary

- <bounded summary with exact anchors>

## Raw Artifact Policy

Do not paste raw logs, full HTML reports, traces, videos, screenshots, cookies,
auth state, signed artifact URLs, query-string tokens, or secret-bearing
snippets here. Prefer local artifact paths. If a URL is unavoidable, redact
query strings, fragments, signatures, tokens, and temporary credentials before
recording it, then reference bounded anchors instead of raw artifact content.
