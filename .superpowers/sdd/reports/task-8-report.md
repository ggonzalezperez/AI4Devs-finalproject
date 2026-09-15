# Task 8 Report: CORS en el backend + CI del frontend + README

## Status: DONE

## Commit
- SHA: `dc7371d3f6e9ab743cd7638a2454fb0e0d10344a`
- Subject: `feat: CORS for frontend, frontend CI job and README`
- Branch: `feature-entrega2-chispa`

## Files Changed
| File | Action |
|------|--------|
| `backend/app/config.py` | Added `cors_origins: str = "http://localhost:5173"` field |
| `backend/app/main.py` | Added CORSMiddleware with `get_settings().cors_origins` |
| `backend/tests/test_cors.py` | Created CORS test (exact code from brief) |
| `.github/workflows/ci.yml` | Added `frontend` job alongside existing `backend` job |
| `README.md` | Created root README with local start instructions |
| `frontend/tsconfig.json` | Added `"vite/client"` to types (fixed pre-existing lint error) |
| `frontend/src/api/client.test.ts` | Fixed `vi.fn` generic type for `spy.mock.calls` (pre-existing TS error) |

## Test Results
- **Backend**: `20 passed` (19 prior + 1 new CORS test)
- **Frontend lint**: `tsc --noEmit` exits 0 (fixed 3 pre-existing TypeScript errors)
- **Frontend tests**: `14 passed` across 8 test files

## Notes / Concerns
- `frontend/package-lock.json` was already committed in a prior task — `npm install` confirmed it up-to-date with no changes.
- Two pre-existing TypeScript errors were fixed as part of getting `npm run lint` to pass:
  1. `client.ts`: missing `"vite/client"` in `tsconfig.json` types (caused `import.meta.env` to error).
  2. `client.test.ts`: `vi.fn` needed an explicit generic `(url: string, init?: RequestInit) => Promise<Response>` so `spy.mock.calls[0][1]` resolved to `RequestInit | undefined` instead of `undefined`.
- These fixes are additive and do not change runtime behavior.
- A `StarletteDeprecationWarning` about `httpx` appears in backend tests — pre-existing, unrelated to this task.

## Report file path
`C:/Users/gerx_/Desktop/LIDR/Proyecto Final/chispa/.superpowers/sdd/reports/task-8-report.md`
