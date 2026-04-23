# Kueue Code Style and Conventions

## 1. Language and Frameworks

**Language:** Go 1.25 (as specified in `go.mod`).

**Core Frameworks and Libraries:**
- **controller-runtime** (`sigs.k8s.io/controller-runtime`) — primary Kubernetes controller framework for reconcilers, webhooks, and manager lifecycle.
- **client-go** (`k8s.io/client-go`) — Kubernetes API client, event recording, work queues.
- **go-logr / zap** — structured logging via `github.com/go-logr/logr` and `go.uber.org/zap`.
- **Ginkgo v2 + Gomega** — BDD test framework for integration/e2e tests.
- **go-cmp** — deep equality comparison in unit tests.
- **MockGen** (`go.uber.org/mock`) — interface mocking.
- **Prometheus client** — metrics via `github.com/prometheus/client_golang`.
- **k8s.io/component-base featuregate** — feature flag system.
- **kubebuilder markers** — CRD and webhook generation through code comments.

## 2. Naming Conventions

### Variables
- `camelCase` throughout. Short names are idiomatic in tight scopes (`wl`, `cq`, `log`, `r`).
- Receiver names are short abbreviations of the type: `r` for a reconciler, `c` for cache, `w` for webhook, `s` for scheduler.
- Context always named `ctx`.
- Unexported errors use lowercase: `errQNotFound`; exported errors use `Err` prefix: `ErrCohortNotFound`.

### Functions and Methods
- `PascalCase` for exported, `camelCase` for unexported.
- Constructor functions follow the `New<Type>` pattern: `NewWorkloadReconciler`, `NewClusterQueue`.
- Functional option constructors follow `With<Feature>`: `WithWaitForPodsReady`, `WithFairSharing`.
- Test helper functions use `Make<Type>` builders: `MakeWorkload`, `MakeClusterQueue`.
- `Obj()` is the terminal method on builder/wrapper types.

### Types
- Exported structs use `PascalCase`: `WorkloadReconciler`, `ClusterQueueSnapshot`.
- Typed string aliases for domain concepts: `ClusterQueueReference`, `CohortReference`, `PodSetReference`.
- Interface names are descriptive nouns or `<Verb>er` patterns: `GenericJob`, `WorkloadUpdateWatcher`.

### Files
- `snake_case` filenames throughout Go source.
- Convention: `<resource>_<kind>.go` — e.g., `workload_controller.go`, `clusterqueue_webhook.go`.
- Generated files prefixed `zz_generated.`.

## 3. Import Organization

Managed with **gci**, organized into four sections:
1. **Standard library** — `"context"`, `"fmt"`, `"slices"`
2. **Third-party** — `github.com/go-logr/logr`, `k8s.io/...`, `sigs.k8s.io/controller-runtime/...`
3. **Internal kueue** — `sigs.k8s.io/kueue/...`
4. **Blank imports** — `_ "k8s.io/client-go/plugin/pkg/client/auth"`

Import aliases: `corev1`, `batchv1`, `metav1`, `kueue`, `config`, `ctrl`, `apierrors`, `apimeta`.

## 4. Error Handling Patterns

- Sentinel errors as package-level `var` blocks with `errors.New`.
- Error wrapping with `fmt.Errorf("...: %w", err)`.
- controller-runtime conventions: `ctrl.Result{}, nil` on success, `ctrl.Result{}, err` for requeue.
- `client.IgnoreNotFound(err)` for delete operations.
- Validation errors use `field.ErrorList` with `.ToAggregate()`.
- `utilruntime.Must(...)` in `init()` for scheme registration.

## 5. Testing Patterns

### Unit Tests
- Table-driven tests with `map[string]struct{}` pattern.
- `cmp.Diff` for equality (never `reflect.DeepEqual`).
- `t.Context()` instead of `context.Background()`.
- Fake clocks: `testingclock.NewFakeClock(now)`.

### Integration / E2E Tests
- Ginkgo v2 with Gomega, structured with `Describe`/`BeforeEach`/`It`.
- `envtest` for integration tests.
- `Eventually` and `Consistently` for condition polling.
- Labels: `ginkgo.Label("area:<area>", "feature:<feature>")`.

### Test Helpers
- `Make<Type>` builders in `pkg/util/testing/` — fluent chaining ending with `.Obj()`.
- MockGen mocks in `/internal/mocks/`.
- Feature gate manipulation: `features.SetFeatureGateDuringTest(tb, features.SomeFeature, true)`.

## 6. Code Organization

```
apis/                   # CRD API type definitions (config/, kueue/)
cmd/kueue/              # binary entrypoint
client-go/              # generated typed clients
pkg/
  cache/                # hierarchy, queue, scheduler caches
  controller/           # core controllers, jobframework, per-integration jobs
  features/             # feature gate definitions
  metrics/              # Prometheus metrics
  scheduler/            # scheduling loop, flavor assignment, preemption
  util/                 # utilities, testing helpers
  webhooks/             # defaulting and validation
  workload/             # workload domain logic
internal/mocks/         # generated mockgen interfaces
test/integration/       # envtest-based tests
test/e2e/               # end-to-end tests
hack/                   # scripts, code generation
```

## 7. Comment and Documentation Style

- Apache 2.0 license header on every `.go` file.
- Exported symbols have `//` doc comments starting with the symbol name.
- kubebuilder markers for RBAC, CRD validation, webhooks.
- Feature gate constants have structured `// owner:` / `// kep:` comments.

## 8. Common Idioms

- Functional options pattern for constructors with many parameters.
- `ptr.To(value)` from `k8s.io/utils/ptr` for pointer helpers.
- `slices` package instead of `sort` (enforced by `forbidigo`).
- `sync.WaitGroup.Go` over manual `Add`/`Done` (enforced by `revive`).
- Struct embedding for compile-time interface assertions: `var _ reconcile.Reconciler = (*Reconciler)(nil)`.
- `ctrl.LoggerFrom(ctx)` for structured logging with V-levels (V(2) normal, V(3) detailed, V(5) webhook).

## Reviewer Preferences

Extracted from PR review comments on recent PRs. Listed most-to-least frequently observed.

### 1. Import Ordering (Enforced by `gci`)
Four groups: std / third-party / kueue / blank. PRs fail CI if wrong. (All Go PRs)

### 2. `cmp.Diff` Over `reflect.DeepEqual`
Use `cmp.Diff` with `cmpopts` for all test equality assertions. Format: `(-want +got)`. (#10192)

### 3. `slices` Package Instead of `sort` (Enforced by `forbidigo`)
Never use `sort.Slice`, `sort.Sort`, etc. Use `slices.SortFunc`, `slices.Sort`. (CI)

### 4. `Make<Type>` Constructor Naming — No `Wrapper` Suffix
Test builders named `Make<Type>`, not `Make<Type>Wrapper`. `Wrapper` stays on the struct type only. (#10191, #10169)

### 5. Typed `field.ErrorList` Assertions
Assert against `field.ErrorList` not `wantErr bool + wantErrCount int`. Compare with `cmp.Diff` + `cmpopts.IgnoreFields`. (#10192)

### 6. Field Doc Comments Start with camelCase Name
API field comments must start with the serialized JSON field name. Enforced by KAL `commentstart`. (#10185)

### 7. No Variable Shadowing of Package Aliases
Local variables must not shadow imported package aliases. (#10185)

### 8. No Commented-Out Code
Delete commented-out code before merge. (#10185)

### 9. `t.Context()` in Tests (Enforced by `usetesting`)
Use `t.Context()` not `context.Background()` or `context.TODO()` in tests. (CI)

### 10. `//nolint` Must Name Linter + Explain
Every `//nolint:` needs specific linter name and explanation. Enforced by `nolintlint`. (CI)

### 11. No Thin Redundant Wrapper Functions
Don't create convenience wrappers that merely forward arguments. (#10226)

### 12. Self-Documenting Makefile Variables
Makefile variables should be self-explanatory or have inline comments. (#10199)

### 13. Doc Persona Separation
`tasks/run/` = batch user, `tasks/manage/` = admin. No "Overview" as first heading. (#10077)

### 14. API Type Conventions (KAL `kubeapilinter`)
No bool/float/Duration fields. Only int32/int64. Optional = pointer + omitempty. Required = non-pointer, no omitempty. Every field needs `// +optional` or `// +required`. (CI)

### 15. `sync.WaitGroup.Go` (Enforced by `revive`)
Prefer `wg.Go(func() { ... })` over manual `Add`/`Done`. (#9892)

### 16. Extract Shared Test Helpers
Deduplicate repeated test setup into `pkg/util/testing` or `test/util`. (#9788, #9969)

### 17. Split Large Utility Packages
Split monolithic util packages into focused sub-packages. (#10121, #10142)
