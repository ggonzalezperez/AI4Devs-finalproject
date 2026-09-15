# Task i18n Report: Multilenguaje (detección de navegador + selección por el usuario)

## Status: DONE

## Commit
- SHA: `1732fe7`
- Subject: `feat(frontend): i18n (browser detection + language switcher, es/en)`
- Branch: `feature-entrega2-chispa`
- Files changed: 15 (4 new, 11 modified)

## New files created
- `frontend/src/i18n/translations.ts` — Lang type, LANGS array, `translations` dict for `es`/`en` with 26 keys each
- `frontend/src/i18n/I18nContext.tsx` — `I18nProvider`, `useI18n`, `detectLang` (localStorage → navigator.language fallback)
- `frontend/src/components/LanguageSwitcher.tsx` — select widget consuming `useI18n`
- `frontend/src/i18n/I18nContext.test.tsx` — 2 tests: detectLang persistence, t() switching

## Files modified
- `frontend/src/main.tsx` — wrapped tree in `<I18nProvider>`
- `frontend/src/screens/CreateFamily.tsx` — refactored to use `t()`; added `<LanguageSwitcher />`
- `frontend/src/screens/Login.tsx` — refactored to use `t()`; added `<LanguageSwitcher />`
- `frontend/src/screens/AddExplorer.tsx` — refactored to use `t()`
- `frontend/src/screens/WhoExplores.tsx` — refactored to use `t()`
- `frontend/src/screens/ChildAccess.tsx` — refactored to use `t()`
- `frontend/src/screens/CreateFamily.test.tsx` — wrapped render in `<I18nProvider initialLang="es">`
- `frontend/src/screens/WhoExplores.test.tsx` — wrapped render in `<I18nProvider initialLang="es">`
- `frontend/src/screens/ChildAccess.test.tsx` — wrapped render in `<I18nProvider initialLang="es">`
- `frontend/src/App.test.tsx` — wrapped render in `<I18nProvider initialLang="es">`

## Test results
- 9 test files, **16 tests — all passed**
- New i18n test: 2/2 passed (detectLang + t() switching)
- Existing screen tests: all passed with `initialLang="es"` wrapper

## Lint
- `npm run lint` (tsc --noEmit): **no errors, no warnings**

## Concerns
- None. All code matches the brief verbatim.
- The React Router v7 future-flag warnings in test output are pre-existing (not introduced by this task).
