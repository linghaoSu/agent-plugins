<!-- generated: 2026-04-03 | commits-analyzed: 5fa00453114ab0ae9b6c1b6ee6bae3c351b7ebc0 -->

# Argo CD Code Style and Conventions

## 1. Languages and Frameworks

**Backend (Go)**
- Go 1.26, module `github.com/argoproj/argo-cd/v3`
- gRPC for inter-service communication, Cobra for CLI, Logrus (aliased `log`) for logging
- controller-runtime + client-go for Kubernetes controllers
- testify (`assert`, `require`, `mock`) for testing; golangci-lint with gofumpt/goimports

**Frontend (TypeScript/React)**
- TypeScript 4.9.5 (`noImplicitAny: true`), React 16, Webpack 5, SASS
- RxJS 6, superagent for HTTP, argo-ui design system, monaco-editor
- ESLint 9 (flat config) + prettier; Jest 29 with ts-jest

## 2. Naming Conventions

**Go**: PascalCase exported, camelCase unexported. Short receivers (`s`, `ctrl`). Error vars prefixed `Err`. Constants PascalCase (`CompareWithLatest`).

**TypeScript**: PascalCase interfaces/types/components, camelCase functions/utils, kebab-case filenames (`application-details.tsx`).

## 3. Import Organization

**Go** — three groups: stdlib, third-party, internal. Mandatory aliases enforced by `.golangci.yaml`:
- `log "github.com/sirupsen/logrus"`, `appv1 "...v1alpha1"`, `apierrors "k8s.io/apimachinery/pkg/api/errors"`, etc.
- Standard lib aliased when colliding: `goio "io"`, `gosync "sync"`

**TypeScript** — third-party first, then internal, SCSS imports last. `* as models` namespace pattern common.

## 4. Error Handling

**Go**: `(T, error)` returns, `fmt.Errorf("...: %w", err)` wrapping, `status.Error(codes.*, ...)` at gRPC boundary. Security errors deliberately opaque (`PermissionDeniedAPIError`).

**TypeScript**: Promise `.then()/.catch()`, async/await, Observable error propagation.

## 5. Testing

**Go unit**: testify assert/require, table-driven `t.Run()`, mocks via mockery in `mocks/` sub-packages, `t.Context()` for contexts.
**Go E2E**: fluent Given/When/Then DSL in `test/e2e/`, dot-imports for DSL readability.
**TypeScript**: Jest 29, `test()` (not `it()`), co-located `*.test.ts(x)` files.

## 6. Key Patterns

- Constructor functions `New<Type>`, interface-backed mocks, structured logging with `log.WithFields`
- Environment config via `util/env.ParseNumFromEnv` / `ParseBoolFromEnv`
- Kubernetes work queue pattern with typed `workqueue.TypedRateLimitingInterface[T]`
- React: FC<Props>, services singleton, DataLoader from argo-ui, SCSS co-location

## Reviewer Preferences

### 1. Named Constants Over Magic Strings (PRs #27049, #26793)
Use existing or newly introduced named constants instead of literal strings (e.g., `appv1.KubernetesInClusterName` instead of `"in-cluster"`).

### 2. Narrow Focused Helpers Over Broad Function Reuse (PRs #26793, #26898)
When a caller needs only one field from a broad function like `GetSettings()`, extract a focused helper that reads only that data.

### 3. Explicit Nil-Guards Before Dereferencing (PRs #27049, #27001)
After any function call that can return nil (informers, cached objects), add an explicit nil-guard returning `fmt.Errorf(...)`.

### 4. Idiomatic Goroutine/Test Patterns (PR #27049)
Standard `wg.Add/Done` + error channels; never `require.*` from non-test goroutines. `for range N` over `for j := range N` when unused.

### 5. Self-Describing Parameter Names; Avoid Bare Booleans (PR #26673)
Prefer descriptive names, enums/options structs, or sibling methods over bare `bool` parameters.

### 6. Test Coverage for Every New Branch (PRs #26876, #27049)
Every new conditional branch needs a dedicated test fixture. Test names must describe actual behavior.

### 7. Keep Comments Synchronized With Implementation (PRs #26864, #27049)
Update all nearby comments when changing algorithms. Reference function names, not line numbers.

### 8. Warn/Log When CLI Flags Silently Overridden (PR #27022)
Emit `log.Warn` or add help-text when user-supplied flags are silently ignored.

### 9. Collect Errors in Loops (PR #26673)
Prefer error slices or `errors.Join` over a single `lastError` variable. Reset on success if using single slot.

### 10. Accurate Log/Status Messages (PR #26673)
Log messages must reflect actual behavior, not the intent of copied-from code. Watch for copy-paste errors.

### 11. Use `t.Context()` in Tests (PR #26673)
Use `t.Context()` rather than `context.Background()` in test code.

### 12. Update Docs/Release Notes When Expanding Features (PR #26898)
Feature scope expansions require documentation updates and release notes.
