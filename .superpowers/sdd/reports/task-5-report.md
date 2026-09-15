# Task 5 Report: Enrutado con rutas protegidas

## Status
COMPLETE

## Commit
- SHA: fecdb84
- Subject: `feat(frontend): routing with protected routes and providers`
- Branch: `feature-entrega2-chispa`

## Files Changed
- **Created**: `frontend/src/routes/ProtectedRoute.tsx` — layout route that reads `isAuthenticated` from `useSession()` and either renders `<Outlet />` or redirects to `/login`.
- **Created**: `frontend/src/routes/ProtectedRoute.test.tsx` — TDD test written before implementation; 2 tests (redirect when unauthenticated, render content when authenticated).
- **Modified**: `frontend/src/App.tsx` — replaced single-h1 component with route tree: `/login` (public), `/familia` (protected via `<ProtectedRoute>`), `*` catch-all redirects to `/login`.
- **Modified**: `frontend/src/main.tsx` — wrapped app in `<SessionProvider>` + `<BrowserRouter>`.
- **Modified**: `frontend/src/App.test.tsx` — replaced old heading test with `MemoryRouter`+`SessionProvider` integration test.

## Test Summary
5 test files, 10 tests — all PASS (1.04 s)

| File | Tests |
|---|---|
| src/api/client.test.ts | 4 ✓ |
| src/routes/ProtectedRoute.test.tsx | 2 ✓ |
| src/App.test.tsx | 1 ✓ |
| src/auth/SessionContext.test.tsx | 1 ✓ |
| src/components/Button.test.tsx | 2 ✓ |

## TDD Order Followed
1. Wrote `ProtectedRoute.test.tsx` first — confirmed FAIL (module not found).
2. Created `ProtectedRoute.tsx` — tests green.
3. Updated `App.tsx`, `main.tsx`, `App.test.tsx`.
4. Full suite green.

## Concerns / Notes
- React Router v6 emits two future-flag warnings about `v7_startTransition` and `v7_relativeSplatPath`. These are advisory only, do not affect tests, and are expected with react-router-dom v6 without explicit future flags. No action needed for this task.
- `main.tsx` is not covered by tests (entry-point convention), which is standard for Vite+React projects.
