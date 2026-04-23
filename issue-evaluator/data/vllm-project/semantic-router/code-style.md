<!-- generated: 2026-04-08 | commits-analyzed: 3a6197ddd0e67212cc7eb470eca0629120ae27cc -->

# Code Style Guide — Semantic Router Dashboard Frontend

**Path:** `dashboard/frontend/src/`
**Stack:** React 18, TypeScript 5, Vite 5, Zustand 5, React Router 6, CSS Modules

---

## 1. Language and Framework

- **TypeScript** with strict mode (`strict: true`, `noUnusedLocals`, `noUnusedParameters`, `noFallthroughCasesInSwitch`). All source files use `.ts` / `.tsx`.
- **React 18** with functional components only. The sole exception is `ErrorBoundary`, which uses a class component (required by React's error boundary API).
- **Vite** as bundler with `moduleResolution: "bundler"`, `target: ES2020`, `jsx: "react-jsx"`.
- **Zustand** for global/shared state. Local component state uses `useState` / `useReducer`.
- **React Router 6** for client-side routing.

## 2. TypeScript Conventions

- All function parameters and return values must be typed.
- `any` is allowed only as a warning — treat as a lint warning to clean up.
- Unused variables prefixed with `_` are exempted from `no-unused-vars` (`argsIgnorePattern: "^_"`).
- **`interface`** for object shapes (props, context values, store state/actions).
- **`type`** for union types, discriminated unions, aliases, and function signatures.
- Always narrow errors with `err instanceof Error ? err.message : String(err)`.
- Use `@/` alias (maps to `./src/`) for imports that cross directory boundaries. Relative imports only within the same directory.

## 3. Naming Conventions

| Item | Convention | Example |
|---|---|---|
| React components | `PascalCase` | `BuilderPage`, `DashboardHealthCard` |
| Prop interfaces | `PascalCase` + `Props` suffix | `BuilderStatusBarProps` |
| Custom hooks | `camelCase` + `use` prefix | `useBuilderEntityActions` |
| Zustand store hooks | `use` + name + `Store` | `useDSLStore` |
| Functions/helpers | `camelCase` | `renderAuthenticatedRoutes` |
| Module-level constants | `SCREAMING_SNAKE_CASE` | `VALIDATE_DEBOUNCE_MS` |
| Types/interfaces | `PascalCase` | `DSLState`, `EditorMode` |
| CSS module classes | `camelCase` | `styles.statusBar` |
| Component files | `PascalCase.tsx` | `BuilderPage.tsx` |
| Support/util files | `camelCase.ts` | `builderPageTypes.ts` |
| CSS modules | `ComponentName.module.css` | `BuilderPage.module.css` |
| Page sub-files | Prefixed with page name | `builderPageStatusBar.tsx` |

## 4. File and Directory Organization

```
src/
  App.tsx               # Route shell only
  appRouteSupport.tsx   # Route table
  components/           # Shared/reusable UI
  pages/                # Pages + page-scoped support
  stores/               # Zustand (state + types + helpers split)
  contexts/             # React contexts (provider + shared + hook)
  hooks/                # Reusable custom hooks
  types/                # Pure TS types
  utils/                # Stateless utilities
  lib/                  # Low-level integrations (WASM, DSL)
```

### Splitting rules
- `FooPage.tsx` — component; `fooPageSupport.ts` — helpers; `fooPageTypes.ts` — types; `fooPageBar.tsx` — sub-components; `useFooActions.ts` — extracted hooks
- Stores: `dslStore.ts` (create), `dslStoreTypes.ts` (interfaces), `dslStoreSupport.ts` (helpers)
- Contexts: `FooContext.tsx` (createContext), `FooContextShared.ts` (types), `FooProvider.tsx` (provider), `useFoo.ts` (hook)

## 5. Component Patterns

- All components are `React.FC` or `React.FC<Props>`.
- **Default export** for page components. **Named export** for sub-components, hooks, utilities.
- Props interface defined immediately before the component, or in `fooPageTypes.ts` for shared types.
- Section dividers: `// ---------- Section Name ----------`

## 6. State Management

- `useState` for UI state. `useRef` for non-rendering mutable values.
- Zustand: destructure only what you need. Imperative: `useDSLStore.getState()`.
- `useMemo` / `useCallback` with complete dependency arrays.
- Async in effects: wrap in inner async function, call with `void`.

## 7. Import Organization

1. React core
2. Third-party libraries
3. `@/stores/...`
4. `@/types/...` (with `import type`)
5. CSS module import
6. Local relative imports
7. `@/contexts/...`, `@/utils/...`, `@/hooks/...`

## 8. Styling

- CSS Modules for scoped styles. Design tokens via CSS custom properties in `index.css`.
- Never hard-code colors, font sizes, spacing — use `var(--token-name)`.
- Inline styles only for dynamic values.

## 9. Error Handling

- Display errors as inline banners with retry. Don't swallow silently.
- Console logging with bracketed module prefix: `console.error('[ModuleName] ...')`.
- Silent polling errors only when transient.

## 10. API / Fetch Patterns

- Use patched `window.fetch` (auto Bearer token). Inline in store actions/hooks.
- Always check `resp.ok`. Parse with typed cast.
- Custom events for cross-component communication bypassing the store.

## 11. Routing

- Routes in `appRouteSupport.tsx` as `ReadonlyArray<LayoutRouteDefinition>`.
- Route paths use kebab-case.

## 12. Anti-patterns to Avoid

- No page-specific logic in `App.tsx`.
- No context Provider import from the `useXxx` hook file.
- No `@ts-ignore` without explanation.
- No hard-coded design values.
- No `async` effects without inner function wrapper.
- No `ReadonlyArray` mutation — always return new objects from `set(...)`.

---

## Reviewer Preferences

### 1. Fill in PR Template Completely (5 PRs: #1717, #1716, #1690, #1699, #1670)
Every PR must have meaningful Purpose, Test Plan, Test Result sections. Title must use module-aligned prefix (e.g., `[CLI]`, `[Docs]`).

### 2. Docs/Examples Must Match Actual Config Schema (4 PRs: #1687, #1686, #1671, #1702)
Only document fields that exist in the current schema. Land implementation first, then docs.

### 3. Use Structured Logging; No `fmt.Printf` in Runtime Code (3 PRs: #1692, #1689, #1687)
Use `logging.Debugf`, `ComponentEvent`, etc. Never `fmt.Printf` to stdout from library code.

### 4. Prefer String-Literal Unions Over Plain `string` (2 PRs: #1707, #1719)
Fields with a fixed set of valid values must be typed as string-literal unions, not `string`.

### 5. Add Nil Guards to Exported Callback-Accepting Functions (PR #1692)
Exported helpers accepting function arguments must guard against `nil`.

### 6. Comments Must Be Technically Accurate (3 PRs: #1689, #1538, #1671)
No inaccurate format descriptions, unexplained magic numbers, or misleading analogies.

### 7. Use `errors.Is` / `os.IsNotExist` Over String-Matching Errors (PR #1687)
Substring-matching error messages is brittle across OSes and wrapped errors.

### 8. Avoid Fixed `time.Sleep` in Tests (PR #1538)
Use bounded retry/poll loops with `ctx.Done()` instead.

### 9. Test Assertions Should Use Named Constants (PR #1538)
Reference the controlling constant, not a magic number.

### 10. Wire New Tests Into CI / Make Targets (PR #1697)
Tests not invoked by any CI gate provide no real coverage.

### 11. Avoid Computing Same Expression Twice in JSX (PR #1707)
Store computed values in a local variable; don't call the same helper twice.

### 12. Declare Transitive npm Dependencies Explicitly (PR #1689)
Don't rely on hoisted transitive deps — add as direct dependency.

### 13. Centralize Module/Key Lists (PR #1704)
Same list in multiple places creates drift risk. Single source of truth.

### 14. Keep Translation `source_commit` in Sync (PR #1719)
Update translation frontmatter when English source changes in the same PR.

### 15. Use Canonical Field Names Consistently (PR #1670)
Align field names across config schema to avoid silent misconfiguration.

### 16. Avoid Hardcoding Values Already in Config (PR #1719)
Source URLs/constants from shared config, don't duplicate.

### 17. Image Alt Text Must Be Descriptive (PR #1722)
No empty alt text — provide meaningful description for accessibility.
