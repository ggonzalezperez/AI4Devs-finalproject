# Task PWD-b Report: Change-password screen + forgot-password recovery flow

## Status: DONE

## Commit
- SHA: `5a09ac1`
- Subject: `feat(frontend): change-password screen + forgot-password recovery flow`

## Files Changed (11 files, 265 insertions, 5 deletions)

### Modified
- `frontend/src/api/auth.ts` — Added `RegisterResult` type; updated `registerFamily` return type to `RegisterResult`; added `changePassword` and `resetPassword` functions.
- `frontend/src/i18n/translations.ts` — Added all `pwd.*` keys (16 keys) to both `es` and `en` sections.
- `frontend/src/screens/CreateFamily.tsx` — Added `pending` state; changed register flow to show recovery code panel first without calling `login()`; "Continuar" button calls `login(token)` + navigate.
- `frontend/src/screens/Login.tsx` — Added "¿Olvidaste tu contraseña?" link pointing to `/recuperar`.
- `frontend/src/screens/WhoExplores.tsx` — Added `🔑 Cambiar contraseña` link pointing to `/familia/password`.
- `frontend/src/App.tsx` — Added imports for `ChangePassword` and `ResetPassword`; added public route `/recuperar`; added protected route `/familia/password`.
- `frontend/src/screens/CreateFamily.test.tsx` — Updated fetch mock to return `recovery_code`; updated assertion to check recovery code panel appears, then clicks "Continuar" and checks token stored.

### Created
- `frontend/src/screens/ChangePassword.tsx` — New screen with current/new/confirm password fields; calls `changePassword` API; redirects to `/familia` after 1.2s on success.
- `frontend/src/screens/ResetPassword.tsx` — New screen with email/recovery-code/new/confirm fields; calls `resetPassword` API; shows new recovery code on success.
- `frontend/src/screens/ChangePassword.test.tsx` — Simple render test verifying all form fields and submit button present.
- `frontend/src/screens/ResetPassword.test.tsx` — Simple render test verifying all form fields and submit button present.

## Test Results
- 26 test files, 46 tests — all passed.
- `CreateFamily.test.tsx`: all 3 tests green, including updated flow.
- `ChangePassword.test.tsx`: 1 test green.
- `ResetPassword.test.tsx`: 1 test green.

## Lint Results
- `tsc --noEmit` — no TypeScript errors, clean output.

## Key Implementation Notes
- The `isAuthenticated` guard in `CreateFamily` is preserved. Because `login()` is only called when the user clicks "Continuar" (not immediately after `registerFamily`), the recovery code panel renders correctly without triggering the redirect.
- `ApiError` is imported from `"../api/client"` (not `"../api/auth"`) in both new screens, as per brief.
- Test label queries used `getAllByLabelText` for `/nueva contraseña/i` to avoid ambiguity with "Repite la nueva contraseña" matching the same regex.

## Concerns
None. All flows implemented per brief, all tests green, TypeScript clean.

## Fix: setTimeout cleanup
- Changed direct setTimeout to useEffect with clearTimeout cleanup in ChangePassword.tsx
- Tests: 26 test files, 46 tests — all passed.
- Lint: clean

## Final Branch Review
Verdict: SHIP

### Open minor findings (no blocker)
- ChangePassword 400 mapping: any 400 (not just wrong-password) shows "current password incorrect" — confirm backend contract (low risk: backend only returns 400 for wrong current password)
- ResetPassword success panel: no `role="alert"` / accessible announcement for screen readers
- Copy button in CreateFamily: silent failure on non-HTTPS (clipboard API unavailable); no feedback to user
- ChangePassword back link `<Link to="/familia/explorar">←</Link>` lacks accessible label
- No submit-flow tests on ChangePassword or ResetPassword (smoke only)
