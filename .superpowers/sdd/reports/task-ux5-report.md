# Task UX5 Report: Onboarding hints (demo mode + PIN explanation)

## Status: DONE

## Commit
- SHA: 31834e0
- Subject: `feat(frontend): onboarding hints (demo mode + PIN explanation)`
- Branch: `feature-ux-improvements` (no push)

## Changes

### `frontend/src/i18n/translations.ts`
Added 2 new keys to both `es` and `en` locales:
- `who.demoHint` — demo mode notice shown above the AI config link
- `addExplorer.pinHint` — PIN explanation shown below the PIN input

### `frontend/src/screens/WhoExplores.tsx`
Added a `<p>` element with `{t("who.demoHint")}` immediately above the `<Link to="/familia/ia">` element.

### `frontend/src/screens/AddExplorer.tsx`
Added `<small style={{ color: "#0a5a53", fontWeight: 600 }}>{t("addExplorer.pinHint")}</small>` as a sibling element after the PIN `<label>` (not inside it) to preserve the accessible name used by `getByLabelText(/Clave de 4 dígitos/i)` in the test.

## Tests
All 27 tests passed (17 test files). AddExplorer.test.tsx `getByLabelText` selectors unaffected because the `<small>` hint is a sibling of the `<label>`, not nested inside it.

## Lint
`npm run lint` (tsc --noEmit) exited cleanly with no output.

## Concerns
None. The placement of `<small>` as a sibling (not child) of the PIN label was required to avoid breaking the accessible label name used in the test.
