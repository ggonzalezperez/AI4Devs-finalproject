# Task 7 Report: Añadir explorador, elegir explorador y acceso del niño con PIN

## Status: COMPLETE

## Commit
- SHA: `2013cfd`
- Subject: `feat(frontend): add explorer, crew selection and child PIN access`
- Branch: `feature-entrega2-chispa`

## Files Created/Modified
- **Created** `frontend/src/api/children.ts` — `listChildren`, `createChild`, `childLogin` using `apiFetch` with auth
- **Created** `frontend/src/screens/WhoExplores.test.tsx` — test: lists children from mocked API
- **Created** `frontend/src/screens/WhoExplores.tsx` — screen showing child buttons navigating to `/explorar/:id`
- **Created** `frontend/src/screens/AddExplorer.tsx` — form with name/birthdate/PIN, live age helper, `createChild` on submit
- **Created** `frontend/src/screens/ChildAccess.test.tsx` — test: 4-digit PIN triggers login and stores token in localStorage
- **Created** `frontend/src/screens/ChildAccess.tsx` — PIN keypad (buttons labeled 1-9, 0, ⌫), auto-submits on 4 digits
- **Modified** `frontend/src/App.tsx` — replaced with brief's version: `/familia` → redirect to `/familia/explorar`, new routes for WhoExplores, AddExplorer, ChildAccess

## Test Results
**14 tests passed, 0 failed** (8 test files total)
- `client.test.ts` (4), `Button.test.tsx` (2), `SessionContext.test.tsx` (1), `ProtectedRoute.test.tsx` (2), `App.test.tsx` (1), `WhoExplores.test.tsx` (1), `ChildAccess.test.tsx` (1), `CreateFamily.test.tsx` (2)
- `App.test.tsx` still passes (CreateFamily at root unchanged)

## Self-Review
- PIN keypad buttons use plain text content ("1"–"9", "0", "⌫") as their accessible names; `getByRole("button", { name: d })` finds them correctly in tests.
- `ageFrom()` correctly subtracts 1 year when the birthday hasn't passed yet in the current year (checks month and day).
- `ApiError` and `setToken` are properly exported from `../api/client`; imports verified.
- TDD order followed: WhoExplores test written before implementation (Step 2 → Step 3); ChildAccess test before implementation (Step 5 → Step 6).

## Concerns
None. All tests green, implementation matches brief exactly.
