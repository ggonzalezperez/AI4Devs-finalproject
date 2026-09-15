# Task B1b Report — Conversational lesson follow-up chips (frontend)

**Status:** DONE

**Commit:** `706d710` — `feat(frontend): conversational lesson follow-up chips`

**Branch:** `feature-lecciones-ricas` (no push)

## Files changed

- `frontend/src/api/nucleo.ts` — added `follow_ups: string[]` to `Lesson` type
- `frontend/src/i18n/translations.ts` — added `"lesson.more"` key in es + en
- `frontend/src/screens/LessonScreen.tsx` — full rewrite per brief: `busy` state, `useEffect` resets `lesson/playing/result` on `id` change, `startFollowUp()` helper, `moreChips` rendered on intro screen and correct-answer screen
- `frontend/src/screens/LessonScreen.test.tsx` — added `follow_ups` to mock, added assertions for `¿Quieres saber más?` and `¿Por qué llueve?`

## Test results

`npm test`: **33 tests passed, 0 failed** (20 test files)
`npm run lint` (tsc --noEmit): **clean**

## Self-review

- Chips appear on the lesson intro (below "¡A jugar!") and on the correct-answer screen (below "Ver mis islas").
- Tapping a chip calls `createLesson(question)` then navigates to `/jugar/leccion/${next.id}`.
- The `useEffect` dependency on `id` resets all state, so navigating to a new lesson shows its intro and not a stale quiz/result.
- All pre-existing test assertions remain green; the new assertions verify i18n label and chip text render.

## Concerns

None. Implementation matches brief exactly.
