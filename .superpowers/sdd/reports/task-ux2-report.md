# Task UX2 Report: Separate Family and Child Sessions

## Status: DONE

## Commit
- SHA: `55ec229`
- Subject: `fix(frontend): separate family and child sessions (parent stays logged in)`
- Branch: `feature-ux-improvements` (not pushed)

## Changes Applied

### `frontend/src/api/client.ts`
- Added `CHILD_TOKEN_KEY = "chispa_child_token"` constant.
- Exported `setChildToken(token)` and `getChildToken()` for the child slot.
- Changed `Options.auth` type from `boolean` to `boolean | "child"`.
- `apiFetch` now picks token by: `auth === "child"` → `getChildToken()`, else `getToken()`.

### `frontend/src/api/nucleo.ts`
- All 5 functions (`createLesson`, `getLesson`, `answerLesson`, `getSuggestions`, `getKnowledge`) changed from `auth: true` to `auth: "child"`.

### `frontend/src/screens/ChildAccess.tsx`
- Swapped `setToken` import for `setChildToken`.
- Child login result stored via `setChildToken(res.access_token)` — family token (`chispa_token`) is never touched.

### Test files (5 files)
- `nucleo.test.ts`, `Spark.test.tsx`, `LessonScreen.test.tsx`, `MyKnowledge.test.tsx`: changed `setToken("child-tok")` → `setChildToken("child-tok")` and updated imports.
- `ChildAccess.test.tsx`: changed assertion from `localStorage.getItem("chispa_token")` to `localStorage.getItem("chispa_child_token")`.

## Test Results
- 16 test files, 26 tests — all PASS.

## Lint
- `tsc --noEmit` — clean, no errors.

## Self-Review
- Family token (`chispa_token`) is never written by child login — `ChildAccess` now calls `setChildToken` only.
- All nucleo API calls (child-world) use `auth: "child"` which resolves to `getChildToken()` (`chispa_child_token`).
- Family session (`SessionContext`, `setToken`) remains completely isolated from child PIN login flow.
- No concerns identified.
