# Task UX4 Report: Child-World Header + Lesson Readability

## Status: DONE

## Commit
- SHA: `7e6ef1f`
- Subject: `feat(frontend): child-world header (name + islands + home) and clearer lesson body`
- Branch: `feature-ux-improvements` (no push)

## Files Changed
- `frontend/src/api/nucleo.ts` — added `ChildProfile` type and `getProfile()` function
- `frontend/src/i18n/translations.ts` — added `child.hi`, `child.home`, `child.islands` keys (es + en)
- `frontend/src/components/ChildHeader.tsx` — new component (fetches /me/profile, shows home link + greeting + islands badge)
- `frontend/src/components/ChildHeader.test.tsx` — new test: verifies child name and islands render
- `frontend/src/screens/Spark.tsx` — `<ChildHeader />` as first child of `<ScreenCard>`
- `frontend/src/screens/MyKnowledge.tsx` — `<ChildHeader />` as first child of `<ScreenCard>`
- `frontend/src/screens/LessonScreen.tsx` — `<ChildHeader />` as first child in non-playing view; lesson body wrapped in white readable card (`<div>` replacing `<p>`)

## Tests
- 27/27 tests pass across 17 test files. All pre-existing screen tests remain green.
- `ChildHeader.test.tsx` (1 new test) verifies name and islands display.
- The `p?.name` guard in ChildHeader ensures screens whose fetch mocks return non-profile data do not break.

## Lint
- `npm run lint` (tsc --noEmit) exits clean with no errors.

## Concerns
- None. Implementation matches brief exactly.
