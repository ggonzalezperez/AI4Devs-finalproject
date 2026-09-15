# Task QR Report: "Connect another device" screen

## Status: DONE

## Commit
- `fb83af2` feat(frontend): in-app 'connect device' screen with URL + QR

## Files changed
- `frontend/package.json` + `frontend/package-lock.json` — added `qrcode.react` dependency
- `frontend/src/i18n/translations.ts` — added 6 `connect.*` keys to both `es` and `en` sections
- `frontend/src/screens/ConnectDevice.tsx` — new screen (verbatim from brief)
- `frontend/src/App.tsx` — added import + route `/familia/conectar` inside `<ProtectedRoute />`
- `frontend/src/screens/WhoExplores.tsx` — added link to `/familia/conectar` with `connect.link` key
- `frontend/src/screens/ConnectDevice.test.tsx` — new test (verbatim from brief)

## Self-review checklist
- [x] URL shown = `window.location.origin`
- [x] QR encodes it (`<svg>` present in the DOM via `<QRCodeSVG>`)
- [x] Localhost warning (`role="alert"`) appears only when `isLocal` is true
- [x] Link added in WhoExplores family screen
- [x] Route `/familia/conectar` is inside `<ProtectedRoute />` in App.tsx
- [x] No extra features added (YAGNI)

## Test results
All 39 tests passed (22 test files). The new ConnectDevice test passed with no flakiness — `document.querySelector("svg")` reliably finds the QR SVG in jsdom.

## Lint results
`npm run lint` (tsc --noEmit) exited clean with no errors.

## Notes
- `qrcode.react` renders locally, no external service calls
- The localhost warning is visible in jsdom tests (since `window.location.origin` is `http://localhost:3000`)
- The brief's verbatim test code worked without adaptation

## Task Review (Spec + Quality)

**Spec compliance:** PASS — all 12 requirements verified in diff.
**Task quality:** Approved

Minor findings (no fix required for merge):
- `setTimeout` in `copy()` lacks cleanup on unmount (React 18 strict mode warning risk)
- Back link `←` has no `aria-label` for screen readers
- Inline styles throughout (matches brief but inconsistent with codebase CSS patterns)
