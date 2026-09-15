# Task 3 Report: Cliente de API tipado + almacenamiento de token

## Status: DONE

## TDD Evidence

### RED (FAIL)
Ran `npm test src/api/client.test.ts` before creating `client.ts`.
Result: **FAIL** — `Error: Failed to resolve import "./client"` (module did not exist).

### GREEN (PASS)
After creating `frontend/src/api/client.ts` with exact code from brief:
```
src/api/client.test.ts (4 tests) 6ms
Test Files: 1 passed (1)
Tests:      4 passed (4)
```

## Full Suite
```
src/api/client.test.ts  (4 tests) - PASS
src/App.test.tsx        (1 test)  - PASS
src/components/Button.test.tsx (2 tests) - PASS

Test Files: 3 passed (3)
Tests:      7 passed (7)
Duration:   1.05s
```

## Files Created
- `frontend/src/api/client.ts` — `ApiError` class, `setToken`/`getToken` (localStorage key `chispa_token`), `apiFetch<T>` typed fetch wrapper.
- `frontend/src/api/client.test.ts` — 4 tests per brief spec (verbatim).

## Commit
- SHA: `f34a620`
- Message: `feat(frontend): typed API client with token storage and ApiError`
- Scope: only `frontend/` staged

## Concerns
None. All tests pass, implementation matches brief verbatim.
