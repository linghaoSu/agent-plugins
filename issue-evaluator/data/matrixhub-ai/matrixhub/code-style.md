<!-- generated: 2026-04-03 | commits-analyzed: 8d926d3f93f9ba290083b04bf11ff3a2a6d8fd34 -->

# MatrixHub UI Code Style Guide

## Stack
- TypeScript 5.9 (strict), React 19, Vite 7, pnpm
- Mantine v8, TanStack Router v1 (file-based), TanStack Query v5, TanStack Form v1, Zod 4
- i18next + react-i18next, @tabler/icons-react, mantine-react-table v2 beta
- API: gRPC/HTTP gateway, SDK at `@matrixhub/api-ts/*`

## TypeScript
- `strict: true`, `verbatimModuleSyntax`, `erasableSyntaxOnly`
- Always `import type` for type-only imports
- Prefer type inference over explicit generics
- Use `satisfies` over `as`; `as const` on query key arrays
- `interface` for object shapes, `type` for unions/aliases
- Prefix unused params with `_`

## Naming
- Components: `PascalCase.tsx`; Hooks: `camelCase.ts` with `use` prefix
- Query files: `{feature}.query.ts`, mutations: `{feature}.mutation.ts`, schemas: `{feature}.schema.ts`
- Variables/functions: `camelCase`; Constants: `SCREAMING_SNAKE_CASE`
- Props interfaces: `{ComponentName}Props`, exported alongside component

## Imports
Ordered: built-in → external → internal (`@/*`, `@matrixhub/api-ts/*`) → relative → type-only. Blank line between groups. SVGs use `?react` suffix.

## Formatting (ESLint @stylistic, no Prettier)
- Single quotes, 2-space indent, 150 char max line, trailing commas on multiline
- 1tbs brace style, always use braces for `if`/`else`
- Blank lines: after type/interface declarations, before `return`, before function declarations

## Components
- Named function declarations (not arrow functions at module level)
- Use Mantine layout primitives (Stack, Group, Flex, Box, Paper) over raw `div`
- `useDisclosure` for boolean open/close; `useEffectEvent` for stable callbacks
- JSX: shorthand fragments `<>`, boolean shorthand, no useless fragments

## TanStack Query
- Query key factories with `as const`; `queryOptions()` / `mutationOptions()` factory functions
- Custom hooks only when adding real behavior (e.g., `placeholderData: keepPreviousData`)
- Global error/notification handling via `QueryCache`/`MutationCache` — no per-component try-catch

## TanStack Router
- Route files are thin adapters; complex UI in `src/features`
- `validateSearch` with Zod, use `.default()` + `.catch()` for search params
- `void context.queryClient.ensureQueryData(...)` in loaders (non-blocking)
- `getRouteApi(...)` for typed hooks outside route files

## TanStack Form
- Import `useForm` from `@/shared/hooks/useForm` (not `@tanstack/react-form`)
- Schema-first: define Zod schema, pass as field validators
- `fieldError(field)` from `@/shared/utils/form` for error display
- Reset forms on modal open via `useEffectEvent` + `useEffect`

## i18n
- All user-facing strings through locale files, never hardcoded
- Both `en` and `zh` must be in sync
- Locale JSON keys use nested objects; files organized by `locales/{lang}/*.json`

## Styling
- Mantine-first: component props → semantic CSS vars → `--app-*` tokens → palette indices (last resort)
- Never hardcode hex colors, raw font sizes, or spacing values
- CSS Modules sparingly, co-located with component

## Reviewer Preferences
1. Reuse shared utilities — never duplicate existing helpers
2. Prefer framework built-ins (Mantine, TanStack) over ad-hoc workarounds
3. Zod v4: `.catch()` + `.default()`, use `error` not `message` in `refine`
4. i18n completeness: both locales in sync, correct key specificity, full-width Chinese punctuation
5. Boolean props: `enable*` prefix (default `true`) not `hide*` (default `false`)
6. Accessibility: all interactive icons must be keyboard-focusable with `aria-label`
7. Normalize query keys; preserve `placeholderData` when refactoring
8. Remove dead/commented-out code before merging
9. Use router utilities for navigation, not native browser APIs
10. Follow existing patterns for pagination, modal sizes, status rendering
