---
name: antifragile-system
description: Audit the target project for resilience gaps — external dependency fallbacks, error handling, single points of failure, data safety, and observability.
argument-hint: "[focus-area] — optional: 'api', 'data', 'infra', 'all' (default: all)"
allowed-tools:
  - Bash
  - Read
  - Agent
---

# Antifragile System Audit

Audit the project in the current working directory for resilience and antifragility gaps. This is a codebase-level review, not an agent/plugin review.

If the user specifies a focus area, narrow the audit to that dimension. Otherwise audit all.

## Audit Dimensions

### 1. External Dependency Resilience

- **Third-party API calls**: find all HTTP client usage (fetch, axios, requests, http.Client, etc.). For each call site:
  - Is there a timeout configured? No timeout → Warning.
  - Is there retry logic with backoff? No retry on transient errors → Info.
  - Is there a fallback or circuit breaker? Critical path with no fallback → Warning.
- **Service dependencies**: find database connections, message queue connections, cache clients. Check for:
  - Connection pooling and reconnect logic.
  - Graceful degradation when the dependency is down (does the app crash or degrade?).
- **SDK/library version pins**: check if dependencies are pinned (`package-lock.json`, `go.sum`, `requirements.txt` with `==`). Unpinned dependencies → Info.

### 2. Error Handling Coverage

- **Unhandled promise rejections / uncaught exceptions**: find async calls without try/catch or `.catch()`. Look for `async` functions where errors would propagate unhandled.
- **Empty catch blocks**: find `catch {}` or `catch (e) {}` with no logic — swallowed errors hide failures.
- **Error propagation**: do errors bubble up with enough context? Look for `throw e` without wrapping (loses stack in some languages) or generic error messages that won't help debugging.
- **Input validation at boundaries**: check API endpoints, CLI argument parsing, config file loading. External input without validation → Warning.

### 3. Single Points of Failure

- **In-memory state without persistence**: find critical state stored only in memory (caches used as primary store, in-memory queues). Process restart = data loss → Critical.
- **Single-instance assumptions**: look for file locks, port bindings, or singleton patterns that prevent horizontal scaling. Flag as Info (may be intentional).
- **Hardcoded endpoints/credentials**: find hardcoded URLs, IPs, or credential strings. Should be environment variables or config → Warning.

### 4. Data Safety

- **Write operations without transactions**: find database writes (INSERT, UPDATE, DELETE) that aren't wrapped in transactions when they should be (multi-step mutations). No transaction on multi-step write → Warning.
- **Idempotency**: find API endpoints or message handlers that mutate state. Are they idempotent? Can a retry cause double-processing? Non-idempotent mutation endpoint → Warning.
- **Backup and migration**: check for database migration files. Are they reversible (has a down/rollback)? Irreversible migration → Info.

### 5. Observability Gaps

- **Logging coverage**: find critical paths (payment processing, auth, data mutations). Are errors logged with context (user ID, request ID, input)? Critical path with no logging → Warning.
- **Health checks**: does the app expose a health/readiness endpoint? Missing → Info for services.
- **Metrics**: are there any metrics/instrumentation (Prometheus, StatsD, OpenTelemetry)? Missing on a production service → Info.

### 6. Configuration Fragility

- **Environment-specific logic**: find `if env == "production"` or similar branching. Too many environment branches → Info.
- **Missing defaults**: find config reads (`process.env.X`, `os.Getenv`, `os.environ`) without fallback defaults. Missing default on non-secret config → Warning.
- **Secret management**: are secrets read from environment variables (good) or from files committed to the repo (Critical)?

## Output Format

Write the report to stdout:

```
# Antifragile System Audit

**Project:** <directory name>
**Language/Stack:** <detected>
**Date:** <date>
**Focus:** <focus-area or "all">

## Critical (data loss, security, or total failure risk)
- [ ] <finding> — <file:line> — <fix>

## Warning (degraded reliability under stress)
- [ ] <finding> — <file:line> — <fix>

## Info (hardening opportunity)
- [ ] <finding> — <file:line> — <fix>

## Passed
- <what looked good>

## Recommendations
1. <top priority fix>
2. <second priority>
3. <third priority>
```

Adapt the audit dimensions to the detected tech stack — skip dimensions that don't apply (e.g., don't check for database transactions in a pure CLI tool). Focus on findings that would actually cause production incidents, not theoretical concerns.
